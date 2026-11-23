"""Queue behavior is tested without network access or a physical RG Rotate."""
import io
import zipfile
import json
from pathlib import Path

import pytest
import batch_setup


def make_apk(path):
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('AndroidManifest.xml', b'\x03\x00ANDROID')
        archive.writestr('classes.dex', b'\x64\x65\x78')


def test_recommended_installer_is_well_scoped():
    assert batch_setup.RECOMMENDED == (
        'Cocoon Shell', 'PPSSPP', 'RetroArch', 'Android Platform Tools', 'CHDman')
    assert 'DuckStation' not in batch_setup.RECOMMENDED
    assert set(batch_setup.RECOMMENDED) <= set(batch_setup.DESCRIPTION)


def test_batch_reports_per_app_updates_and_keeps_going_after_failure(tmp_path, monkeypatch):
    workspace = tmp_path / 'VirtualCard'; workspace.mkdir()
    host = tmp_path / 'WindowsTools'
    statuses = []
    progress = []
    attempts = []
    def mock_apk(name, workspace, progress=None, cancel=None):
        attempts.append(name)
        if name == 'PPSSPP':
            raise RuntimeError('official source temporarily unavailable')
        if progress: progress(name, 40, 100)
        return {'status': 'verified APK structure', 'file': str(workspace / 'SetupPackages' / f'{name}.apk')}
    def mock_adb(host, progress=None, cancel=None):
        attempts.append('Android Platform Tools')
        return {'name': 'Android Platform Tools', 'ok': True, 'state': 'downloaded and unpacked'}
    monkeypatch.setattr(batch_setup.software, 'download_apk', mock_apk)
    monkeypatch.setattr(batch_setup.tool_setup, 'install_adb', mock_adb)
    report = batch_setup.prepare_batch(
        ['Cocoon Shell', 'PPSSPP', 'Android Platform Tools'],workspace,host,
        progress=lambda *a: progress.append(a), on_state=lambda *a: statuses.append(a))
    assert attempts == ['Cocoon Shell','PPSSPP','Android Platform Tools']
    assert len(report['results']) == 3 and sum(x['ok'] for x in report['results']) == 2
    assert any(name == 'PPSSPP' and 'Needs attention' in status for name,status in statuses)
    assert any(name == 'Cocoon Shell' and 'APK ready' in status for name,status in statuses)
    assert any('Installer queue finished' in p[0] for p in progress)


def test_run_uses_existing_verified_android_apk(tmp_path, monkeypatch):
    from software import download_apk
    workspace = tmp_path / 'VirtualCard'; (workspace / 'SetupPackages').mkdir(parents=True)
    apk = workspace / 'SetupPackages' / 'Cocoon-3.11.apk'
    make_apk(apk)
    import hashlib
    with apk.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    receipt=workspace/'.retro-library'/'receipts';receipt.mkdir(parents=True)
    (receipt/'Cocoon_Shell.json').write_text(json.dumps({
        'file':str(apk), 'url':'https://github.com/KansoMirai/CocoonFE/releases/download/x/Cocoon-3.11.apk',
        'sha256':digest}))
    monkeypatch.setattr('software.resolve',lambda name:('https://github.com/KansoMirai/CocoonFE/releases/download/x/Cocoon-3.11.apk','Cocoon-3.11.apk'))
    monkeypatch.setattr('software._urlopen',lambda *a,**k: pytest.fail('Existing APK should not cause download'))
    result = download_apk('Cocoon Shell', workspace)
    assert result['status'] == 'already downloaded'
    assert apk.read_bytes()


def test_readiness_never_claims_apk_installed_on_android(tmp_path, monkeypatch):
    workspace=tmp_path/'VirtualCard'; root=workspace/'SetupPackages'; root.mkdir(parents=True)
    host=tmp_path/'WindowsTools'
    installer=root/'Cocoon.apk'; make_apk(installer)
    receipt=workspace/'.retro-library'/'receipts'; receipt.mkdir(parents=True)
    import hashlib
    with installer.open('rb') as file: digest=hashlib.file_digest(file,'sha256').hexdigest()
    (receipt/'Cocoon_Shell.json').write_text(json.dumps({
        'file':str(installer), 'sha256':digest,
        'url':'https://github.com/KansoMirai/CocoonFE/releases/download/x/Cocoon.apk'}))
    monkeypatch.setattr(batch_setup.tool_setup,'tool_status',lambda root:{
        'Android Platform Tools': {'installed': True}, 'CHDman': {'installed':False}})
    result=batch_setup.readiness(workspace,host)
    assert result['Cocoon Shell'].startswith('APK ready')
    assert 'installed' not in result['Cocoon Shell'].lower()
    assert result['Android Platform Tools'] == 'Ready on Windows'
    assert result['CHDman'] == 'Not prepared'


def test_unknown_and_duplicate_names_rejected_before_file_operations(tmp_path):
    with pytest.raises(ValueError,match='Unknown'):
        batch_setup.prepare_batch(['Random Mirror'], tmp_path, tmp_path)
    with pytest.raises(ValueError,match='Duplicate'):
        batch_setup.prepare_batch(['PPSSPP','PPSSPP'],tmp_path,tmp_path)


def test_cancel_before_start_does_no_operations(tmp_path):
    from threading import Event
    cancelled=Event();cancelled.set()
    result=batch_setup.prepare_batch(['Cocoon Shell'],tmp_path,tmp_path,cancel=cancelled)
    assert result['cancelled'] and not result['results']


def test_optional_ps1_app_is_not_untrusted_autodownload(tmp_path):
    output=batch_setup.prepare_batch(['DuckStation'],tmp_path,tmp_path)
    assert not output['results'][0]['ok']
    assert 'compatibility' in output['results'][0]['state']


def test_app_source_connects_queue_status_to_ui():
    code=(Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8')
    assert '↓  Install Recommended Setup' in code
    assert 'work.signals.app_state.connect(self.on_app_state)' in code
    assert "'mode': 'setup'" in code
    assert "elif typ == 'app_state':" in code
    assert 'self.import_apks' in code


def test_unverified_same_name_is_not_mistaken_for_official_download(tmp_path, monkeypatch):
    from software import download_apk
    workspace=tmp_path/'Card';packages=workspace/'SetupPackages';packages.mkdir(parents=True)
    apk=packages/'Cocoon.apk';make_apk(apk)
    monkeypatch.setattr('software.resolve', lambda name:(
        'https://github.com/KansoMirai/CocoonFE/releases/download/v3/Cocoon.apk','Cocoon.apk'))
    monkeypatch.setattr('software._urlopen', lambda *args, **kwargs: pytest.fail('No network when conflicting local APK exists'))
    with pytest.raises(FileExistsError, match='origin is unverified'):
        download_apk('Cocoon Shell', workspace)
    assert apk.exists()
