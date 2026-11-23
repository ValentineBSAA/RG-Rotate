"""v1.6.1: Actual 7z extraction, PSN PBP classification and mocked helper bridge.

Does not claim encrypted Sony PSN decryption on a real EBOOT. User-provided
PSXtract and real CHDman remain separate Windows acceptance gates.
"""
from __future__ import annotations
import struct
from pathlib import Path

import pytest

from core import inventory
from library_presentation import group_games, format_badge_info
from ps1_pipeline import guided_import
from ps1_psn import (pbp_disc_signature, is_ps1_classic, package_title,
                     ordered_psn_cues, extract_psn_with_helper, psn_companions)


def fake_pbp(path: Path, *, multi=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    signature = b'PSTITLEIMG000000' if multi else b'PSISOIMG0000'
    # The eight offsets point into a minimal synthetic PSAR. Not a usable game.
    path.write_bytes(b'\0PBP' + struct.pack('<I', 0x10000) +
                     struct.pack('<8I', *(40 for _ in range(8))) +
                     signature + b'\x00' * 128)
    return path


def fake_cue(folder: Path, title: str):
    folder.mkdir(parents=True, exist_ok=True)
    binfile = folder / (title + '.bin')
    binfile.write_bytes(b'\x01' * (2352 * 4))
    cue = folder / (title + '.cue')
    cue.write_text(f'FILE "{binfile.name}" BINARY\n'
                   ' TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n')
    return cue


def fake_chdman(tmp_path):
    binary = tmp_path / 'chdman.exe'
    binary.write_bytes(b'MOCK')
    return binary


def fake_converter(cue, output, binary, **kwargs):
    out = Path(output) / (Path(cue).stem + '.chd')
    out.write_bytes(b'SYNTHETIC CHD ' + cue.stem.encode())
    return {'output': str(out), 'verified': True, 'cancelled': False}


def mock_psxtract(pbp, output, helper, **kwargs):
    return [fake_cue(Path(output), f'Sony Disc {i}') for i in (3,1,2)]


def test_pbp_with_keys_is_ps1_classic_not_native_psp(tmp_path):
    d = tmp_path / 'Final Fantasy VII (English)(PSN)' / 'NPEF00069'
    p = fake_pbp(d / 'EBOOT.PBP')
    key = d / 'KEYS.BIN'; key.write_bytes(b'FAKE_KEY_NOT_REAL')
    doc = d / 'DOCUMENT.DAT'; doc.write_bytes(b'DOC')
    assert is_ps1_classic(p) and pbp_disc_signature(p) == 'multi'
    assert psn_companions(p) == (doc,key)
    assert package_title(p) == 'Final Fantasy VII'
    assert not is_ps1_classic(d / 'KEYS.BIN')
    assert not is_ps1_classic(d / 'DOCUMENT.DAT')


def test_psn_three_discs_into_one_chd_collection_with_original_keys_untouched(tmp_path):
    d = tmp_path / 'Final Fantasy VII (English)(PSN)' / 'NPEF00069'
    p = fake_pbp(d / 'EBOOT.PBP')
    k = d / 'KEYS.BIN'; k.write_bytes(b'FAKE_KEY_NOT_REAL')
    doc = d / 'DOCUMENT.DAT'; doc.write_bytes(b'DOC')
    original = [(item, item.read_bytes()) for item in (p,k,doc)]
    card = tmp_path / 'virtual'
    report = guided_import([p,k,doc], card, 'PS1', fake_chdman(tmp_path),
                           auto_artwork=False, converter=fake_converter,
                           psn_extractor=mock_psxtract)
    assert report['converted'] == 3 and report['playlists'] == 1
    assert not report['errors']
    dest = card/'ROMs'/'psx'/'Final Fantasy VII'
    assert sorted(p.name for p in dest.glob('*.chd')) == [
        f'Final Fantasy VII (Disc {n}).chd' for n in (1,2,3)]
    playlist = dest/'Final Fantasy VII.m3u'
    assert playlist.read_text().splitlines() == [
        f'Final Fantasy VII (Disc {n}).chd' for n in (1,2,3)]
    groups = group_games(inventory(card)[0])
    assert len(groups) == 1 and len(groups[0]) == 4
    assert format_badge_info(groups[0][0],groups[0])['badge'] == '3 DISCS'
    assert not list(card.glob('**/KEYS.BIN'))
    assert all(file.read_bytes() == expected for file,expected in original)


def test_missing_optional_external_extractor_fails_cleanly_and_preserves_keys(tmp_path):
    d=tmp_path/'Final Fantasy VII'/'NPEF00069'
    p=fake_pbp(d/'EBOOT.PBP')
    k=d/'KEYS.BIN';k.write_bytes(b'ORIGINAL')
    report=guided_import([p,k],tmp_path/'card','PS1',fake_chdman(tmp_path),
                         auto_artwork=False,
                         psxtract_binary=tmp_path/'MISSING'/'psxtract.exe')
    assert report['converted'] == 0
    assert any('PSXtract' in s for s in report['errors'])
    assert k.read_bytes() == b'ORIGINAL'
    assert not list((tmp_path/'card').glob('**/*.chd'))


def test_unknown_psp_eboot_not_falsely_converted_to_ps1(tmp_path):
    d=tmp_path/'PSP game';d.mkdir()
    pbp=d/'EBOOT.PBP';pbp.write_bytes(b'\0PBP' + b'\x00'*60)
    assert not is_ps1_classic(pbp)
    report=guided_import([pbp],tmp_path/'card','PS1',fake_chdman(tmp_path),
                         auto_artwork=False)
    assert report['converted'] == 0
    assert any('Not a recognizable PS1 Classics' in s for s in report['errors'])
    assert not list((tmp_path/'card').glob('**/*.pbp'))


def test_ambiguous_psn_disc_order_is_refused_without_chd(tmp_path):
    d=tmp_path/'temp'
    cues=[fake_cue(d,'Alpha'),fake_cue(d,'Beta'),fake_cue(d,'Gamma')]
    with pytest.raises(ValueError, match='Cannot prove the order'):
        ordered_psn_cues(cues,'Final Fantasy VII',multi_expected=True)
    with pytest.raises(ValueError,match='fewer than two'):
        ordered_psn_cues(cues[:1],'Final Fantasy VII',multi_expected=True)


def test_direct_real_7z_three_cue_bin_discs_convert_with_valid_playlist(tmp_path):
    py7zr=pytest.importorskip('py7zr')
    root=tmp_path/'source';root.mkdir()
    for n in (1,2,3):
        fake_cue(root,f'Final Fantasy VII (USA) (Disc {n})')
    archive=tmp_path/'Final Fantasy VII (USA).7z'
    with py7zr.SevenZipFile(archive,'w') as z:
        for source in sorted(root.iterdir()):
            z.write(source,arcname=source.name)
    card=tmp_path/'virtual'
    result=guided_import([archive],card,'PS1',fake_chdman(tmp_path),
                         auto_artwork=False,converter=fake_converter)
    assert result['converted']==3 and result['playlists']==1 and not result['errors']
    groups=group_games(inventory(card)[0])
    assert len(groups)==1 and format_badge_info(groups[0][0],groups[0])['badge']=='3 DISCS'
    assert archive.exists() and len(list(root.iterdir())) == 6


def test_real_7z_psn_package_routes_keys_as_companion_with_title_hint(tmp_path):
    py7zr=pytest.importorskip('py7zr')
    source=tmp_path/'source'/'NPEF00069'
    pbp=fake_pbp(source/'EBOOT.PBP')
    key=source/'KEYS.BIN';key.write_bytes(b'FAKE_KEY')
    doc=source/'DOCUMENT.DAT';doc.write_bytes(b'DOC')
    archive=tmp_path/'Final Fantasy VII (English)(PSN).7z'
    with py7zr.SevenZipFile(archive,'w') as z:
        for src in (pbp,key,doc):
            z.write(src,arcname='NPEF00069/'+src.name)
    report=guided_import([archive],tmp_path/'virtual','PS1',fake_chdman(tmp_path),
                         auto_artwork=False,converter=fake_converter,
                         psn_extractor=mock_psxtract)
    assert report['converted']==3 and report['playlists']==1 and not report['errors']
    folder=tmp_path/'virtual'/'ROMs'/'psx'/'Final Fantasy VII'
    assert (folder/'Final Fantasy VII.m3u').exists()
    assert archive.exists()
    assert not list((tmp_path/'virtual').glob('**/KEYS.BIN'))
