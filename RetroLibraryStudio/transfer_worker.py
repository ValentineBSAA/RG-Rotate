"""Isolated verified-card transfer and preview helper.

The UI never waits on a potentially stalled NAS read. STOP is cooperative;
forced termination is offered in the GUI only with an explicit warning.
Completed files are published only after SHA-256 comparison. Interrupted
writes remain as .retro-part and are revalidated on retry.
"""
from __future__ import annotations

import json
import sys
import threading
import time
from dataclasses import asdict
from pathlib import Path

from sync_engine import make_plan, transfer_verified


def emit(kind: str, **values) -> None:
    print(json.dumps({'type': kind, **values}, separators=(',', ':'), ensure_ascii=True), flush=True)


def watch_stop(cancel: threading.Event) -> None:
    try:
        for line in sys.stdin:
            if line.strip().upper() == 'STOP':
                cancel.set()
                return
    except (OSError, UnicodeError):
        pass


def handle(request: dict, cancel: threading.Event) -> dict:
    mode = request.get('mode')
    if mode not in {'preview', 'copy'}:
        raise ValueError('Invalid transfer mode')
    source = Path(request['workspace'])
    destination = Path(request['target'])
    simulation = request.get('simulation', False)
    if not isinstance(simulation, bool):
        raise ValueError('Invalid simulation flag')
    if mode == 'preview':
        plan = make_plan(source, destination, simulation=simulation, cancel=cancel)
        return {'mode': mode, 'plan': asdict(plan)}
    # A deliberate re-plan takes place inside transfer_verified, so a stale
    # preview cannot bypass free-space, path-overlap or companion limits.
    last_sent = [0.0]
    def progress(stage, copied, total, filename, speed, eta):
        now = time.monotonic()
        if now - last_sent[0] >= .15 or copied >= total or stage.startswith(('Error', 'Files verified')):
            emit('progress', stage=stage, copied=copied, total=total,
                 filename=filename, speed=speed, eta=eta)
            last_sent[0] = now
    result = transfer_verified(source, destination, progress=progress,
                               simulation=simulation, cancel=cancel)
    return {'mode': mode, 'copy': result}


def main() -> int:
    cancel = threading.Event()
    try:
        line = sys.stdin.readline()
        if not line:
            raise ValueError('Transfer request missing')
        request = json.loads(line)
        if not isinstance(request, dict):
            raise ValueError('Transfer request must be an object')
        threading.Thread(target=watch_stop, args=(cancel,), daemon=True).start()
        emit('started', mode=request.get('mode'))
        data = handle(request, cancel)
        emit('result', data=data)
        return 0
    except Exception as exc:
        emit('error', message=f'{type(exc).__name__}: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
