"""No-network safety tests for artwork gallery and isolated artwork helper."""
import base64
import json
import os
import subprocess
import sys
from pathlib import Path
from threading import Event

import pytest
import artwork_gallery as art
from core import prepare_layout

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAOZrkK0AAAAASUVORK5CYII=')
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def local_cache(monkeypatch, tmp_path):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'local-data'))


def test_region_tags_are_cleaned_but_edition_names_remain():
    assert art.clean_title('Resident Evil Gore Edition (USA)') == 'Resident Evil Gore Edition'
    assert art.key_title('Resident Evil Gore Edition (USA)') != art.key_title('Resident Evil (USA)')
    assert art.key_title('Resident Evil (USA) (En)') == art.key_title('Resident Evil (Europe)')


def test_conservative_match_never_misassigns_special_edition():
    index = ['Resident Evil (USA)', 'Resident Evil (Europe)', 'Resident Evil 2 (USA)']
    direct = art.find_art_matches('Resident Evil (USA)', index)
    assert direct['automatic'] == 'Resident Evil (USA)'
    special = art.find_art_matches('Resident Evil Gore Edition.img', index)
    assert special['automatic'] is None
    assert any('Resident Evil' in c['title'] for c in special['suggestions'])
    assert special['needs_review']


def test_catalog_index_parser_ignores_junk_and_url_decodes():
    html = b'<a href="../">Parent</a><a href="Resident%20Evil%20%28USA%29.png">cover</a><a href="bad.exe">no</a><a href="Resident%20Evil%20%28USA%29.png">dup</a>'
    assert art.parse_index(html) == ['Resident Evil (USA)']


def test_no_auto_match_when_titles_have_extra_meaningful_words():
    opts = ['Final Fantasy VII (USA)', 'Final Fantasy VIII (USA)', 'Final Fantasy IX (USA)']
    result = art.find_art_matches('Final Fantasy VII Retranslated Edition', opts)
    assert result['automatic'] is None


def test_atomic_cover_stage_preserves_first_cover_and_local_preview(tmp_path):
    workspace = tmp_path/'card'; prepare_layout(workspace)
    result = art.save_cover_bytes(workspace, 'PS1', 'Sample', PNG)
    assert result['status'] == 'downloaded'
    assert Path(result['target']).read_bytes() == PNG
    assert Path(result['preview']).read_bytes() == PNG
    second = art.save_cover_bytes(workspace, 'PS1', 'Sample', PNG, replace=False)
    assert second['status'] == 'already present'
    assert Path(second['target']).read_bytes() == PNG
    assert not list(workspace.rglob('*.retro-art-part'))


def test_explicit_cover_replacement_and_non_destructive_source(tmp_path):
    workspace = tmp_path/'card'
    user = tmp_path/'user.png'; user.write_bytes(PNG)
    art.save_cover_bytes(workspace, 'PS1', 'Game', PNG)
    result = art.stage_local_cover(workspace, 'PS1', 'Game', user, replace=True)
    assert result['status']=='replaced' and user.read_bytes()==PNG
    assert Path(result['target']).read_bytes()==PNG


def test_bad_png_does_not_create_published_artwork(tmp_path):
    card = tmp_path / 'card'
    with pytest.raises(ValueError):
        art.save_cover_bytes(card, 'PS1', 'Game', b'untrusted')
    assert not list(card.rglob('Game.png'))


def test_no_network_covers_needs_review_instead_of_guess(tmp_path,monkeypatch):
    monkeypatch.setattr(art,'catalog_for',lambda system,workspace: ['Resident Evil (USA)'])
    card = tmp_path/'card'
    result = art.process_batch(card,[{'system':'PS1','label':'Resident Evil Gore Edition'}])
    assert result['stats']['review'] == 1
    assert not list(card.rglob('*.png'))
    index = art.local_index(card)
    assert index['PS1:Resident Evil Gore Edition']['status']=='review'


def test_batch_downloads_only_strict_matches(tmp_path,monkeypatch):
    monkeypatch.setattr(art,'catalog_for',lambda system,workspace: ['Sample Game (USA)', 'Sample Game (Europe)'])
    monkeypatch.setattr(art,'stage_online_cover',lambda workspace,system,stem,source_title:
                    art.save_cover_bytes(workspace,system,stem,PNG,source=source_title))
    card=tmp_path/'card'
    results = art.process_batch(card,[{'system':'PS1','label':'Sample Game'},
                                      {'system':'PS1','label':'Another Edition'}])
    assert results['stats']['downloaded']==1
    assert results['stats']['review']==1
    assert art.cached_preview(card,'PS1','Sample Game').exists()
    assert not art.cached_preview(card,'PS1','Another Edition').exists()


def test_cancelled_batch_does_not_start_writes(tmp_path):
    event=Event(); event.set()
    out=art.process_batch(tmp_path/'card',[{'system':'PS1','label':'Sample Game'}],cancelled=event)
    assert out['cancelled'] and out['stats']['downloaded']==0
    assert not (tmp_path/'card').exists()


def test_local_index_corruption_is_nonfatal(tmp_path):
    card=tmp_path/'card'; path=art.local_cache_root(card)/'matches.json'
    path.parent.mkdir(parents=True);path.write_text('unparseable!',encoding='utf8')
    assert art.local_index(card)=={}


def test_artwork_helper_subprocess_stages_png_without_touching_games(tmp_path):
    image=tmp_path/'cover.png';image.write_bytes(PNG)
    card=tmp_path/'card';prepare_layout(card)
    game=card/'ROMs'/'psx'/'Sample.img';game.write_bytes(b'original image bytes')
    req={'mode':'local','workspace':str(card),'system':'PS1','label':'Sample','source_path':str(image)}
    worker=subprocess.Popen([sys.executable,'-u',str(ROOT/'artwork_worker.py')],cwd=ROOT,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
        env={**os.environ, 'LOCALAPPDATA':str(tmp_path/'local-cache')})
    stdout,stderr=worker.communicate(json.dumps(req)+'\n',timeout=10)
    assert worker.returncode==0,stderr
    messages=[json.loads(x) for x in stdout.splitlines()]
    assert messages[-1]['data']['status']=='downloaded'
    assert (card/'Media'/'BoxArt'/'psx'/'Sample.png').read_bytes()==PNG
    assert game.read_bytes()==b'original image bytes'


def test_workflow_wires_galleries_and_uses_isolated_worker():
    src=(ROOT/'app.py').read_text(encoding='utf8')
    bat=(ROOT/'Build_Windows_EXE.bat').read_text(encoding='utf8')
    for term in ('Cover gallery', 'def edit_cover(', 'def start_artwork_process(',
                 'def _stop_artwork_process(', 'self.pending_auto_artwork',
                 'self.gallery_visible_cap', 'Find missing covers'):
        assert term in src
    assert 'RetroLibraryArtwork.exe' in bat


def test_source_roms_are_not_deleted_by_gallery_code():
    src=(ROOT/'artwork_gallery.py').read_text(encoding='utf8')
    assert ".retro-art-part" in src
    assert 'cover_destination(' in src
    assert 'shutil.rmtree' not in src


def test_existing_nas_cover_restores_missing_local_cache_without_network(tmp_path,monkeypatch):
    card=tmp_path/'card'; prepare_layout(card)
    dest = card/'Media'/'BoxArt'/'psx'/'Game.png'
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(PNG)
    def never_online(*args,**kwargs):
        pytest.fail('Stored artwork should never require internet')
    monkeypatch.setattr(art,'catalog_for',never_online)
    result=art.process_batch(card,[{'system':'PS1','label':'Game'}])
    assert result['stats']['already present'] == 1
    assert art.cached_preview(card,'PS1','Game').read_bytes()==PNG


def test_batch_does_not_override_manual_cover_when_online_title_matches(tmp_path,monkeypatch):
    card=tmp_path/'card'; prepare_layout(card)
    art.save_cover_bytes(card,'PS1','Sample Game',PNG,source='manual')
    monkeypatch.setattr(art,'catalog_for',lambda *args: pytest.fail('Already covered'))
    outcome=art.process_batch(card,[{'system':'PS1','label':'Sample Game'}])
    assert outcome['stats']['already present'] == 1
    assert (card/'Media'/'BoxArt'/'psx'/'Sample Game.png').read_bytes()==PNG


def test_subprocess_force_stop_does_not_affect_original_game(tmp_path):
    # Reproduce a worker that is stuck inside a remote write, then kill it.
    import time
    src=tmp_path/'cover.png';src.write_bytes(PNG)
    card=tmp_path/'card';prepare_layout(card)
    game=card/'ROMs'/'psx'/'Game.img';game.write_bytes(b'ROM unchanged')
    command = "import artwork_worker,time;artwork_worker.stage_local_cover=lambda *a,**k:time.sleep(30);raise SystemExit(artwork_worker.main())"
    proc=subprocess.Popen([sys.executable,'-u','-c',command],cwd=ROOT,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        payload={'mode':'local','workspace':str(card),'system':'PS1',
                 'label':'Game','source_path':str(src)}
        proc.stdin.write(json.dumps(payload)+'\n');proc.stdin.flush()
        assert json.loads(proc.stdout.readline())['type']=='started'
        proc.kill();proc.wait(timeout=5)
        assert proc.returncode != 0
        assert game.read_bytes()==b'ROM unchanged'
        assert not (card/'Media'/'BoxArt'/'psx'/'Game.png').exists()
    finally:
        if proc.poll() is None: proc.kill();proc.wait(timeout=5)


def test_libretro_plaintext_index_support():
    content = b'Named_Boxarts/Resident%20Evil%20%28USA%29.png\nNamed_Boxarts/Biohazard.png\nNamed_Titles/ignore.exe\n'
    assert art.parse_index_text(content) == ['Resident Evil (USA)', 'Biohazard']
