"""Conservative PS1 multi-disc identity, UI grouping and safe M3U updates.

Only explicit Disc/Disk/CD numbers group games. Never erase region or edition.
GUI reads exclusively worker-produced inventory metadata; it never reads NAS
playlists on the paint path.
"""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

_DISC = re.compile(r'\s*(?:\(\s*(?:disc|disk|cd)\s*(\d{1,2})\s*\)|'
                   r'\[\s*(?:disc|disk|cd)\s*(\d{1,2})\s*\]|'
                   r'[-_ ]+(?:disc|disk|cd)\s*(\d{1,2})(?=\s*(?:$|\(|\[)))', re.I)
_RE2_ROLE = re.compile(r'\s*\((?:Leon|Claire)\)\s*$', re.I)
_INVALID_WIN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_WIN = re.compile(r'(?i)^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?$')


def disc_identity(stem: str) -> tuple[str, int | None]:
    """One game title and optional disc number; tracks never count as discs."""
    name = str(stem).strip()
    match = _DISC.search(name)
    if match is None:
        return name, None
    number = int(next(v for v in match.groups() if v is not None))
    title = _DISC.sub('', name).strip(' -._')
    if title.casefold().startswith('resident evil 2'):
        title = _RE2_ROLE.sub('', title).strip(' -._')
    return title, number


def folder_title(title: str) -> str:
    """Reject unsafe Windows folder names instead of conflating unrelated games."""
    title = title.strip()
    if (not title or len(title) > 170 or title[-1] in ' .' or
            _INVALID_WIN.search(title) or _RESERVED_WIN.fullmatch(title)):
        raise ValueError('Game title is not a safe Windows folder name; files were not changed')
    return title


def disc_numbers_are_contiguous(numbers) -> bool:
    """A completed published playlist must be 1..N without gaps or duplicates."""
    ordered = sorted(numbers)
    return bool(ordered) and len(ordered) == len(set(ordered)) and ordered == list(range(1, ordered[-1] + 1))


def same_game_disc(stem: str, parent_title: str) -> int | None:
    title, number = disc_identity(stem)
    return number if number is not None and title.casefold() == parent_title.casefold() else None


def logical_disc_groups(entries):
    """One M3U cover tile when the scan worker validated all its CHD references.

    Never hide a disc under a missing/unsafe/incomplete or misordered playlist.
    Entry.members are populated by inventory() in a separate worker process.
    """
    ordered = list(entries)
    by_path = {os.path.normcase(os.path.abspath(str(e.path))): e for e in ordered}
    claimed = set()
    collections = {}
    for item in ordered:
        if item.system != 'PS1' or item.extension.lower() != '.m3u':
            continue
        members = []
        for filename in getattr(item, 'members', ()):
            child = by_path.get(os.path.normcase(os.path.abspath(str(filename))))
            if child is None or child.extension.lower() != '.chd' or child.path.parent != item.path.parent:
                members = []
                break
            members.append(child)
        if len(members) < 2 or len(members) != len(set(str(m.path) for m in members)):
            continue
        numbers = [same_game_disc(m.path.stem, item.path.stem) for m in members]
        if any(n is None for n in numbers) or not disc_numbers_are_contiguous(numbers):
            continue
        if numbers != sorted(numbers):
            continue
        collections[os.path.normcase(os.path.abspath(str(item.path)))] = [item, *members]
        claimed.update(os.path.normcase(os.path.abspath(str(m.path))) for m in members)
    return collections, claimed


def publish_playlist(discs: list[Path], playlist: Path, cancel=None) -> str:
    """Publish/extend M3U without overwriting conflicting user-authored playlists.

    Only a strictly in-order subset of the new, verified CHD sequence can be
    extended. This permits Disc 3 being added later; conflicting edits remain.
    """
    playlist = Path(playlist)
    discs = [Path(p) for p in discs]
    if len(discs) < 2 or playlist.suffix.casefold() != '.m3u':
        raise ValueError('A multi-disc playlist requires at least two CHDs')
    numbers = [same_game_disc(p.stem, playlist.stem) for p in discs]
    if any(n is None for n in numbers) or not disc_numbers_are_contiguous(numbers):
        raise ValueError('Disc numbering is missing, duplicated or not consecutive from Disc 1')
    for p in discs:
        if p.parent != playlist.parent or p.suffix.casefold() != '.chd' or not p.is_file():
            raise ValueError('Only real CHDs in the same game folder can be in the M3U')
    names = [p.name for p in discs]
    if len({n.casefold() for n in names}) != len(names) or any('\n' in n or '\r' in n for n in names):
        raise ValueError('Ambiguous CHD filenames cannot form one playlist')
    if cancel is not None and cancel.is_set():
        raise InterruptedError('Playlist generation stopped')
    if playlist.is_symlink():
        raise ValueError('Refusing to replace a linked playlist')
    previous = None
    if playlist.exists():
        if not playlist.is_file() or playlist.stat().st_size > 4 * 1024 * 1024:
            raise ValueError('Existing playlist is not a safe ordinary M3U')
        previous = playlist.read_text(encoding='utf-8-sig').splitlines()
        if previous == names:
            return 'unchanged'
        if not previous or len(previous) != len(set(x.casefold() for x in previous)):
            raise FileExistsError('Existing playlist is invalid; it was preserved')
        if [name for name in names if name in previous] != previous:
            raise FileExistsError('Existing custom/alternate playlist conflicts with the disc order; not overwritten')
    playlist.parent.mkdir(parents=True, exist_ok=True)
    if previous is None:
        with playlist.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write('\n'.join(names) + '\n')
        return 'created'
    temp = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='\n',
                                         suffix='.retro-m3u-tmp', prefix=playlist.stem+'-',
                                         dir=playlist.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write('\n'.join(names) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        if cancel is not None and cancel.is_set():
            raise InterruptedError('Playlist update stopped')
        os.replace(temp, playlist)
        return 'updated'
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
