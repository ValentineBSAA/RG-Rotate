"""v1.6.3 regression: actual PSN title identity, folder safety and Stop.

Only synthetic PBP/PARAM.SFO/CUE/CHD fixtures. No Sony keys or game data.
"""
from __future__ import annotations

import struct
import threading
import zipfile
from pathlib import Path

import pytest

from ps1_batch import batch_guided_import
from ps1_psn import meaningful_title, package_title, pbp_metadata_title
from ps1_duplicates import decide_repeat
from core import inventory
from library_presentation import group_games


def fake_pbp(path: Path, title: str | None, marker: bytes = b'X') -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    sfo = b''
    if title is not None:
        key = b'TITLE\0'
        value = title.encode('utf-8') + b'\0'
        sfo = (struct.pack('<4sIIII', b'\0PSF', 0x101, 36, 36 + len(key), 1)
               + struct.pack('<HBBIII', 0, 4, 2, len(value), len(value), 0)
               + key + value)
    psar_start = 40 + len(sfo)
    path.write_bytes(
        b'\0PBP' + struct.pack('<I', 0x10000)
        + struct.pack('<8I', 40, *([psar_start] * 7))
        + sfo + b'PSTITLEIMG000000' + marker * 128
    )
    return path


def archive_game(pbp: Path, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'w') as z:
        z.write(pbp, arcname='NPEF00069/EBOOT.PBP')
    return target


def fake_cue(temp: Path, number: int) -> Path:
    temp.mkdir(parents=True, exist_ok=True)
    name = f'Generic Disc {number}'
    (temp / (name + '.bin')).write_bytes(bytes([number]) * (2352 * 3))
    cue = temp / (name + '.cue')
    cue.write_text(
        f'FILE "{name}.bin" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n',
        encoding='utf-8'
    )
    return cue


def mock_extract(pbp, temp, helper, *, cancel=None, progress=None):
    return [fake_cue(Path(temp), n) for n in (1, 2, 3)]


def mock_convert(cue, temp, binary, *, cancel=None, progress=None):
    dest = Path(temp) / (Path(cue).stem + '.chd')
    dest.write_bytes(b'SYNTHETIC VERIFIED CHD ' + Path(cue).stem.encode('utf-8'))
    return {'output': str(dest), 'verified': True, 'cancelled': False}


def mock_binary(tmp: Path) -> Path:
    p = tmp / 'chdman.exe'
    p.write_bytes(b'TEST ONLY')
    return p


@pytest.mark.parametrize('name', ['PS1', 'PSX', 'PlayStation', 'PlayStation One',
                                  'Game', 'NPEF00069', 'Disc 1', 'PSP'])
def test_generic_name_cannot_identify_game(name):
    assert meaningful_title(name) is None


def test_param_sfo_title_overrides_generic_archive_and_storage_names(tmp_path):
    pbp = fake_pbp(tmp_path / 'rgl-archive-test' / 'NPEF00069' / 'EBOOT.PBP',
                   'Final Fantasy VII')
    assert pbp_metadata_title(pbp) == 'Final Fantasy VII'
    assert package_title(pbp, 'PS1') == 'Final Fantasy VII'


def test_generic_ps1_without_metadata_fails_closed(tmp_path):
    pbp = fake_pbp(tmp_path / 'rgl-archive-test' / 'NPEF00069' / 'EBOOT.PBP',
                   None)
    with pytest.raises(ValueError, match='Cannot identify'):
        package_title(pbp, 'PS1')


def test_generic_archives_with_different_embedded_titles_do_not_merge(tmp_path):
    a = archive_game(fake_pbp(tmp_path / 'a' / 'EBOOT.PBP', 'Final Fantasy VII', b'A'),
                     tmp_path / 'source_a' / 'PS1.zip')
    b = archive_game(fake_pbp(tmp_path / 'b' / 'EBOOT.PBP', 'Final Fantasy VIII', b'B'),
                     tmp_path / 'source_b' / 'PS1.zip')
    card = tmp_path / 'virtual'
    messages = []
    result = batch_guided_import([a, b], card, 'PS1', mock_binary(tmp_path),
        progress=lambda m, n, t: messages.append(m),
        auto_artwork=False, converter=mock_convert, psn_extractor=mock_extract)
    assert not result['errors']
    assert result['batch_completed'] == 2
    assert [x['name'] for x in result['batch_items']] == [
        'Final Fantasy VII', 'Final Fantasy VIII']
    assert all('PS1.zip' not in x['name'] for x in result['batch_items'])
    for title in ('Final Fantasy VII', 'Final Fantasy VIII'):
        root = card / 'ROMs' / 'psx' / title
        assert len(list(root.glob('*.chd'))) == 3
        assert (root / (title + '.m3u')).is_file()
    assert not (card / 'ROMs' / 'psx' / 'PS1').exists()
    assert len(group_games(inventory(card)[0])) == 2
    assert any('Batch 1/2 • Final Fantasy VII •' in m for m in messages)
    assert any('Batch 2/2 • Final Fantasy VIII •' in m for m in messages)
    assert all(item['folder'].endswith(item['name']) for item in result['batch_items'])


def test_unidentifiable_archive_needs_attention_without_publishing_ps1_chd(tmp_path):
    bad = archive_game(fake_pbp(tmp_path / 'bad' / 'EBOOT.PBP', None, b'B'),
                       tmp_path / 'batch' / 'PS1.zip')
    good = archive_game(fake_pbp(tmp_path / 'good' / 'EBOOT.PBP', 'Suikoden', b'G'),
                        tmp_path / 'other' / 'PS1.zip')
    card = tmp_path / 'virtual'
    result = batch_guided_import([bad, good], card, 'PS1', mock_binary(tmp_path),
        auto_artwork=False, converter=mock_convert, psn_extractor=mock_extract)
    assert result['batch_needs_attention'] == 1
    assert result['batch_completed'] == 1
    assert not (card / 'ROMs' / 'psx' / 'PS1').exists()
    assert (card / 'ROMs' / 'psx' / 'Suikoden' / 'Suikoden.m3u').exists()
    assert bad.is_file()


def test_cancel_mid_first_game_never_starts_second_package(tmp_path):
    a = archive_game(fake_pbp(tmp_path / 'a' / 'EBOOT.PBP', 'Final Fantasy VII'),
                     tmp_path / 'a_out' / 'PS1.zip')
    b = archive_game(fake_pbp(tmp_path / 'b' / 'EBOOT.PBP', 'Suikoden'),
                     tmp_path / 'b_out' / 'PS1.zip')
    stop = threading.Event()
    calls = []
    def stop_extract(pbp, temp, helper, **kwargs):
        calls.append(Path(pbp))
        stop.set()
        return mock_extract(pbp, temp, helper)
    result = batch_guided_import([a, b], tmp_path / 'virtual', 'PS1',
        mock_binary(tmp_path), auto_artwork=False, cancel=stop,
        converter=mock_convert, psn_extractor=stop_extract)
    assert result['cancelled']
    assert len(calls) == 1
    assert b.is_file()


def test_verified_single_disc_gets_fingerprint_receipt_and_skips_repeat(tmp_path):
    pbp = fake_pbp(tmp_path / 'src' / 'NPEF00069' / 'EBOOT.PBP', 'Clock Tower')
    first = archive_game(pbp, tmp_path / 'first' / 'PS1.zip')
    second = archive_game(pbp, tmp_path / 'second' / 'PS1.zip')
    card = tmp_path / 'virtual'
    calls = []
    def one_disc(pbp, temp, helper, **kwargs):
        calls.append(1)
        return [fake_cue(Path(temp), 1)]
    result = batch_guided_import([first, second], card, 'PS1',
        mock_binary(tmp_path), auto_artwork=False, converter=mock_convert,
        psn_extractor=one_disc)
    assert not result['errors']
    assert (result['batch_completed'], result['batch_skipped']) == (1, 1)
    assert len(calls) == 1
    root = card / 'ROMs' / 'psx' / 'Clock Tower'
    assert (root / 'Clock Tower (Disc 1).chd').is_file()
    assert not list(root.glob('*.m3u'))
