"""PS1 Classics provenance on top of library-wide duplicate screening.

Receipts go under the *ignored* .retro-library directory so they do not
appear as game tiles. The source EBOOT is SHA-256 hashed; KEYS.BIN is never
read, hashed, logged or staged as provenance. Unknown legacy CHD collections
are preserved for manual review rather than silently assumed identical.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from core import sha256
from ps1_collections import disc_numbers_are_contiguous, disc_identity, folder_title

_RECEIPT_DIR = ('.retro-library', 'psn-sources')
_RECORD_EXT = '.json'
_STORE_TAG = re.compile(r'(?i)\s*\((?:PSN|English)\)\s*$')


def title_key(title: str) -> str:
    name = str(title).strip()
    while True:
        newer = _STORE_TAG.sub('', name).strip()
        if newer == name:
            break
        name = newer
    # Region and revision tags intentionally remain distinct.
    return re.sub(r'[^\w\d]', '', name.casefold())


def fingerprint_pbp(pbp: Path, cancel=None) -> str:
    if Path(pbp).suffix.lower() != '.pbp':
        raise ValueError('Source fingerprint requires an EBOOT.PBP, not a key file')
    return sha256(Path(pbp), cancel=cancel)


def _members(folder: Path) -> list[Path]:
    folder = Path(folder)
    if folder.is_symlink() or not folder.is_dir():
        return []
    playlist = folder / f'{folder.name}.m3u'
    if playlist.is_symlink() or not playlist.is_file() or playlist.stat().st_size > 1024 * 1024:
        return []
    try:
        names = playlist.read_text(encoding='utf-8-sig').splitlines()
    except (OSError, UnicodeError):
        return []
    if len(names) < 2 or len(names) > 40:
        return []
    members, numbers = [], []
    for name in names:
        if not name or name != Path(name).name or '/' in name or '\\' in name:
            return []
        child = folder / name
        base, disc = disc_identity(child.stem)
        if base.casefold() != folder.name.casefold() or disc is None:
            return []
        if child.suffix.casefold() != '.chd' or child.is_symlink() or not child.is_file() or child.stat().st_size <= 0:
            return []
        members.append(child)
        numbers.append(disc)
    return members if numbers == sorted(numbers) and disc_numbers_are_contiguous(numbers) else []


def existing_collections(workspace: Path, title: str) -> list[Path]:
    root = Path(workspace) / 'ROMs' / 'psx'
    if not root.is_dir() or root.is_symlink():
        return []
    wanted = title_key(title)
    return sorted((folder for folder in root.iterdir()
                   if folder.is_dir() and not folder.is_symlink()
                   and title_key(folder.name) == wanted and _members(folder)),
                  key=lambda p: p.name.casefold())


def _receipt_path(workspace: Path, digest: str) -> Path:
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid PS1 Classics package fingerprint')
    return Path(workspace).joinpath(*_RECEIPT_DIR) / (digest + _RECORD_EXT)


def decide_repeat(workspace: Path, title: str, source_hash: str) -> tuple[str, str]:
    """Exact proven repeat, suspected same title, or safe new import."""
    receipt = _receipt_path(workspace, source_hash)
    if receipt.is_file() and not receipt.is_symlink() and receipt.stat().st_size <= 8192:
        try:
            record = json.loads(receipt.read_text(encoding='utf-8'))
            if record.get('version') == 1 and record.get('system') == 'PS1':
                folder_name = folder_title(record.get('collection', ''))
                folder = Path(workspace) / 'ROMs' / 'psx' / folder_name
                members = _members(folder)
                if len(members) == record.get('discs'):
                    return ('same', f'Already imported to PS1: {folder_name} • all {len(members)} CHDs still present')
        except (ValueError, OSError, TypeError):
            pass
    matches = existing_collections(workspace, title)
    if matches:
        return ('review', 'Possible duplicate: ' +
                ', '.join(folder.name for folder in matches[:3]) +
                ' already has a complete PS1 CHD/M3U collection. '
                'The earlier source has no matching EBOOT fingerprint, so this import '
                'was safely skipped rather than mixing different releases.')
    return 'new', ''


def record_import(workspace: Path, folder: Path, pbp_sha256: str, *, disc_count: int) -> None:
    folder = Path(folder)
    if folder.name != folder_title(folder.name):
        raise ValueError('Unsafe PS1 collection title')
    members = _members(folder)
    if len(members) != disc_count:
        raise ValueError('Cannot record unverified or incomplete CHD/M3U collection')
    target = _receipt_path(workspace, pbp_sha256)
    payload = {'version': 1, 'system': 'PS1', 'collection': folder.name, 'discs': disc_count}
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        raise FileExistsError('Unsafe PS1 source record; original games untouched')
    if target.exists():
        try:
            existing = json.loads(target.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            raise FileExistsError('Existing PS1 fingerprint record invalid; not overwritten')
        if existing == payload:
            return
        raise FileExistsError('Different PS1 collection already owns this fingerprint')
    with target.open('x', encoding='utf-8', newline='\n') as out:
        json.dump(payload, out, sort_keys=True)
        out.write('\n')
        out.flush()
        os.fsync(out.fileno())
