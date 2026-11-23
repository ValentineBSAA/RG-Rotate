"""Regress the real v1.4.3 failure: restart forgot practice mode and rejected a folder."""
from pathlib import Path

from destination_mode import is_volume_root, restore_destination_mode, same_location
from core import prepare_layout
from transfer_worker import handle
import threading


def test_old_version_practice_location_recovers_after_restart():
    prior = r'C:\Users\Example\Documents\Retro Library Studio\PracticeTransfer'
    default = Path(prior)
    assert restore_destination_mode(Path(prior), '', default) == 'practice'
    assert not is_volume_root(prior)


def test_saved_practice_mode_survives_restart_and_custom_folder():
    custom = Path(r'D:\Test Collections\My Practice')
    assert restore_destination_mode(custom, 'practice', Path(r'C:\Users\abc\PracticeTransfer')) == 'practice'
    assert restore_destination_mode(custom, '', Path(r'C:\Users\abc\PracticeTransfer')) == 'unconfirmed'


def test_card_root_cannot_be_reclassified_as_practice():
    assert is_volume_root('F:\\')
    assert is_volume_root('\\\\server\\share\\')
    assert not is_volume_root(r'F:\PracticeTransfer')
    assert restore_destination_mode(Path('F:\\'), 'practice', Path(r'F:\PracticeTransfer')) == 'physical'
    assert restore_destination_mode(Path('F:\\'), 'physical', Path(r'C:\PracticeTransfer')) == 'physical'


def test_real_card_mode_is_not_inferred_from_an_arbitrary_folder():
    folder=Path(r'C:\Users\Example\Documents\Some Folder')
    assert restore_destination_mode(folder, 'physical', Path(r'C:\Users\Example\Documents\PracticeTransfer')) == 'unconfirmed'
    assert same_location(folder, r'c:/USERS/EXAMPLE/documents/Some Folder')


def test_practice_second_run_still_verifies_all_existing(tmp_path):
    virtual=tmp_path/'Virtual Card'; prepare_layout(virtual)
    (virtual/'ROMs'/'psx'/'game.img').write_bytes(b'PS1 game file'*1000)
    (virtual/'SetupPackages'/'cocon-311.apk').write_bytes(b'APK placeholder'*500)
    dest=tmp_path/'PracticeTransfer'; dest.mkdir()
    request={'mode':'copy','workspace':str(virtual),'target':str(dest),'simulation':True}
    first=handle(request,threading.Event())['copy']
    assert first['copied']==2 and first['verified']==2 and not first['errors']
    second=handle(request,threading.Event())['copy']
    assert second['copied']==0 and second['skipped']==2 and second['verified']==2 and not second['errors']


def test_ui_persists_mode_and_refuses_wrong_destination_in_preview():
    text=(Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8')
    assert "self.settings.setValue('target_mode', mode)" in text
    assert "self.simulation.setChecked(self.saved_destination_mode == 'practice')" in text
    assert "restore_destination_mode(" in text
    assert 'def _selected_transfer_mode(self):' in text
    assert text.count('self._selected_transfer_mode()') >= 2
    assert 'if practice and is_volume_root(self.target):' in text
    assert "self._remember_destination(directory, 'practice')" in text
    assert "self._remember_destination(candidates[choices.index(selected)].root, 'physical')" in text
