"""Batch PS1 Classics: real ZIP/7Z extraction, safe per-game isolation and dedupe.

Synthetic EBOOT.PBP and synthetic CUE/BIN only. Real commercial
PSXtract decryption still requires user hardware/file acceptance.
"""
from __future__ import annotations

import struct
import threading
import zipfile
from pathlib import Path

import pytest

from ps1_batch import batch_guided_import
from ps1_duplicates import decide_repeat, fingerprint_pbp
from library_presentation import group_games, format_badge_info
from core import inventory
from import_worker import handle as worker_handle


def fake_psn(path: Path, marker=b'X'):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\0PBP' + struct.pack('<I', 0x10000) +
                     struct.pack('<8I', *(40 for _ in range(8))) +
                     b'PSTITLEIMG000000' + marker * 128)
    (path.parent/'KEYS.BIN').write_bytes(b'SYNTHETIC-NON-REAL-KEY')
    (path.parent/'DOCUMENT.DAT').write_bytes(b'SYNTHETIC-MANUAL')
    return path


def fake_cue(folder: Path, n: int):
    folder.mkdir(parents=True, exist_ok=True)
    name = f'Fake Disc {n}'
    (folder/(name+'.bin')).write_bytes(bytes([n])*2352*3)
    cue=folder/(name+'.cue')
    cue.write_text(f'FILE "{name}.bin" BINARY\n'
                   ' TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n',
                   encoding='utf-8')
    return cue


def mock_extractor(pbp, temp, helper, *, cancel=None, progress=None):
    return [fake_cue(Path(temp), n) for n in (1,2,3)]


def mock_converter(cue, output, binary, **kwargs):
    file=Path(output)/(Path(cue).stem+'.chd')
    file.write_bytes(b'SYNTHETIC CHD ' + cue.stem.encode('utf-8'))
    return {'output':str(file),'verified':True,'cancelled':False}


def zip_game(source: Path, output: Path):
    with zipfile.ZipFile(output, 'w') as archive:
        for p in sorted(source.parent.iterdir()):
            archive.write(p, arcname='NPEF00069/'+p.name)
    return output


def mock_chdman(tmp_path):
    file=tmp_path/'chdman.exe'
    file.write_bytes(b'MOCK-NOT-AN-EXE')
    return file


def test_batch_two_distinct_psn_archives_create_separate_titles_and_playlists(tmp_path):
    src=tmp_path/'unpacked';src.mkdir()
    a=fake_psn(src/'A'/'NPEF00069'/'EBOOT.PBP', b'A')
    b=fake_psn(src/'B'/'NPEF00070'/'EBOOT.PBP', b'B')
    one=zip_game(a,tmp_path/'Final Fantasy VII (English)(PSN).zip')
    two=zip_game(b,tmp_path/'Final Fantasy VIII (English)(PSN).zip')
    virtual=tmp_path/'virtual'
    msgs=[]
    result=batch_guided_import([one,two],virtual,'PS1',mock_chdman(tmp_path),
        auto_artwork=False,converter=mock_converter,psn_extractor=mock_extractor,
        progress=lambda msg,n,total: msgs.append((msg,n,total)))
    assert not result['errors']
    assert (result['batch_total'],result['batch_completed'],result['batch_needs_attention'])==(2,2,0)
    assert (result['converted'],result['playlists'])==(6,2)
    assert len(result['batch_items'])==2
    for title in ('Final Fantasy VII','Final Fantasy VIII'):
        root=virtual/'ROMs'/'psx'/title
        assert len(list(root.glob('*.chd')))==3
        assert (root/(title+'.m3u')).exists()
    groups=group_games(inventory(virtual)[0])
    assert len(groups)==2 and all(
        format_badge_info(g[0],g)['badge']=='3 DISCS' for g in groups)
    assert not list(virtual.glob('**/KEYS.BIN'))
    assert any('Batch 2/2' in m for m,n,t in msgs)


def test_batch_repackaged_same_eboot_skips_without_reextracting_or_new_tiles(tmp_path):
    source=fake_psn(tmp_path/'input'/'NPEF00069'/'EBOOT.PBP', b'A')
    a=zip_game(source,tmp_path/'Final Fantasy VII (English)(PSN).zip')
    b=zip_game(source,tmp_path/'Final Fantasy VII copy (PSN).zip')
    virtual=tmp_path/'virtual'
    calls=[]
    def extract(*args,**kwargs):
        calls.append(1)
        return mock_extractor(*args,**kwargs)
    result=batch_guided_import([a,b],virtual,'PS1',mock_chdman(tmp_path),
        auto_artwork=False,converter=mock_converter,psn_extractor=extract)
    assert (result['batch_completed'],result['batch_skipped']) == (1,1)
    assert len(calls)==1
    assert not result['errors']
    assert len(list((virtual/'ROMs'/'psx').glob('*/Final Fantasy VII*.m3u')))==1


def test_one_broken_archive_does_not_prevent_next_good_psn_game(tmp_path):
    bad=tmp_path/'Broken.zip';bad.write_bytes(b'NOT_A_ZIP')
    good=zip_game(fake_psn(tmp_path/'src'/'NPEF00069'/'EBOOT.PBP'),
                  tmp_path/'Final Fantasy VII (English)(PSN).zip')
    virtual=tmp_path/'virtual'
    result=batch_guided_import([bad,good],virtual,'PS1',mock_chdman(tmp_path),
        auto_artwork=False,converter=mock_converter,psn_extractor=mock_extractor)
    assert result['batch_total']==2
    assert result['batch_completed']==1
    assert result['batch_needs_attention']==1
    assert result['errors'] and result['batch_items'][0]['status']=='needs attention'
    assert (virtual/'ROMs'/'psx'/'Final Fantasy VII'/'Final Fantasy VII.m3u').exists()
    assert bad.read_bytes()==b'NOT_A_ZIP'


def test_batch_mixed_native_psp_eboot_is_not_falsely_converted_to_ps1(tmp_path):
    unknown=tmp_path/'PSP-homebrew'/'EBOOT.PBP'
    unknown.parent.mkdir();unknown.write_bytes(b'\0PBP'+b'\x00'*128)
    real=fake_psn(tmp_path/'Final Fantasy VII'/'NPEF00069'/'EBOOT.PBP')
    virtual=tmp_path/'virtual'
    result=batch_guided_import([unknown,real],virtual,'PS1',mock_chdman(tmp_path),
        auto_artwork=False,converter=mock_converter,psn_extractor=mock_extractor)
    assert result['batch_needs_attention']==1 and result['batch_completed']==1
    assert any('Not a recognizable PS1 Classics PBP' in e for e in result['errors'])
    assert not list((virtual/'ROMs'/'psx').rglob('EBOOT.PBP'))


def test_batch_import_folder_worker_discovers_nested_archives_and_eboots(tmp_path,monkeypatch):
    root=tmp_path/'PSN_collection';root.mkdir()
    good=zip_game(fake_psn(root/'source'/'NPEF00069'/'EBOOT.PBP'),
                  root/'Final Fantasy VII (English)(PSN).zip')
    extra=fake_psn(root/'Final Fantasy VIII'/'NPEF00070'/'EBOOT.PBP',b'B')
    # Don't process unarchived source of the same game twice; dedupe should catch it.
    seen={}
    def stub(paths,*args,**kwargs):
        seen['names']=[str(p) for p in paths]
        return {'batch_total':len(paths),'cancelled':False}
    import ps1_batch
    monkeypatch.setattr(ps1_batch,'batch_guided_import',stub)
    request={'mode':'batch_psn_folder', 'folder':str(root),
             'workspace':str(tmp_path/'virtual'), 'fallback':'PS1',
             'auto_ps1_chd':True, 'auto_artwork':False, 'binary':str(mock_chdman(tmp_path))}
    result=worker_handle(request,threading.Event())
    assert result['batch_total']==3
    assert len(seen['names'])==3
    assert good in [Path(p) for p in seen['names']]
    assert extra in [Path(p) for p in seen['names']]
    assert all(Path(p).suffix.casefold() in ('.zip','.7z','.pbp') for p in seen['names'])


def test_batch_real_7z_and_zip_both_queued_independently(tmp_path):
    py7zr=pytest.importorskip('py7zr')
    src=tmp_path/'raw';src.mkdir()
    a=fake_psn(src/'NPEF00069'/'EBOOT.PBP',b'A')
    one=zip_game(a,tmp_path/'Final Fantasy VII (English)(PSN).zip')
    b=fake_psn(src/'NPEF00070'/'EBOOT.PBP',b'B')
    two=tmp_path/'Final Fantasy VIII (English)(PSN).7z'
    with py7zr.SevenZipFile(two,'w') as z:
        for p in sorted(b.parent.iterdir()):
            z.write(p,arcname='NPEF00070/'+p.name)
    result=batch_guided_import([one,two],tmp_path/'virtual','PS1',mock_chdman(tmp_path),
        auto_artwork=False,converter=mock_converter,psn_extractor=mock_extractor)
    assert result['batch_total']==2 and result['batch_completed']==2
    assert result['converted']==6 and result['playlists']==2


def test_cancellation_prevents_starting_next_game(tmp_path):
    one=zip_game(fake_psn(tmp_path/'raw'/'NPEF00069'/'EBOOT.PBP'),
                 tmp_path/'First Game.zip')
    two=zip_game(fake_psn(tmp_path/'raw2'/'NPEF00070'/'EBOOT.PBP',b'B'),
                 tmp_path/'Second Game.zip')
    stopped=threading.Event()
    calls=[]
    def extractor(*args,**kw):
        calls.append(1)
        stopped.set()
        return mock_extractor(*args,**kw)
    result=batch_guided_import([one,two],tmp_path/'virtual','PS1',mock_chdman(tmp_path),
        cancel=stopped,auto_artwork=False,converter=mock_converter,
        psn_extractor=extractor)
    assert result['cancelled'] and len(calls)==1
    assert len(result['batch_items'])<=1
