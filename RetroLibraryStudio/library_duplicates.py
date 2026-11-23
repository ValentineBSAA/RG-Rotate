"""Shared safe duplicate checks for every supported console.

Run in disposable import workers only, NEVER on the GUI paint path.
Compare game bytes only within the SAME platform. An exact SHA-256 match may
be skipped, but different bytes with the same normalized title are NOT merged:
they are left alone and reported for user review. No ROMs are deleted.
"""
from __future__ import annotations

import re
from pathlib import Path

from core import ROM_EXT, SYSTEM_DIR, safe_walk, sha256

# A CUE/playlist is a descriptor; BIN tracks and sidecars may be identical
# across distinct discs and must not be deduplicated independently.
_SINGLE_GAME = ROM_EXT - {
    '.cue', '.bin', '.m3u', '.ccd', '.sub', '.mdf', '.mds', '.gdi',
}


def is_single_game_file(source: Path) -> bool:
    return Path(source).suffix.casefold() in _SINGLE_GAME


def game_title_key(stem: str) -> str:
    """Preserve edition, region, revision, disc, language and product markers.

    Removes only whitespace and punctuation differences, not semantic tags.
    """
    return re.sub(r'[^\w\d]', '', str(stem).casefold(), flags=re.UNICODE)


def inspect_game_duplicate(source: Path, workspace: Path, system: str,
                           *, planned_destination: Path | None = None,
                           cancel=None) -> tuple[str, str]:
    """Return (new|exact|review, helpful explanation), without side effects.

    Excludes self and other systems. Always check byte hash for a claim of exact
    identity; do not decide from file name, size or cover art alone.
    """
    source = Path(source)
    if system not in SYSTEM_DIR or not is_single_game_file(source):
        return 'new', ''
    root = Path(workspace) / 'ROMs' / SYSTEM_DIR[system]
    if not root.is_dir():
        return 'new', ''
    try:
        stat = source.stat()
        source_size = stat.st_size
    except OSError:
        return 'new', ''
    # Generic container filenames carry no title; content can still match,
    # but unrelated PSP homebrew EBOOT.PBP files must never collide by name.
    generic_names = {'eboot', 'game', 'rom', 'image', 'disc', 'disk', 'track01'}
    source_key = ('' if source.stem.casefold() in generic_names
                  else game_title_key(source.stem))
    same_size = []
    same_name = []
    for candidate in safe_walk(root, cancel=cancel):
        if cancel is not None and cancel.is_set():
            raise InterruptedError('Duplicate check stopped')
        if not is_single_game_file(candidate):
            continue
        if planned_destination is not None and candidate == source:
            continue
        try:
            cstat = candidate.stat()
        except OSError:
            continue
        if cstat.st_size == source_size:
            same_size.append(candidate)
        if source_key and game_title_key(candidate.stem) == source_key:
            same_name.append(candidate)
    if same_size:
        digest = sha256(source, cancel=cancel)
        for candidate in same_size:
            if cancel is not None and cancel.is_set():
                raise InterruptedError('Duplicate check stopped')
            # Identical source bytes under different names/archive wrappers are
            # provably the same game payload, not just a similar title.
            if sha256(candidate, cancel=cancel) == digest:
                return 'exact', f'Already imported to {system}: {candidate.name} (exact SHA-256 match)'
    if same_name:
        return ('review',
                f'Possible duplicate on {system}: {source.name} and '
                f'{same_name[0].name} have the same game title but different '
                'contents or formats. Import paused for this file to protect '
                'different editions and revisions. Nothing was overwritten.')
    return 'new', ''
