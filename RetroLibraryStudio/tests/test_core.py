import os
import stat
import threading
import zipfile
from pathlib import Path

import pytest

from core import (CAPACITY, copy_atomic, expected_import_size, import_candidates,
                  import_files, incoming_inventory, inventory, prepare_layout,
                  sanitize_archive_member, transfer, within)


def test_layout_and_storage(tmp_path):
    w = tmp_path / 'stage'
    prepare_layout(w)
    assert (w / 'ROMs' / 'psx').is_dir()
    assert (w / 'ROMs' / 'psp').is_dir()
    a, total, count = inventory(w)
    assert not a and not total and not count
    assert CAPACITY == 512_000_000_000


def test_file_import_and_original_retained(tmp_path):
    incoming = tmp_path / 'incoming'; incoming.mkdir()
    source = incoming / 'My PSP Game.iso'; source.write_bytes(b'ISODATA')
    w = tmp_path / 'stage'; prepare_layout(w)
    assert import_files([source], w, 'PSP') == (1, 0, [])
    assert source.read_bytes() == b'ISODATA'
    assert (w / 'ROMs' / 'psp' / source.name).read_bytes() == b'ISODATA'
    assert import_files([source], w, 'PSP') == (0, 1, [])


def test_cue_companions(tmp_path):
    incoming = tmp_path / 'incoming'; incoming.mkdir()
    cue = incoming / 'Demo.cue'; cue.write_text('FILE "track01.bin" BINARY\n  TRACK 01 MODE2/2352')
    track = incoming / 'track01.bin'; track.write_bytes(b'disc track')
    assert import_candidates([cue, track]) == [cue]
    w = tmp_path / 'stage'; prepare_layout(w)
    assert import_files([cue, track], w, 'PS1') == (2, 0, [])
    assert (w / 'ROMs' / 'psx' / 'Demo' / 'Demo.cue').exists()
    assert (w / 'ROMs' / 'psx' / 'Demo' / 'track01.bin').exists()


def test_multidisc_m3u(tmp_path):
    incoming = tmp_path / 'incoming'; incoming.mkdir()
    p = incoming / 'Disk 1'; p.mkdir()
    (p / 'disc.cue').write_text('FILE "disc.bin" BINARY')
    (p / 'disc.bin').write_bytes(b'disc')
    m = incoming / 'My Multi Game.m3u'; m.write_text('Disk 1/disc.cue\n')
    w = tmp_path / 'stage'; prepare_layout(w)
    assert import_files([m], w, 'PS1') == (3, 0, [])
    assert (w / 'ROMs' / 'psx' / 'My Multi Game' / 'Disk 1' / 'disc.bin').exists()


def test_zip_import(tmp_path):
    incoming = tmp_path / 'incoming'; incoming.mkdir()
    z = incoming / 'Archived Game.zip'
    with zipfile.ZipFile(z, 'w') as a:
        a.writestr('Game.cue', 'FILE "track.bin" BINARY')
        a.writestr('track.bin', 'TRACK')
    w = tmp_path / 'stage'; prepare_layout(w)
    assert import_files([z], w, 'PS1') == (2, 0, [])
    assert (w / 'ROMs' / 'psx' / 'Archived Game' / 'track.bin').exists()


@pytest.mark.parametrize('name', ['../malware.iso','/tmp/malware.iso','C:/Windows/file.bin',
                                  'a:evil.iso','CON.bin','folder/../../escape.iso','com1.txt'])
def test_archive_path_rejected(name):
    with pytest.raises(ValueError):
        sanitize_archive_member(name)


def test_zip_slip_rejected(tmp_path):
    archive = tmp_path / 'attack.zip'
    with zipfile.ZipFile(archive, 'w') as a:
        a.writestr('../outside.iso', 'BAD')
    w = tmp_path / 'workspace'; prepare_layout(w)
    result = import_files([archive], w, 'PSP')
    assert result[0] == 0 and result[2]
    assert not (tmp_path / 'outside.iso').exists()


def test_zip_symlink_rejected(tmp_path):
    archive = tmp_path / 'links.zip'
    with zipfile.ZipFile(archive, 'w') as a:
        info = zipfile.ZipInfo('link.iso')
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        a.writestr(info, '../outside')
    w = tmp_path / 'workspace'; prepare_layout(w)
    result = import_files([archive], w, 'PSP')
    assert result[0] == 0 and result[2]


def test_conflict_never_overwrites(tmp_path):
    a = tmp_path / 'a.iso'; a.write_bytes(b'new')
    b = tmp_path / 'b.iso'; b.write_bytes(b'old')
    with pytest.raises(FileExistsError):
        copy_atomic(a, b)
    assert b.read_bytes() == b'old'
    assert not (tmp_path / 'b.iso.retro-part').exists()


def test_transfer(tmp_path):
    w = tmp_path / 'virtual'; prepare_layout(w)
    src = w / 'ROMs' / 'psp' / 'game.cso'; src.write_bytes(b'gamecontent')
    target = tmp_path / 'destination'; target.mkdir()
    assert transfer(w, target) == (1, 0, [])
    assert (target / 'ROMs' / 'psp' / 'game.cso').read_bytes() == b'gamecontent'
    assert transfer(w, target) == (0, 1, [])
    with pytest.raises(ValueError):
        transfer(w, w)


def test_cancelled_copy_is_rolled_back(tmp_path):
    source = tmp_path / 'source.iso'; source.write_bytes(b'x' * 1024)
    target = tmp_path / 'target.iso'
    stop = threading.Event(); stop.set()
    with pytest.raises(InterruptedError):
        copy_atomic(source, target, cancel=stop)
    assert not target.exists()
    assert not (tmp_path / 'target.iso.retro-part').exists()


def test_incoming_inventory(tmp_path):
    download = tmp_path / 'downloads'; download.mkdir()
    (download / 'one.iso').write_bytes(b'1234')
    (download / 'two.7z').write_bytes(b'789')
    (download / 'notes.txt').write_text('note')
    items, size = incoming_inventory(download)
    assert len(items) == 2
    assert size == 7


def test_512gb_preflight(tmp_path, monkeypatch):
    # NTFS truncate(512 GB) can allocate/zero real storage. Simulate occupied
    # capacity at the inventory boundary instead of creating an enormous file.
    import core
    w = tmp_path / 'virtual'; prepare_layout(w)
    monkeypatch.setattr(core, 'inventory', lambda *a, **k: ([], CAPACITY, 1))
    incoming = tmp_path / 'game.iso'; incoming.write_bytes(b'a')
    assert import_files([incoming], w, 'PSP')[2]
    assert not (w / 'ROMs' / 'psp' / incoming.name).exists()


def test_partial_files_never_transfer(tmp_path):
    w = tmp_path / 'virtual'; prepare_layout(w)
    (w / 'ROMs' / 'psp' / 'unfinished.iso.retro-part').write_bytes(b'partial')
    dest = tmp_path / 'sd'; dest.mkdir()
    with pytest.raises(ValueError, match='empty'):
        transfer(w, dest)
