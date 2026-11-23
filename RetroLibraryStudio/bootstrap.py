"""Self-repairing Windows launcher for Retro Library Studio (standard library only).

This runs OUTSIDE the virtual environment, then installs and verifies all GUI
requirements INSIDE that virtual environment before starting app.py.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIREMENTS = ROOT / "requirements.txt"
CHECK_CODE = r"""
from importlib.metadata import version
from packaging.version import Version
from PySide6.QtCore import __version__ as qt_version
import py7zr
assert Version(qt_version) >= Version('6.8') and Version(qt_version) < Version('7')
assert Version(version('py7zr')) >= Version('1.1.3') and Version(version('py7zr')) < Version('2')
assert Version(version('packaging')) >= Version('24') and Version(version('packaging')) < Version('27')
"""

class StartupError(Exception):
    pass

class Reporter:
    def __init__(self, root: Path):
        self.path = root / "logs" / "startup_last.log"
        self.handle = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.handle = self.path.open("w", encoding="utf-8", errors="replace")
            self.handle.write("Retro Library Studio startup log\n")
            self.handle.write(datetime.now().astimezone().isoformat(timespec="seconds") + "\n")
            self.handle.flush()
        except OSError:
            self.handle = None

    def tell(self, message: str):
        print(message, flush=True)
        if self.handle:
            self.handle.write(message + "\n")
            self.handle.flush()

    def run(self, command: list[str], *, stage: str) -> int:
        self.tell(f"\n{stage}...")
        try:
            proc = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, stdin=None,
                                    text=True, errors="replace", bufsize=1)
            assert proc.stdout is not None
            for line in proc.stdout:
                self.tell(line.rstrip("\r\n"))
            return proc.wait()
        except OSError as exc:
            raise StartupError(f"Cannot start {stage}: {exc}") from exc

    def close(self):
        if self.handle:
            self.handle.close()


def venv_python(root: Path, *, platform: str | None = None) -> Path:
    platform = platform or os.name
    return root / ".venv" / ("Scripts/python.exe" if platform == "nt" else "bin/python")


def dependencies_ready(python: Path) -> tuple[bool, str]:
    try:
        result = subprocess.run([str(python), "-c", CHECK_CODE], cwd=ROOT,
                                capture_output=True, text=True, errors="replace", timeout=45)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    return result.returncode == 0, (result.stderr or result.stdout).strip()


def prepare_environment(root: Path, reporter: Reporter, *, base_python: str | None = None) -> Path:
    """Recheck packages on EVERY launch; don't trust a stale setup marker."""
    py = venv_python(root)
    if not py.exists():
        reporter.tell("First-time setup: creating a private Python environment.")
        if reporter.run([base_python or sys.executable, "-m", "venv", str(root / ".venv")],
                        stage="Creating app environment") != 0:
            raise StartupError("Could not create the Python environment. Ensure Python 3.11+ is installed.")
    if not py.exists():
        raise StartupError(f"Python environment was not created: {py}")
    reporter.tell("Checking PySide6 and archive support...")
    ready, reason = dependencies_ready(py)
    if not ready:
        reporter.tell("Required libraries are missing or incomplete; installing/repairing them now.")
        if reason:
            reporter.tell("Dependency check: " + reason.splitlines()[-1])
        pip_cmd = [str(py), "-m", "pip", "install", "--disable-pip-version-check",
                   "--prefer-binary", "-r", str(root / "requirements.txt")]
        result = reporter.run(pip_cmd, stage="Installing required libraries (internet needed the first time)")
        if result != 0:
            raise StartupError("Automatic library installation failed. See the messages above and the startup log. Check internet access and Python compatibility, then run this launcher again.")
        ready, reason = dependencies_ready(py)
        if not ready:
            raise StartupError("Libraries were downloaded but PySide6 still cannot load. "
                               + (reason.splitlines()[-1] if reason else "See startup log."))
    reporter.tell("All required libraries are ready.")
    return py


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="keep diagnostic console open")
    parser.add_argument("--check-only", action="store_true", help="prepare environment only")
    args = parser.parse_args(argv)
    reporter = Reporter(ROOT)
    try:
        if sys.version_info < (3, 11):
            raise StartupError(f"Python {sys.version.split()[0]} is too old. Install 64-bit Python 3.11 or later.")
        if sys.maxsize <= 2**32:
            raise StartupError("This app needs 64-bit Python for PySide6. Install 64-bit Python 3.11+.")
        py = prepare_environment(ROOT, reporter)
        if args.check_only:
            reporter.tell("Startup check passed.")
            return 0
        reporter.tell("Starting Retro Library Studio...")
        status = reporter.run([str(py), str(ROOT / "app.py")], stage="Opening app")
        if status:
            reporter.tell(f"\nThe app exited with error code {status}. Diagnostics: {reporter.path}")
            return status
        reporter.tell("Retro Library Studio closed normally.")
        return 0
    except StartupError as exc:
        reporter.tell(f"\nSETUP NOT COMPLETE: {exc}")
        reporter.tell(f"Log: {reporter.path}")
        return 1
    finally:
        reporter.close()


if __name__ == "__main__":
    raise SystemExit(main())
