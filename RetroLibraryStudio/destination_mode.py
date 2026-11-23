"""Destination type persistence with conservative real-card safety rules.

A practice folder is never inferred to be a physical microSD. For old app
settings, only the application's exact known practice folder is upgraded
automatically; other ambiguous paths require deliberate user confirmation.
"""
from __future__ import annotations
import re
from pathlib import Path, PureWindowsPath


def is_volume_root(value) -> bool:
    if value is None:
        return False
    raw = str(value)
    if re.match(r'^[A-Za-z]:[\\/]', raw) or raw.startswith('\\\\'):
        path = PureWindowsPath(raw)
    else:
        path = Path(raw)
    return bool(path.anchor) and path == type(path)(path.anchor)


def same_location(a, b) -> bool:
    if a is None or b is None:
        return False
    def normalized(x):
        return str(x).replace('\\','/').rstrip('/').casefold()
    return normalized(a) == normalized(b)


def restore_destination_mode(target, saved_mode, default_practice_folder) -> str:
    if target is None:
        return 'unset'
    root = is_volume_root(target)
    if saved_mode == 'practice' and not root:
        return 'practice'
    if saved_mode == 'physical' and root:
        return 'physical'
    # Migration from v1.4.3, which saved the folder but not its mode.
    if same_location(target, default_practice_folder) and not root:
        return 'practice'
    if root:
        return 'physical'
    return 'unconfirmed'
