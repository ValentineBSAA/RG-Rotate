"""Verified, non-destructive incremental folder-to-card copy with safe resume."""
from __future__ import annotations
import hashlib
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from core import FREE_RESERVE, COMPANION_BUDGET, CAPACITY, safe_walk, within, filesystem_name

BLOCK = 4 * 1024 * 1024
Progress = Callable[[str, int, int, str, float, float], None]


@dataclass
class SyncPlan:
    files: int
    bytes_total: int
    bytes_new: int
    bytes_already_present: int
    conflicts: list[str]
    current_target_free: int
    target_capacity: int
    is_simulation: bool = False
    existing_files: int = 0  # Size-only matches; SHA-256 verification happens during transfer.


def _hash(path: Path, cancel=None) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        while True:
            if cancel is not None and cancel.is_set():
                raise InterruptedError('Verification stopped; existing files are unchanged')
            block = f.read(BLOCK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _all_source_files(workspace: Path, cancel=None) -> list[Path]:
    result = sorted(safe_walk(workspace, cancel=cancel), key=lambda p: str(p).casefold())
    if cancel is not None and cancel.is_set():
        raise InterruptedError('Reading source file list cancelled')
    return result


def make_plan(workspace: Path, target: Path, free_reserve: int = FREE_RESERVE,
              companion_budget: int = COMPANION_BUDGET, simulation: bool = False,
              cancel=None) -> SyncPlan:
    if not workspace.is_dir() or not target.is_dir():
        raise ValueError('Workspace or destination folder does not exist')
    if within(workspace, target) or within(target, workspace):
        raise ValueError('Workspace and destination cannot contain one another')
    source_files = _all_source_files(workspace, cancel=cancel)
    if cancel is not None and cancel.is_set():
        raise InterruptedError('Transfer preview cancelled')
    usage = shutil.disk_usage(target)
    fs_name = filesystem_name(target) if not simulation else None
    byte_total, byte_new, existing, existing_files = 0, 0, 0, 0
    conflicts = []
    if fs_name and fs_name.upper() == 'FAT32' and any(p.stat().st_size >= 4_294_967_296 for p in source_files):
        conflicts.append('FAT32 cannot hold files of 4 GiB or more; use a compatible card filesystem (e.g., exFAT) after backing up')
    companion_used = 0
    for src in source_files:
        if cancel is not None and cancel.is_set():
            raise InterruptedError('Transfer preview cancelled')
        rel = src.relative_to(workspace)
        dest = target / rel
        # Reject destination parent junctions/symlinks that could escape the selected card.
        if not within(dest.parent, target):
            conflicts.append(f'{rel}: destination path resolves outside selected card')
            continue
        sz = src.stat().st_size
        byte_total += sz
        if rel.parts[0].casefold() == 'companiondata':
            companion_used += sz
        if dest.is_symlink() or (dest.exists() and not dest.is_file()):
            conflicts.append(f'{rel}: destination is not a regular file')
        elif dest.exists():
            if dest.stat().st_size != sz:
                conflicts.append(f'{rel}: existing file has different size')
            else:
                existing += sz  # Must hash-verify before skipping later.
                existing_files += 1
        else:
            # An interrupted partial file can resume; assume its size is usable only if verified.
            part = dest.with_name(dest.name + '.retro-part')
            part_sz = part.stat().st_size if part.is_file() and not part.is_symlink() else 0
            byte_new += max(0, sz - min(sz, part_sz))
    if companion_used > companion_budget:
        conflicts.append('CompanionData exceeds its dedicated storage budget')
    # The 512 GB simulation includes both companion files and regular files.
    if not simulation and byte_total + max(0, companion_budget - companion_used) + free_reserve > CAPACITY:
        conflicts.append('Virtual card exceeds 512 GB profile after protected budgets')
    if not simulation and byte_total + max(0, companion_budget - companion_used) + free_reserve > usage.total:
        conflicts.append('Real microSD formatted capacity is too small for staged files and both protected budgets')
    if not simulation and byte_new + free_reserve > usage.free:
        conflicts.append('Real microSD does not have sufficient free space for new transfer data plus 8 GiB protected reserve')
    return SyncPlan(len(source_files), byte_total, byte_new, existing, conflicts,
                    usage.free, usage.total, simulation, existing_files)


def _copy_verified(src: Path, dest: Path, report: Callable[[int], None], cancel=None,
                   on_verify=None) -> tuple[str, int]:
    if src.is_symlink() or not src.is_file() or dest.is_symlink():
        raise ValueError('Symlinks are not supported')
    initial = src.stat()
    length = initial.st_size
    if dest.exists():
        if not dest.is_file():
            raise FileExistsError(f'Not a regular destination: {dest}')
        if dest.stat().st_size == length:
            if on_verify: on_verify()
            same = _hash(src, cancel) == _hash(dest, cancel)
        else:
            same = False
        if same:
            report(length)
            return 'unchanged', 0
        raise FileExistsError(f'Conflicting destination file (kept unchanged): {dest}')
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + '.retro-part')
    if part.is_symlink() or (part.exists() and not part.is_file()):
        raise ValueError(f'Unsafe partial destination: {part}')
    existing = part.stat().st_size if part.exists() else 0
    if existing > length:
        raise ValueError(f'Oversized interrupted transfer: {part}')
    digest = hashlib.sha256()
    # Verify every already-copied byte against the corresponding source bytes.
    if existing:
        with src.open('rb') as a, part.open('rb') as b:
            left = existing
            while left:
                if cancel is not None and cancel.is_set():
                    raise InterruptedError('Transfer paused; partial file retained for safe resume')
                n = min(left, BLOCK)
                ab, bb = a.read(n), b.read(n)
                if ab != bb or len(ab) != n:
                    raise ValueError(f'Interrupted file differs from source: {part}')
                digest.update(ab)
                left -= n
        report(existing)
    copied_new = 0
    try:
        with src.open('rb') as inp, part.open('ab' if existing else 'xb') as out:
            inp.seek(existing)
            while True:
                if cancel is not None and cancel.is_set():
                    raise InterruptedError('Transfer paused; partial file retained for safe resume')
                block = inp.read(BLOCK)
                if not block:
                    break
                out.write(block)
                digest.update(block)
                copied_new += len(block)
                report(len(block))
            out.flush()
            os.fsync(out.fileno())
        later = src.stat()
        if later.st_size != initial.st_size or later.st_mtime_ns != initial.st_mtime_ns:
            raise RuntimeError(f'Source changed during transfer: {src.name}')
        if on_verify: on_verify()
        if _hash(part, cancel) != digest.hexdigest():
            raise IOError(f'SHA-256 verification failed for {src.name}; partial retained')
        if dest.exists():
            raise FileExistsError(f'Another process created destination: {dest}')
        part.rename(dest)
        return 'copied', copied_new
    except Exception:
        # Do not delete partials: next run verifies the prefix before resuming.
        raise


def transfer_verified(workspace: Path, target: Path, progress: Progress | None = None,
                      cancel=None, reserve_bytes: int = FREE_RESERVE,
                      companion_budget: int = COMPANION_BUDGET,
                      simulation: bool = False) -> dict:
    """Requires caller-confirmed destination. Never deletes or overwrites unrelated files."""
    try:
        plan = make_plan(workspace, target, reserve_bytes, companion_budget, simulation, cancel=cancel)
    except InterruptedError:
        return {'copied': 0, 'skipped': 0, 'verified': 0, 'files': 0,
                'errors': [], 'cancelled': True, 'bytes_total': 0}
    if plan.conflicts:
        return {'copied': 0, 'skipped': 0, 'errors': plan.conflicts, 'cancelled': False, 'verified': 0}
    if plan.files == 0:
        raise ValueError('The virtual card contains no files')
    if not simulation and plan.current_target_free - plan.bytes_new < reserve_bytes:
        raise OSError('Not enough physical free space for transfer plus 8 GiB safety reserve')
    if not simulation and plan.current_target_free < reserve_bytes:
        raise OSError('The destination already violates the protected free-space reserve')
    processed = 0
    copied = skipped = verified = 0
    errors = []
    start = time.monotonic()
    try:
        source_files = _all_source_files(workspace, cancel=cancel)
    except InterruptedError:
        return {'copied': 0, 'skipped': 0, 'verified': 0, 'files': plan.files,
                'errors': [], 'cancelled': True, 'bytes_total': plan.bytes_total}
    for index, src in enumerate(source_files, 1):
        if cancel is not None and cancel.is_set():
            break
        rel = src.relative_to(workspace)
        dest = target / rel
        name = f'{index}/{plan.files}  {rel}'
        def report(count: int) -> None:
            nonlocal processed
            processed += count
            elapsed = max(.001, time.monotonic() - start)
            speed = processed / elapsed
            eta = max(0., (plan.bytes_total - processed) / speed) if speed else 0.
            if progress:
                progress('Transferring and verifying', processed, plan.bytes_total, name, speed, eta)
        try:
            def show_verify() -> None:
                if progress:
                    progress('Verifying SHA-256', processed, plan.bytes_total, name, 0., 0.)
            result, _ = _copy_verified(src, dest, report, cancel, on_verify=show_verify)
            if result == 'copied':
                copied += 1
            else:
                skipped += 1
            verified += 1
            if progress:
                elapsed = max(.001, time.monotonic() - start)
                progress(f'Files verified: {verified}/{plan.files}', processed, plan.bytes_total,
                         name, processed / elapsed, max(0., (plan.bytes_total - processed) / max(1., processed / elapsed)))
        except InterruptedError:
            break
        except Exception as exc:
            errors.append(f'{rel}: {exc}')
            # Charge remaining failed bytes to progress so file accounting still terminates.
            remaining = src.stat().st_size
            # No success is reported for this file.
            if progress:
                progress('Error: ' + str(rel), processed, plan.bytes_total, name, 0, 0)
    return {'copied': copied, 'skipped': skipped, 'verified': verified, 'files': plan.files,
            'errors': errors, 'cancelled': cancel is not None and cancel.is_set(),
            'elapsed': round(time.monotonic()-start, 2), 'bytes_total': plan.bytes_total}
