"""Regression tests for the exact `cocon-311.apk` user-reported mismatch."""
import zipfile
from pathlib import Path

import pytest
import batch_setup
import tool_setup
from apk_import import stage_local_apks, staged_apks
from core import prepare_layout


def valid_apk(path):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('AndroidManifest.xml', b'manifest')
        z.writestr('classes.dex', b'dex')


def test_cocon_311_import_is_recognized_in_ninite_and_skips_redownload(tmp_path, monkeypatch):
    workspace = tmp_path / 'Card'
    prepare_layout(workspace)
    original = tmp_path / 'cocon-311.apk'
    valid_apk(original)
    saved = stage_local_apks([original], workspace)
    assert saved['added'] == 1
    assert saved['errors'] == []
    assert (workspace / 'SetupPackages' / 'cocon-311.apk').is_file()
    assert batch_setup.manual_apk_for(workspace, 'Cocoon Shell').name == 'cocon-311.apk'
    assert 'Cocoon Shell' in staged_apks(workspace)[0]['label']
    monkeypatch.setattr(tool_setup, 'tool_status', lambda p: {
        'Android Platform Tools': {'installed': False}, 'CHDman': {'installed': False}
    })
    status = batch_setup.readiness(workspace, tmp_path / 'WindowsTools')
    assert status['Cocoon Shell'] == 'My APK ready • publisher unverified'
    monkeypatch.setattr(batch_setup.software, 'download_apk', lambda *a, **k:
                        pytest.fail('Existing manually imported Cocoon must not redownload'))
    report = batch_setup.prepare_batch(['Cocoon Shell'], workspace, tmp_path / 'WindowsTools')
    assert len(report['results']) == 1 and report['results'][0]['ok']
    assert 'publisher unverified' in report['results'][0]['state']
    assert report['results'][0]['path'].endswith('cocon-311.apk')
    assert original.is_file()


def test_similar_non_cocoon_name_is_not_silently_assigned(tmp_path):
    workspace = tmp_path / 'Card'; prepare_layout(workspace)
    source = tmp_path / 'coconut-tools.apk'
    valid_apk(source)
    stage_local_apks([source], workspace)
    assert batch_setup.manual_apk_for(workspace, 'Cocoon Shell') is None


def test_tampered_cocon_apk_is_not_recognized(tmp_path):
    workspace = tmp_path / 'Card'; prepare_layout(workspace)
    source = tmp_path / 'cocon-311.apk'; valid_apk(source)
    stage_local_apks([source], workspace)
    with (workspace / 'SetupPackages' / source.name).open('ab') as dest:
        dest.write(b'changed')
    assert batch_setup.manual_apk_for(workspace, 'Cocoon Shell') is None


def test_cocoon_alias_does_not_count_as_publisher_verification(tmp_path):
    workspace = tmp_path / 'Card'; prepare_layout(workspace)
    source = tmp_path / 'cocon-311.apk'; valid_apk(source)
    stage_local_apks([source], workspace)
    manual = batch_setup.manual_apk_for(workspace, 'Cocoon Shell')
    assert manual is not None
    assert 'unverified' in batch_setup.prepare_batch(['Cocoon Shell'], workspace, tmp_path / 'WindowsTools')['results'][0]['state']
