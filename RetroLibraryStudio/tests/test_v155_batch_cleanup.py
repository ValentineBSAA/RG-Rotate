"""Batch PS1 lossless CHD workflow, destructive cleanup scope, and UI preview fit."""
from pathlib import Path
from threading import Event
import os
import pytest

from ps1_organizer import (convert_selected_game, batch_convert_ps1,
                            batch_sources, _delete_verified_working_sources)
from test_v154_organizer import fixture, stub_converter, stub_verify


def test_explicit_delete_only_removes_virtual_card_sources(tmp_path):
    card, cue, b1, b2, tool = fixture(tmp_path)
    external = tmp_path/'separate NAS original archive'
    external.mkdir()
    original = external/'Clock Tower (Track 1).bin'
    original.write_bytes(b1.read_bytes())
    contents = original.read_bytes()
    result = convert_selected_game(cue,card,tool,converter=stub_converter,verifier=stub_verify,
                                   cleanup_mode='delete')
    assert not result['errors'] and result['converted']==1
    assert result['deleted_files']==3 and result['freed_bytes']>0
    assert result['backup']=='' and not cue.exists() and not b1.exists() and not b2.exists()
    assert (cue.parent/'Clock Tower.chd').exists()
    assert original.read_bytes()==contents
    assert not list(tmp_path.glob('*Conversion Backups*'))


def test_failed_chd_verification_never_deletes_tracks(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    def fail_verify(*args,**kwargs): raise ValueError('simulated CHD verification failure')
    r=convert_selected_game(cue,card,tool,converter=stub_converter,verifier=fail_verify,
                            cleanup_mode='delete')
    assert r['errors'] and not r['deleted_files']
    assert cue.exists() and b1.exists() and b2.exists()


def test_batch_conversion_deletes_only_completed_card_sets(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    another = card/'ROMs'/'psx'/'Game Two'
    another.mkdir()
    (another/'Game Two.bin').write_bytes(b'abc'*1024)
    (another/'Game Two.cue').write_text('FILE "Game Two.bin" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n')
    source_archive = tmp_path/'original-source'
    source_archive.mkdir()
    (source_archive/'Game Two.bin').write_bytes(b'Important original outside the card')
    stages=[]
    r=batch_convert_ps1(card,tool,cleanup_mode='delete',
        converter=stub_converter,verifier=stub_verify,
        progress=lambda desc,n,total: stages.append((desc,n,total)))
    assert not r['errors'] and r['converted']==2 and r['total']==2
    assert r['completed']==2 and r['deleted_files']==5
    assert not cue.exists() and not (another/'Game Two.cue').exists()
    assert (another/'Game Two.chd').exists()
    assert (source_archive/'Game Two.bin').read_bytes()==b'Important original outside the card'
    assert stages[-1][1:]==(100,100)
    assert not r['backups']


def test_batch_recovery_mode_moves_but_never_deletes(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    r=batch_convert_ps1(card,tool,cleanup_mode='backup',
                        converter=stub_converter,verifier=stub_verify)
    assert not r['errors'] and len(r['backups'])==1
    backup=Path(r['backups'][0])
    assert (backup/cue.name).exists() and (backup/b1.name).exists()
    assert r['nas_bytes_reclaimed']==0 and r['deleted_files']==0
    assert backup.is_relative_to(card.parent) and not backup.is_relative_to(card)


def test_batch_ignores_img_referenced_by_cue(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    b1.unlink();b2.unlink()
    img=cue.with_suffix('.img')
    img.write_bytes(b'data'*1024)
    cue.write_text(f'FILE "{img.name}" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n')
    assert batch_sources(card)==[cue]


def test_batch_reports_bad_discs_but_continues_others(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    another=card/'ROMs'/'psx'/'Bad'
    another.mkdir()
    (another/'Bad.cue').write_text('FILE "missing.bin" BINARY\n TRACK 01 AUDIO\n INDEX 01 00:00:00\n')
    r=batch_convert_ps1(card,tool,cleanup_mode='delete',
                        converter=stub_converter,verifier=stub_verify)
    assert r['converted']==1 and r['total']==2 and r['errors']
    assert (another/'Bad.cue').exists() and (cue.parent/'Clock Tower.chd').exists()


def test_batch_stop_prevents_deletion(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    stop=Event();stop.set()
    r=batch_convert_ps1(card,tool,cleanup_mode='delete',cancel=stop,
                        converter=stub_converter,verifier=stub_verify)
    assert r['cancelled'] and r['deleted_files']==0 and cue.exists()


def test_cleanup_refuses_external_paths_even_if_called_directly(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    outside=tmp_path/'external-original.bin';outside.write_bytes(b'important')
    with pytest.raises(ValueError):
        _delete_verified_working_sources([cue,outside],card)
    assert cue.exists() and outside.exists()


def test_gui_preview_fits_when_resized():
    pytest.importorskip('PySide6')
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import Qt
    from app import FittedCoverPreview
    qt=QApplication.instance() or QApplication([])
    view=FittedCoverPreview()
    view.resize(480,280); view.show(); qt.processEvents()
    source=QPixmap(800,1600); source.fill(Qt.GlobalColor.blue)
    view.set_cover(source); qt.processEvents()
    assert view.pixmap().width() <= view.contentsRect().width()
    assert view.pixmap().height() <= view.contentsRect().height()
    view.resize(180,120);qt.processEvents()
    assert view.pixmap().width() <= 180 and view.pixmap().height() <= 120
    view.close()
