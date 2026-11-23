"""v1.6.7 regression tests for readable PSXtract failures and compact game picker.

Synthetic-only: no real Sony keys, no decrypted content or third-party helpers.
"""
from pathlib import Path
import struct
import io
import pytest

import ps1_psn

from ps1_progress import PSXtractMilestones
from ps1_psn import describe_extractor_failure, psn_companions
from psn_picker import scan_psn_sources


def title_eboot(path, title='Clock Tower II - The Struggle Within'):
    path.parent.mkdir(parents=True, exist_ok=True)
    key = b'TITLE\0'
    val = title.encode('utf-8') + b'\0'
    sfo = (struct.pack('<4sIIII', b'\0PSF', 0x101, 36, 36 + len(key), 1)
           + struct.pack('<HBBIII', 0, 4, 2, len(val), len(val), 0)
           + key + val)
    off = 40 + len(sfo)
    path.write_bytes(b'\0PBP' + struct.pack('<I', 0x10000) +
                     struct.pack('<8I', 40, *([off] * 7)) +
                     sfo + b'PSISOIMG00000000' + b'X' * 200)
    return path


def test_console_pgd_failure_is_visible_but_never_exposes_key_or_source_path():
    progress = PSXtractMilestones()
    assert progress.event('PGD: Invalid 0x80 MAC hash!') == (
        'PS1 extraction blocked • Protected image-header authentication failed')
    assert progress.event('ERROR: ISO header decryption failed!') == (
        'PS1 extraction blocked • Could not read the protected disc header')
    assert progress.pgd_header_failed and progress.iso_header_failed
    result = describe_extractor_failure(
        progress, has_document=False, has_keys=True, returncode=-4294967295)
    assert '0x80 MAC' in result and 'CHD conversion never started' in result
    assert 'KEYS.BIN was found' in result
    assert 'DOCUMENT.DAT' in result
    assert '-4294967295' not in result
    assert 'No actual game data' not in result
    assert 'KEY BYTES' not in result


def test_failure_with_both_companions_distinguishes_provided_files():
    p = PSXtractMilestones()
    p.event('PGD: Invalid 0x80 MAC hash!')
    result = describe_extractor_failure(p, has_document=True, has_keys=True, returncode=1)
    assert 'Available companion files were supplied' in result
    assert 'built-in key calculation' not in result


def test_failure_without_any_companion_explains_key_derivation_not_missing_game():
    p = PSXtractMilestones()
    p.event('ERROR: ISO header decryption failed!')
    text = describe_extractor_failure(p, has_document=False, has_keys=False, returncode=1)
    assert 'No adjacent KEYS.BIN' in text
    assert 'Original files remain untouched' in text


def test_generic_non_crypto_error_keeps_diagnostics_without_bad_claim():
    p = PSXtractMilestones()
    text = describe_extractor_failure(p, has_document=False, has_keys=False, returncode=3)
    assert 'Helper status: 3' in text
    assert '0x80 MAC' not in text
    assert 'CHD conversion was not attempted' in text


def test_picker_reports_sidecar_presence_without_exposing_contents(tmp_path):
    root = tmp_path / 'PS1'
    game = title_eboot(root / 'SLUS00695' / 'EBOOT.PBP')
    key = game.parent / 'KEYS.BIN'
    key.write_bytes(b'NOT_A_REAL_KEY')
    before = key.read_bytes()
    games = scan_psn_sources(root)['games']
    assert len(games) == 1
    assert games[0]['title'] == 'Clock Tower II - The Struggle Within'
    assert games[0]['code'] == 'SLUS00695'
    assert 'key file: present' in games[0]['detail']
    assert 'manual: not found' in games[0]['detail']
    assert 'key-only positional' in games[0]['detail']
    assert 'NOT_A_REAL_KEY' not in str(games)
    assert key.read_bytes() == before
    assert psn_companions(game) == (None, key)


def test_picker_compact_text_and_no_opaque_full_path_header():
    app = (Path(__file__).resolve().parents[1] / 'app.py').read_text('utf-8')
    assert 'Select PlayStation games' in app
    assert "Source: {folder.name}" in app
    assert "Search game name or Sony ID" in app
    assert "Game import results" in app
    assert 'Titles come from EBOOT metadata where available, not guessed Sony folder IDs.' not in app



def test_verified_psxtract_v3_key_only_requires_approved_helper_receipt(tmp_path, monkeypatch):
    helper = tmp_path / 'WindowsTools' / 'psxtract' / 'psxtract.exe'
    helper.parent.mkdir(parents=True)
    helper.write_bytes(b'NOT_AN_EXE')
    monkeypatch.setattr('tool_setup.tool_status', lambda root: {
        'PSXtract': {'installed': True}})
    assert ps1_psn.verified_psxtract_v3_key_only(helper)
    assert not ps1_psn.verified_psxtract_v3_key_only(tmp_path / 'untrusted.exe')
    monkeypatch.setattr('tool_setup.tool_status', lambda root: {
        'PSXtract': {'installed': False}})
    assert not ps1_psn.verified_psxtract_v3_key_only(helper)


@pytest.mark.parametrize('verified,with_manual,expected_keys', [
    (True, False, True),
    (False, False, False),
    (False, True, True),
])
def test_extractor_keys_argument_is_used_safely_with_verified_v3(
        tmp_path, monkeypatch, verified, with_manual, expected_keys):
    game = title_eboot(tmp_path / 'source' / 'SLUS00695' / 'EBOOT.PBP')
    keys = game.parent / 'KEYS.BIN'
    keys.write_bytes(b'FAKE_KEY_BYTES_NEVER_SHARED')
    manual = game.parent / 'DOCUMENT.DAT'
    if with_manual:
        manual.write_bytes(b'FAKE_DOC')
    helper = tmp_path / 'psxtract' / 'psxtract.exe'
    helper.parent.mkdir()
    helper.write_bytes(b'NOT_AN_EXECUTABLE')
    output = tmp_path / 'out'
    output.mkdir()
    calls = []
    monkeypatch.setattr(ps1_psn, 'verified_psxtract_v3_key_only',
                        lambda h: verified)
    class Proc:
        def __init__(self, args, **kwargs):
            calls.append(args)
            self.stdout = io.BytesIO(
                b'PGD: Invalid 0x80 MAC hash!\n'
                b'ERROR: ISO header decryption failed!\n')
            self.returncode = 1
        def poll(self):
            return 1
    monkeypatch.setattr(ps1_psn.subprocess, 'Popen', Proc)
    with pytest.raises(RuntimeError, match='0x80 MAC') as exc:
        ps1_psn.extract_psn_with_helper(game, output, helper)
    assert len(calls) == 1
    args = calls[0]
    if with_manual:
        assert args[-2:] == [str(manual.resolve()), str(keys.resolve())]
    elif expected_keys:
        assert args[-2:] == ['', str(keys.resolve())]
    else:
        assert len(args) == 3
    assert (str(keys.resolve()) in args) == expected_keys
    assert ('was passed to the verified v3' in str(exc.value)) == (
        verified and not with_manual)
    assert 'FAKE_KEY_BYTES_NEVER_SHARED' not in str(exc.value)
    assert keys.read_bytes() == b'FAKE_KEY_BYTES_NEVER_SHARED'
    assert game.is_file()
