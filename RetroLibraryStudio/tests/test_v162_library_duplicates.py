"""v1.6.2 library-wide dedupe: all supported consoles, archives, PS1 receipts.

Tests use synthetic payloads only; no copyrighted games, Sony keys, BIOSes.
"""
from __future__ import annotations

import io
import struct
import threading
from pathlib import Path
import pytest

from core import SYSTEM_DIR, import_files, inventory
from library_duplicates import inspect_game_duplicate, is_single_game_file
from ps1_duplicates import decide_repeat, fingerprint_pbp, record_import
from ps1_progress import PSXtractMilestones
from ps1_pipeline import guided_import
from ps1_psn import extract_psn_with_helper


@pytest.mark.parametrize('system,extension', [
    ('PS1', '.chd'), ('PSP', '.iso'), ('PS2', '.iso'),
    ('Nintendo DS', '.nds'), ('GBA', '.gba'), ('GB', '.gb'),
    ('GBC', '.gbc'), ('NES', '.nes'), ('SNES', '.sfc'),
    ('Genesis', '.md'), ('Nintendo 64', '.n64'),
    ('Dreamcast', '.cdi'), ('GameCube', '.gcm')
])
def test_skip_identical_bytes_on_every_supported_console_even_with_different_names(
        tmp_path, system, extension):
    workspace = tmp_path/'virtual'
    source_dir = tmp_path/'downloads'; source_dir.mkdir()
    source = source_dir/('FirstCopy' + extension)
    source.write_bytes(b'SYNTHETIC GAME CONTENT'*125)
    c,s,errors=import_files([source],workspace,system)
    assert (c,s,errors)==(1,0,[])
    renamed = source_dir/('CompletelyDifferentName' + extension)
    renamed.write_bytes(source.read_bytes())
    c,s,errors=import_files([renamed],workspace,system)
    assert (c,s,errors)==(0,1,[])
    actual=list((workspace/'ROMs'/SYSTEM_DIR[system]).rglob('*'+extension))
    assert len(actual)==1 and actual[0].name==source.name


def test_same_payload_may_exist_on_different_consoles(tmp_path):
    workspace=tmp_path/'virtual';downloads=tmp_path/'downloads'
    downloads.mkdir()
    game=downloads/'CommonName.iso';game.write_bytes(b'GAME_PAYLOAD')
    assert import_files([game],workspace,'PSP')==(1,0,[])
    assert import_files([game],workspace,'PS2')==(1,0,[])
    assert len(list((workspace/'ROMs'/'psp').glob('*.iso')))==1
    assert len(list((workspace/'ROMs'/'ps2').glob('*.iso')))==1


def test_same_title_different_bytes_flags_for_review_and_preserves_old(tmp_path):
    virtual=tmp_path/'virtual';source=tmp_path/'New'/'Game (USA).gba'
    source.parent.mkdir();source.write_bytes(b'FIRST_VERSION')
    assert import_files([source],virtual,'GBA')==(1,0,[])
    original=(virtual/'ROMs'/'gba'/source.name).read_bytes()
    second=tmp_path/'Other'/'Game (USA).gba'
    second.parent.mkdir();second.write_bytes(b'SECOND_VERSION')
    c,s,errors=import_files([second],virtual,'GBA')
    assert (c,s)==(0,0)
    assert errors and 'Possible duplicate on GBA' in errors[0]
    assert (virtual/'ROMs'/'gba'/source.name).read_bytes()==original


def test_distinct_regions_and_revisions_are_not_false_duplicates(tmp_path):
    virtual=tmp_path/'virtual';source_dir=tmp_path/'games';source_dir.mkdir()
    for title in ('Game (USA)', 'Game (Europe)', 'Game (USA) (Rev 1)'):
        p=source_dir/(title+'.nds');p.write_bytes(title.encode())
        assert import_files([p],virtual,'Nintendo DS')==(1,0,[])
    assert len(list((virtual/'ROMs'/'nds').glob('*.nds')))==3


def test_generic_psp_eboot_names_do_not_block_unrelated_games(tmp_path):
    virtual=tmp_path/'virtual'
    for index in (1,2):
        directory=tmp_path/f'PSP-GAME{index}';directory.mkdir()
        f=directory/'EBOOT.PBP';f.write_bytes(bytes([index])*128)
        copied, skipped, errors = import_files([f], virtual, 'PSP')
        if index == 1:
            assert (copied, skipped, errors) == (1, 0, [])
        else:
            assert (copied, skipped) == (0, 0)
            assert errors and 'Conflicting file exists' in errors[0]
    # Existing filename collision is refused by copy_atomic, not presented as
    # proof that different PSP EBOOTs are duplicates.
    assert (virtual/'ROMs'/'psp'/'EBOOT.PBP').read_bytes()==b'\x01'*128


def test_cue_bin_and_playlist_companion_files_not_deduped_independently(tmp_path):
    for name in ('track.bin','disc.cue','game.m3u','disc.gdi','image.sub'):
        assert not is_single_game_file(Path(name))


@pytest.mark.parametrize('extension', ['.zip','.7z'])
def test_repackaged_archive_with_same_game_bytes_is_skipped(tmp_path,extension):
    if extension=='.7z':
        zmod=pytest.importorskip('py7zr')
    else:
        import zipfile
    virtual=tmp_path/'virtual';folder=tmp_path/'source';folder.mkdir()
    member=folder/'SharedGame.gba';member.write_bytes(b'SAME GAME'*200)
    assert import_files([member],virtual,'GBA')==(1,0,[])
    archive=tmp_path/('TotallyNewArchiveName'+extension)
    if extension=='.zip':
        with zipfile.ZipFile(archive,'w') as z:
            z.write(member,arcname='SharedGame.gba')
    else:
        with zmod.SevenZipFile(archive,'w') as z:
            z.write(member,arcname='SharedGame.gba')
    c,s,errors=import_files([archive],virtual,'GBA')
    assert (c,s,errors)==(0,1,[])
    assert len(list((virtual/'ROMs'/'gba').rglob('*.gba')))==1
    assert archive.exists()


def test_archive_with_conflicting_named_game_does_not_partially_import(tmp_path):
    import zipfile
    virtual=tmp_path/'virtual'
    downloads=tmp_path/'downloads';downloads.mkdir()
    original=downloads/'Collision.gba';original.write_bytes(b'ONE')
    assert import_files([original],virtual,'GBA')==(1,0,[])
    archive=downloads/'package.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('NewGame.gba',b'NEW')
        z.writestr('Collision.gba',b'DIFFERENT')
    c,s,errs=import_files([archive],virtual,'GBA')
    assert (c,s)==(0,0) and any('Possible duplicate' in e for e in errs)
    assert not (virtual/'ROMs'/'gba'/'package').exists()


def test_psxtract_live_messages_are_disc_specific_and_do_not_leak_keys():
    milestones=PSXtractMilestones()
    captured=[]
    lines=[
        'Multi-disc game detected!',
        'Disc 1 serial: SCES_00867',
        'Building data track for disc 1...',
        'Disc 1 successfully converted using prebaked CUE file!',
        'Disc 2 serial: SCES_10867',
        'Building data track for disc 2...',
        'Disc 2 successfully converted using prebaked CUE file!',
        'Disc 3 serial: SCES_20867',
        'Building data track for disc 3...',
        'Disc 3 successfully converted using prebaked CUE file!',
        'MD5 verification result: PASS',
        'KEYS.BIN raw-private-data secret',
    ]
    for line in lines:
        result=milestones.event(line)
        if result:captured.append(result)
    assert any('Disc 1: rebuilding' in m for m in captured)
    assert any('Disc 2 reconstructed' in m for m in captured)
    assert any('Disc 3 reconstructed' in m for m in captured)
    assert any('MD5' in m and 'passed' in m for m in captured)
    assert not any('KEYS' in m or 'SCES_' in m or 'secret' in m for m in captured)
    assert milestones.completed=={1,2,3}


def synthetic_pbp(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'\0PBP'+struct.pack('<I',65536)
                     +struct.pack('<8I',*(40 for _ in range(8)))
                     +b'PSTITLEIMG000000'+b'\x00'*128)
    return path


def synthetic_cue(folder,n):
    folder.mkdir(parents=True,exist_ok=True)
    name=f'Sony Disc {n}'
    (folder/(name+'.bin')).write_bytes(b'\x00'*(2352*3))
    c=folder/(name+'.cue')
    c.write_text(f'FILE "{name}.bin" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n')
    return c


def fake_chd_converter(cue,output,binary,**kwargs):
    p=Path(output)/(Path(cue).stem+'.chd')
    p.write_bytes(b'FAKE_CHD_'+cue.stem.encode())
    return {'output':str(p),'verified':True,'cancelled':False}


def test_psn_source_receipt_does_not_create_extra_rom_tile_and_prevents_repeat(tmp_path):
    pbp=synthetic_pbp(tmp_path/'Final Fantasy VII'/'NPEF00069'/'EBOOT.PBP')
    key=pbp.parent/'KEYS.BIN';key.write_bytes(b'PRIVATE_KEY_MATERIAL_NOT_HERE')
    doc=pbp.parent/'DOCUMENT.DAT';doc.write_bytes(b'SAMPLE')
    exe=tmp_path/'chdman.exe';exe.write_bytes(b'MOCK')
    calls=[]
    def extractor(pbp,folder,helper,**kwargs):
        calls.append('decrypted')
        return [synthetic_cue(folder,n) for n in (1,2,3)]
    virtual=tmp_path/'virtual'
    first=guided_import([pbp,key,doc],virtual,'PS1',exe,
                        auto_artwork=False,converter=fake_chd_converter,
                        psn_extractor=extractor)
    assert first['converted']==3 and first['playlists']==1 and not first['errors']
    assert calls==['decrypted']
    assert decide_repeat(virtual,'Final Fantasy VII',fingerprint_pbp(pbp))[0]=='same'
    assert (virtual/'.retro-library'/'psn-sources').is_dir()
    assert not list((virtual/'ROMs').rglob('.retro-ps1-source.json'))
    before=inventory(virtual)[0]
    assert len([e for e in before if e.extension=='.json'])==0
    second=guided_import([pbp,key,doc],virtual,'PS1',exe,
                         auto_artwork=False,converter=fake_chd_converter,
                         psn_extractor=extractor)
    assert calls==['decrypted']
    assert second['converted']==0 and second['skipped']==1
    assert not second['errors']
    assert key.read_bytes()==b'PRIVATE_KEY_MATERIAL_NOT_HERE'


def test_existing_legacy_ps1_collection_requires_review_not_unproven_skip(tmp_path):
    virtual=tmp_path/'virtual';folder=virtual/'ROMs'/'psx'/'Final Fantasy VII'
    folder.mkdir(parents=True)
    for n in (1,2,3):
        (folder/f'Final Fantasy VII (Disc {n}).chd').write_bytes(b'CHD'+bytes([n]))
    (folder/'Final Fantasy VII.m3u').write_text(
        ''.join(f'Final Fantasy VII (Disc {n}).chd\n' for n in (1,2,3)))
    decision,note=decide_repeat(virtual,'FinalFantasyVII','a'*64)
    assert decision=='review' and 'source' in note
    assert len(list(folder.iterdir()))==4


def test_extractor_output_bridge_yields_live_events_without_raw_console(tmp_path,monkeypatch):
    from ps1_psn import extract_psn_with_helper
    import ps1_psn
    pbp=synthetic_pbp(tmp_path/'Final Fantasy VII'/'EBOOT.PBP')
    helper=tmp_path/'psxtract.exe';helper.write_bytes(b'fake')
    output=tmp_path/'temporary';output.mkdir()
    synthetic_cue(output,1)
    class FakeProc:
        def __init__(self,**kwargs):
            self.stdout=io.BytesIO(
                b'Multi-disc game detected!\n'
                b'Disc 1 serial: SCES_00867\n'
                b'Building data track for disc 1...\n'
                b'Disc 1 successfully converted using prebaked CUE file!\n'
                b'Secret KEYS.BIN should not be shown\n')
            self.returncode=0
        def poll(self):return 0
        def wait(self,timeout=None):return 0
        def kill(self):return None
    monkeypatch.setattr(ps1_psn.subprocess,'Popen',lambda *args,**kwargs:FakeProc())
    notices=[]
    def progress(message,n,total):notices.append(message)
    # Extraction requires an empty target, so create cue files only after
    # validating the source and invoking the mocked converter.
    for f in output.iterdir():f.unlink()
    # The real converter would generate files; provide one when fake process starts.
    def fake_start(*args,**kwargs):
        synthetic_cue(output,1)
        return FakeProc()
    monkeypatch.setattr(ps1_psn.subprocess,'Popen',fake_start)
    cues=extract_psn_with_helper(pbp,output,helper,progress=progress)
    assert len(cues)==1 and cues[0].suffix=='.cue'
    assert any('Disc 1 identified' in x for x in notices)
    assert any('Disc 1 reconstructed' in x for x in notices)
    assert all('KEYS.BIN' not in x for x in notices)

def test_duplicate_files_inside_one_zip_do_not_create_two_game_tiles(tmp_path):
    import zipfile
    workspace=tmp_path/'virtual'
    archive=tmp_path/'TwoCopies.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('FirstGame.gba',b'ONE IDENTICAL PAYLOAD')
        z.writestr('RenamedCopy.gba',b'ONE IDENTICAL PAYLOAD')
    copied, skipped, errors=import_files([archive],workspace,'GBA')
    assert (copied,skipped,errors)==(1,1,[])
    assert len(list((workspace/'ROMs'/'gba').rglob('*.gba')))==1
    assert archive.exists()

