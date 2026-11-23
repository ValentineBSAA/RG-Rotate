"""v1.6.8: console capture and honest PSXtract extraction preflight.

The Windows smoke test reproduces the upstream GUI helper's AttachConsole
behavior using a console-DETACHED Python import worker. No commercial PBP
and no actual keys are accessed or persisted.
"""
from __future__ import annotations

import io
import os
from pathlib import Path
import subprocess
import sys

import pytest

import ps1_psn
import import_worker
from ps1_psn import friendly_helper_status, extract_psn_with_helper
from test_v167_psn_extract_diagnostics import title_eboot


def test_windows_unsigned_minus_one_becomes_short_readable_status():
    assert friendly_helper_status(4294967295) == '-1'
    assert friendly_helper_status(-1) == '-1'
    assert friendly_helper_status(3) == '3'


def test_worker_console_detach_is_windows_only_and_import_scoped():
    if os.name != 'nt':
        assert import_worker.detach_parent_console_for_psxtract() is False
    code = Path(import_worker.__file__).read_text('utf-8')
    assert "if request.get('auto_ps1_chd'):" in code
    assert 'detach_parent_console_for_psxtract()' in code
    assert 'from worker_lifetime import contain_children' in code
    assert 'if __name__' in code


@pytest.mark.skipif(os.name != 'nt', reason='Windows Win32 console API')
def test_windows_worker_can_detach_console_and_keep_pipe_for_gui_helper(tmp_path):
    gui = Path(sys.executable).with_name('pythonw.exe')
    if not gui.is_file():
        pytest.skip('Windows GUI interpreter not installed')
    psx = tmp_path / 'fake_gui_extractor.py'
    psx.write_text(
        'import ctypes\n'
        'kernel=ctypes.WinDLL("kernel32",use_last_error=True)\n'
        'kernel.AttachConsole.argtypes=[ctypes.c_uint]\n'
        'kernel.AttachConsole.restype=ctypes.c_int\n'
        'attached=kernel.AttachConsole(0xFFFFFFFF)\n'
        'print("GUI_ATTACHED="+str(attached),flush=True)\n'
        'print("PGD: Invalid 0x80 MAC hash!",flush=True)\n',
        encoding='utf-8'
    )
    # Mimics real import_worker.py: detached once, then launches PSXtract
    # as a direct child and forwards only safe progress, with QProcess pipes.
    worker = tmp_path / 'fake_import_worker.py'
    worker.write_text(
        'import ctypes,subprocess,sys\n'
        'kernel=ctypes.WinDLL("kernel32",use_last_error=True)\n'
        'kernel.FreeConsole()\n'
        'print("WORKER_PIPE_ALIVE",flush=True)\n'
        'data=sys.stdin.readline().strip()\n'
        'print("WORKER_STDIN="+data,flush=True)\n'
        'p=subprocess.run([sys.argv[1],sys.argv[2]],stdout=subprocess.PIPE,'
        'stderr=subprocess.STDOUT,timeout=15,check=True)\n'
        'safe=p.stdout.decode("utf-8",errors="replace")\n'
        'print("CHILD_CAPTURE="+safe.replace("\\r","").replace("\\n","|"),flush=True)\n',
        encoding='utf-8'
    )
    p = subprocess.run([sys.executable, '-u', str(worker), str(gui), str(psx)],
                       input=b'STOP-TEST\n',
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=25, check=True)
    out = p.stdout.decode('utf-8',errors='replace')
    assert 'WORKER_PIPE_ALIVE' in out
    assert 'WORKER_STDIN=STOP-TEST' in out
    assert 'GUI_ATTACHED=0' in out
    assert 'PGD: Invalid 0x80 MAC hash!' in out


def test_real_helper_popen_is_direct_child_with_redirected_output(tmp_path, monkeypatch):
    pbp = title_eboot(tmp_path / 'Sony' / 'SLUS00695' / 'EBOOT.PBP')
    helper = tmp_path / 'psxtract.exe'
    helper.write_bytes(b'SYNTHETIC-ONLY')
    scratch = tmp_path / 'out'
    scratch.mkdir()
    calls = []
    class FakeProc:
        def __init__(self, args, **opts):
            calls.append((args,opts))
            self.stdout = io.BytesIO(b'PGD: Invalid 0x80 MAC hash!\n'
                                     b'ERROR: ISO header decryption failed!\n')
            self.returncode = 4294967295
        def poll(self): return 4294967295
    monkeypatch.setattr(ps1_psn.subprocess, 'Popen', FakeProc)
    with pytest.raises(RuntimeError, match='0x80 MAC check failed') as err:
        extract_psn_with_helper(pbp, scratch, helper)
    assert len(calls) == 1
    assert calls[0][1]['stdout'] == subprocess.PIPE
    assert calls[0][1]['stderr'] == subprocess.STDOUT
    assert 'creationflags' not in calls[0][1]
    assert 'CHD conversion never started' in str(err.value)
    assert '4294967295' not in str(err.value)


def test_incomplete_adjacent_keys_is_rejected_before_helper_launch(tmp_path, monkeypatch):
    pbp = title_eboot(tmp_path / 'Sony' / 'SLUS00695' / 'EBOOT.PBP')
    key = pbp.parent / 'KEYS.BIN'
    key.write_bytes(b'tiny')
    helper = tmp_path / 'psxtract.exe'
    helper.write_bytes(b'SYNTHETIC-ONLY')
    scratch = tmp_path / 'out'
    scratch.mkdir()
    def explode(*args,**kwargs):
        pytest.fail('Must reject incomplete key before launching PSXtract')
    monkeypatch.setattr(ps1_psn.subprocess, 'Popen', explode)
    with pytest.raises(ValueError, match='shorter than the 16 bytes'):
        extract_psn_with_helper(pbp, scratch, helper)
    assert key.read_bytes() == b'tiny'
    assert pbp.exists()


def test_unrecognized_helper_failure_uses_signed_code_and_does_not_blame_chd(tmp_path, monkeypatch):
    pbp = title_eboot(tmp_path / 'Sony' / 'SLUS00695' / 'EBOOT.PBP')
    helper = tmp_path / 'psxtract.exe'
    helper.write_bytes(b'SYNTHETIC-ONLY')
    scratch = tmp_path / 'out'
    scratch.mkdir()
    class FakeProc:
        def __init__(self,*args,**opts):
            self.stdout = io.BytesIO(b'Generic unexpected failure\n')
            self.returncode = 4294967295
        def poll(self): return 4294967295
    monkeypatch.setattr(ps1_psn.subprocess,'Popen',FakeProc)
    with pytest.raises(RuntimeError) as error:
        extract_psn_with_helper(pbp,scratch,helper)
    message=str(error.value)
    assert 'Helper status: -1.' in message
    assert 'did not report a recognized decryption milestone' in message
    assert '4294967295' not in message
    assert 'CHD conversion was not attempted' in message
