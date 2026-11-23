"""Launcher safety: neither normal nor debug should skip dependency checking."""
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

import pytest

import bootstrap


class ReporterStub:
    def __init__(self, result=0):
        self.result = result
        self.commands = []
        self.messages = []

    def tell(self, text):
        self.messages.append(text)

    def run(self, cmd, *, stage):
        self.commands.append((cmd, stage))
        return self.result


def test_paths_use_windows_scripts(tmp_path):
    assert bootstrap.venv_python(tmp_path, platform='nt') == tmp_path / '.venv' / 'Scripts/python.exe'
    assert bootstrap.venv_python(tmp_path, platform='posix') == tmp_path / '.venv' / 'bin/python'


def test_existing_venv_with_missing_qt_repairs(tmp_path):
    venv = bootstrap.venv_python(tmp_path)
    venv.parent.mkdir(parents=True)
    venv.touch()
    reporter = ReporterStub()
    with patch.object(bootstrap, 'dependencies_ready', side_effect=[(False, 'ModuleNotFoundError: No module named PySide6'), (True, '')]) as probe:
        assert bootstrap.prepare_environment(tmp_path, reporter) == venv
    assert probe.call_count == 2
    assert len(reporter.commands) == 1
    command, stage = reporter.commands[0]
    assert command[:4] == [str(venv), '-m', 'pip', 'install']
    assert '-r' in command and 'requirements.txt' in command[-1]
    assert 'Installing required libraries' in stage


def test_existing_venv_with_good_deps_does_not_reinstall(tmp_path):
    venv = bootstrap.venv_python(tmp_path)
    venv.parent.mkdir(parents=True)
    venv.touch()
    reporter = ReporterStub()
    with patch.object(bootstrap, 'dependencies_ready', return_value=(True, '')):
        assert bootstrap.prepare_environment(tmp_path, reporter) == venv
    assert reporter.commands == []


def test_cannot_launch_when_installation_fails(tmp_path):
    venv = bootstrap.venv_python(tmp_path)
    venv.parent.mkdir(parents=True)
    venv.touch()
    reporter = ReporterStub(result=1)
    with patch.object(bootstrap, 'dependencies_ready', return_value=(False, 'missing')):
        with pytest.raises(bootstrap.StartupError, match='installation failed'):
            bootstrap.prepare_environment(tmp_path, reporter)


def test_cannot_launch_when_pyside_still_missing_after_install(tmp_path):
    venv = bootstrap.venv_python(tmp_path)
    venv.parent.mkdir(parents=True)
    venv.touch()
    reporter = ReporterStub()
    with patch.object(bootstrap, 'dependencies_ready', side_effect=[(False, 'missing'), (False, 'No module named PySide6')]):
        with pytest.raises(bootstrap.StartupError, match='still cannot load'):
            bootstrap.prepare_environment(tmp_path, reporter)


def test_both_bats_use_same_bootstrap():
    for name in ['Start_Retro_Library_Studio.bat', 'Start_Debug.bat']:
        content = (Path(bootstrap.__file__).parent / name).read_text(encoding='utf-8')
        assert 'bootstrap.py' in content
        assert 'python.exe" app.py' not in content


def test_probe_unavailable_dependency_reports_failure(tmp_path):
    with patch.object(bootstrap.subprocess, 'run', return_value=SimpleNamespace(returncode=1, stderr='No module named PySide6', stdout='')):
        ok, reason = bootstrap.dependencies_ready(tmp_path / 'fake.exe')
    assert not ok and 'PySide6' in reason
