"""Opt-in full library audit. Never removes duplicates or modifies game files."""
from __future__ import annotations
import hashlib
from collections import defaultdict
from pathlib import Path
from core import _cue_companions, safe_walk, ROM_EXT


def inspect_library(workspace: Path, progress=None, cancel=None) -> dict:
    games = sorted(p for p in safe_walk(workspace/'ROMs') if p.suffix.lower() in ROM_EXT)
    grouped: dict[int,list[Path]] = defaultdict(list)
    broken=[]
    examined=0
    for i,p in enumerate(games,1):
        if cancel is not None and cancel.is_set():
            break
        if p.suffix.lower() in {'.cue','.m3u'}:
            try:_cue_companions(p)
            except (ValueError,OSError) as exc:
                broken.append(f'{p.relative_to(workspace)}: {exc}')
        grouped[p.stat().st_size].append(p)
        examined+=1
        if progress and i%100==0: progress(f'Indexing {i}/{len(games)}',i,len(games))
    # Hash only files with identical sizes; avoid full 512GB scan unnecessarily.
    maybe=[p for x in grouped.values() if len(x)>1 for p in x]
    duplicates={}
    for i,p in enumerate(maybe,1):
        if cancel is not None and cancel.is_set():break
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(4*1024**2),b''):
                if cancel is not None and cancel.is_set():break
                h.update(chunk)
        duplicates.setdefault((p.stat().st_size,h.hexdigest()),[]).append(str(p.relative_to(workspace)))
        if progress: progress(f'Checking duplicates {i}/{len(maybe)}',i,len(maybe))
    groups=[items for items in duplicates.values() if len(items)>1]
    return {'inspected_game_files':examined,'possible_duplicates':groups,
            'broken_playlists_or_cues':broken,'cancelled':cancel is not None and cancel.is_set(),
            'note':'Duplicate groups are informational only. Multi-track games can intentionally contain matching files.'}
