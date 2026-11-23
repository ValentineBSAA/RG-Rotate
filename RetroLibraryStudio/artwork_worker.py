"""Disposable, cancellable artwork helper for NAS-backed virtual cards.

All remote catalog requests, NAS writes, and NAS image reads happen here,
never inside a Qt paint callback. Written covers use .retro-art-part and an
atomic rename. Stopping this process never modifies game/ROM files.
"""
from __future__ import annotations
import json
import sys
import threading
from pathlib import Path

from artwork_gallery import (process_batch, catalog_for, find_art_matches,
                             stage_online_cover, stage_local_cover, local_index,
                             store_local_index, game_key,
                             manual_search_results, preview_search_cover)


def emit(kind: str, **data):
    print(json.dumps({'type': kind, **data}, ensure_ascii=True, separators=(',', ':')), flush=True)


def listen(cancel):
    try:
        for line in sys.stdin:
            if line.strip().upper() == 'STOP':
                cancel.set()
                return
    except (OSError, UnicodeError):
        pass


def handle(request, cancel):
    workspace = Path(request['workspace'])
    mode = request['mode']
    if mode == 'batch':
        return process_batch(workspace, request.get('games', []),
                             progress=lambda name, n, total: emit('progress', message=name, current=n, total=total),
                             cancelled=cancel, max_items=80)
    system = request['system']
    stem = request['label']
    if cancel.is_set():
        return {'cancelled': True}
    if mode == 'search':
        query = str(request.get('query', '')).strip()[:160]
        if not query:
            return {'mode': 'search', 'query': query, 'results': [], 'catalog_size': 0,
                    'system': system, 'label': stem}
        catalog = catalog_for(system, workspace)
        return {'mode': 'search', 'system': system, 'label': stem, 'query': query,
                'results': manual_search_results(query, catalog),
                'catalog_size': len(catalog), 'cancelled': cancel.is_set()}
    if mode == 'preview':
        file = preview_search_cover(workspace, system, str(request['source_title']))
        return {'mode': 'preview', 'system': system, 'label': stem,
                'source_title': request['source_title'], 'preview_path': str(file)}
    if mode == 'suggest':
        catalog = catalog_for(system, workspace)
        match = find_art_matches(stem, catalog)
        return {'mode': 'suggest', 'system': system, 'label': stem,
                'suggestions': match['suggestions'], 'catalog_size': len(catalog),
                'cancelled': cancel.is_set()}
    if mode == 'pick':
        result = stage_online_cover(workspace, system, stem, request['source_title'],
                                    replace=bool(request.get('replace', False)))
    elif mode == 'local':
        result = stage_local_cover(workspace, system, stem, Path(request['source_path']),
                                   replace=bool(request.get('replace', False)))
    else:
        raise ValueError('Unsupported artwork operation')
    index = local_index(workspace)
    index[game_key(system, stem)] = {'system': system, 'label': stem, **result}
    store_local_index(workspace, index)
    return {'mode': mode, 'system': system, 'label': stem, **result}


def main():
    cancel = threading.Event()
    try:
        line = sys.stdin.readline()
        if not line:
            raise ValueError('Missing artwork request')
        request = json.loads(line)
        if not isinstance(request, dict):
            raise ValueError('Artwork request must be an object')
        threading.Thread(target=listen, args=(cancel,), daemon=True).start()
        emit('started', mode=request.get('mode'))
        result = handle(request, cancel)
        emit('result', data=result)
        return 0
    except Exception as exc:
        emit('error', message=f'{type(exc).__name__}: {exc}')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
