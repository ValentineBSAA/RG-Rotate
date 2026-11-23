"""Disposable IMPORT worker for slow SMB-backed virtual card directories.

Protocol: the first stdin line is a JSON request (mode=files/folder); subsequent
lines may contain STOP. stdout is newline-delimited JSON progress/result/error.
The worker NEVER removes source games. Imported games are published by core's
atomic .retro-part -> final rename, so a killed worker cannot publish a partially
written game as complete. A hard kill can leave a .retro-part to review.
"""
from __future__ import annotations

import json
import os
import sys
import threading
from pathlib import Path

from core import SUPPORTED, safe_walk
from library_import import import_grouped


def emit(kind: str, **values) -> None:
    print(json.dumps({'type': kind, **values}, ensure_ascii=True, separators=(',', ':')), flush=True)


def _listen_for_stop(cancel: threading.Event) -> None:
    try:
        for line in sys.stdin:
            if line.strip().upper() == 'STOP':
                cancel.set()
                return
    except (OSError, UnicodeError):
        return


def handle(request: dict, cancel: threading.Event) -> dict:
    mode = request.get('mode')
    if mode in ('inspect_discs', 'convert_discs', 'playlist', 'setup', 'optimize_existing_ps1', 'convert_selected_ps1', 'batch_convert_ps1'):
        def progress(message, current, total):
            emit('progress', message=str(message), current=int(current), total=int(total))
        if mode == 'batch_convert_ps1':
            from ps1_organizer import batch_convert_ps1
            return batch_convert_ps1(Path(request['workspace']), Path(request['binary']),
                  progress=progress, cancel=cancel, cleanup_mode=request.get('cleanup_mode','backup'))
        if mode == 'convert_selected_ps1':
            from ps1_organizer import convert_selected_game
            return convert_selected_game(Path(request['source']), Path(request['workspace']),
                Path(request['binary']), progress=progress, cancel=cancel)
        if mode == 'optimize_existing_ps1':
            from ps1_pipeline import guided_import
            workspace = Path(request['workspace'])
            cues = [p for p in safe_walk(workspace / 'ROMs' / 'psx', cancel=cancel)
                    if p.suffix.lower() == '.cue']
            return guided_import(cues, workspace, 'PS1', Path(request['binary']),
                                 progress=progress, cancel=cancel,
                                 auto_artwork=bool(request.get('auto_artwork', True)),
                                 optimize_existing=True)
        if mode == 'inspect_discs':
            from disc_sets import inspect_cue
            return {'results': [inspect_cue(Path(p), cancel=cancel) for p in request['paths']]}
        if mode == 'convert_discs':
            from disc_sets import convert_discs
            return convert_discs(request['paths'], request['output_dir'], request['binary'], progress=progress, cancel=cancel)
        if mode == 'playlist':
            from disc_sets import write_playlist
            return {'playlist': write_playlist([Path(p) for p in request['paths']], Path(request['destination']))}
        from batch_setup import prepare_batch
        return prepare_batch(request['names'], Path(request['workspace']), Path(request['host_tools']),
                             progress=progress, cancel=cancel,
                             on_state=lambda name, state: emit('app_state', name=name, state=state))
    workspace = Path(request['workspace'])
    if mode == 'apks':
        from apk_import import stage_local_apks
        def apk_progress(message: str, current: int, total: int) -> None:
            emit('progress', message=str(message), current=int(current), total=int(total))
        return stage_local_apks([Path(p) for p in request['paths']], workspace,
                                progress=apk_progress, cancel=cancel)
    fallback = str(request['fallback'])
    if mode == 'files':
        files = [Path(p) for p in request['paths']]
    elif mode in ('folder', 'batch_psn_folder'):
        folder = Path(request['folder'])
        # Check overlap inside worker, not the GUI. Avoid blocking on NAS path.resolve().
        src_norm = os.path.normcase(os.path.abspath(str(folder)))
        dst_norm = os.path.normcase(os.path.abspath(str(workspace)))
        try:
            common = os.path.commonpath([src_norm, dst_norm])
        except ValueError:
            common = ''
        if common in (src_norm, dst_norm):
            raise ValueError('Original games folder must not overlap the virtual card')
        # Keep the potentially unresponsive SMB folder enumeration inside the child.
        files = [p for p in safe_walk(folder, cancel=cancel)
                 if (p.suffix.lower() in ('.zip', '.7z', '.pbp') if mode == 'batch_psn_folder'
                     else p.suffix.lower() in SUPPORTED)]
        if not files:
            return {'copied': 0, 'skipped': 0, 'errors': [], 'empty': not cancel.is_set(),
                    'cancelled': cancel.is_set()}
    else:
        raise ValueError('Invalid import request')

    if cancel.is_set():
        return {'copied': 0, 'skipped': 0, 'errors': [], 'cancelled': True}

    def progress(message: str, current: int, total: int) -> None:
        emit('progress', message=str(message), current=int(current), total=int(total))

    if request.get('auto_ps1_chd', False):
        from ps1_pipeline import guided_import
        archives_or_pbps = [p for p in files if p.suffix.lower() in ('.zip', '.7z', '.pbp')]
        # Run a separate game job for each archive/PBP when batch is requested
        # or there are multiple package inputs. Direct CUE/BIN files remain a
        # single set so their existing M3U collection semantics don't change.
        if mode == 'batch_psn_folder' or len(archives_or_pbps) > 1:
            from ps1_batch import batch_guided_import
            return batch_guided_import(files, workspace, fallback, Path(request['binary']),
                                       progress=progress, cancel=cancel,
                                       auto_artwork=bool(request.get('auto_artwork', True)),
                                       psxtract_binary=request.get('psxtract_binary'))
        return guided_import(files, workspace, fallback, Path(request['binary']),
                             progress=progress, cancel=cancel,
                             auto_artwork=bool(request.get('auto_artwork', True)),
                             psxtract_binary=request.get('psxtract_binary'))
    return import_grouped(files, workspace, fallback, progress=progress, cancel=cancel)


def main() -> int:
    cancel = threading.Event()
    try:
        request_line = sys.stdin.readline()
        if not request_line:
            raise ValueError('No import request received')
        request = json.loads(request_line)
        if not isinstance(request, dict):
            raise ValueError('Import request must be an object')
        if request.get('mode') == 'convert_discs' or request.get('auto_ps1_chd') or request.get('mode') in ('optimize_existing_ps1', 'convert_selected_ps1', 'batch_convert_ps1'):
            from worker_lifetime import contain_children
            contain_children()
        watcher = threading.Thread(target=_listen_for_stop, args=(cancel,), daemon=True)
        watcher.start()
        emit('started', mode=request.get('mode', 'unknown'))
        result = handle(request, cancel)
        emit('result', data=result)
        return 0
    except Exception as exc:
        emit('error', message=f'{type(exc).__name__}: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
