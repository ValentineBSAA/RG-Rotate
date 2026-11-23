"""APK import end-to-end tests, including the GUI race discovered on NAS."""
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from threading import Event

from apk_import import stage_local_apks
from batch_setup import manual_apk_for
from core import prepare_layout

ROOT = Path(__file__).resolve().parents[1]


def apk(path: Path) -> None:
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('AndroidManifest.xml', b'manifest')
        z.writestr('classes.dex', b'dex')


def test_apk_worker_real_subprocess_saves_file_receipt_and_reports_path(tmp_path):
    source = tmp_path / 'Cocoon-3.11.apk'
    apk(source)
    original = source.read_bytes()
    workspace = tmp_path / 'Card'
    prepare_layout(workspace)
    req = {'mode': 'apks', 'workspace': str(workspace), 'paths': [str(source)]}
    output = subprocess.run([sys.executable, '-u', str(ROOT / 'import_worker.py')],
                            input=json.dumps(req)+'\n', text=True, capture_output=True,
                            timeout=20)
    assert output.returncode == 0, output.stderr or output.stdout
    messages = [json.loads(line) for line in output.stdout.splitlines()]
    assert messages[0] == {'type': 'started', 'mode': 'apks'}
    result = next(m['data'] for m in messages if m['type'] == 'result')
    dest = workspace / 'SetupPackages' / source.name
    assert result['added'] == 1 and result['already'] == 0
    assert result['paths'] == [str(dest)] and result['errors'] == []
    assert dest.read_bytes() == original == source.read_bytes()
    assert manual_apk_for(workspace, 'Cocoon Shell') == dest


def test_apk_duplicate_is_quick_and_reported_without_rescanning(tmp_path, monkeypatch):
    source = tmp_path/'Cocoon-3.11.apk'
    apk(source)
    card = tmp_path/'Card'
    prepare_layout(card)
    assert stage_local_apks([source], card)['added'] == 1
    import apk_import as module
    monkeypatch.setattr(module, 'inventory', lambda *a, **kw: (_ for _ in ()).throw(
        AssertionError('Already prepared APK should not require a full workspace scan')))
    result = stage_local_apks([source], card)
    assert result['added'] == 0 and result['already'] == 1
    assert result['paths'] == [str(card/'SetupPackages'/source.name)]


def test_invalid_apk_does_not_publish_a_ready_file(tmp_path):
    source = tmp_path/'Cocoon-3.11.apk'; source.write_bytes(b'not an APK')
    card = tmp_path/'Card'; prepare_layout(card)
    report = stage_local_apks([source], card)
    assert report['added'] == 0 and report['already'] == 0 and report['errors']
    assert not (card/'SetupPackages'/source.name).exists()
    assert manual_apk_for(card, 'Cocoon Shell') is None


def test_pre_cancelled_apk_import_changes_nothing(tmp_path):
    source = tmp_path/'Cocoon-3.11.apk'; apk(source)
    card = tmp_path/'Card'; prepare_layout(card)
    cancel = Event(); cancel.set()
    outcome = stage_local_apks([source], card, cancel=cancel)
    assert outcome['cancelled'] and not outcome['paths']
    assert not (card/'SetupPackages'/source.name).exists()


def test_user_interface_does_not_launch_app_status_scan_before_importing():
    ui = (ROOT/'app.py').read_text(encoding='utf-8')
    assert 'self.navigate(2, refresh_apps=False)' in ui
    assert 'if i == 2 and refresh_apps and i != previous and not self.current_task:' in ui
    assert 'self.start_import_process({\'mode\': \'apks\'' in ui
    assert 'self.job(stage_local_apks' not in ui
    assert 'QTimer.singleShot(0, self.update_tools_status)' in ui
    assert 'self.import_finished_callback or self.import_completed' in ui


def test_subprocess_apk_error_is_reported_as_error_not_success(tmp_path):
    source = tmp_path/'fake.apk'; source.write_text('html file, not apk')
    card = tmp_path/'Card'; prepare_layout(card)
    output = subprocess.run([sys.executable, '-u', str(ROOT / 'import_worker.py')],
        input=json.dumps({'mode':'apks', 'workspace':str(card), 'paths':[str(source)]})+'\n',
        text=True, capture_output=True, timeout=20)
    assert output.returncode == 0
    last = next(json.loads(x)['data'] for x in output.stdout.splitlines()
                if json.loads(x)['type'] == 'result')
    assert not last['added'] and not last['already'] and last['errors']
    assert not (card/'SetupPackages'/'fake.apk').exists()
