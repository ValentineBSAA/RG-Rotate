"""The first-run card location must be reliable and non-destructive."""
from __future__ import annotations

import threading
from pathlib import Path

import pytest

from core import prepare_layout
from workspace_setup import (
    VIRTUAL_CARD_NAME, suggested_workspace, count_workspace_files,
    copy_existing_workspace,
)


def test_empty_explicit_folder_is_used_as_selected(tmp_path):
    chosen = tmp_path / 'My RG Rotate'
    chosen.mkdir()
    proposed, dedicated = suggested_workspace(chosen)
    assert proposed == chosen
    assert not dedicated
    assert list(chosen.iterdir()) == []


def test_populated_unrelated_folder_gets_dedicated_child_without_writes(tmp_path):
    chosen = tmp_path / 'Stuff'
    chosen.mkdir()
    (chosen/'photos.jpg').write_bytes(b'mine')
    proposed, dedicated = suggested_workspace(chosen)
    assert proposed == chosen / VIRTUAL_CARD_NAME
    assert dedicated
    assert not proposed.exists()
    assert (chosen/'photos.jpg').read_bytes() == b'mine'


def test_existing_card_folder_is_recognized(tmp_path):
    prepare_layout(tmp_path/'MyLibrary')
    proposed, dedicated = suggested_workspace(tmp_path/'MyLibrary')
    assert proposed == tmp_path/'MyLibrary'
    assert not dedicated


def test_switching_into_existing_card_is_rejected(tmp_path):
    card = tmp_path/'old'
    prepare_layout(card)
    child = card/'ROMs'
    with pytest.raises(ValueError, match='inside'):
        suggested_workspace(child, old_workspace=card)


def test_will_not_confuse_real_card_with_virtual(tmp_path):
    root = tmp_path/'selected'
    root.mkdir()
    with pytest.raises(ValueError, match='separate'):
        suggested_workspace(root, physical_destination=root)


def test_symlink_location_rejected(tmp_path):
    actual = tmp_path/'actual'
    actual.mkdir()
    alias = tmp_path/'alias'
    try:
        alias.symlink_to(actual, target_is_directory=True)
    except OSError:
        pytest.skip('Symlinks unavailable on current host')
    with pytest.raises(ValueError, match='symbolic link'):
        suggested_workspace(alias)


def test_move_is_verified_copy_and_never_deletes_source(tmp_path):
    old = tmp_path/'first'
    prepare_layout(old)
    source = old/'ROMs'/'psp'/'test.cso'
    source.write_bytes(b'PSP'+b'A'*4096)
    new = tmp_path/'second'
    result = copy_existing_workspace(old, new)
    assert result['verified'] == result['files'] == 1
    assert not result['errors'] and not result['cancelled']
    assert (new/'ROMs'/'psp'/'test.cso').read_bytes() == source.read_bytes()
    assert source.read_bytes().startswith(b'PSP')
    again = copy_existing_workspace(old, new)
    assert again['verified'] == 1 and again['skipped'] == 1


def test_conflicting_same_name_does_not_get_overwritten(tmp_path):
    old = tmp_path/'old'
    prepare_layout(old)
    src = old/'ROMs'/'gba'/'puzzle.gba'
    src.write_bytes(b'original')
    target = tmp_path/'new'/'ROMs'/'gba'
    target.mkdir(parents=True)
    dest = target/'puzzle.gba'
    dest.write_bytes(b'not-same-length')
    with pytest.raises(ValueError, match='Cannot copy safely'):
        copy_existing_workspace(old, tmp_path/'new')
    assert dest.read_bytes() == b'not-same-length'
    assert src.read_bytes() == b'original'


def test_workspace_copy_resumes_matching_partial(tmp_path):
    old = tmp_path/'old'
    prepare_layout(old)
    data = b'hello'*500
    (old/'ROMs'/'gb'/'item.gb').write_bytes(data)
    folder = tmp_path/'dest'/'ROMs'/'gb'
    folder.mkdir(parents=True)
    partial = folder/'item.gb.retro-part'
    partial.write_bytes(data[:700])
    res = copy_existing_workspace(old, tmp_path/'dest')
    assert res['verified']==1 and not res['errors']
    assert (folder/'item.gb').read_bytes() == data
    assert not partial.exists()


def test_cancelled_copy_does_not_report_success(tmp_path):
    old = tmp_path/'old'
    prepare_layout(old)
    (old/'ROMs'/'nes'/'game.nes').write_bytes(b'NES')
    cancel = threading.Event(); cancel.set()
    res = copy_existing_workspace(old, tmp_path/'new', cancel=cancel)
    assert res['cancelled'] and res['verified'] == 0
    assert (old/'ROMs'/'nes'/'game.nes').is_file()


def test_cancelled_count_is_not_mistaken_for_empty_library(tmp_path):
    prepare_layout(tmp_path/'old')
    stop = threading.Event(); stop.set()
    assert count_workspace_files(tmp_path/'old', cancel=stop) is None


def test_v1_1_5_ui_exposes_location_on_home_and_every_page():
    text = (Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8')
    for snippet in (
        'Your library folder on PC or NAS',
        'Choose your library folder in the strip above.',
        'Choose location…',
        'Change card location',
        'Copying FROM: your virtual card on this PC',
        'workspace_copy_finished',
        'self.settings.setValue(\'workspace\'',
        'offer_first_location',
    ):
        assert snippet in text


def test_app_side_receipts_migrate_but_not_to_physical_card(tmp_path):
    old = tmp_path/'existing'
    prepare_layout(old)
    (old/'ROMs'/'gb'/'handheld.gb').write_bytes(b'rom')
    receipts = old/'.retro-library'
    receipts.mkdir(exist_ok=True)
    (receipts/'receipt.json').write_text('{"source":"official"}', encoding='utf-8')
    new = tmp_path/'chosen'
    moved = copy_existing_workspace(old, new)
    assert moved['verified'] == moved['files'] == 2
    assert not moved['errors']
    assert (new/'.retro-library'/'receipt.json').read_text() == '{"source":"official"}'
    assert (old/'.retro-library'/'receipt.json').is_file()


def test_conflicting_workspace_receipt_is_preserved_and_switch_prevented(tmp_path):
    old = tmp_path/'old'
    prepare_layout(old)
    (old/'ROMs'/'gba'/'title.gba').write_bytes(b'game')
    folder=old/'.retro-library'
    folder.mkdir(exist_ok=True)
    (folder/'notes.json').write_bytes(b'original')
    dest=tmp_path/'new'/'.retro-library'
    dest.mkdir(parents=True)
    (dest/'notes.json').write_bytes(b'other')
    with pytest.raises(ValueError, match='metadata differs'):
        copy_existing_workspace(old, tmp_path/'new')
    assert (dest/'notes.json').read_bytes() == b'other'
    assert (old/'ROMs'/'gba'/'title.gba').read_bytes() == b'game'


def test_inventory_reports_count_without_examining_downloads(tmp_path):
    from core import inventory
    card=tmp_path/'virtual'
    prepare_layout(card)
    for i in range(205):
        (card/'ROMs'/'gb'/f'game{i}.gb').write_bytes(b'x')
    progress=[]
    entries,used,count=inventory(card,progress=lambda msg,cur,total:progress.append((msg,cur,total)))
    assert len(entries)==205 and count==205 and used==205
    assert progress and progress[0][1]==200
    assert 'files found' in progress[0][0]


def test_ui_cannot_stage_before_virtual_card_location_is_selected():
    import ast
    source = (Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8')
    cls = next(x for x in ast.parse(source).body if isinstance(x, ast.ClassDef) and x.name == 'Window')
    methods = {x.name: x for x in cls.body if isinstance(x, ast.FunctionDef)}
    guarded = ('pick_files', 'pick_folder', 'pick_apks', 'import_apks',
               'import_folder_path', 'import_paths', 'install_recommended',
               'prepare_essentials', 'start_preflight', 'start_transfer')
    for name in guarded:
        first = methods[name].body[0]
        assert isinstance(first, ast.If), f'{name} must check configured workspace first'
        calls = [n.func.attr for n in ast.walk(first) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)]
        assert 'ensure_workspace' in calls, f'{name} must check configured workspace first'
