"""v1.4.3: real incremental transfer and trustworthy UI summaries."""
from __future__ import annotations

import hashlib
import subprocess
import sys
import json
from pathlib import Path

from core import pretty_bytes, prepare_layout
from sync_engine import make_plan
from transfer_feedback import preview_explanation, copy_explanation

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / 'transfer_worker.py'


def request(mode, source, dest):
    result = subprocess.run(
        [sys.executable, '-u', str(WORKER)],
        input=json.dumps({'mode': mode, 'workspace':str(source), 'target':str(dest), 'simulation': True}) + '\n',
        text=True, capture_output=True, timeout=20)
    return result, [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def sample_library(tmp_path):
    src = tmp_path / 'virtual'; prepare_layout(src)
    game = src / 'ROMs' / 'psx' / 'Example.chd'; game.write_bytes(b'retro game'*3000)
    for i in range(3):
        (src / 'SetupPackages' / f'example{i}.apk').write_bytes(bytes([i+30])*2048)
    (src / 'Media' / 'BoxArt' / 'example.png').parent.mkdir(parents=True, exist_ok=True)
    (src / 'Media' / 'BoxArt' / 'example.png').write_bytes(b'image'*555)
    (src / 'CompanionData' / 'Settings' / 'profile.json').parent.mkdir(parents=True, exist_ok=True)
    (src / 'CompanionData' / 'Settings' / 'profile.json').write_text('{"model":"sample"}')
    dest=tmp_path/'practice'; dest.mkdir()
    return src,dest


def test_preview_is_not_a_verified_result(tmp_path):
    src,dest=sample_library(tmp_path)
    first, events=request('copy',src,dest)
    assert first.returncode==0, first.stderr
    assert events[-1]['data']['copy']['copied']==6
    assert events[-1]['data']['copy']['verified']==6

    preview, events=request('preview',src,dest)
    assert preview.returncode==0, preview.stderr
    plan=events[-1]['data']['plan']
    assert plan['files']==6
    assert plan['existing_files']==6
    assert plan['bytes_new']==0
    assert plan['bytes_already_present']==plan['bytes_total']
    from sync_engine import SyncPlan
    details, action, status = preview_explanation(SyncPlan(**plan), pretty_bytes)
    assert 'did NOT hash-verify' in details
    assert '0 B' in details
    assert 'Verify 6 existing' in action
    assert 'need verification' in status


def test_second_verified_copy_skips_all_existing_files(tmp_path):
    src,dest=sample_library(tmp_path)
    first, _=request('copy',src,dest)
    assert first.returncode==0
    second, events=request('copy',src,dest)
    assert second.returncode==0, second.stderr
    r=events[-1]['data']['copy']
    assert r['copied']==0
    assert r['skipped']==6
    assert r['verified']==6 and not r['errors']
    summary, title, popup, ok=copy_explanation(r, True)
    assert ok and 'New files copied: 0' in summary
    assert 'Existing identical files: 6' in summary
    assert 'Nothing needed copying' in title
    assert 'normal Windows test folder' in popup
    assert 'eject the card' not in popup.lower()
    for path in src.rglob('*'):
        if path.is_file():
            mirror=dest/path.relative_to(src)
            assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(mirror.read_bytes()).digest()


def test_same_size_corrupt_file_not_skipped_and_not_overwritten(tmp_path):
    src,dest=sample_library(tmp_path)
    first,_=request('copy',src,dest)
    assert first.returncode==0
    target=dest/'ROMs'/'psx'/'Example.chd'
    target.write_bytes(b'Z'*target.stat().st_size)
    plan=make_plan(src,dest,simulation=True)
    # The preview cannot call this a pass: equal length is not equal content.
    assert plan.existing_files==6 and plan.bytes_new==0
    note,_,_=preview_explanation(plan,pretty_bytes)
    assert 'did NOT hash-verify' in note
    repeat, events=request('copy',src,dest)
    assert repeat.returncode==0
    r=events[-1]['data']['copy']
    assert r['verified']==5 and r['copied']==0 and r['skipped']==5
    assert r['errors']
    assert target.read_bytes()==b'Z'*target.stat().st_size
    _, title, popup, ok=copy_explanation(r, True)
    assert not ok and 'needs attention' in title
    assert 'Issues' in popup


def test_no_false_success_for_cancelled_or_empty_result():
    for report in ({'copied':0,'skipped':0,'files':0,'verified':0,'errors':[],'cancelled':False},
                   {'copied':0,'skipped':6,'files':6,'verified':6,'errors':[],'cancelled':True}):
        assert not copy_explanation(report, True)[3]


def test_gui_wiring_tracks_last_run_and_clears_old_progress():
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    assert 'self.copy_scroll.ensureWidgetVisible' in app
    assert "self.copy_meter.setValue(0)" in app
    assert 'self.last_transfer_note' in app
    assert 'preview_explanation(plan, pretty_bytes)' in app
    assert 'copy_explanation(result, self.transfer_simulation)' in app
    assert "'Confirm verification' if plan.bytes_new == 0" in app


def test_empty_preview_requires_import_not_verification(tmp_path):
    src=tmp_path/'empty'; prepare_layout(src)
    dest=tmp_path/'practice'; dest.mkdir()
    plan=make_plan(src,dest,simulation=True)
    detail,action,status=preview_explanation(plan, pretty_bytes)
    assert plan.files==0
    assert 'No staged files' in detail
    assert action=='Add Files Before Copying'
    assert 'empty' in status
