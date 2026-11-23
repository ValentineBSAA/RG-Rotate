"""v1.6.8: real Windows console capture and PSXtract extraction preflight.

The Windows smoke test reproduces has207 PSXtract v3's AttachConsole call.
It never uses or reads commercial ROMs, real keys or private file metadata.
"""
from __future__ import annotations
import io
import os
from pathlib import Path
import subprocess
import sys

import pytest

import ps1_psn
from ps1_psn import (
    friendly_helper_status, psxtract_launch_options,
    extract_psn_with_helper,
)
from test_v167_psn_extract_diagnostics import title_eboot


def test_windows_unsigned_minus_one_has_short_readable_result():
    assert friendly_helper_status(4294967295) == '-1'
    assert friendly_helper_status(-1) == '-1'
    assert friendly_helper_status(3) == '3'


def test_console_capture_settings_platform_specific():
    params = psxtract_launch_options()
    if os.name == 'nt':
        assert params['creationflags'] & subprocess.CREATE_NEW_CONSOLE
        assert params['startupinfo'].dwFlags & subprocess.STARTF_USESHOWWINDOW
        assert params['startupinfo'].wShowWindow == subprocess.SW_HIDE
    else:
        assert params == {}


@pytest.mark.skipif(os.name != 'nt', reason='Real AttachConsole behavior requires Windows')
def test_windows_process_trying_to_attach_parent_does_not_steal_stdout():
    # This imitates the exact upstream AttachConsole(ATTACH_PARENT_PROCESS)
    # *before* emitting a PGD error, using only a tiny local Python child.
    code = (
        'import ctypes, sys\n'
        'kernel = ctypes.WinDLL("kernel32", use_last_error=True)\n'
        'kernel.AttachConsole.argtypes = [ctypes.c_uint]\n'
        'kernel.AttachConsole.restype = ctypes.c_int\n'
        'attached = kernel.AttachConsole(0xFFFFFFFF)\n'
        'print("ATTACH_RESULT=" + str(attached), flush=True)\n'
        'print("PGD: Invalid 0x80 MAC hash!", flush=True)\n'
    )
    r = subprocess.run([sys.executable, '-c', code],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=20, check=True, **psxtract_launch_options())
    txt = r.stdout.decode('utf-8', errors='replace')
    assert 'ATTACH_RESULT=0' in txt
    assert 'PGD: Invalid 0x80 MAC hash!' in txt


@pytest.mark.skipif(os.name != 'nt', reason='GUI subsystem helper is Windows only')
def test_windows_gui_subsystem_child_does_not_reconnect_to_parent_console(tmp_path):
    # pythonw.exe is a Windows GUI-subsystem executable, just like the
    # upstream psxtract.exe. Reproduce AttachConsole and pipe output without
    # needing commercial packages or running downloaded executables.
    gui = Path(sys.executable).with_name('pythonw.exe')
    if not gui.is_file():
        pytest.skip('pythonw.exe not provided by this interpreter')
    script = tmp_path / 'gui_helper.py'
    script.write_text(
        'import ctypes\n'
        'from pathlib import Path\n'
        'kernel = ctypes.WinDLL("kernel32", use_last_error=True)\n'
        'kernel.AttachConsole.argtypes=[ctypes.c_uint]\n'
        'kernel.AttachConsole.restype=ctypes.c_int\n'
        'result = kernel.AttachConsole(0xFFFFFFFF)\n'
        'print("GUI_ATTACHED="+str(result),flush=True)\n'
        'print("PGD: Invalid 0x80 MAC hash!",flush=True)\n',
        encoding='utf-8'
    )
    proc = subprocess.run([str(gui), str(script)],
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                          timeout=20,check=True,**psxtract_launch_options())
    out = proc.stdout.decode('utf-8', errors='replace')
    assert 'GUI_ATTACHED=0' in out
    assert 'PGD: Invalid 0x80 MAC hash!' in out


def test_real_helper_launch_uses_capture_options_and_reports_known_pgd(tmp_path, monkeypatch):
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
    assert calls[0][1].get('creationflags',0) == psxtract_launch_options().get('creationflags',0)
    assert 'CHD conversion never started' in str(err.value)
    assert '4294967295' not in str(err.value)


def test_too_short_adjacent_keys_is_not_passed_to_helper(tmp_path, monkeypatch):
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


def test_generic_helper_error_uses_signed_status_and_acknowledges_no_stage(tmp_path, monkeypatch):
    pbp = title_eboot(tmp_path / 'Sony' / 'SLUS00695' / 'EBOOT.PBP')
    helper = tmp_path / 'psxtract.exe'
    helper.write_bytes(b'SYNTHETIC-ONLY')
    scratch = tmp_path / 'out'
    scratch.mkdir()
    class FakeProc:
        def __init__(self,*args,**opts):
            self.stdout = io.BytesIO(b'Unrecognized non-sensitive failure\n')
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
