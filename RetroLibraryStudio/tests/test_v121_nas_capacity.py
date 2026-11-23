"""No USB card or actual NAS required for capacity behavior tests."""
import subprocess
from pathlib import Path
import pytest
import storage_probe as sp


def test_unchanged_local_space_probe(tmp_path):
    result = sp.check_space_bounded(tmp_path, timeout=.1)
    assert result.path == str(tmp_path) and result.free > 0


def test_timeout_on_slow_unc(monkeypatch):
    monkeypatch.setattr(sp.os, 'name', 'nt')
    monkeypatch.setattr(sp, 'is_network_path', lambda p: True)
    monkeypatch.setattr(sp, 'sys', type('FakeSys', (), {'frozen': False, 'executable': 'python.exe'}))
    def too_slow(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs['timeout'])
    monkeypatch.setattr(sp.subprocess, 'run', too_slow)
    with pytest.raises(TimeoutError, match='optional'):
        sp.check_space_bounded(Path('//NAS/Share/Card'), timeout=.01)


def test_successful_remote_probe(monkeypatch):
    monkeypatch.setattr(sp.os, 'name', 'nt')
    monkeypatch.setattr(sp, 'is_network_path', lambda p: True)
    monkeypatch.setattr(sp, 'sys', type('FakeSys', (), {'frozen': False, 'executable': 'python.exe'}))
    def response(*args, **kwargs):
        assert kwargs['timeout'] == 5
        return subprocess.CompletedProcess(args[0],0,'{"total":150,"used":20,"free":130}\n','')
    monkeypatch.setattr(sp.subprocess, 'run', response)
    space = sp.check_space_bounded(Path('//NAS/Share/Card'),timeout=5)
    assert space.free == 130 and space.network


def test_unavailable_remote_probe_has_error(monkeypatch):
    monkeypatch.setattr(sp.os, 'name', 'nt')
    monkeypatch.setattr(sp, 'is_network_path', lambda p: True)
    monkeypatch.setattr(sp, 'sys', type('FakeSys', (), {'frozen': False, 'executable': 'python.exe'}))
    monkeypatch.setattr(sp.subprocess, 'run',lambda *a,**k:subprocess.CompletedProcess(a,1,'','NAS offline'))
    with pytest.raises(OSError, match='NAS offline'):
        sp.check_space_bounded(Path('//NAS/Share/Card'))


def test_gui_does_not_automatically_probe_network_drive():
    source=(Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8')
    block=source[source.index('def update_workspace_location(self):'):source.index('def check_workspace_space(self):')]
    assert "if is_network_path(self.workspace):" in block
    assert 'No automatic SMB capacity lookup' in block
    assert "self.check_workspace_space()" in block.split('else:',1)[-1]
    assert 'self.capacity_button' in source
