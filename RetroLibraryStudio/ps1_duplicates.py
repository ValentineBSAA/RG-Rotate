"""Conservative PS1 Classics repeat-import guard across ZIP/7Z/PBP inputs.

Fingerprint the CONTENT of EBOOT.PBP, not its archive path or archive bytes.
Never hash/record KEYS.BIN. Skip only a verified, previously recorded matching
PBP whose CHD/M3U members still exist; uncertain name collisions are held for
manual review rather than silently merging different releases or regions.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from ps1_collections import disc_numbers_are_contiguous, disc_identity, folder_title

_RECORD = '.retro-ps1-source.json'
_END_TAG = re.compile(r'(?i)\s*\((?:PSN|English)\)\s*$')
_REGION = re.compile(r'(?i)\s*\((?:Europe|USA|US|Japan|NTSC-U|NTSC-J|PAL)\)\s*$')


def title_key(title: str, *, ignore_region=False) -> str:
    name = str(title).strip()
    while True:
        newer = _END_TAG.sub('', name)
        if ignore_region:
            newer = _REGION.sub('', newer)
        newer = newer.strip()
        if newer == name:
            break
        name = newer
    return re.sub(r'[^a-z0-9]', '', name.casefold())


def fingerprint_pbp(pbp: Path, cancel=None) -> str:
    """Incremental SHA-256 over the game package, NEVER companion key files."""
    source = Path(pbp)
    digest = hashlib.sha256()
    with source.open('rb') as stream:
        while True:
            if cancel is not None and cancel.is_set():
                raise InterruptedError('Duplicate check stopped')
            data = stream.read(4 * 1024 * 1024)
            if not data:
                return digest.hexdigest()
            digest.update(data)


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
        if not name or name.startswith('#') or name != Path(name).name or '/' in name or '\\' in name:
            return []
        file = folder / name
        base, disc = disc_identity(file.stem)
        if base.casefold() != folder.name.casefold() or disc is None:
            return []
        if file.suffix.casefold() != '.chd' or file.is_symlink() or not file.is_file() or file.stat().st_size <= 0:
            return []
        members.append(file)
        numbers.append(disc)
    if numbers != sorted(numbers) or not disc_numbers_are_contiguous(numbers):
        return []
    return members


def existing_collections(workspace: Path, title: str) -> list[Path]:
    """Shallow scan in PS1 folders only; does not modify or read CHD contents."""
    root = Path(workspace) / 'ROMs' / 'psx'
    if not root.is_dir() or root.is_symlink():
        return []
    wanted = title_key(title, ignore_region=True)
    if not wanted:
        return []
    matches = []
    for folder in root.iterdir():
        if not folder.is_dir() or folder.is_symlink():
            continue
        if title_key(folder.name, ignore_region=True) == wanted and _members(folder):
            matches.append(folder)
    return sorted(matches, key=lambda p: p.name.casefold())


def _receipt(folder: Path) -> dict | None:
    meta = Path(folder) / _RECORD
    if meta.is_symlink() or not meta.is_file() or meta.stat().st_size > 8192:
        return None
    try:
        value = json.loads(meta.read_text(encoding='utf-8'))
        if value.get('version') == 1 and isinstance(value.get('pbp_sha256'), str):
            return value
    except (ValueError, TypeError, OSError, AttributeError):
        pass
    return None


def decide_repeat(workspace: Path, title: str, source_hash: str) -> tuple[str, str]:
    """(new|same|review, explanation) WITHOUT falsely equating editions."""
    candidates = existing_collections(workspace, title)
    if not candidates:
        return 'new', ''
    exact = []
    for folder in candidates:
        record = _receipt(folder)
        if (record and record.get('pbp_sha256') == source_hash
                and record.get('collection') == folder.name
                and record.get('discs') == len(_members(folder))):
            exact.append(folder)
    if len(exact) == 1:
        return 'same', f'Already imported from this EBOOT: {exact[0].name}. Verified CHD playlist is still present.'
    return ('review',
            'A PS1 collection with a matching or similar title already exists: '
            + ', '.join(x.name for x in candidates[:3])
            + '. The sources may be different editions or archives. '
            'Nothing new was imported to avoid duplicate game tiles or mismatched discs.')


def record_import(folder: Path, pbp_sha256: str, *, disc_count: int) -> None:
    """Record only proven completed collections, atomic create only.

    A preexisting provenance receipt is never overwritten by a different EBOOT.
    No source paths, raw key bytes, console serials or personal data are stored.
    """
    folder = Path(folder)
    safe = folder_title(folder.name)
    if safe != folder.name or len(pbp_sha256) != 64 or any(c not in '0123456789abcdef' for c in pbp_sha256):
        raise ValueError('Unsafe provenance record')
    members = _members(folder)
    if len(members) != disc_count:
        raise ValueError('Cannot record incomplete CHD/M3U collection')
    value = {'version':1, 'collection':folder.name,
             'pbp_sha256':pbp_sha256, 'discs':len(members)}
    path = folder / _RECORD
    if path.exists() or path.is_symlink():
        old = _receipt(folder)
        if old == value:
            return
        raise FileExistsError('Conflicting source receipt preserved; no deduplication proof saved')
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
