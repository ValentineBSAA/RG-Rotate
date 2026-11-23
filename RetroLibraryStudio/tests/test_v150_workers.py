import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_real_disc_inspection_worker_reports_missing_track(tmp_path):
    cue = tmp_path / 'Disc 1.cue'
    cue.write_text('FILE "Disc 1.bin" BINARY\nTRACK 01 MODE2/2352\n')
    request = {'mode': 'inspect_discs', 'paths': [str(cue)]}
    result = subprocess.run([sys.executable, '-u', str(ROOT / 'import_worker.py')],
                            input=json.dumps(request) + '\n', capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    records = [json.loads(line) for line in result.stdout.splitlines()]
    assert 'missing track' in records[-1]['data']['results'][0]['errors'][0]
    assert cue.is_file()


def test_inventory_worker_reports_audio_track_companions(tmp_path):
    from core import prepare_layout
    prepare_layout(tmp_path)
    folder = tmp_path / 'ROMs' / 'psx'
    (folder / 'Game.cue').write_text('FILE "Track 01.bin" BINARY\nTRACK 01 MODE2/2352\nFILE "Audio.bin" BINARY\nTRACK 02 AUDIO')
    for name in ('Track 01.bin', 'Audio.bin'): (folder / name).write_bytes(b'track fixture')
    result = subprocess.run([sys.executable, '-u', str(ROOT / 'readonly_scan.py'), '--mode', 'inventory', '--path', str(tmp_path)],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0
    final = json.loads(result.stdout.splitlines()[-1])
    assert {Path(p).name for p in final['disc_tracks']} == {'Track 01.bin', 'Audio.bin'}
    assert len(final['entries']) == 3  # All actual files remain in the file list.


def test_transfer_reports_completed_verified_file_count(tmp_path):
    from core import prepare_layout
    from sync_engine import transfer_verified
    source = tmp_path / 'source'; prepare_layout(source)
    target = tmp_path / 'target'; target.mkdir()
    (source / 'ROMs' / 'gba' / 'Game.gba').write_bytes(b'fixture')
    updates = []
    result = transfer_verified(source, target, simulation=True, progress=lambda *args: updates.append(args))
    assert result['verified'] == 1
    assert any(event[0] == 'Files verified: 1/1' for event in updates)


@pytest.mark.skipif(os.name != 'nt', reason='Windows job object lifecycle')
def test_force_stopping_conversion_worker_also_stops_child():
    import ctypes
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]; kernel.OpenProcess.restype = w.HANDLE
    kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
    kernel.CloseHandle.argtypes = [w.HANDLE]
    script = ("from worker_lifetime import contain_children; contain_children(); "
              "import subprocess,sys,time; "
              "child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(90)']); "
              "print(child.pid,flush=True); time.sleep(90)")
    worker = subprocess.Popen([sys.executable, '-u', '-c', script], cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    handle = None
    try:
        line = worker.stdout.readline()
        assert line.strip().isdigit(), worker.stderr.read() if worker.poll() is not None else 'Child did not start'
        handle = kernel.OpenProcess(0x100000, False, int(line))  # SYNCHRONIZE
        assert handle
        worker.kill(); worker.wait(timeout=5)
        assert kernel.WaitForSingleObject(handle, 5000) == 0, 'CHDman-like child survived worker force stop'
    finally:
        if worker.poll() is None: worker.kill(); worker.wait(timeout=5)
        if handle: kernel.CloseHandle(handle)
