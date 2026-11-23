"""v1.6.0: usable premium dialog and safe USB SDXC identity regression tests."""
from pathlib import Path
import os
import pytest

from card_capacity import physical_card_preview
from card_identity import card_candidate, fingerprint, matches, verify_card
from drives import Volume
from sync_engine import SyncPlan


def card(root='E:\\', *, guid='volume-abc', serial=982127,
         filesystem='exFAT', removable=True, size=511_800_000_000):
    return Volume(Path(root), 'MICROSD', filesystem, size, size-1000,
                  removable, guid, serial)


def test_512gb_usb_card_detected_and_identity_is_not_just_the_drive_letter():
    actual = card()
    f = fingerprint(actual)
    assert f['filesystem'] == 'EXFAT' and f['serial'] == 982127
    assert card_candidate(actual, Path('C:\\'))
    assert matches(f, actual)
    assert not matches(f, card(guid='volume-swapped'))
    assert not matches(f, card(serial=982128))
    assert not matches(f, card(size=511_800_000_001))
    assert not matches(f, card(filesystem='FAT32'))
    assert not matches(f, card(root='F:\\'))
    assert not matches({'root': f['root'], 'capacity': f['capacity']}, actual)


def test_fixed_disk_is_only_suggested_if_plausible_and_must_be_confirmed():
    assert card_candidate(card(removable=False), Path('C:\\'))
    assert not card_candidate(card(root='C:\\'), Path('C:\\'))
    assert not card_candidate(card(removable=False, size=2_000_000_000_000))
    assert not card_candidate(card(removable=False, size=64_000_000_000))
    assert card_candidate(card(removable=True, size=64_000_000_000))


def test_card_identity_refuses_swap_bad_format_or_unknown_identity():
    expected = fingerprint(card())
    assert verify_card(Path('E:\\'), expected, validator=lambda target: card())
    with pytest.raises(ValueError, match='identity changed'):
        verify_card(Path('E:\\'), expected, validator=lambda t: card(serial=1))
    with pytest.raises(ValueError, match='identity changed'):
        verify_card(Path('E:\\'), expected, validator=lambda t: card(guid='other'))
    with pytest.raises(ValueError, match='not exFAT'):
        verify_card(Path('E:\\'), fingerprint(card(filesystem='FAT32')),
                    validator=lambda t: card(filesystem='FAT32'))


def test_preview_protocol_includes_identity_and_refuses_unconfirmed_copy(monkeypatch,tmp_path):
    import transfer_worker as worker
    expected=fingerprint(card())
    fake=SyncPlan(1, 100, 100, 0, [], 30_000_000_000,
                  511_800_000_000, False, 0)
    monkeypatch.setattr(worker,'make_plan',lambda *args,**kw:fake)
    monkeypatch.setattr(worker,'validate_physical_root',lambda target:card())
    result=worker.handle({'mode':'preview','workspace':str(tmp_path),
                          'target':'E:\\','simulation':False},None)
    assert result['plan']['card_identity'] == expected
    with pytest.raises(ValueError,match='fresh, confirmed'):
        worker.handle({'mode':'copy','workspace':str(tmp_path),
                       'target':'E:\\','simulation':False},None)


def test_transfer_worker_rejects_changed_card_before_any_write(monkeypatch,tmp_path):
    import transfer_worker as worker
    called=[]
    monkeypatch.setattr(worker,'verify_card',
                        lambda path,identity: (_ for _ in ()).throw(ValueError('identity changed')))
    monkeypatch.setattr(worker,'transfer_verified',
                        lambda *args,**kwargs:called.append('WRITE'))
    with pytest.raises(ValueError,match='identity changed'):
        worker.handle({'mode':'copy','workspace':str(tmp_path),'target':'E:\\',
                       'simulation':False,'expected_card_identity':fingerprint(card())},None)
    assert not called


def test_transfer_worker_passes_identity_to_per_file_guards(monkeypatch,tmp_path):
    import transfer_worker as worker
    expected=fingerprint(card())
    observed=[]
    monkeypatch.setattr(worker,'verify_card',lambda *args:observed.append('verified'))
    monkeypatch.setattr(worker,'transfer_verified',
                        lambda *args,**kw:observed.append(kw['expected_card_identity']) or {'verified':1})
    result=worker.handle({'mode':'copy','workspace':str(tmp_path),'target':'E:\\',
                          'simulation':False,'expected_card_identity':expected},None)
    assert result['copy']['verified']==1
    assert observed==['verified',expected]


@pytest.mark.parametrize('scale',[100,125,150])
def test_premium_detail_dialogs_are_readable_at_scales(scale):
    pytest.importorskip('PySide6')
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication,QPushButton,QPlainTextEdit
    from friendly_dialogs import DetailsDialog
    qt=QApplication.instance() or QApplication([])
    dialog=DetailsDialog(None, title='Resident Evil 2',
         subtitle='2 DISCS • one game',sections=[
             ('Your game',[('Format','Two verified CHDs'),('Listed size','1.10 GB')]),
             ('Your card',[('Available space','492.09 GB')])],
         items=['Resident Evil 2 (USA).m3u','Disc 1.chd','Disc 2.chd'],
         technical='Exact bytes 1,234,567',note='No files were modified.')
    dialog.resize(int(690*scale/100),int(565*scale/100))
    try:
        children=dialog.findChildren(QPushButton)
        assert any(b.text()=='Done' for b in children)
        exp=next(b for b in children if b.text().startswith('Show exact'))
        raw=dialog.findChild(QPlainTextEdit)
        assert raw is not None and raw.isHidden()
        exp.click()
        assert not raw.isHidden()
        assert '1,234,567' in raw.toPlainText()
        exp.click()
        assert raw.isHidden()
    finally:
        dialog.close()
        qt.processEvents()


def test_app_formats_game_and_card_data_into_short_sections(tmp_path,monkeypatch):
    pytest.importorskip('PySide6')
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings
    from core import Entry
    import app

    qt=QApplication.instance() or QApplication([])
    settings=QSettings(str(tmp_path/'isolated.ini'),QSettings.Format.IniFormat)
    root=tmp_path/'card';root.mkdir();settings.setValue('workspace',str(root))
    monkeypatch.setattr(app,'QSettings',lambda *args:settings)
    for name in ('offer_first_location','refresh','update_tools_status','update_workspace_location'):
        monkeypatch.setattr(app.Window,name,lambda *a,**kw:None)
    recorded=[]
    class Capture:
        def __init__(self,*a,**kw):recorded.append(kw)
        def exec(self):return 0
    monkeypatch.setattr(app,'DetailsDialog',Capture)
    w=app.Window()
    try:
        w.staged_bytes=2_708_438_498
        w.show_card_plan_details()
        w.show_virtual_exfat_details()
        assert len(recorded)==2
        assert 'card space' in recorded[0]['title'].lower()
        assert 'virtual' in recorded[1]['title'].lower()
        assert recorded[0]['technical'] and recorded[1]['technical']
        folder=root/'ROMs'/'psx'/'Resident Evil 2 (USA)'
        m=Entry(folder/'Resident Evil 2 (USA).m3u','Resident Evil 2 (USA)','PS1',1_100_000_000,'.m3u')
        a=Entry(folder/'Resident Evil 2 (USA) (Disc 1).chd','Disc 1','PS1',561_400_000,'.chd')
        b=Entry(folder/'Resident Evil 2 (USA) (Disc 2).chd','Disc 2','PS1',534_400_000,'.chd')
        w.show_game_format(m,[m,a,b])
        assert len(recorded)==3
        assert len(recorded[-1]['items'])==3
        assert '2 discs' in str(recorded[-1]['sections']).lower()
    finally:
        w.close();qt.processEvents()
