"""Safe staging of user-supplied Android APK installers into the virtual card.

This verifies ZIP/APK structure, not publisher identity or Android compatibility.
It does not execute, install, overwrite, or remove originals.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from core import (CAPACITY, COMPANION_BUDGET, FREE_RESERVE, copy_atomic,
                  inventory, safe_walk, sha256, within)
from software import _apk_ok

APK_LIMIT = 750 * 1024 ** 2


def staged_apks(workspace: Path) -> list[dict]:
    root = workspace / 'SetupPackages'
    files = sorted((p for p in safe_walk(root) if p.parent == root and p.suffix.lower() == '.apk'),
                   key=lambda p: p.name.casefold())
    result = []
    for file in files:
        try:
            size = file.stat().st_size
            label = ('Cocoon Shell (filename suggests)' if file.name.casefold().startswith(('cocoon', 'cocon-'))
                     else 'Android installer')
            result.append({'name': file.name, 'label': label, 'size': size, 'path': str(file)})
        except OSError:
            continue
    return result


def stage_local_apks(paths: Iterable[Path], workspace: Path, progress=None, cancel=None) -> dict:
    """Import APKs using atomic copy and conservative reserved capacity checks.

    A conflicted filename with DIFFERENT bytes is an error, never overwritten.
    """
    items = list(dict.fromkeys(Path(p) for p in paths))
    result = {'added': 0, 'already': 0, 'errors': [], 'cancelled': False, 'paths': []}
    root = workspace / 'SetupPackages'
    root.mkdir(parents=True, exist_ok=True)
    receipt_dir = workspace / '.retro-library' / 'receipts'
    # Inspect workspace usage once for the entire batch. The operation runs in
    # the isolated import helper so a slow SMB share never holds the GUI hostage.
    # Update this tally after each successful addition.
    used = None
    for i, source in enumerate(items, 1):
        if cancel is not None and cancel.is_set():
            result['cancelled'] = True
            break
        try:
            if source.suffix.lower() != '.apk' or source.name in {'.', '..'} or '\\' in source.name:
                raise ValueError('Only .apk Android installers can be added here')
            if not source.is_file() or source.is_symlink():
                raise ValueError('APK must be a regular file, not a shortcut')
            if source.stat().st_size > APK_LIMIT:
                raise ValueError('APK exceeds 750 MiB safety limit')
            if within(source, workspace):
                raise ValueError('This APK is already inside the virtual card')
            _apk_ok(source)
            dest = root / source.name
            needs_addition = not dest.exists()
            if needs_addition and used is None:
                if progress:
                    progress('Checking virtual-card budget (this may take longer on a NAS)…', 0, 0)
                _, used, _ = inventory(workspace, cancel=cancel)
                if cancel is not None and cancel.is_set():
                    raise InterruptedError('APK import cancelled during capacity check')
            # Existing same-name files can be verified even when the budget is full.
            if needs_addition and used + source.stat().st_size + COMPANION_BUDGET + FREE_RESERVE > CAPACITY:
                raise OSError('Virtual-card budget would be exceeded')
            state = copy_atomic(source, dest, cancel=cancel,
                                progress=(lambda name, done, total: progress(name, done, total)) if progress else None)
            if state == 'copied':
                result['added'] += 1
                used = (used or 0) + source.stat().st_size
            else:
                result['already'] += 1
            receipt_dir.mkdir(parents=True, exist_ok=True)
            receipt = {'filename': dest.name, 'size': dest.stat().st_size,
                       'sha256': sha256(dest), 'source': 'user imported: publisher unverified',
                       'created_utc': datetime.now(timezone.utc).isoformat()}
            safe_filename = re.sub(r'[^A-Za-z0-9._-]+', '_', dest.name)
            (receipt_dir / f'local_{safe_filename}.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
            result['paths'].append(str(dest))
        except InterruptedError:
            result['cancelled'] = True
            break
        except Exception as exc:
            result['errors'].append(f'{source.name}: {exc}')
        if progress:
            progress(f'APK {i}/{len(items)} checked: {source.name}', i, len(items))
    return result
