"""v1.6.5 regression: selectable Sony EBOOT game titles, no guessed IDs,
last-folder/source code wiring and automatic exact Libretro artwork.

All synthetic content; no DRM keys, commercial EBOOT or internet required.
"""
from __future__ import annotations

import struct
import threading
import zipfile
from pathlib import Path

import pytest

from psn_picker import scan_psn_sources
from import_worker import handle
from artwork_gallery import find_art_matches, direct_cover_fallback


def fake_ps1(p: Path, title: str, *, key=True):
    p.parent.mkdir(parents=True, exist_ok=True)
    name = title.encode('utf-8') + b'\0'
    sfo = (struct.pack('<4sIIII', b'\0PSF', 0x101, 36, 42, 1)
           + struct.pack('<HBBIII', 0, 4, 2, len(name), len(name), 0)
           + b'TITLE\0' + name)
    pos = 40 + len(sfo)
    p.write_bytes(b'\0PBP' + struct.pack('<I', 0x10000) +
                  struct.pack('<8I', 40, *([pos] * 7)) +
                  sfo + b'PSISOIMG00000000' + b'A' * 128)
    if key:
        (p.parent / 'KEYS.BIN').write_bytes(b'TEST-SIDECAR-NOT-A-REAL-KEY')
    return p


def test_code_folder_is_identified_by_actual_pbp_title_not_fake_np_database(tmp_path):
    root = tmp_path / 'PS1'
    fake_ps1(root / 'NPEE00001' / 'EBOOT.PBP', 'Crash Bandicoot™')
    fake_ps1(root / 'NPEE00008' / 'EBOOT.PBP', 'Final Fantasy VII')
    entries = scan_psn_sources(root)
    assert [x['title'] for x in entries['games']] == ['Crash Bandicoot™', 'Final Fantasy VII']
    assert [x['code'] for x in entries['games']] == ['NPEE00001', 'NPEE00008']
    assert all(x['identified'] for x in entries['games'])
    assert all(x['kind'] == 'PS1 Classic EBOOT' for x in entries['games'])
    assert all(x['path'].endswith('EBOOT.PBP') for x in entries['games'])
    # The explanation may mention the sidecar, but the picker must not expose
    # it as a separately selectable game.
    assert all(not x['path'].upper().endswith('KEYS.BIN') for x in entries['games'])


def test_unnamed_pbp_does_not_invent_identity_from_product_code(tmp_path):
    p = tmp_path / 'PS1' / 'NPEE98765' / 'EBOOT.PBP'
    p.parent.mkdir(parents=True)
    p.write_bytes(b'\0PBP' + struct.pack('<I', 0x10000)
                  + struct.pack('<8I', *([40] * 8))
                  + b'PSISOIMG00000000' + b'X' * 128)
    out = scan_psn_sources(tmp_path / 'PS1')
    assert len(out['games']) == 1
    assert out['games'][0]['identified'] is False
    assert out['games'][0]['title'] == 'Title not yet identified'


def test_archives_listed_separately_no_gigabyte_extraction_during_preview(tmp_path):
    root = tmp_path / 'PSN'
    root.mkdir()
    for name in ('Crash Bandicoot (USA).zip', 'PS1.7z'):
        (root / name).write_bytes(b'NOT_EXTRACTED_PREVIEW')
    result = scan_psn_sources(root)
    assert len(result['games']) == 2
    assert result['games'][0]['title'] == 'Crash Bandicoot (USA)'
    assert result['games'][1]['title'] == 'Title not yet identified'
    assert not (root / 'rgl-psn-extract').exists()


def test_cancelled_scan_never_modifies_sources_or_returns_partial_picker(tmp_path):
    game = fake_ps1(tmp_path / 'PS1' / 'NPEE00001' / 'EBOOT.PBP', 'Crash Bandicoot™')
    stop = threading.Event()
    stop.set()
    out = scan_psn_sources(tmp_path / 'PS1', cancel=stop)
    assert out['cancelled'] and out['games'] == []
    assert game.is_file()


def test_worker_selects_only_user_checked_eboots_and_handles_sidecars(tmp_path, monkeypatch):
    root = tmp_path / 'PS1'
    a = fake_ps1(root / 'NPEE00001' / 'EBOOT.PBP', 'Crash Bandicoot™')
    b = fake_ps1(root / 'NPEE00008' / 'EBOOT.PBP', 'Final Fantasy VII')
    scan = handle({'mode':'scan_psn_catalog', 'folder':str(root)}, threading.Event())
    assert {x['title'] for x in scan['games']} == {'Crash Bandicoot™', 'Final Fantasy VII'}
    selected = [scan['games'][0]['path']]
    import ps1_batch
    seen = {}
    def stub(paths, workspace, fallback, binary, **kwargs):
        seen['paths'] = [str(p) for p in paths]
        seen['auto_artwork'] = kwargs['auto_artwork']
        return {'batch_total':len(paths),'batch_completed':1,'cancelled':False}
    monkeypatch.setattr(ps1_batch, 'batch_guided_import', stub)
    request = {'mode':'batch_psn_selected', 'paths':selected,
               'workspace':str(tmp_path / 'virtual'), 'fallback':'PS1',
               'auto_ps1_chd':True, 'auto_artwork':True,
               'binary':str(tmp_path / 'chdman.exe')}
    out = handle(request, threading.Event())
    assert out['batch_total'] == 1 and out['batch_completed'] == 1
    assert seen['paths'] == selected
    assert seen['auto_artwork'] is True
    assert all(not p.endswith('KEYS.BIN') for p in seen['paths'])
    assert a.exists() and b.exists()


def test_worker_does_not_accept_keys_bin_as_game(tmp_path):
    key = tmp_path / 'KEYS.BIN'
    key.write_bytes(b'keys')
    with pytest.raises(ValueError, match='EBOOT'):
        handle({'mode':'batch_psn_selected', 'paths':[str(key)],
                'workspace':str(tmp_path / 'card'), 'fallback':'PS1',
                'auto_ps1_chd':True, 'binary':'chdman.exe'},
               threading.Event())


def test_auto_cover_chooses_usa_when_disc_region_not_known():
    candidates = ['Crash Bandicoot (Europe)', 'Crash Bandicoot (USA)',
                  'Crash Bandicoot Racing (USA)']
    result = find_art_matches('Crash Bandicoot™', candidates)
    assert result['automatic'] == 'Crash Bandicoot (USA)'


def test_explicit_european_disc_region_not_overridden_by_usa_preference():
    names = ['Crash Bandicoot (USA)', 'Crash Bandicoot (Europe)']
    assert find_art_matches('Crash Bandicoot (Europe)', names)['automatic'] == 'Crash Bandicoot (Europe)'
    assert find_art_matches('Crash Bandicoot (Japan)', names)['automatic'] is None


def test_offline_index_fallback_strips_trademark_and_prefers_usa(tmp_path):
    titles = []
    def mock_download(workspace, system, stem, title):
        titles.append(title)
        return {'status':'downloaded','source_title':title}
    result = direct_cover_fallback(tmp_path / 'card', 'PS1', 'Crash Bandicoot™',
                                   downloader=mock_download)
    assert result['status'] == 'downloaded'
    assert titles == ['Crash Bandicoot (USA)']


def test_app_has_title_selector_last_directory_and_main_progress():
    app = (Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8')
    assert "last_game_folder" in app
    assert 'def _show_psn_game_picker' in app
    assert 'Import selected games' in app
    assert 'batch_psn_selected' in app
    assert 'CHD VERIFICATION' in app
    assert 'MD5' in app
