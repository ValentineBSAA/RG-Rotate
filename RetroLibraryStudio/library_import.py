"""System inference and existing-game import routing (Qt-independent)."""
from __future__ import annotations
from pathlib import Path
from core import SYSTEM_DIR, import_files

def infer_system(file: Path, default: str) -> str:
    """Infer only unambiguous formats or nearby platform folder names."""
    names = {p.casefold() for p in file.parent.parts[-4:]}
    for system, folder in SYSTEM_DIR.items():
        if folder.casefold() in names or system.casefold() in names:
            return system
    suffix = file.suffix.lower()
    precise = {'.gba':'GBA', '.gb':'GB', '.gbc':'GBC', '.nes':'NES',
               '.sfc':'SNES', '.smc':'SNES', '.md':'Genesis', '.gen':'Genesis',
               '.nds':'Nintendo DS', '.n64':'Nintendo 64', '.z64':'Nintendo 64',
               '.v64':'Nintendo 64', '.cso':'PSP',
               '.cue':'PS1', '.ccd':'PS1', '.m3u':'PS1', '.gdi':'Dreamcast',
               '.cdi':'Dreamcast', '.gcm':'GameCube'}
    return precise.get(suffix, default)


def import_grouped(paths: list[Path], virtual: Path, fallback: str, progress=None, cancel=None):
    groups: dict[str, list[Path]] = {}
    for path in paths:
        groups.setdefault(infer_system(path, fallback), []).append(path)
    copied = skipped = 0
    errors = []
    for i, (system, files) in enumerate(groups.items(), 1):
        if cancel is not None and cancel.is_set():
            break
        if progress:
            progress(f'Importing {system} ({i}/{len(groups)} groups)', i-1, len(groups))
        c, s, e = import_files(files, virtual, system, progress=progress, cancel=cancel)
        copied += c; skipped += s; errors.extend(e)
    return {'copied': copied, 'skipped': skipped, 'errors': errors,
            'cancelled': cancel is not None and cancel.is_set()}

