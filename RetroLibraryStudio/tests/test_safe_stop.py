"""Cancellation tests for NAS safe-stop and cooperative write paths.

No external NAS or Qt installation required for these protocol and engine tests.
GUI integration still requires a Windows/PySide6 acceptance test.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
import threading
import time
import zipfile
from pathlib import Path

import pytest

import core
from core import prepare_layout, copy_atomic
from sync_engine import make_plan, transfer_verified

ROOT = Path(__file__).resolve().parents[1]


def call_scan(mode: str, location: Path):
    result = subprocess.run([sys.executable, '-u', str(ROOT/'readonly_scan.py'),
                             '--mode', mode, '--path', str(location)],
                            capture_output=True, text=True, timeout=8)
    records = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    return result, records


def test_inventory_child_reads_games_without_changing_workspace(tmp_path):
    card=tmp_path/'card'; prepare_layout(card)
    game=card/'ROMs'/'gb'/'Demo.gb'; game.write_bytes(b'lawful demo')
    result, messages=call_scan('inventory', card)
    assert result.returncode == 0
    final=messages[-1]
    assert final['type']=='result' and final['mode']=='inventory'
    assert final['count']==1 and final['used']==len(b'lawful demo')
    assert final['entries'][0][0] == str(game)
    assert game.read_bytes()==b'lawful demo'


def test_readonly_count_preserves_receipts(tmp_path):
    card=tmp_path/'card'; prepare_layout(card)
    receipt=card/'.retro-library'/'status.json'; receipt.write_text('test')
    result, messages=call_scan('count', card)
    assert result.returncode==0
    assert messages[-1]['count']==1
    assert receipt.read_text()=='test'


def test_app_status_child_reports_no_apks_in_empty_workspace(tmp_path):
    card=tmp_path/'card'; prepare_layout(card)
    result, messages=call_scan('apps', card)
    assert result.returncode==0, result.stderr
    assert messages[-1]['type']=='result' and messages[-1]['apks']==[]
    assert 'Cocoon Shell' in messages[-1]['states']


def test_failed_child_reports_error_without_fabricating_success(tmp_path):
    result, messages=call_scan('inventory', tmp_path/'missing')
    assert result.returncode!=0
    assert messages[-1]['type']=='error'
    assert not any(m['type']=='result' for m in messages)


def test_readonly_child_can_be_force_stopped_if_stuck(tmp_path):
    card=tmp_path/'card'; prepare_layout(card)
    script=("import readonly_scan,time;"
            "readonly_scan.inventory=lambda *args, **kwargs: time.sleep(30);"
            f"readonly_scan.scan('inventory',{str(card)!r})")
    # Use a real Path rather than a str in the child.
    script=("import readonly_scan,time;from pathlib import Path;"
            "readonly_scan.inventory=lambda *args, **kwargs: time.sleep(30);"
            f"readonly_scan.scan('inventory',Path({str(card)!r}))")
    proc=subprocess.Popen([sys.executable,'-u','-c',script],cwd=ROOT,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        time.sleep(.15)
        assert proc.poll() is None
        proc.kill()
        proc.communicate(timeout=3)
        assert proc.returncode!=0
        assert list((card/'ROMs'/'gb').iterdir())==[]
    finally:
        if proc.poll() is None:
            proc.kill(); proc.wait(timeout=3)


def test_hash_comparison_checks_cancellation_between_chunks(tmp_path):
    src=tmp_path/'src.bin'; dst=tmp_path/'dst.bin'
    data=b'a'*(9*1024*1024)
    src.write_bytes(data); dst.write_bytes(data)
    class StopSoon:
        def __init__(self): self.calls=0
        def is_set(self):
            self.calls+=1
            return self.calls>=3
    with pytest.raises(InterruptedError):
        core.same_file(src,dst,StopSoon())
    assert src.read_bytes()==dst.read_bytes()


def test_import_preflight_respects_stop(tmp_path):
    workspace=tmp_path/'work'; prepare_layout(workspace)
    game=tmp_path/'demo.gba'; game.write_bytes(b'sample')
    stop=threading.Event(); stop.set()
    assert core.import_files([game], workspace, 'GBA', cancel=stop)==(0,0,[])
    assert not (workspace/'ROMs'/'gba'/'demo.gba').exists()


def test_zip_extraction_honors_stop(tmp_path,monkeypatch):
    zip_path=tmp_path/'archive.zip'
    with zipfile.ZipFile(zip_path,'w') as z:
        z.writestr('game.iso', b'Z'*(3*1024*1024))
    card=tmp_path/'card'; prepare_layout(card)
    stop=threading.Event()
    original=zipfile.ZipExtFile.read
    def cancelling_read(stream,n=-1):
        block=original(stream,n)
        if block: stop.set()
        return block
    monkeypatch.setattr(zipfile.ZipExtFile,'read',cancelling_read)
    with pytest.raises(InterruptedError):
        core._import_one(zip_path,card,'PSP',None,stop)
    assert not (card/'ROMs'/'psp'/'archive'/'game.iso').exists()
    assert zip_path.is_file()


def test_transfer_preflight_stops_without_touching_target(tmp_path):
    source=tmp_path/'virtual'; prepare_layout(source)
    (source/'ROMs'/'gb'/'demo.gb').write_bytes(b'demo')
    target=tmp_path/'physical'; target.mkdir()
    stop=threading.Event(); stop.set()
    with pytest.raises(InterruptedError):
        make_plan(source,target,simulation=True,cancel=stop)
    result=transfer_verified(source,target,simulation=True,cancel=stop)
    assert result['cancelled'] and result['verified']==0
    assert not (target/'ROMs').exists()


def test_gui_uses_killable_subprocess_for_nas_readonly_scans():
    source=(ROOT/'app.py').read_text(encoding='utf-8')
    tree=ast.parse(source)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Window')
    methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
    assert 'QProcess(self)' in source and 'child.terminate()' in source
    assert 'proc.kill()' in source and 'self.scan_cancelled' in source
    assert 'self.start_readonly_scan(\'inventory\'' in source
    assert 'self.start_readonly_scan(\'count\'' in source
    assert 'self.start_readonly_scan(\'apps\'' in source
    assert 'has_workspace_payload_fast' in source
    assert 'not is_network_path(self.workspace)' in source
    assert 'if self.current_task:' in ast.get_source_segment(source,methods['closeEvent'])
