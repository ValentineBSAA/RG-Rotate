"""Disposable, read-only inventory process for potentially blocked SMB shares.

A Qt window can terminate this child without corrupting or modifying game files.
The protocol is newline-delimited ASCII JSON on stdout. This module never writes
inside the selected virtual card. Run with --mode inventory or --mode count.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from core import inventory, safe_walk
from workspace_setup import count_workspace_files


def emit(kind: str, **fields) -> None:
    print(json.dumps({'type': kind, **fields}, ensure_ascii=True, separators=(',', ':')), flush=True)


def scan(mode: str, path: Path) -> int:
    try:
        if not path.is_dir():
            raise FileNotFoundError(f'Virtual card folder is unavailable: {path}')
        if mode == 'inventory':
            def report(message: str, current: int, total: int) -> None:
                emit('progress', message=message, current=current, total=total)
            from virtual_exfat import MODEL_CLUSTER_BYTES
            metrics = {'allocation_unit': MODEL_CLUSTER_BYTES}
            entries, used, count = inventory(path, progress=report, metrics=metrics)
            from disc_sets import cue_references
            disc_tracks = []
            for entry in entries:
                if entry.extension.lower() == '.cue':
                    try: disc_tracks.extend(cue_references(entry.path))
                    except OSError: pass  # Converter reports unavailable tracks in detail.
                # M3U CHDs are NOT discarded. The gallery needs their scan
                # entries to build one validated collection with N DISCS info.
                # library_presentation hides them only after membership checks.
            companion = sum(f.stat().st_size for f in safe_walk(path/'CompanionData'))
            emit('result', mode=mode, path=str(path), used=used, count=count,
                 companion=companion, disc_tracks=disc_tracks,
                 exfat_cluster_padding=int(metrics['cluster_padding']), entries=[
                     [str(e.path), e.label, e.system, e.size, e.extension, list(e.members)]
                     for e in entries])
        elif mode == 'apps':
            from tool_setup import tool_status, tools_root
            from batch_setup import readiness
            from apk_import import staged_apks
            emit('result', mode=mode, path=str(path), tools=tool_status(),
                 states=readiness(path, tools_root()), apks=staged_apks(path))
        elif mode == 'count':
            def report(message: str, current: int, total: int) -> None:
                emit('progress', message=message, current=current, total=total)
            outcome = count_workspace_files(path, progress=report)
            if outcome is None:
                raise InterruptedError('Card inspection cancelled')
            count, used = outcome
            emit('result', mode=mode, path=str(path), count=count, used=used)
        else:
            raise ValueError('Unsupported read-only operation')
        return 0
    except Exception as exc:
        emit('error', message=f'{type(exc).__name__}: {exc}')
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Retro Library Studio read-only scan')
    parser.add_argument('--mode', required=True, choices=('inventory', 'count', 'apps'))
    parser.add_argument('--path', required=True)
    ns = parser.parse_args(argv)
    return scan(ns.mode, Path(ns.path))


if __name__ == '__main__':
    raise SystemExit(main())
