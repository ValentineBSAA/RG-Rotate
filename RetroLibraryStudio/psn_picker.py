"""Read-only PS1 Classics source catalog for the selectable game-folder UI.

Sony product-code folders are opaque identifiers, NOT game titles. Prefer
bounded public PBP PARAM.SFO metadata and honest named archives; never invent
a mapping between an NP... product code and an unrelated game.
This code runs in the isolated cancellable import worker, not in Qt.
"""
from __future__ import annotations

from pathlib import Path

from core import safe_walk
from ps1_psn import is_ps1_classic, meaningful_title, package_title

_MAX_GAMES = 1500
_ARCHIVES = {'.zip', '.7z'}


def scan_psn_sources(folder: Path, *, cancel=None, progress=None,
                     max_items: int = _MAX_GAMES) -> dict:
    root = Path(folder)
    if not root.is_dir() or root.is_symlink():
        raise ValueError('Select a readable folder containing PS1 Classics EBOOT or archives')
    if max_items < 1 or max_items > _MAX_GAMES:
        raise ValueError('Invalid PS1 catalog limit')
    entries = []
    truncated = False
    scanned = 0
    for p in safe_walk(root, cancel=cancel):
        if cancel is not None and cancel.is_set():
            return {'cancelled': True, 'games': [], 'folder': str(root)}
        if p.is_symlink() or p.suffix.casefold() not in _ARCHIVES | {'.pbp'}:
            continue
        if len(entries) >= max_items:
            truncated = True
            break
        if p.suffix.casefold() == '.pbp':
            if not is_ps1_classic(p):
                continue
            try:
                title = package_title(p)
                identified = True
            except ValueError:
                title = None
                identified = False
            parent = p.parent
            product_code = parent.name if parent.name != root.name else ''
            kind = 'PS1 Classic EBOOT'
            detail = 'EBOOT.PBP • companion KEYS.BIN detected automatically when present'
        else:
            # Do not extract multi-GB archives merely to show this chooser.
            # The importer will identify a PBP inside after selection.
            title = meaningful_title(p.stem)
            identified = title is not None
            product_code = p.parent.name if p.parent != root else ''
            kind = 'PS1 archive (inspect during import)'
            detail = 'Contents are checked before a game is published'
        try:
            size = p.stat().st_size
        except OSError:
            continue
        entries.append({
            'title': title or 'Title not yet identified',
            'identified': identified,
            'path': str(p),
            'code': product_code,
            'kind': kind,
            'bytes': size,
            'detail': detail
        })
        scanned += 1
        if progress:
            progress(f'Identifying PS1 games: {scanned} package(s) found', 0, 0)
    entries.sort(key=lambda item: (not item['identified'],
                                  item['title'].casefold(),
                                  item['code'].casefold(), item['path'].casefold()))
    return {'games': entries, 'folder': str(root), 'truncated': truncated,
            'cancelled': bool(cancel is not None and cancel.is_set())}
