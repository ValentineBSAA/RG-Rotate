"""Subprocess import acceptance and hard-stop safety tests; Qt not required."""
from __future__ import annotations
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest
from core import copy_atomic, prepare_layout

ROOT = Path(__file__).resolve().parents[1]
WORKER = str(ROOT / 'import_worker.py')


def run_request(request, command=None):
    cmd = command or [sys.executable, '-u', WORKER]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, cwd=ROOT)
    out, err = proc.communicate(json.dumps(request) + '\n', timeout=12)
    return proc.returncode, [json.loads(line) for line in out.splitlines()], err


def test_import_process_publishes_complete_game_and_keeps_source(tmp_path):
    src = tmp_path/'original.gba'; src.write_bytes(b'homebrew bytes')
    workspace = tmp_path/'virtual'
    code, lines, err = run_request({'mode':'files','paths':[str(src)],
                                   'workspace':str(workspace),'fallback':'PS1'})
    assert code == 0, err
    assert lines[0]['type']=='started'
    assert lines[-1]['type']=='result'
    assert lines[-1]['data']['copied'] == 1
    assert (workspace/'ROMs'/'gba'/'original.gba').read_bytes() == b'homebrew bytes'
    assert src.read_bytes() == b'homebrew bytes'


def test_import_folder_subprocess_discovers_games(tmp_path):
    folder = tmp_path/'downloads'; folder.mkdir()
    (folder/'demo.nes').write_bytes(b'homebrew NES')
    virtual = tmp_path/'card'
    code, lines, err = run_request({'mode':'folder','folder':str(folder),
                                   'workspace':str(virtual),'fallback':'PS1'})
    assert code == 0, err
    assert lines[-1]['data']['copied'] == 1
    assert (virtual/'ROMs'/'nes'/'demo.nes').read_bytes() == b'homebrew NES'


def test_import_folder_overlap_rejected_without_mutation(tmp_path):
    virtual=tmp_path/'virtual'; virtual.mkdir()
    code, lines, err=run_request({'mode':'folder','folder':str(virtual),
                                  'workspace':str(virtual),'fallback':'PS1'})
    assert code != 0
    assert lines[-1]['type']=='error'
    assert 'overlap' in lines[-1]['message']


def test_force_killed_import_worker_does_not_publish_false_success(tmp_path):
    src = tmp_path/'demo.gba'; src.write_bytes(b'untouched')
    card = tmp_path/'card'
    # Simulate a library-import step that is stuck inside a network call.
    script = "import import_worker,time;import_worker.import_grouped=lambda *a,**k:time.sleep(30);raise SystemExit(import_worker.main())"
    cmd=[sys.executable,'-u','-c',script]
    proc=subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, cwd=ROOT)
    try:
        proc.stdin.write(json.dumps({'mode':'files','paths':[str(src)],
                                     'workspace':str(card),'fallback':'GBA'})+'\n')
        proc.stdin.flush()
        assert json.loads(proc.stdout.readline())['type']=='started'
        proc.kill()
        proc.wait(timeout=3)
        assert proc.returncode != 0
        assert src.read_bytes() == b'untouched'
        assert not (card/'ROMs'/'gba'/'demo.gba').exists()
    finally:
        if proc.poll() is None: proc.kill(); proc.wait(timeout=3)


def test_resumes_exact_matching_partial_without_overwriting_other_files(tmp_path):
    src = tmp_path/'game.gba'; data=b'GBA-homebrew-'*1000; src.write_bytes(data)
    target=tmp_path/'card'/'ROMs'/'gba'/'game.gba';target.parent.mkdir(parents=True)
    partial=target.with_name(target.name+'.retro-part');partial.write_bytes(data[:1300])
    assert copy_atomic(src,target)=='copied'
    assert target.read_bytes()==data
    assert not partial.exists()
    assert src.read_bytes()==data


def test_mismatched_partial_is_not_overwritten(tmp_path):
    src=tmp_path/'game.gba';src.write_bytes(b'originalgame')
    target=tmp_path/'card'/'game.gba';target.parent.mkdir()
    partial=target.with_name(target.name+'.retro-part');partial.write_bytes(b'notmatch')
    with pytest.raises(ValueError,match='differs from source'):
        copy_atomic(src,target)
    assert partial.read_bytes()==b'notmatch'
    assert not target.exists()


def test_gui_import_wiring_uses_child_and_build_creates_helper():
    gui=(ROOT/'app.py').read_text(encoding='utf8')
    bat=(ROOT/'Build_Windows_EXE.bat').read_text(encoding='utf8')
    assert 'def _stop_import_process(self)' in gui
    assert 'def _import_process_finished(self, code, status)' in gui
    assert "self.start_import_process({'mode': 'files'" in gui
    assert "self.start_import_process({'mode': 'folder'" in gui
    assert 'proc.kill()' in gui
    assert 'RetroLibraryImport.exe' in bat


def test_hard_stop_after_partial_write_leaves_only_staging_file(tmp_path):
    src = tmp_path/'game.gba'; data=b'example-safe-game'*100; src.write_bytes(data)
    card = tmp_path/'card'; dest = card/'ROMs'/'gba'/'game.gba'
    # Simulate the child being terminated after writing a temporary sibling, but
    # before the complete-file publish (which is intentionally a separate step).
    script = ("import import_worker,time;from pathlib import Path;"
              f"part=Path({str(dest)!r}+'.retro-part');"
              "part.parent.mkdir(parents=True,exist_ok=True);"
              "part.write_bytes(b'example-safe');"
              "import_worker.import_grouped=lambda *a,**k:time.sleep(30);"
              "raise SystemExit(import_worker.main())")
    proc=subprocess.Popen([sys.executable,'-u','-c',script],cwd=ROOT,
                          stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,text=True)
    try:
        proc.stdin.write(json.dumps({'mode':'files','paths':[str(src)],
                                      'workspace':str(card),'fallback':'GBA'})+'\n')
        proc.stdin.flush()
        assert json.loads(proc.stdout.readline())['type']=='started'
        # Wait until simulated network writer publishes its partial.
        for _ in range(30):
            if dest.with_name(dest.name+'.retro-part').exists(): break
            time.sleep(.03)
        assert dest.with_name(dest.name+'.retro-part').exists()
        proc.kill(); proc.wait(timeout=3)
        assert not dest.exists()
        assert src.read_bytes()==data
        assert copy_atomic(src,dest)=='copied'  # verified-prefix retry
        assert dest.read_bytes()==data
    finally:
        if proc.poll() is None: proc.kill(); proc.wait(timeout=3)
