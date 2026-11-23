"""Network-safe, non-allocating workspace capacity detection.

Reports only actual free bytes on the backing filesystem. Never assumes that
512 GB of a *virtual* library is preallocated.
"""
from __future__ import annotations
import os
import shutil
import sys
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class SpaceInfo:
    path: str
    total: int
    used: int
    free: int
    network: bool


def is_network_path(path: Path) -> bool:
    text = str(path)
    if text.startswith('\\\\') or text.startswith('//'):
        return True
    if os.name == 'nt':
        try:
            import ctypes
            root = Path(path).anchor
            return bool(root and ctypes.windll.kernel32.GetDriveTypeW(root) == 4)
        except (AttributeError, OSError, ValueError):
            return False
    return False


def check_space(path: Path) -> SpaceInfo:
    directory = Path(path)
    # An unavailable network drive must not silently fall back to its parent
    # on an unrelated disk or report an irrelevant amount of free space.
    if not directory.exists():
        raise FileNotFoundError(f'The selected workspace is not available: {directory}')
    if not directory.is_dir():
        raise NotADirectoryError(str(directory))
    usage = shutil.disk_usage(directory)
    return SpaceInfo(str(directory), usage.total, usage.used, usage.free, is_network_path(directory))


def usable_stage_bytes(staged: int, free_on_host: int,
                       virtual_capacity: int, companion_budget: int, reserve: int) -> int:
    """Actual next-write headroom: host free space AND remaining game budget."""
    planned_remaining = max(0, virtual_capacity - companion_budget - reserve - staged)
    return max(0, min(planned_remaining, free_on_host))


def has_workspace_payload_fast(path: Path) -> bool:
    """Stop at first staged file. An empty freshly structured card is fast.

    Never assumes an empty card based solely on stale UI counters. Metadata
    receipts also count: users may wish to migrate PC-only setup records.
    """
    path = Path(path)
    if not path.exists():
        return False
    for directory, dirs, files in os.walk(path, followlinks=False):
        # Never traverse junctions or symlinks.
        dirs[:] = [d for d in dirs if not (Path(directory)/d).is_symlink()]
        if files:
            return True
        if directory == str(path) and len(dirs) > 500:
            raise ValueError('Selected workspace has too many top-level folders; use the background scan')
    return False


def has_interrupted_files(path: Path) -> bool:
    """A partial staged write should not be abandoned during a location change."""
    for directory, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(directory)/d).is_symlink()]
        if any(name.endswith('.retro-part') for name in files):
            return True
    return False


def describe_bytes(n: int) -> str:
    """Show both binary (Windows-like) and decimal units to avoid fake mismatches."""
    return f'{n / 1024**3:,.2f} GiB ({n / 1_000_000_000:,.2f} GB)'


def check_space_bounded(path: Path, timeout: float = 6.0) -> SpaceInfo:
    """Bound remote free-space queries so an unresponsive SMB server cannot
    indefinitely monopolize the background capacity worker. No directory walk.

    Windows UNC / mapped-network requests run in a disposable child process;
    killing that child at the deadline does not touch or modify NAS files.
    """
    path = Path(path)
    if os.name != 'nt' or not is_network_path(path):
        return check_space(path)
    frozen = getattr(sys, 'frozen', False)
    if frozen:
        command = [sys.executable, '--retro-probe-storage', str(path)]
    else:
        snippet = (
            'import sys,json,shutil,os;'
            'p=sys.argv[1];'
            'u=shutil.disk_usage(p);'
            'print(json.dumps({"total":u.total,"used":u.used,"free":u.free}))'
        )
        command = [sys.executable, '-c', snippet, str(path)]
    try:
        finished = subprocess.run(
            command, capture_output=True, text=True, check=False,
            timeout=timeout, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f'NAS did not answer the free-space request within {timeout:g} seconds. '
            'This is optional; you can still use your virtual card.'
        ) from exc
    if finished.returncode:
        details = (finished.stderr or finished.stdout or 'The NAS did not return capacity information.').strip()
        raise OSError(f'NAS capacity query failed: {details[-450:]}')
    try:
        stats = json.loads(finished.stdout.strip().splitlines()[-1])
        return SpaceInfo(str(path), int(stats['total']), int(stats['used']), int(stats['free']), True)
    except (IndexError, KeyError, ValueError, TypeError) as exc:
        raise OSError('The NAS returned an unreadable capacity response.') from exc


def probe_storage_cli(path: str) -> int:
    """Small CLI for PyInstaller executables re-executed as child probes."""
    try:
        usage = shutil.disk_usage(path)
        print(json.dumps({'total': usage.total, 'used': usage.used, 'free': usage.free}), flush=True)
        return 0
    except Exception as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        return 1
