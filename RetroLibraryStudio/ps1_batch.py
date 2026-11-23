"""Safe multi-game queue for PS1 Classics archives and EBOOT.PBP sources.

Each ZIP/7Z or standalone PSN package is a separate job, so one bad game
cannot cause the next archive's EBOOT to be mislabeled or mixed with its
neighbor. The existing guided_import handles one game at a time. Non-archive
CUE/BIN sets still process together to preserve the multi-disc collection.
This module never removes, rewrites or moves source games or Sony key files.
"""
from __future__ import annotations

from pathlib import Path

from ps1_pipeline import guided_import

_METRICS = ('copied', 'skipped', 'converted', 'playlists', 'playlists_updated')


def batch_guided_import(paths, workspace, fallback, binary, *, progress=None,
                        cancel=None, auto_artwork=True,
                        psxtract_binary=None, converter=None,
                        verify_existing=None, psn_extractor=None):
    unique = list(dict.fromkeys(Path(p) for p in paths))
    packages = [p for p in unique if p.suffix.casefold() in ('.zip', '.7z', '.pbp')]
    # An adjacent KEYS.BIN or DOCUMENT.DAT is a sidecar, not a separate
    # game job. guided_import([pbp]) finds these files in their own directory.
    package_dirs = {p.parent for p in packages if p.suffix.casefold() == '.pbp'}
    loose = [p for p in unique if p not in packages
             and not (p.parent in package_dirs
                      and p.name.casefold() in ('keys.bin', 'document.dat'))]
    jobs = [('package', p.name, [p]) for p in packages]
    if loose:
        jobs.append(('loose', f'{len(loose)} loose game/disc file(s)', loose))
    result = {'copied': 0, 'skipped': 0, 'converted': 0, 'playlists': 0,
              'playlists_updated': 0, 'errors': [], 'cancelled': False,
              'artwork_attempted': False, 'artwork': {}, 'artwork_games': [],
              'duplicate_notes': [], 'batch_items': [], 'batch_total': len(jobs),
              'batch_completed': 0, 'batch_skipped': 0, 'batch_needs_attention': 0}
    if not jobs:
        result['empty'] = True
        return result
    total = len(jobs)
    for number, (category, display, subset) in enumerate(jobs, 1):
        if cancel is not None and cancel.is_set():
            result['cancelled'] = True
            break
        if progress:
            progress(f'Batch {number}/{total} • {display} • preparing', number - 1, total)

        def child_progress(message, current, length):
            if progress:
                # The child stages are NOT percentages of the whole batch.
                # Keep the overall game count and show actual disc milestones.
                progress(f'Batch {number}/{total} • {display} • {message}', 0, 0)
        try:
            # Isolate this archive or EBOOT. In particular, never give the
            # archive's filename as the title hint for other PSN games.
            part = guided_import(subset, workspace, fallback, binary,
                                 progress=child_progress, cancel=cancel,
                                 auto_artwork=auto_artwork,
                                 psxtract_binary=psxtract_binary,
                                 converter=converter,
                                 verify_existing=verify_existing,
                                 psn_extractor=psn_extractor)
        except InterruptedError:
            result['cancelled'] = True
            break
        except Exception as exc:
            # Continue to the next archive while preserving all originals.
            reason = f'{display}: {type(exc).__name__}: {exc}'
            result['errors'].append(reason)
            result['batch_needs_attention'] += 1
            result['batch_items'].append({'name': display,
                                          'status': 'needs attention',
                                          'message': str(exc)[:350]})
            if progress:
                progress(f'Batch {number}/{total} • {display} • needs attention; next game is safe',
                         number, total)
            continue
        for metric in _METRICS:
            result[metric] += int(part.get(metric, 0))
        errors = [f'{display}: {str(e)}' for e in part.get('errors', [])]
        result['errors'].extend(errors)
        result['artwork_attempted'] |= bool(part.get('artwork_attempted'))
        result['artwork_games'].extend(part.get('artwork_games') or [])
        result['duplicate_notes'].extend(part.get('duplicate_notes') or [])
        for key, value in (part.get('artwork') or {}).items():
            if isinstance(value, int):
                result['artwork'][key] = result['artwork'].get(key, 0) + value
            elif key not in result['artwork']:
                result['artwork'][key] = value
        if part.get('cancelled'):
            result['cancelled'] = True
            state = 'stopped'
        elif errors:
            state = 'needs attention'
            result['batch_needs_attention'] += 1
        elif int(part.get('converted', 0)) or int(part.get('copied', 0)):
            state = 'imported'
            result['batch_completed'] += 1
        elif int(part.get('skipped', 0)):
            state = 'already present'
            result['batch_skipped'] += 1
        else:
            state = 'no changes'
            result['batch_skipped'] += 1
        result['batch_items'].append({
            'name': display, 'status': state,
            'discs': int(part.get('converted', 0)),
            'playlists': int(part.get('playlists', 0)),
            'message': (errors[0][:350] if errors else
                        (part.get('duplicate_notes') or [''])[0][:350])
        })
        if progress:
            progress(f'Batch {number}/{total} • {display} • {state}', number, total)
        if result['cancelled']:
            break
    if progress and not result['cancelled']:
        progress(f'Batch complete • {result["batch_completed"]} imported, '
                 f'{result["batch_skipped"]} already present/no changes, '
                 f'{result["batch_needs_attention"]} need attention',
                 total, total)
    return result
