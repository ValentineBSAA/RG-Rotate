"""Arrival-day tests for isolated preview/copy worker (does not need PySide6)."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from core import prepare_layout
from transfer_worker import handle

ROOT = Path(__file__).resolve().parents[1]
WORKER = str(ROOT / 'transfer_worker.py')


def call_worker(request):
    done = subprocess.run([sys.executable, '-u', WORKER],
                          input=json.dumps(request)+'\n',
                          capture_output=True, text=True, timeout=12)
    lines = [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    return done, lines


def fixture(tmp_path):
    source=tmp_path/'virtual'; prepare_layout(source)
    original=source/'ROMs'/'psx'/'public_domain.chd'
    original.write_bytes(b'owned test data'*1000)
    dest=tmp_path/'sd'; dest.mkdir()
    return source, dest, original


def test_worker_preflight_does_not_change_destination(tmp_path):
    source,dest,original=fixture(tmp_path)
    done,lines=call_worker({'mode':'preview','workspace':str(source),'target':str(dest),'simulation':True})
    assert done.returncode==0, done.stderr
    assert lines[-1]['data']['plan']['bytes_new']==original.stat().st_size
    assert not (dest/'ROMs').exists()


def test_worker_copy_verifies_and_retries_without_recopied_data(tmp_path):
    source,dest,original=fixture(tmp_path)
    request={'mode':'copy','workspace':str(source),'target':str(dest),'simulation':True}
    done,lines=call_worker(request)
    assert done.returncode==0, done.stderr
    assert lines[-1]['data']['copy']['verified']==1
    output=dest/'ROMs'/'psx'/original.name
    assert output.read_bytes()==original.read_bytes()
    again,events=call_worker(request)
    assert again.returncode==0
    assert events[-1]['data']['copy']['skipped']==1
    assert events[-1]['data']['copy']['verified']==1


def test_worker_refuses_different_existing_file(tmp_path):
    source,dest,original=fixture(tmp_path)
    target=dest/'ROMs'/'psx'/original.name; target.parent.mkdir(parents=True)
    different=b'Z'*original.stat().st_size
    target.write_bytes(different)
    done,events=call_worker({'mode':'copy','workspace':str(source),'target':str(dest),'simulation':True})
    assert done.returncode==0
    assert events[-1]['data']['copy']['errors']
    assert target.read_bytes()==different


def test_worker_invalid_destination_never_creates_it(tmp_path):
    src,dest,_=fixture(tmp_path)
    outside=tmp_path/'missing-target'
    done,events=call_worker({'mode':'preview','workspace':str(src),'target':str(outside),'simulation':True})
    assert done.returncode!=0
    assert events[-1]['type']=='error'
    assert not outside.exists()


def test_cooperative_cancel_before_writes(tmp_path):
    src,dest,_=fixture(tmp_path)
    event=threading.Event(); event.set()
    report=handle({'mode':'copy','workspace':str(src),'target':str(dest),'simulation':True},event)
    assert report['copy']['cancelled'] and not (dest/'ROMs').exists()


def test_partial_resume_after_interruption(tmp_path):
    src,dest,original=fixture(tmp_path)
    partial=dest/'ROMs'/'psx'/(original.name+'.retro-part');partial.parent.mkdir(parents=True)
    partial.write_bytes(original.read_bytes()[:100])
    done,events=call_worker({'mode':'copy','workspace':str(src),'target':str(dest),'simulation':True})
    assert done.returncode==0
    assert events[-1]['data']['copy']['verified']==1
    assert (partial.parent/original.name).read_bytes()==original.read_bytes()
    assert not partial.exists()


def test_transfer_gui_wiring_and_windows_build_helper():
    src=(ROOT/'app.py').read_text(encoding='utf8')
    bat=(ROOT/'Build_Windows_EXE.bat').read_text(encoding='utf8')
    for term in ('def start_transfer_process(', 'def _stop_transfer_process(',
                 'def _transfer_process_finished(', "self.start_transfer_process('preview'",
                 "self.start_transfer_process('copy'", 'RetroLibraryTransfer.exe'):
        assert term in src
    assert 'transfer_worker.py' in bat and '--name "RetroLibraryTransfer"' in bat
    assert 'RetroLibraryTransfer.exe' in bat
