"""Manual cover title search, online preview, and non-destructive user selection."""
import ast
import json
import os
import subprocess
import sys
from pathlib import Path
import base64

import pytest
import artwork_gallery as art
from core import prepare_layout

ROOT = Path(__file__).resolve().parents[1]
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAOZrkK0AAAAASUVORK5CYII=')

@pytest.fixture(autouse=True)
def local_cache(tmp_path,monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path/'AppData'))


def test_manual_search_finds_shortened_game_names():
    catalog = ['Resident Evil (USA)', 'Resident Evil (Europe)',
               'Resident Evil 2 (USA)', 'Resident Evil 3 - Nemesis (USA)',
               'Resident Evil - Survivor (USA)', 'Biohazard (Japan)',
               'Ridge Racer (USA)']
    matches = art.manual_search_results('Resident Evil',catalog)
    assert matches[0]['title'] == 'Resident Evil (USA)'
    assert len([x for x in matches if 'Resident Evil' in x['title']]) == 5
    assert not any('Ridge Racer' in x['title'] for x in matches)
    assert art.manual_search_results('   ', catalog) == []


def test_manual_search_is_editable_and_tolerates_minor_typos():
    titles=['Final Fantasy VII (USA)','Final Fantasy VIII (USA)','Metal Gear Solid (USA)']
    assert any('Final Fantasy VII' in v['title'] for v in art.manual_search_results('Final Fantasy VII',titles))
    assert any('Metal Gear Solid' in v['title'] for v in art.manual_search_results('Metl Gear Solid',titles))
    assert not art.manual_search_results('xy',titles)


def test_search_does_not_assign_cover_even_on_exact_match(tmp_path):
    card=tmp_path/'VirtualCard'
    titles=['Resident Evil (USA)', 'Resident Evil (Europe)']
    found=art.manual_search_results('Resident Evil',titles)
    assert found
    assert not (card/'Media').exists()
    assert not art.cached_preview(card, 'PS1', 'Resident Evil Gore Edition').exists()


def test_preview_uses_local_windows_cache_and_keeps_nas_unmodified(tmp_path):
    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self,*exc): pass
        def geturl(self): return 'https://thumbnails.libretro.com/Sony%20-%20PlayStation/Named_Boxarts/Resident%20Evil%20%28USA%29.png'
        def read(self,n): return PNG
    opener_calls=[]
    def opener(request,timeout=None):
        opener_calls.append(request.full_url)
        return FakeResponse()
    card=tmp_path/'my-card'
    path=art.preview_search_cover(card,'PS1','Resident Evil (USA)',opener=opener)
    assert path.is_file() and path.read_bytes()==PNG
    assert 'ArtworkCache' in str(path)
    assert not card.exists()
    again=art.preview_search_cover(card,'PS1','Resident Evil (USA)',opener=lambda *args,**kw: pytest.fail('Should use cache'))
    assert again==path and len(opener_calls)==1


def test_preview_rejects_malicious_redirect(tmp_path):
    class Response:
        def __enter__(self):return self
        def __exit__(self,*exc):pass
        def geturl(self): return 'https://not-libretro.example/bad.png'
        def read(self,n): return PNG
    with pytest.raises(ValueError,match='redirect'):
        art.preview_search_cover(tmp_path/'card','PS1','Resident Evil (USA)',opener=lambda *args,**kw: Response())


def test_worker_manual_search_from_cached_catalog_with_real_game_unchanged(tmp_path):
    card=tmp_path/'card'
    prepare_layout(card)
    game=card/'ROMs'/'psx'/'Resident Evil Gore Edition.img'
    game.write_bytes(b'Test game file untouched')
    catalog=art.local_cache_root(card)/'catalog'/'PS1.json'
    catalog.parent.mkdir(parents=True,exist_ok=True)
    catalog.write_text(json.dumps(['Resident Evil (USA)','Resident Evil (Europe)','Biohazard (Japan)']))
    req={'mode':'search','workspace':str(card),'system':'PS1','label':game.stem,'query':'Resident Evil'}
    process=subprocess.Popen([sys.executable,'-u',str(ROOT/'artwork_worker.py')],cwd=ROOT,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
        env={**os.environ,'LOCALAPPDATA':os.environ['LOCALAPPDATA']})
    stdout,stderr=process.communicate(json.dumps(req)+'\n',timeout=10)
    assert process.returncode==0,stderr
    result=[json.loads(l) for l in stdout.splitlines() if l.strip()][-1]['data']
    assert result['mode']=='search' and len(result['results'])==2
    assert game.read_bytes()==b'Test game file untouched'
    assert not list(card.rglob('*.png'))


def test_application_wires_manual_search_and_preview_in_isolated_artwork_worker():
    src=(ROOT/'app.py').read_text(encoding='utf8')
    worker=(ROOT/'artwork_worker.py').read_text(encoding='utf8')
    ast.parse(src)
    for word in ['def open_manual_cover_search', 'def run_manual_cover_search',
                 'def preview_manual_cover', 'def apply_manual_cover',
                 'def manual_local_cover', 'Search for a game cover…',
                 "'mode':'search'", "'mode':'preview'"]:
        assert word in src
    assert "mode == 'search'" in worker and "mode == 'preview'" in worker
    assert 'QListWidget#CoverSearchResults' in src


def test_theme_scales_with_manual_results_selection():
    source=(ROOT/'app.py').read_text(encoding='utf8')
    definition=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='theme')
    scope={}
    exec(compile(ast.Module(body=[definition],type_ignores=[]),'theme','exec'),scope)
    for scale in (100,125,150):
        css=scope['theme'](scale)
        assert 'QListWidget#CoverSearchResults' in css
        assert 'background:#70b8ff' in css
