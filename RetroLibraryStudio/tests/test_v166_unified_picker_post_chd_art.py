"""v1.6.6 regressions: one/many PS1 title chooser and *post-CHD* artwork.

Only synthetic PBP, CUE, CHD, and PNG data; no commercial game/keys or network.
"""
from __future__ import annotations

import base64
import struct
from pathlib import Path

import pytest

import artwork_gallery as art
from psn_picker import ps1_parent_from_last_location
from ps1_pipeline import guided_import

PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAOZrkK0AAAAASUVORK5CYII=')


def pbp_with_title(path: Path, title: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    key = b'TITLE\0'
    data = title.encode('utf-8') + b'\0'
    sfo = (struct.pack('<4sIIII', b'\0PSF', 0x101, 36, 36 + len(key), 1)
           + struct.pack('<HBBIII', 0, 4, 2, len(data), len(data), 0)
           + key + data)
    start = 40 + len(sfo)
    path.write_bytes(b'\0PBP' + struct.pack('<I', 0x10000)
                     + struct.pack('<8I', 40, *([start] * 7))
                     + sfo + b'PSISOIMG00000000' + b'X' * 128)
    return path


def extracted_cue(pbp, temp, helper, **kwargs):
    temp = Path(temp)
    (temp / 'data_1.bin').write_bytes(b'\x00' * (2352 * 4))
    cue = temp / 'Disc 1.cue'
    cue.write_text('FILE "data_1.bin" BINARY\n'
                   ' TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n', encoding='utf-8')
    return [cue]


def test_last_ps1_location_routes_to_parent_for_one_or_many_game_codes():
    src = Path('/source/PSTV/PSP/GAME/PS1/NPEE00008/EBOOT.PBP')
    assert ps1_parent_from_last_location(src) == Path('/source/PSTV/PSP/GAME/PS1')
    assert ps1_parent_from_last_location(src.parent) == src.parent.parent
    assert ps1_parent_from_last_location(src.parent.parent) == src.parent.parent
    assert ps1_parent_from_last_location(Path('/source/SNES/Games')) is None


def test_trademark_artwork_search_matches_canonical_us_cover_exactly():
    titles = ['Crash Bandicoot (Europe)', 'Crash Bandicoot (USA)',
              'Crash Bandicoot Racing (USA)']
    assert art.find_art_matches('Crash Bandicoot™', titles)['automatic'] == 'Crash Bandicoot (USA)'
    assert art.find_art_matches('Crash Bandicoot 2™', [
        'Crash Bandicoot 2 (USA)', 'Crash Bandicoot 3 (USA)'])['automatic'] == 'Crash Bandicoot 2 (USA)'


def test_post_chd_cover_applies_automatically_without_prompt_and_retains_chd(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'local-cache'))
    title = 'Crash Bandicoot 2™'
    pbp = pbp_with_title(tmp_path / 'source' / 'PS1' / 'NPEE00008' / 'EBOOT.PBP', title)
    workspace = tmp_path / 'card'
    binary = tmp_path / 'chdman.exe'
    binary.write_bytes(b'TEST-ONLY')
    stages = []

    def converter(cue, temp, binary, **kwargs):
        stages.append('convert')
        assert cue.is_file()
        output = Path(temp) / 'output.chd'
        output.write_bytes(b'SYNTHETIC VERIFIED CHD')
        return {'output': str(output), 'verified': True, 'cancelled': False}

    def fake_catalog(system, workspace):
        stages.append('catalog')
        assert (workspace / 'ROMs' / 'psx' / title / f'{title} (Disc 1).chd').is_file()
        return ['Crash Bandicoot 2 (USA)', 'Crash Bandicoot 2 (Europe)']

    def fake_stage(workspace, system, stem, source_title):
        stages.append('cover')
        assert source_title == 'Crash Bandicoot 2 (USA)'
        return art.save_cover_bytes(workspace, system, stem, PNG, source=source_title)

    monkeypatch.setattr(art, 'catalog_for', fake_catalog)
    monkeypatch.setattr(art, 'stage_online_cover', fake_stage)
    result = guided_import([pbp], workspace, 'PS1', binary,
        psn_extractor=extracted_cue, converter=converter,
        auto_artwork=True)
    assert not result['errors']
    assert result['copied'] == 1
    assert result['artwork_attempted']
    assert result['artwork']['downloaded'] == 1
    assert stages == ['convert', 'catalog', 'cover']
    assert (workspace / 'Media' / 'BoxArt' / 'psx' / f'{title}.png').is_file()

    # The exact package is now a known complete CHD. Reimport must not call
    # converter/PSXtract again, while an existing/missing cover is checked.
    def no_extract(*args, **kwargs):
        pytest.fail('PSXtract must not run when EBOOT receipt matches')
    repeat = guided_import([pbp], workspace, 'PS1', binary,
        psn_extractor=no_extract, converter=converter,
        auto_artwork=True)
    assert not repeat['errors']
    assert repeat['skipped'] == 1 and repeat['converted'] == 0
    assert repeat['artwork_attempted']
    assert repeat['artwork']['already present'] == 1
    assert stages == ['convert', 'catalog', 'cover']


def test_failed_artwork_remains_nonfatal_after_verified_chd(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'local-cache'))
    title = 'Crash Bandicoot™'
    pbp = pbp_with_title(tmp_path / 'PS1' / 'NPEE00001' / 'EBOOT.PBP', title)
    binary = tmp_path / 'chdman.exe'
    binary.write_bytes(b'TEST')

    def converter(cue, temp, binary, **kwargs):
        out = Path(temp) / 'verified.chd'
        out.write_bytes(b'SYNTHETIC VERIFIED CHD')
        return {'output': str(out), 'verified': True, 'cancelled': False}

    monkeypatch.setattr(art, 'catalog_for',
                        lambda *args: (_ for _ in ()).throw(OSError('offline')))
    workspace = tmp_path / 'card'
    result = guided_import([pbp], workspace, 'PS1', binary,
        psn_extractor=extracted_cue, converter=converter, auto_artwork=True)
    assert result['converted'] == 1
    assert (workspace / 'ROMs' / 'psx' / title / f'{title} (Disc 1).chd').is_file()
    assert result['artwork_attempted']
    assert result['artwork'].get('error') or result['artwork'].get('review')
