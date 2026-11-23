"""Non-destructive PC workspace selection and verified workspace copying.

Pure Python: testable without PySide6. A virtual card is an ordinary
Windows folder, never a reserved partition or filesystem image.
"""
from __future__ import annotations

import os
import shutil
import threading
from pathlib import Path
from typing import Callable

from core import safe_walk, within
from sync_engine import make_plan, transfer_verified, _copy_verified, _hash

VIRTUAL_CARD_NAME = 'RG Rotate Virtual Card'
KNOWN_CARD_FOLDERS = {'ROMs', 'BIOS', 'Media', 'CocoonData', 'SetupPackages', 'CompanionData'}


def is_workspace(path: Path) -> bool:
    """Only trust a directory with known top-level card structure."""
    return path.is_dir() and any((path / name).is_dir() for name in KNOWN_CARD_FOLDERS)


def _reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    if os.name == 'nt' and path.exists():
        import stat
        try:
            return bool(path.stat(follow_symlinks=False).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except AttributeError:
            return False
    return False


def _check_ancestors(path: Path) -> None:
    for ancestor in (path, *path.parents):
        if _reparse_point(ancestor):
            raise ValueError('Choose a regular local folder, not a symbolic link or junction.')


def suggested_workspace(selection: Path, old_workspace: Path | None = None,
                        physical_destination: Path | None = None) -> tuple[Path, bool]:
    """Return safe card folder and whether a dedicated subfolder was chosen.

    Selecting drive root, Home, Downloads, Documents, or unrelated nonempty folder
    creates a *proposal* for a dedicated subfolder: this function writes nothing.
    """
    raw = Path(selection).expanduser()
    selected = raw.resolve(strict=False)
    if raw.exists() and not raw.is_dir():
        raise ValueError('The chosen location is a file, not a folder.')
    _check_ancestors(raw)
    if not selected.exists():
        raise ValueError('Choose an existing parent folder. Use the folder picker to create a new folder.')
    if old_workspace and (within(selected, old_workspace) or within(old_workspace, selected)):
        if selected == old_workspace.resolve(strict=False):
            return selected, False
        # Choosing parent of current workspace is valid; we'll create its card child.
        if within(selected, old_workspace):
            raise ValueError('The new virtual card cannot be placed inside the old virtual card.')
    common = {Path.home().resolve(strict=False)}
    for name in ('Documents', 'Downloads', 'Desktop'):
        common.add((Path.home() / name).resolve(strict=False))
    broad = selected == selected.parent or selected in common
    # Never adopt an unrelated, populated folder as the card root.
    unrelated = selected.is_dir() and any(selected.iterdir()) and not is_workspace(selected)
    if broad or unrelated:
        candidate = selected / VIRTUAL_CARD_NAME
        if old_workspace and (within(candidate, old_workspace) or within(old_workspace, candidate)):
            raise ValueError('Choose a different location; it overlaps your existing virtual card.')
        if physical_destination and (within(candidate, physical_destination) or within(physical_destination, candidate)):
            raise ValueError('This location overlaps the real microSD destination.')
        if candidate.exists() and not candidate.is_dir():
            raise ValueError('A file already occupies the proposed virtual-card folder name.')
        if candidate.exists() and any(candidate.iterdir()) and not is_workspace(candidate):
            raise ValueError('The proposed folder already has unrelated files. Choose or create another folder.')
        return candidate, True
    if physical_destination and (within(selected, physical_destination) or within(physical_destination, selected)):
        raise ValueError('The virtual card must be on your PC, separate from the real card destination.')
    return selected, False


def count_workspace_files(workspace: Path, progress: Callable | None = None, cancel=None) -> tuple[int, int] | None:
    """Background inventory before changing a nonempty workspace.

    Detects interrupted .retro-part writes instead of silently abandoning them.
    Includes app-only receipts so a migration can preserve them.
    """
    count = size = 0
    if cancel is not None and cancel.is_set():
        return None
    for directory, dirs, files in os.walk(workspace, followlinks=False):
        dirs[:] = [name for name in dirs if not _reparse_point(Path(directory)/name)]
        for name in files:
            if cancel is not None and cancel.is_set():
                return None
            file = Path(directory)/name
            if name.endswith('.retro-part'):
                raise ValueError('Unfinished .retro-part file found. Finish or recover the interrupted operation before changing card locations.')
            if _reparse_point(file) or not file.is_file():
                continue
            count += 1
            size += file.stat().st_size
            if progress is not None and count % 200 == 0:
                progress(f'Checking existing card: {count:,} files found', count, 0)
    return count, size


def copy_existing_workspace(source: Path, destination: Path,
                            progress: Callable | None = None,
                            cancel: threading.Event | None = None) -> dict:
    """Copy with content verification and safe retries; never delete originals."""
    source = Path(source).resolve(strict=False)
    destination = Path(destination).resolve(strict=False)
    if not source.is_dir():
        raise ValueError('The original virtual card cannot be found.')
    if within(source, destination) or within(destination, source):
        raise ValueError('The old and new virtual cards must not overlap.')
    _check_ancestors(destination)
    if destination.exists() and not destination.is_dir():
        raise ValueError('The destination is not a folder.')
    destination.mkdir(parents=True, exist_ok=True)
    try:
        plan = make_plan(source, destination, simulation=True, cancel=cancel)
    except InterruptedError:
        return {'copied': 0, 'skipped': 0, 'verified': 0, 'files': 0,
                'errors': [], 'cancelled': True}
    if plan.conflicts:
        raise ValueError('Cannot copy safely:\n' + '\n'.join(plan.conflicts[:10]))
    # The app's PC-only receipts should travel when the virtual workspace moves,
    # even though they are intentionally excluded from physical SD transfers.
    metadata_root = source / '.retro-library'
    metadata = list(safe_walk(metadata_root))
    metadata_new = 0
    for file in metadata:
        relative = file.relative_to(source)
        dest = destination / relative
        if not within(dest.parent, destination):
            raise ValueError('Unsafe destination for workspace metadata.')
        if dest.exists():
            if dest.is_symlink() or not dest.is_file() or _hash(dest) != _hash(file):
                raise ValueError(f'Existing workspace metadata differs: {relative}')
        else:
            metadata_new += file.stat().st_size
    # Physical free disk space is a limit even during a practice-mode copy.
    if plan.bytes_new + metadata_new > shutil.disk_usage(destination).free:
        raise OSError('Not enough free space on the selected Windows drive to copy the virtual card.')
    if cancel is not None and cancel.is_set():
        return {'copied': 0, 'skipped': 0, 'verified': 0, 'files': plan.files,
                'errors': [], 'cancelled': True}
    if plan.files == 0:
        result = {'copied': 0, 'skipped': 0, 'verified': 0, 'files': 0,
                  'errors': [], 'cancelled': False}
    else:
        result = transfer_verified(source, destination, progress=progress,
                                   cancel=cancel, simulation=True)
    if result.get('errors') or result.get('cancelled'):
        return result
    result['files'] += len(metadata)
    for file in metadata:
        if cancel is not None and cancel.is_set():
            result['cancelled'] = True
            break
        relative = file.relative_to(source)
        try:
            def report(wrote: int):
                if progress is not None:
                    progress('Copying PC library settings', wrote, max(1,file.stat().st_size),
                             str(relative), 0., 0.)
            state, _ = _copy_verified(file, destination / relative, report, cancel)
            result['verified'] += 1
            if state == 'copied':
                result['copied'] += 1
            else:
                result['skipped'] += 1
        except InterruptedError:
            result['cancelled'] = True
            break
        except Exception as exc:
            result['errors'].append(f'{relative}: {exc}')
            break
    return result
