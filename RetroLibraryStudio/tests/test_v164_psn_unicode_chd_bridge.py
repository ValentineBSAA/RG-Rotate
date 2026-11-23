"""v1.6.4: legacy Windows CHDman Unicode CUE path regression tests.

All fixtures are synthetic. No commercial game files, no actual CHDman.
"""
from __future__ import annotations

import struct
import threading
from pathlib import Path

import pytest

from disc_sets import inspect_cue
from ps1_chd_bridge import ascii_psn_cue
from ps1_pipeline import guided_import


def cue_track(folder: Path, filename: str, trackname: str = 'data_1.bin') -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / trackname).write_bytes(b'\x01' * 2352 * 4)
    cue = folder / filename
    cue.write_text(f'FILE "{trackname}" BINARY\n TRACK 01 MODE2/2352\n'
                   ' INDEX 01 00:00:00\n', encoding='utf-8')
    return cue


def test_unicode_trademark_cue_uses_ascii_alias_in_same_folder_and_cleans_up(tmp_path):
    cue = cue_track(tmp_path, 'Crash Bandicoot™ (Disc 1).cue')
    original = cue.read_bytes()
    with ascii_psn_cue(cue) as alias:
        assert alias != cue
        assert alias.is_file() and str(alias).isascii()
        assert alias.parent == cue.parent
        assert not inspect_cue(alias)['errors']
        assert (alias.parent / 'data_1.bin').is_file()
    assert cue.read_bytes() == original
    assert not alias.exists()
    assert not list(tmp_path.glob('rgl-disc-*.cue'))


def test_ascii_cue_requires_no_extra_work(tmp_path):
    cue = cue_track(tmp_path, 'Test Game (Disc 1).cue')
    with ascii_psn_cue(cue) as source:
        assert source == cue
    assert cue.exists()


def test_unicode_named_bin_uses_temporary_hardlink_without_copying_data(tmp_path):
    cue = cue_track(tmp_path, 'Crash™ (Disc 1).cue', 'dados™.bin')
    source = tmp_path / 'dados™.bin'
    original = source.read_bytes()
    with ascii_psn_cue(cue) as alias:
        assert str(alias).isascii()
        assert not inspect_cue(alias)['errors']
        payload = alias.read_text(encoding='utf-8')
        assert 'dados™.bin' not in payload
        assert 'rgl-track-' in payload
        staged_tracks = list(tmp_path.glob('rgl-track-*.bin'))
        assert len(staged_tracks) == 1
        assert staged_tracks[0].stat().st_ino == source.stat().st_ino
    assert source.read_bytes() == original
    assert not list(tmp_path.glob('rgl-track-*.bin'))
    assert not alias.exists()


def test_bridge_cancellation_creates_no_alias(tmp_path):
    cue = cue_track(tmp_path, 'Crash Bandicoot™ (Disc 1).cue')
    stop = threading.Event()
    stop.set()
    with pytest.raises(InterruptedError):
        with ascii_psn_cue(cue, cancel=stop):
            pytest.fail('must stop before conversion')
    assert not list(tmp_path.glob('rgl-disc-*.cue'))


def fake_pbp(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    key = b'TITLE\0'
    title = 'Crash Bandicoot™'.encode('utf-8') + b'\0'
    sfo = (struct.pack('<4sIIII', b'\0PSF', 0x101, 36, 36+len(key), 1)
           + struct.pack('<HBBIII', 0, 4, 2, len(title), len(title), 0)
           + key + title)
    psar = 40 + len(sfo)
    path.write_bytes(b'\0PBP' + struct.pack('<I', 0x10000)
                     + struct.pack('<8I', 40, *([psar] * 7))
                     + sfo + b'PSISOIMG00000000' + b'X' * 128)
    return path


def test_psn_unicode_real_title_goes_to_ascii_converter_and_unicode_card(tmp_path):
    pbp = fake_pbp(tmp_path / 'source' / 'NPEF00069' / 'EBOOT.PBP')
    card = tmp_path / 'virtual'
    chdman = tmp_path / 'chdman.exe'
    chdman.write_bytes(b'MOCK')
    encountered = []

    def extractor(pbp, temp, helper, **kwargs):
        # PSXtract produces a generic ASCII CUE, then the naming pipeline
        # replaces it with Crash Bandicoot™ (Disc 1).cue.
        return [cue_track(Path(temp), 'Disc 1.cue')]

    def converter(cue, tmp, binary, **kwargs):
        encountered.append(Path(cue))
        # Emulate legacy Windows CHDman rejecting non-ASCII command paths.
        if not str(cue).isascii():
            raise FileNotFoundError('chdman: no such file or directory')
        assert not inspect_cue(cue)['errors']
        out = Path(tmp) / (cue.stem + '.chd')
        out.write_bytes(b'SYNTHETIC VERIFIED CHD')
        return {'verified': True, 'cancelled': False, 'output': str(out)}

    result = guided_import([pbp], card, 'PS1', chdman,
                           auto_artwork=False, converter=converter,
                           psn_extractor=extractor)
    assert result['errors'] == []
    assert result['converted'] == 1 and result['copied'] == 1
    assert len(encountered) == 1
    assert encountered[0].name.startswith('rgl-disc-')
    root = card / 'ROMs' / 'psx' / 'Crash Bandicoot™'
    assert (root / 'Crash Bandicoot™ (Disc 1).chd').is_file()
    assert result['collection_folder'] == str(root)
    assert not list(card.glob('**/rgl-disc-*.cue'))
    assert not list(card.glob('**/data_1.bin'))
