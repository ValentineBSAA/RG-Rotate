"""Explicit conversion of an existing PS1 library entry to CHD and recoverable tidy.

Only operates on files already inside <virtual card>/ROMs/psx. The CHD is
published/verified before any source file is moved. Cleanup is an explicit
policy: backup off-card, or delete *working copies inside the virtual card*.
External original archives are never touched. Runs inside import_worker.
"""
from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import Callable

from core import _cue_companions, within, safe_walk
from chd_convert import convert_cue, verify_existing_chd


def _raw_img_mode(image: Path) -> str:
    """Support standalone, unambiguous one-track raw PS1 CD images only.

    CloneCD CCD/IMG/SUB cannot be safely flattened to one track from IMG alone.
    Other unspecified IMG files may contain multiple tracks and need a CUE.
    """
    if not image.is_file() or image.is_symlink():
        raise ValueError('The IMG source is missing or is an unsafe link')
    if image.with_suffix('.ccd').exists() or image.with_suffix('.sub').exists():
        raise ValueError('CloneCD CCD/IMG/SUB detected. Its disc and subchannel metadata cannot be safely inferred from IMG alone. Supply a complete compatible CUE or convert the CloneCD set with a metadata-aware tool; originals were not touched.')
    size = image.stat().st_size
    if size <= 0:
        raise ValueError('The IMG is empty')
    if size % 2352 == 0:
        with image.open('rb') as stream:
            first = stream.read(16)
        # Standard PS1 data sector begins with 00 FF x10 00 and the CD mode.
        if first[:12] == b'\0' + b'\xff'*10 + b'\0' and first[15] in (1, 2):
            return f'MODE{first[15]}/2352'
    if size % 2048 == 0 and size > 32768:
        with image.open('rb') as stream:
            stream.seek(16*2048)
            pvd = stream.read(7)
        if len(pvd) == 7 and pvd[:1] == b'\x01' and pvd[1:6] == b'CD001':
            return 'MODE1/2048'
    raise ValueError('IMG format is ambiguous. No safe single-track mode detected. Keep IMG intact; provide the original CUE/CCD metadata or make a verified image from its disc before converting.')


def _detect_cue_for_img(image: Path) -> Path | None:
    matches = []
    for cue in image.parent.glob('*.cue'):
        companions = _cue_companions(cue)
        if image.resolve() in [x.resolve() for x in companions]:
            matches.append(cue)
    if len(matches) > 1:
        raise ValueError('More than one CUE references the IMG. Choose the correct CUE to convert.')
    return matches[0] if matches else None


def _referenced_elsewhere(cue: Path, companions: list[Path]) -> None:
    """Don't relocate shared tracks or break an M3U referencing a source CUE."""
    set_of_files = {p.resolve() for p in [cue, *companions]}
    for other in cue.parent.iterdir():
        if other.is_symlink():
            continue
        if other == cue or other.suffix.lower() not in ('.cue', '.m3u'):
            continue
        links = _cue_companions(other)
        if set_of_files.intersection(x.resolve() for x in links):
            raise ValueError(f'{other.name} still references one or more source files. Convert/update the entire playlist or disc set before tidying.')


def _recoverable_move(files: list[Path], workspace: Path, cancel, progress) -> Path:
    """Move files off-card (same NAS parent) with rollback on ordinary failures."""
    relative_dir = files[0].parent.relative_to(workspace)
    recovery_parent = workspace.parent / (workspace.name + ' - Conversion Backups') / relative_dir
    destination = recovery_parent / ('originals-' + uuid.uuid4().hex[:12])
    destination.mkdir(parents=True, exist_ok=False)
    moved = []
    try:
        for i, source in enumerate(files, 1):
            if cancel is not None and cancel.is_set():
                raise InterruptedError('Tidy stopped; originals will be restored')
            if not source.is_file() or source.is_symlink():
                raise ValueError(f'Source changed during conversion: {source.name}')
            dest = destination / source.name
            if dest.exists():
                raise FileExistsError(f'Backup collision: {dest}')
            source.rename(dest)
            moved.append((source, dest))
            if progress: progress(f'Backing up original track {i}/{len(files)}', 90 + round(9*i/len(files)),100)
    except Exception:
        for source, dest in reversed(moved):
            if not source.exists() and dest.exists():
                dest.rename(source)
        raise
    return destination


def _delete_verified_working_sources(files: list[Path], workspace: Path) -> tuple[int, int]:
    """Remove only source TRACKS inside the active virtual card after CHD verify.

    This cannot ever remove an external imported original NAS file or a
    recovery directory. The caller must require explicit user confirmation.
    Do not poll cancellation mid-deletion: the verified CHD stays complete.
    """
    psx = workspace / 'ROMs' / 'psx'
    for source in files:
        if source.is_symlink() or not source.is_file() or not within(source, psx):
            raise ValueError(f'Source is not a regular file inside the virtual PSX card: {source}')
    removed, total = 0, 0
    for source in files:
        size = source.stat().st_size
        source.unlink()
        removed += 1
        total += size
    return removed, total


def batch_sources(workspace: Path, cancel=None) -> list[Path]:
    """Select each complete PS1 disc once; never treat a referenced IMG as a second disc."""
    psx = Path(workspace) / 'ROMs' / 'psx'
    all_items = [p for p in safe_walk(psx, cancel=cancel)
                 if p.suffix.lower() in ('.cue', '.img')]
    cues = [p for p in all_items if p.suffix.lower() == '.cue']
    referenced = set()
    for cue in cues:
        if cancel is not None and cancel.is_set():
            return []
        try:
            referenced.update(p.resolve() for p in _cue_companions(cue))
        except (ValueError, OSError):
            # Leave incomplete CUE in the candidates to report a clear error.
            pass
    imgs = [p for p in all_items if p.suffix.lower() == '.img' and p.resolve() not in referenced]
    return sorted([*cues, *imgs], key=lambda p: str(p).casefold())


def batch_convert_ps1(workspace: Path, binary: Path, *, cleanup_mode='backup',
                      progress=None, cancel=None, converter=None, verifier=None) -> dict:
    """Convert verified discs one at a time, with one overall progress bar.

    Each source group is isolated. A failed disc is reported and left untouched;
    this task never walks outside the virtual-card PSX subtree for conversion.
    """
    if cleanup_mode not in ('backup', 'delete'):
        raise ValueError('Choose backup or delete mode explicitly')
    workspace = Path(workspace).resolve()
    result = {'converted': 0, 'skipped': 0, 'errors': [], 'cancelled': False,
              'total': 0, 'completed': 0, 'deleted_files': 0,
              'nas_bytes_reclaimed': 0, 'backups': [], 'games': [],
              'cleanup_mode': cleanup_mode}
    try:
        if progress: progress('Finding PS1 CUE/IMG files in your virtual card', 0, 0)
        candidates = batch_sources(workspace, cancel=cancel)
        result['total'] = len(candidates)
        if not candidates:
            if cancel is not None and cancel.is_set():
                result['cancelled'] = True
            return result
        if not Path(binary).is_file():
            result['errors'].append('CHDman is missing. Prepare CHDman in Apps before batch converting.')
            return result
        for i, source in enumerate(candidates):
            if cancel is not None and cancel.is_set():
                result['cancelled'] = True
                break
            def step(message, current, total):
                if progress:
                    percent = 0 if not total else round(100*(i + max(0,min(current,total))/total)/len(candidates))
                    progress(f'{i+1}/{len(candidates)} · {source.stem}: {message}',percent,100)
            item = convert_selected_game(source,workspace,binary,progress=step,cancel=cancel,
                                         converter=converter,verifier=verifier,
                                         cleanup_mode=cleanup_mode)
            result['games'].append({'source':str(source), 'output':item.get('output',''),
                                    'errors':item.get('errors', []), 'backup':item.get('backup','')})
            result['converted'] += item['converted']
            result['skipped'] += item['skipped']
            result['deleted_files'] += item.get('deleted_files',0)
            result['nas_bytes_reclaimed'] += item.get('freed_bytes',0)
            if item.get('backup'):
                result['backups'].append(item['backup'])
            for err in item['errors']:
                result['errors'].append(f'{source.name}: {err}')
            if item.get('cancelled'):
                result['cancelled'] = True
                break
            result['completed'] += 1
            if progress: progress(f'Processed {i+1} of {len(candidates)} PS1 discs',
                                  round(100*(i+1)/len(candidates)),100)
    except InterruptedError:
        result['cancelled'] = True
    except Exception as exc:
        result['errors'].append(str(exc))
    return result


def convert_selected_game(source: Path, workspace: Path, binary: Path, *, progress=None,
                          cancel=None, converter: Callable | None=None,
                          verifier: Callable | None=None, cleanup_mode='backup') -> dict:
    """Explicit one-disc conversion from the existing library; never overwrite.

    Returns errors instead of raising for the import worker UI. The backup is
    outside the virtual-card directory, so only the verified CHD is copied to
    the physical microSD. No permanent deletion occurs.
    """
    if Path(source).is_symlink():
        return {'converted':0, 'copied':0, 'skipped':0, 'playlists':0, 'artwork_games':[],
                'artwork_attempted':False, 'errors':['Linked or junction game sources cannot be optimized'],
                'cancelled':False, 'output':'', 'backup':'', 'deleted_files':0, 'freed_bytes':0}
    workspace, source, binary = Path(workspace).resolve(), Path(source).resolve(), Path(binary)
    if cleanup_mode not in ('backup', 'delete'):
        raise ValueError('Invalid cleanup policy')
    out = {'converted':0, 'copied':0, 'skipped':0, 'playlists':0,
           'artwork_games':[], 'artwork_attempted':False, 'errors':[],
           'cancelled':False, 'output':'', 'backup':''}
    try:
        psx = workspace / 'ROMs' / 'psx'
        if not within(source, psx) or source == psx or not source.is_file() or source.is_symlink():
            raise ValueError('Only existing regular PS1 files inside ROMs/psx can be optimized')
        if source.suffix.lower() not in ('.cue','.img'):
            raise ValueError('Choose a BIN/CUE game or single-track IMG')
        if not binary.is_file():
            raise FileNotFoundError('CHDman is missing. Install CHDman in Prepare Apps first.')
        if cancel is not None and cancel.is_set():
            out['cancelled'] = True; return out
        if progress: progress('Inspecting PS1 disc tracks',4,100)
        generated_cue = None
        cue = source
        try:
            if source.suffix.lower() == '.img':
                cue = _detect_cue_for_img(source)
                if cue is None:
                    mode = _raw_img_mode(source)
                    cue = source.with_suffix('.cue')
                    if cue.exists():
                        raise ValueError(f'{cue.name} exists but does not reference this IMG; choose a valid CUE')
                    # CUE lives next to the IMG briefly to keep FILE relative.
                    # Exclusive creation, and final cleanup even on cancellation.
                    with cue.open('x',encoding='utf-8',newline='\n') as f:
                        f.write(f'FILE "{source.name}" BINARY\n  TRACK 01 {mode}\n    INDEX 01 00:00:00\n')
                    generated_cue = cue
            if source.suffix.lower() == '.img' and (source.with_suffix('.ccd').exists() or source.with_suffix('.sub').exists()):
                raise ValueError('CloneCD sidecar metadata found. Do not convert IMG alone; preserve the complete CCD/IMG/SUB set.')
            companions = list(dict.fromkeys(_cue_companions(cue)))
            if not companions:
                raise ValueError('CUE contains no valid disc tracks')
            files = [cue, *companions]
            # Generated cue is temporary; never back it up.
            backups = [p for p in files if p != generated_cue]
            _referenced_elsewhere(cue, companions)
            final = source.parent / (cue.stem + '.chd')
            # A CUE may refer to nested files; refuse unsafe cleanup until
            # folder-preserving support exists. Never delete outside the game.
            for original in backups:
                if not within(original, psx) or original.parent.resolve() != source.parent.resolve() or original.is_symlink():
                    raise ValueError('Tracks span multiple directories or leave the PSX folder. Leave originals untouched and convert this disc manually.')
            if final.is_symlink():
                raise ValueError('Existing CHD points to an unsafe link')
            if final.exists():
                if progress: progress('Verifying existing CHD with CHDman',50,100)
                (verifier or verify_existing_chd)(final,binary,cancel=cancel)
                out['skipped'] += 1
            else:
                if progress: progress('Converting PS1 disc to CHD',20,100)
                result = (converter or convert_cue)(cue,source.parent,binary,cancel=cancel,
                            progress=lambda message, current, total:
                                progress(message,45 if not total else 20 + round(45*current/max(total,1)),100) if progress else None)
                if result.get('cancelled'):
                    out['cancelled']=True; return out
                if not result.get('verified') or not final.is_file() or final.stat().st_size <= 0:
                    raise ValueError('CHDman did not finish and verify a nonempty CHD. Originals remain.')
                out['converted'] += 1
            if progress: progress('Rechecking CHD on the NAS before cleaning',77,100)
            (verifier or verify_existing_chd)(final,binary,cancel=cancel)
            if cancel is not None and cancel.is_set():
                out['cancelled']=True; return out
            if cleanup_mode == 'delete':
                if progress: progress('Removing verified virtual-card tracks only',87,100)
                count, size = _delete_verified_working_sources(backups, workspace)
                out['deleted_files'] = count
                out['freed_bytes'] = size
                out['output'] = str(final)
                if progress: progress('CHD verified; virtual-card duplicates removed',100,100)
            else:
                if progress: progress('Moving original tracks into recovery backup',87,100)
                backup = _recoverable_move(backups,workspace,cancel,progress)
                out['output']=str(final); out['backup']=str(backup)
                if progress: progress('Verified CHD ready; PSX folder tidied',100,100)
        finally:
            if generated_cue is not None:
                generated_cue.unlink(missing_ok=True)
    except InterruptedError:
        out['cancelled']=True
    except Exception as exc:
        out['errors'].append(str(exc))
    return out
