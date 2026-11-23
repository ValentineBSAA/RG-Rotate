"""Guided PS1 import: inspect -> CHDman createcd -> verify -> stage -> M3U -> cover.

Originals are never moved/removed. This module runs in disposable import_worker,
not in the GUI process. It does not automatically delete already-staged BIN/CUE
files when optimizing older collections: that requires a separate, explicit action.
"""
from __future__ import annotations

import re
import tempfile
import shutil
import zipfile
from contextlib import ExitStack
from pathlib import Path
from typing import Callable

from core import CAPACITY, FREE_RESERVE, COMPANION_BUDGET, copy_atomic, safe_walk, same_file, inventory
from library_import import infer_system, import_grouped
from disc_sets import inspect_cue, write_playlist
from ps1_collections import (disc_identity as collection_identity, folder_title,
                             disc_numbers_are_contiguous, publish_playlist)

_DISC_TAG = re.compile(r'\s*\((?:disc|disk|cd)\s*([0-9]{1,2})\)|\s*\[(?:disc|disk|cd)\s*([0-9]{1,2})\]', re.I)
_RE2_PERSON = re.compile(r'\s*\((?:Claire|Leon)\)(?=\s*$)', re.I)


def disc_identity(stem: str) -> tuple[str, int | None]:
    """Compatibility API for callers; shared identity lives in ps1_collections."""
    return collection_identity(stem)


def _unique_cues(paths: list[Path]) -> list[Path]:
    """If an M3U was selected, follow its safely resolved CUE references."""
    from core import _cue_companions
    cues: list[Path] = []
    for p in dict.fromkeys(Path(x) for x in paths):
        if p.suffix.lower() == '.cue':
            cues.append(p)
        elif p.suffix.lower() == '.m3u':
            cues.extend(ref for ref in _cue_companions(p) if ref.suffix.lower() == '.cue')
    return list(dict.fromkeys(cues))


def _source_checks(cues: list[Path], cancel) -> None:
    if not cues:
        return
    for cue in cues:
        if cancel is not None and cancel.is_set():
            raise InterruptedError('PS1 preparation stopped')
        check = inspect_cue(cue, cancel=cancel)
        if check['errors']:
            raise ValueError(f'{cue.name}: ' + '; '.join(check['errors']))


def stage_ps1_cues(cues: list[Path], workspace: Path, binary: Path, *, progress=None,
                   cancel=None, converter=None, verify_existing=None, optimize_existing=False) -> dict:
    """Convert every input disc, verify, then publish only a verified CHD.

    Existing virtual-card BIN/CUE sets are preserved (and still occupy card space).
    Newly imported CUE/BIN sets stay only at their original source location.
    """
    from chd_convert import convert_cue
    converter = converter or convert_cue
    if verify_existing is None:
        from chd_convert import verify_existing_chd
        verify_existing = verify_existing_chd
    cues = list(dict.fromkeys(Path(x) for x in cues))
    out = {'converted': 0, 'playlists': 0, 'playlists_updated': 0, 'copied': 0, 'skipped': 0,
           'errors': [], 'artwork_games': [], 'cancelled': False}
    if not cues:
        return out
    if not binary.is_file():
        out['errors'].append('CHDman is not installed. Open Install Apps → Prepare CHDman, then retry. No disc was imported.')
        return out
    grouped: dict[str, list[tuple[Path, int | None]]] = {}
    for cue in cues:
        base, disc_num = disc_identity(cue.stem)
        grouped.setdefault(base.casefold(), []).append((cue, disc_num))
    used_bytes = None  # Read virtual-card usage only if a new CHD must be published.
    disc_index = 0
    disc_count = len(cues)
    for name, items in grouped.items():
        items.sort(key=lambda row: (row[1] is None, row[1] or 0, row[0].name.casefold()))
        base = disc_identity(items[0][0].stem)[0]
        disc_numbers = [number for _, number in items if number is not None]
        if len(disc_numbers) != len(set(disc_numbers)):
            out['errors'].append(f'{base}: More than one source CUE claims the same disc number. Review names; no disc was automatically merged.')
            continue
        try:
            safe_base = folder_title(base) if any(n is not None for _, n in items) else base
        except ValueError as exc:
            out['errors'].append(f'{base}: {exc}')
            continue
        # An already-imported CUE is optimized in its existing folder; never
        # silently reorganize or delete that user's imported originals.
        if optimize_existing:
            destination = items[0][0].parent
        else:
            destination = Path(workspace) / 'ROMs' / 'psx' / safe_base if any(n is not None for _, n in items) else Path(workspace) / 'ROMs' / 'psx'
        staged: list[tuple[int, Path]] = []
        for index, (cue, number) in enumerate(items, 1):
            disc_index += 1
            def disc_percent(stage):
                return round(100 * (disc_index - 1 + stage / 100) / max(1, disc_count))
            if cancel is not None and cancel.is_set():
                out['cancelled'] = True
                return out
            if progress:
                progress(f'Inspecting {cue.name} ({disc_index}/{disc_count})', disc_percent(5), 100)
            check = inspect_cue(cue, cancel=cancel)
            if check['errors']:
                out['errors'].append(f'{cue.name}: ' + '; '.join(check['errors']))
                continue
            final = destination / (cue.stem + '.chd')
            try:
                if final.exists():
                    # Only already-produced images are reused; do not overwrite.
                    # The final real-device verification happens when launching.
                    if not final.is_file() or final.stat().st_size == 0:
                        raise ValueError(f'Conflicting CHD at {final}')
                    verify_existing(final, binary, cancel=cancel)
                    out['skipped'] += 1
                    staged.append((number or index, final))
                    continue
                with tempfile.TemporaryDirectory(prefix='retro-ps1-chd-') as d:
                    tmp = Path(d)
                    if progress:
                        progress(f'Converting {cue.stem} to CHD (this can take a while)', 0, 0)
                    result = converter(cue, tmp, binary, cancel=cancel,
                        progress=lambda desc, current, total: progress(
                            f'Converting {cue.name}: {desc}', 0, 0) if 'Converting' in desc else progress(
                            f'{cue.name}: {desc}', disc_percent(60), 100) if progress else None)
                    if result.get('cancelled'):
                        out['cancelled'] = True
                        return out
                    if not result.get('verified'):
                        raise RuntimeError('CHDman did not verify the output')
                    produced = Path(result['output'])
                    if progress:
                        progress(f'Copying verified {produced.name} to the virtual card', disc_percent(75), 100)
                    if used_bytes is None:
                        _, used_bytes, _ = inventory(Path(workspace), cancel=cancel)
                    if used_bytes + produced.stat().st_size + COMPANION_BUDGET + FREE_RESERVE > CAPACITY:
                        raise OSError('PS1 CHD would exceed the protected virtual-card capacity')
                    result_state = copy_atomic(produced, final, cancel=cancel)
                    if result_state == 'copied':
                        used_bytes += produced.stat().st_size
                    if not same_file(produced, final, cancel=cancel):
                        # Do not silently accept an incomplete/corrupted destination.
                        raise RuntimeError(f'CHD copy hash check failed: {final.name}')
                    out['copied' if result_state == 'copied' else 'skipped'] += 1
                out['converted'] += 1
                staged.append((number or index, final))
                if progress:
                    progress(f'Verified {final.name}', disc_percent(100), 100)
            except InterruptedError:
                out['cancelled'] = True
                return out
            except Exception as exc:
                out['errors'].append(f'{cue.name}: {exc}')
        # Construct an M3U only when at least two verified/staged discs exist.
        # A single CHD is complete on its own and needs no playlist.
        existing = []
        if not optimize_existing and destination.is_dir():
            for f in destination.glob('*.chd'):
                fbase, disc_num = disc_identity(f.stem)
                if disc_num is not None and fbase.casefold() == base.casefold() and f not in [p for _, p in staged]:
                    try:
                        verify_existing(f, binary, cancel=cancel)
                        existing.append((disc_num, f))
                    except InterruptedError:
                        out['cancelled'] = True
                        return out
                    except Exception as exc:
                        out['errors'].append(f'{f.name}: could not reuse existing disc: {exc}')
        staged += existing
        if len(staged) >= 2:
            playlist = destination / f'{base}.m3u'
            ordered_pairs = sorted(staged, key=lambda r: r[0])
            numbers = [number for number, _ in ordered_pairs]
            if not disc_numbers_are_contiguous(numbers):
                missing = [n for n in range(1, max(numbers) + 1) if n not in numbers]
                out['errors'].append(f'{base}: disc numbers are duplicated or gaps remain ({missing}). Existing CHDs are safe; no incomplete playlist was published.')
                continue
            ordered = [p for _, p in ordered_pairs]
            try:
                state = publish_playlist(ordered, playlist, cancel=cancel)
                if state == 'created': out['playlists'] += 1
                if state == 'updated': out['playlists_updated'] += 1
                out['artwork_games'].append({'system': 'PS1', 'label': base})
            except InterruptedError:
                out['cancelled'] = True
                return out
            except Exception as exc:
                out['errors'].append(f'{base}: M3U could not be prepared: {exc}')
        elif staged:
            label = base if any(n is not None for _, n in items) else staged[0][1].stem
            out['artwork_games'].append({'system': 'PS1', 'label': label})
    return out



def stage_ps1_chds(chds: list[Path], workspace: Path, binary: Path, *, progress=None,
                   cancel=None, verify_existing=None) -> dict:
    """Verify existing disc-numbered CHDs and group without recompression.

    Verify source and in-card CHD before publishing a collection M3U.
    """
    if verify_existing is None:
        from chd_convert import verify_existing_chd
        verify_existing = verify_existing_chd
    out = {'converted': 0, 'playlists': 0, 'playlists_updated': 0,
           'copied': 0, 'skipped': 0, 'errors': [], 'artwork_games': [], 'cancelled': False}
    if not chds:
        return out
    if not binary.is_file():
        out['errors'].append('CHDman is required to verify existing CHDs before adding them to a multi-disc playlist.')
        return out
    groups = {}
    for image in dict.fromkeys(Path(x) for x in chds):
        base, number = disc_identity(image.stem)
        if number is None:
            continue
        groups.setdefault(base.casefold(), []).append((image, number))
    occupied = None
    for parts in groups.values():
        base = disc_identity(parts[0][0].stem)[0]
        numbers = [num for _, num in parts]
        if len(numbers) != len(set(numbers)):
            out['errors'].append(f'{base}: duplicate disc number; no files combined')
            continue
        try:
            dest = Path(workspace) / 'ROMs' / 'psx' / folder_title(base)
        except ValueError as exc:
            out['errors'].append(f'{base}: {exc}')
            continue
        staged = []
        for image, number in sorted(parts, key=lambda item: item[1]):
            if cancel is not None and cancel.is_set():
                out['cancelled'] = True
                return out
            try:
                if progress: progress(f'Verifying existing CHD: {image.name}', 0, 0)
                verify_existing(image, binary, cancel=cancel)
                target = dest / image.name
                if occupied is None:
                    _, occupied, _ = inventory(Path(workspace), cancel=cancel)
                if not target.exists() and occupied + image.stat().st_size + COMPANION_BUDGET + FREE_RESERVE > CAPACITY:
                    raise OSError('CHD would exceed protected virtual-card capacity')
                state = copy_atomic(image, target, cancel=cancel)
                if not same_file(image, target, cancel=cancel):
                    raise RuntimeError('CHD transfer SHA-256 mismatch')
                verify_existing(target, binary, cancel=cancel)
                if state == 'copied':
                    out['copied'] += 1
                    occupied += image.stat().st_size
                else:
                    out['skipped'] += 1
                staged.append((number, target))
            except InterruptedError:
                out['cancelled'] = True
                return out
            except Exception as exc:
                out['errors'].append(f'{image.name}: {exc}')
        if dest.is_dir():
            already = {f for _, f in staged}
            for old in dest.glob('*.chd'):
                other_base, number = disc_identity(old.stem)
                if number is None or other_base.casefold() != base.casefold() or old in already:
                    continue
                try:
                    verify_existing(old, binary, cancel=cancel)
                    staged.append((number, old))
                except InterruptedError:
                    out['cancelled'] = True
                    return out
                except Exception as exc:
                    out['errors'].append(f'{old.name}: {exc}')
        if len(staged) >= 2:
            ordered_pairs = sorted(staged)
            nums = [num for num, _ in ordered_pairs]
            if not disc_numbers_are_contiguous(nums):
                out['errors'].append(f'{base}: incomplete/duplicate disc numbering; no playlist updated')
                continue
            try:
                state = publish_playlist([f for _, f in ordered_pairs], dest / (base + '.m3u'), cancel=cancel)
                if state == 'created': out['playlists'] += 1
                if state == 'updated': out['playlists_updated'] += 1
                out['artwork_games'].append({'system':'PS1', 'label':base})
            except InterruptedError:
                out['cancelled'] = True
                return out
            except Exception as exc:
                out['errors'].append(f'{base}: {exc}')
        elif staged:
            out['artwork_games'].append({'system':'PS1', 'label':base})
    return out


def guided_import(paths: list[Path], workspace: Path, fallback: str, binary: Path, *,
                  progress=None, cancel=None, auto_artwork=True, converter=None, verify_existing=None,
                  optimize_existing=False, psxtract_binary=None, psn_extractor=None,
                  psn_title_hint=None) -> dict:
    """One coherent progress-driven task for copy, CHD, M3U, and artwork."""
    paths = list(dict.fromkeys(Path(p) for p in paths))
    archives = [p for p in paths if p.suffix.lower() in ('.zip', '.7z')]
    if archives:
        # Extract to disposable LOCAL storage, not on the NAS. The original
        # archive remains intact. CUE companions are then processed normally.
        from core import sanitize_archive_member, verify_zip, verify_7z, safe_walk, MAX_ARCHIVE_BYTES, ARCHIVE_EXT
        with ExitStack() as stack:
            unpacked = []
            for index, archive in enumerate(archives, 1):
                if cancel is not None and cancel.is_set():
                    return {'copied':0, 'skipped':0, 'converted':0, 'playlists':0,
                            'errors':[], 'cancelled':True, 'artwork_attempted':False, 'artwork':{}}
                if progress:
                    progress(f'Extracting {archive.name} ({index}/{len(archives)})', 0, 0)
                tempdir = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='rgl-archive-')))
                if archive.suffix.lower() == '.zip':
                    with zipfile.ZipFile(archive) as z:
                        required = verify_zip(z)
                        if shutil.disk_usage(tempdir).free < required:
                            raise OSError('Not enough Windows temporary storage to unpack archive')
                        for member in z.infolist():
                            if cancel is not None and cancel.is_set():
                                raise InterruptedError('Archive extraction stopped')
                            target = tempdir / sanitize_archive_member(member.filename)
                            if member.is_dir():
                                target.mkdir(parents=True, exist_ok=True)
                            else:
                                target.parent.mkdir(parents=True, exist_ok=True)
                                with z.open(member) as inp, target.open('xb') as dst:
                                    while True:
                                        if cancel is not None and cancel.is_set():
                                            raise InterruptedError('Archive extraction stopped')
                                        block = inp.read(1024*1024)
                                        if not block: break
                                        dst.write(block)
                else:
                    import py7zr
                    from importlib.metadata import version
                    from packaging.version import Version
                    if Version(version('py7zr')) < Version('1.1.3'):
                        raise RuntimeError('py7zr 1.1.3 or newer is required for safe 7Z extraction')
                    with py7zr.SevenZipFile(archive, mode='r', max_extract_size=MAX_ARCHIVE_BYTES) as z:
                        required = verify_7z(z)
                        if shutil.disk_usage(tempdir).free < required:
                            raise OSError('Not enough Windows temporary storage to unpack 7Z archive')
                        z.extractall(path=tempdir)
                extracted = list(safe_walk(tempdir, cancel=cancel))
                if any(p.suffix.lower() in ARCHIVE_EXT for p in extracted):
                    raise ValueError('Nested archives must be unpacked separately')
                unpacked.extend(p for p in extracted if p.suffix.lower() in (
                    '.cue','.bin','.m3u','.chd','.img','.iso','.cso','.pbp','.gba','.gb','.gbc',
                    '.nes','.sfc','.smc','.md','.gen','.nds','.n64','.z64','.v64','.gdi','.cdi')
                    or p.name.casefold() == 'document.dat')
            if not unpacked:
                raise ValueError('No recognized game files found inside the archive')
            # An archive containing an NPEF... directory otherwise loses the
            # actual game title and becomes an anonymous game-code folder.
            # An archive can contain several different PSN EBOOT games.
            # Never force the single archive filename on every game in it.
            from ps1_psn import is_ps1_classic, meaningful_title
            eboots = [p for p in unpacked if p.suffix.lower() == '.pbp'
                      and is_ps1_classic(p)]
            # Generic archive wrappers ('PS1.7z') must not become a title.
            # The containing folder can supply a legitimate title; if neither
            # is meaningful, package_title reads the PBP's PARAM.SFO instead.
            title_hint = psn_title_hint
            if not title_hint and len(archives) == 1 and len(eboots) == 1:
                title_hint = (meaningful_title(archives[0].stem) or
                              meaningful_title(archives[0].parent.name))
            return guided_import([p for p in paths if p not in archives] + unpacked,
                                workspace, fallback, binary, progress=progress,
                                cancel=cancel, auto_artwork=auto_artwork,
                                converter=converter, verify_existing=verify_existing,
                                optimize_existing=optimize_existing,
                                psxtract_binary=psxtract_binary,
                                psn_extractor=psn_extractor, psn_title_hint=title_hint)
    out = {'copied': 0, 'skipped': 0, 'converted': 0, 'playlists': 0, 'playlists_updated': 0,
           'errors': [], 'cancelled': False, 'artwork_attempted': False,
           'artwork': {}, 'artwork_games': [], 'duplicate_notes': []}
    if cancel is not None and cancel.is_set():
        out['cancelled'] = True
        return out
    highest = [0]
    def phase(msg, current, total):
        if total > 0:
            highest[0] = max(highest[0], current)
            current = highest[0]
        if progress: progress(msg, current, total)
    phase('Preparing selected games and checking disc companions', 3, 100)
    # PSN PSOne Classics EBOOT is a PS1 container, not a native PSP ISO.
    # KEYS.BIN is a companion to the package, NEVER a separate PS1 disc.
    from ps1_psn import (is_ps1_classic, psn_companions, pbp_disc_signature,
                         package_title, extract_psn_with_helper, ordered_psn_cues)
    from ps1_duplicates import fingerprint_pbp, decide_repeat, record_import
    psn_files = [p for p in paths if p.suffix.lower() == '.pbp' and is_ps1_classic(p)]
    psn_consumed = set(psn_files)
    psn_related = set()
    for pbp in psn_files:
        doc, keys = psn_companions(pbp)
        psn_related.update(p for p in (doc, keys) if p is not None)
        try:
            title = package_title(pbp, psn_title_hint)
            out['collection_title'] = title
            phase(f'Checking for an existing PS1 collection: {title}', 0, 0)
            digest = fingerprint_pbp(pbp, cancel=cancel)
            decision, note = decide_repeat(workspace, title, digest)
            if decision == 'same':
                out['skipped'] += 1
                out['duplicate_notes'].append(note)
                phase(f'Already imported • {title} • one collection retained', 0, 0)
                continue
            if decision == 'review':
                out['skipped'] += 1
                out['duplicate_notes'].append(note)
                out['errors'].append(f'{title}: {note}')
                phase(f'Possible duplicate • {title} • kept existing files', 0, 0)
                continue
            with tempfile.TemporaryDirectory(prefix='rgl-psn-extract-') as temp:
                dest = Path(temp)
                extract = psn_extractor or extract_psn_with_helper
                helper = Path(psxtract_binary) if psxtract_binary else Path('psxtract.exe')
                if progress:
                    phase(f'Inspecting PS1 Classic {title}', 10, 100)
                extracted = extract(pbp, dest, helper, cancel=cancel, progress=phase)
                prepared = ordered_psn_cues(
                    extracted, title, multi_expected=pbp_disc_signature(pbp) == 'multi')
                converted = stage_ps1_cues(prepared, workspace, binary, progress=phase,
                                          cancel=cancel, converter=converter,
                                          verify_existing=verify_existing)
                # Only expose a finished collection folder as a successful
                # import; do not direct the user to an unverified partial.
                finished = (not converted['cancelled'] and not converted['errors']
                            and len(prepared) > 0
                            and (converted['copied'] > 0 or converted['skipped'] > 0))
                if finished:
                    out['collection_folder'] = str(Path(workspace) / 'ROMs' / 'psx' / title)
                if (finished and
                        ((len(prepared) == 1 and converted['converted'] == 1)
                         or (len(prepared) > 1 and
                             (converted['playlists'] == 1 or
                              converted['playlists_updated'] == 1)))):
                    # Create a receipt only for completed verified singles or
                    # a complete CHD/M3U set; never for a partial conversion.
                    try:
                        record_import(workspace, Path(workspace) / 'ROMs' / 'psx' / title,
                                      digest, disc_count=len(prepared))
                    except (OSError, ValueError) as exc:
                        converted['errors'].append(
                            f'Source dedupe receipt not saved (CHDs are safe): {exc}')
                for key in ('copied', 'skipped', 'converted', 'playlists', 'playlists_updated'):
                    out[key] += converted[key]
                out['errors'].extend(converted['errors'])
                out['artwork_games'].extend(converted['artwork_games'])
                if converted['cancelled']:
                    out['cancelled'] = True
                    return out
        except InterruptedError:
            out['cancelled'] = True
            return out
        except Exception as exc:
            out['errors'].append(f'{pbp.name} (PS1 Classics): {exc}')
    # DOCUMENT.DAT is a digital manual and KEYS.BIN is key material, not an
    # ISO, disc track or native PSP game. Never put them on the virtual card.
    orphan = [p for p in paths if p.name.casefold() in ('keys.bin','document.dat')
              and p not in psn_related]
    for p in orphan:
        out['errors'].append(f'{p.name}: This is PS1 Classics companion data, '
                             'not a game image. Select its matching EBOOT.PBP.')
    excluded = psn_consumed | psn_related | set(orphan)
    # Unknown .PBP with a PS1 fallback may actually be a native PSP EBOOT:
    # refuse ambiguous automatic classification instead of corrupting PS1.
    unsafe_pbp = [p for p in paths if p.suffix.lower() == '.pbp'
                  and p not in excluded and infer_system(p, fallback) == 'PS1']
    for p in unsafe_pbp:
        out['errors'].append(f'{p.name}: Not a recognizable PS1 Classics PBP. '
                             'For a native PSP EBOOT, select PSP instead.')
    excluded.update(unsafe_pbp)
    paths = [p for p in paths if p not in excluded]
    cue_sources = _unique_cues(paths)
    # Exclude BIN tracks that are companions to any CUE/M3U. Standalone BINs
    # cannot be converted reliably and must not show up as separate PS1 games.
    from core import _cue_companions
    # _cue_companions returns resolved paths. The selected paths (especially
    # those read from ZIP extraction on Windows) may use equivalent spelling,
    # short-name aliases or parent/.. segments. Compare canonical paths so
    # referenced BIN tracks cannot be misreported as standalone PS1 discs.
    companions = set()
    for cue in cue_sources:
        try: companions.update(p.resolve() for p in _cue_companions(cue))
        except Exception as exc: out['errors'].append(f'{cue.name}: {exc}')
    # Existing CHD/M3U collections remain importable without conversion.
    # Only playlists referencing unconverted CUE sets are replaced by new M3Us.
    converted_m3us = set()
    for p in paths:
        if p.suffix.lower() == '.m3u':
            try:
                if any(item.suffix.lower() == '.cue' for item in _cue_companions(p)):
                    converted_m3us.add(p)
            except (OSError, ValueError) as exc:
                out['errors'].append(f'{p.name}: {exc}')
                converted_m3us.add(p)
    remaining = [p for p in paths if p.resolve() not in companions and
                 p.suffix.lower() != '.cue' and p not in converted_m3us]
    raw_bins = [p for p in remaining if p.suffix.lower() == '.bin' and infer_system(p, fallback) == 'PS1']
    for f in raw_bins:
        out['errors'].append(f'{f.name}: Select its matching CUE file. A BIN track alone cannot become a complete PS1 CHD.')
    remaining = [p for p in remaining if p not in raw_bins]
    # Already compressed disc-numbered PS1 CHDs share the same collection
    # folder and verified M3U. They are not needlessly recompressed.
    direct_chds = [p for p in remaining if p.suffix.lower() == '.chd'
                   and infer_system(p, fallback) == 'PS1'
                   and disc_identity(p.stem)[1] is not None]
    remaining = [p for p in remaining if p not in direct_chds]
    phase('Validating PlayStation disc tracks', 10, 100)
    disc_result = stage_ps1_cues(cue_sources, workspace, binary, progress=lambda msg, c, t: phase(msg, 0 if t == 0 else 10 + round(.55*c),
                                                   0 if t == 0 else 100),
                                  cancel=cancel, converter=converter, verify_existing=verify_existing,
                                  optimize_existing=optimize_existing)
    for key in ('copied', 'skipped', 'converted', 'playlists', 'playlists_updated'):
        out[key] += disc_result[key]
    out['errors'] += disc_result['errors']
    out['artwork_games'].extend(disc_result['artwork_games'])
    if disc_result['cancelled']:
        out['cancelled'] = True
        return out
    if direct_chds and not optimize_existing:
        existing_result = stage_ps1_chds(direct_chds, workspace, binary, progress=phase,
                                         cancel=cancel, verify_existing=verify_existing)
        for key in ('copied', 'skipped', 'converted', 'playlists', 'playlists_updated'):
            out[key] += existing_result[key]
        out['errors'] += existing_result['errors']
        out['artwork_games'].extend(existing_result['artwork_games'])
        if existing_result['cancelled']:
            out['cancelled'] = True
            return out
    if remaining and not optimize_existing:
        phase('Importing other recognized games', 70, 100)
        imported = import_grouped(remaining, workspace, fallback, progress=lambda msg, cur, total: phase(msg, 70 + round(15*cur/max(total,1)), 100), cancel=cancel)
        out['copied'] += imported['copied']
        out['skipped'] += imported['skipped']
        out['errors'] += imported['errors']
        out['cancelled'] = bool(imported['cancelled'])
        if out['cancelled']:
            return out
        for p in remaining:
            if p.suffix.lower() not in ('.bin', '.img') or infer_system(p, fallback) != 'PS1':
                out['artwork_games'].append({'system': infer_system(p, fallback), 'label': p.stem})
    if auto_artwork and out['artwork_games']:
        out['artwork_attempted'] = True
        from artwork_gallery import process_batch
        phase('Looking for matching cover artwork', 86, 100)
        try:
            unique = list({(g['system'], g['label']):g for g in out['artwork_games']}.values())
            art = process_batch(workspace, unique, cancelled=cancel, max_items=80,
                progress=lambda msg, cur, total: phase(f'{msg} · {cur}/{total}', 86 + round(13*cur/max(total,1)), 100))
            out['artwork'] = art.get('stats', {})
            if art.get('cancelled'): out['cancelled'] = True
        except Exception as exc:
            out['artwork'] = {'error': str(exc)}
    if not out['cancelled']:
        phase('Prepared games, artwork and playlists', 100, 100)
    return out
