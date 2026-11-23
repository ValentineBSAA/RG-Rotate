"""PSOne Classics package recognition and optional PSXtract extraction bridge.

PSN EBOOT.PBP is not a PSP ISO and KEYS.BIN is key material, NOT a disc.
The helper must be installed by the user separately. This bridge never embeds
keys or DRM material, writes to the original package, or publishes unverified
disc images. Temporary CUE/BIN output flows into existing CHDman verification.
"""
from __future__ import annotations

import re
import queue
import threading
import struct
import subprocess
import tempfile
import time
from pathlib import Path

from disc_sets import inspect_cue
from ps1_collections import disc_numbers_are_contiguous, folder_title

_GAME_CODE = re.compile(r'(?i)^(?:[A-Z]{4}\d{4,6}|[A-Z]{3}\d{5,6})$')
_NUMBER = re.compile(r'(?i)(?:disc|disk|cd)[\s._-]*(\d{1,2})(?=\D|$)')
_TRAILING_NUMBER = re.compile(r'(?:^|[\s._-])(\d{1,2})$')
_STRIP_STORE_TAGS = re.compile(r'(?i)\s*\((?:PSN|English)\)\s*$')


def pbp_disc_signature(pbp: Path) -> str:
    """Identify PSOne Classics PSAR signature (not merely the .PBP suffix)."""
    p = Path(pbp)
    if p.suffix.lower() != '.pbp' or not p.is_file() or p.is_symlink():
        return ''
    try:
        with p.open('rb') as stream:
            header = stream.read(40)
            if len(header) != 40 or header[:4] != b'\0PBP':
                return ''
            offsets = struct.unpack('<8I', header[8:])
            end = p.stat().st_size
            if any(offset < 40 or offset >= end for offset in offsets):
                return ''
            if list(offsets) != sorted(offsets):
                return ''
            stream.seek(offsets[-1])
            value = stream.read(16)
            if value.startswith(b'PSTITLEIMG'):
                return 'multi'
            if value.startswith(b'PSISOIMG'):
                return 'single'
    except OSError:
        return ''
    return ''


def psn_companions(pbp: Path) -> tuple[Path | None, Path | None]:
    """Case-insensitive sidecars from the SAME directory as the PBP."""
    parent = Path(pbp).parent
    files = {p.name.casefold(): p for p in parent.iterdir()
             if p.is_file() and not p.is_symlink()} if parent.is_dir() else {}
    return files.get('document.dat'), files.get('keys.bin')


def is_ps1_classic(pbp: Path) -> bool:
    if Path(pbp).suffix.lower() != '.pbp':
        return False
    if pbp_disc_signature(Path(pbp)):
        return True
    if Path(pbp).name.casefold() == 'eboot.pbp':
        _doc, keys = psn_companions(Path(pbp))
        return keys is not None
    return False


_GENERIC_TITLES = {
    'eboot', 'ps1', 'psx', 'psp', 'playstation', 'playstation 1',
    'playstation one', 'psn', 'game', 'games', 'content', 'data',
    'rom', 'roms', 'archive', 'archives', 'source', 'unpacked',
    'collection', 'ps1 classics', 'psn collection', 'ps1 collection',
    'ps1 game', 'ps1 games', 'disc', 'disk', 'cd', 'unknown',
}
_GENERIC_DISC = re.compile(
    r'(?i)^(?:(?:ps1|psx|playstation(?:[ _-]*(?:1|one))?|game|disc|disk|cd)'
    r'[\s._-]*)*(?:disc|disk|cd)?[\s._-]*\d{1,2}


def extract_psn_with_helper(pbp: Path, output: Path, helper: Path, *,
                            cancel=None, progress=None):
    """Run separately-provided PSXtract in disposable local storage, no shell."""
    pbp, output, helper = Path(pbp), Path(output), Path(helper)
    if not helper.is_file():
        raise FileNotFoundError(
            'PS1 Classics need PSXtract in the Windows tools folder '
            '(psxtract/psxtract.exe). CHDman cannot decrypt EBOOT.PBP directly. '
            'Your original PBP, KEYS.BIN and DOCUMENT.DAT have not been changed.')
    if not output.is_dir() or any(output.iterdir()):
        raise ValueError('PSXtract output folder must be a fresh, empty local folder')
    if not pbp_disc_signature(pbp):
        raise ValueError('This PBP is not a recognized PS1 Classics disc package; '
                         'it will not be converted as a PSP game or renamed blindly')
    document, keys = psn_companions(pbp)
    args = [str(helper.resolve()), '-c', str(pbp.resolve())]
    if document:
        args.append(str(document.resolve()))
        if keys:
            args.append(str(keys.resolve()))
    # PSXtract accepts positional DOCUMENT.DAT then KEYS.BIN; without a
    # document, do not misinterpret a KEYS.BIN as a document. The extractor
    # may use the PBP's internal metadata instead.
    if cancel is not None and cancel.is_set():
        raise InterruptedError('PSN extraction stopped')
    if progress:
        progress('Extracting PS1 Classic into temporary Windows storage', 0, 0)
    from ps1_progress import PSXtractMilestones
    milestone = PSXtractMilestones()
    friendly_events = queue.Queue(maxsize=80)
    # An actively draining reader prevents a noisy converter from deadlocking
    # on an unconsumed stdout pipe. No raw log or decrypted source is persisted.
    proc = subprocess.Popen(args, cwd=output, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, shell=False)

    def read_console():
        try:
            for raw in iter(proc.stdout.readline, b''):
                event = milestone.event(raw.decode('utf-8', errors='replace'))
                if event:
                    try:
                        friendly_events.put_nowait(event)
                    except queue.Full:
                        # Keep output bounded if a third-party helper floods stdout.
                        try:
                            friendly_events.get_nowait()
                            friendly_events.put_nowait(event)
                        except queue.Empty:
                            pass
        finally:
            proc.stdout.close()

    reader = threading.Thread(target=read_console, daemon=True,
                              name='PSXtract-Progress-Reader')
    reader.start()

    def send_friendly_events():
        while True:
            try:
                notice = friendly_events.get_nowait()
            except queue.Empty:
                break
            if progress:
                progress(notice, 0, 0)

    try:
        start = time.monotonic()
        while proc.poll() is None:
            send_friendly_events()
            if cancel is not None and cancel.is_set():
                proc.terminate()
                try: proc.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait(timeout=4)
                raise InterruptedError('PSN extraction stopped; source files are intact')
            if time.monotonic() - start > 2 * 60 * 60:
                proc.kill(); proc.wait(timeout=4)
                raise TimeoutError('PSXtract exceeded two-hour safety limit')
            time.sleep(.2)
        reader.join(timeout=3)
        send_friendly_events()
        if proc.returncode:
            raise RuntimeError('PSXtract could not extract complete PS1 disc images. '
                               'Conversion stopped; original EBOOT and keys unchanged. '
                               f'Helper exit code: {proc.returncode}.')
        if milestone.md5_failed:
            raise RuntimeError('PSXtract reported an MD5 mismatch. No disc images were published.')
        if progress:
            progress('PS1 Classic extracted • checking each disc before CHD conversion', 0, 0)
    finally:
        if proc.poll() is None:
            proc.kill(); proc.wait(timeout=4)
        reader.join(timeout=3)

    from core import safe_walk, MAX_ARCHIVE_BYTES
    files = list(safe_walk(output, cancel=cancel))
    total = sum(p.stat().st_size for p in files)
    if total > MAX_ARCHIVE_BYTES:
        raise ValueError('Extracted PS1 game exceeds 32 GB import safety limit')
    return [p for p in files if p.suffix.lower() == '.cue']


def ordered_psn_cues(cues: list[Path], title: str, *, multi_expected=False) -> list[Path]:
    """Never guess the order of ambiguous extracted discs.

    Re-name only CUE *copies* inside temporary extraction storage, leaving
    track references/BIN bytes in place, so our existing stage_ps1_cues and
    CHDman can verify each independently.
    """
    cues = list(dict.fromkeys(Path(x) for x in cues))
    if not cues:
        raise ValueError('PSXtract produced no CUE sheets. No CHDs were published.')
    parsed = []
    for cue in cues:
        check = inspect_cue(cue)
        if check['errors']:
            raise ValueError(f'Extracted {cue.name} is incomplete: ' + '; '.join(check['errors']))
        m = _NUMBER.search(cue.stem) or _TRAILING_NUMBER.search(cue.stem)
        parsed.append((int(m.group(1)) if m else None, cue))
    if multi_expected and len(cues) < 2:
        raise ValueError('Multi-disc PBP produced fewer than two disc CUE files; '
                         'refusing to publish an incomplete collection')
    if len(cues) == 1:
        parsed = [(1, parsed[0][1])]
    else:
        known = [n for n, _ in parsed if n is not None]
        if len(known) == len(cues) - 1 and set(known) == set(range(2, len(cues) + 1)):
            parsed = [(1 if n is None else n, p) for n, p in parsed]
        numbers = [n for n, _ in parsed]
        if any(n is None for n in numbers) or not disc_numbers_are_contiguous(numbers):
            raise ValueError(
                'Cannot prove the order of the extracted PS1 discs. '
                'No CHDs or playlist were added; review the PSXtract CUE filenames.')
    staged = []
    for n, cue in sorted(parsed):
        name = f'{title} (Disc {n}).cue'
        new = cue.parent / name
        if new.exists() and new != cue:
            raise FileExistsError('Extracted CUE naming conflict; nothing overwritten')
        if new != cue:
            new.write_bytes(cue.read_bytes())
        staged.append(new)
    return staged
)


def meaningful_title(raw: str | None) -> str | None:
    """A generic storage name is NEVER evidence of a game's identity."""
    name = str(raw or '').strip()
    while True:
        new = _STRIP_STORE_TAGS.sub('', name).strip()
        if new == name:
            break
        name = new
    if (not name or name.casefold() in _GENERIC_TITLES
            or _GENERIC_DISC.fullmatch(name)
            or _GAME_CODE.fullmatch(name)
            or name.casefold().startswith(('rgl-archive-', 'rgl-psn-extract-',
                                          'retro-ps1-chd-'))):
        return None
    return folder_title(name)


def pbp_metadata_title(pbp: Path) -> str | None:
    """Read only the public TITLE string in PARAM.SFO inside a PBP.

    No game payload, PSAR encryption, DRM keys or personal identifiers are read.
    Invalid and oversized SFO tables are ignored rather than guessed.
    """
    try:
        with Path(pbp).open('rb') as stream:
            header = stream.read(40)
            if len(header) != 40 or header[:4] != b'\0PBP':
                return None
            offsets = struct.unpack('<8I', header[8:])
            size = Path(pbp).stat().st_size
            start, end = offsets[:2]
            if start < 40 or end <= start or end > size or end - start > 1024 * 1024:
                return None
            stream.seek(start)
            data = stream.read(end - start)
        if len(data) < 20:
            return None
        magic, _version, keys_at, values_at, count = struct.unpack_from('<4sIIII', data)
        if magic != b'\0PSF' or count > 128 or 20 + count * 16 > len(data):
            return None
        for i in range(count):
            key_offset, _align, _fmt, length, _max_length, data_offset = struct.unpack_from(
                '<HBBIII', data, 20 + i * 16)
            key_pos = keys_at + key_offset
            value_pos = values_at + data_offset
            if key_pos < 0 or key_pos >= len(data) or length > 2048:
                continue
            if value_pos < 0 or value_pos + length > len(data):
                continue
            if data[key_pos:key_pos + 6] != b'TITLE\0':
                continue
            raw = data[value_pos:value_pos + length].split(b'\0', 1)[0]
            return meaningful_title(raw.decode('utf-8', errors='replace'))
    except (OSError, ValueError, struct.error):
        return None
    return None


def package_title(pbp: Path, title_hint: str | None = None) -> str:
    """Identify from a *meaningful* source name, then PBP's title metadata.

    PS1.zip / PlayStation.7z / EBOOT.PBP must never create a "PS1" CHD tile.
    """
    pbp = Path(pbp)
    candidates = (title_hint, pbp.stem if pbp.stem.casefold() != 'eboot' else None,
                  pbp.parent.name)
    for raw in candidates:
        if title := meaningful_title(raw):
            return title
    if title := pbp_metadata_title(pbp):
        return title
    # Common PSN packages are Title / NPEFxxxx / EBOOT.PBP.
    if title := meaningful_title(pbp.parent.parent.name):
        return title
    raise ValueError(
        'Cannot identify the game title safely. The package was NOT converted. '
        'Use a descriptively named game archive/folder or a PBP with a valid TITLE '
        'in PARAM.SFO. Generic PS1/PlayStation/Disc names are not game titles.')


def extract_psn_with_helper(pbp: Path, output: Path, helper: Path, *,
                            cancel=None, progress=None):
    """Run separately-provided PSXtract in disposable local storage, no shell."""
    pbp, output, helper = Path(pbp), Path(output), Path(helper)
    if not helper.is_file():
        raise FileNotFoundError(
            'PS1 Classics need PSXtract in the Windows tools folder '
            '(psxtract/psxtract.exe). CHDman cannot decrypt EBOOT.PBP directly. '
            'Your original PBP, KEYS.BIN and DOCUMENT.DAT have not been changed.')
    if not output.is_dir() or any(output.iterdir()):
        raise ValueError('PSXtract output folder must be a fresh, empty local folder')
    if not pbp_disc_signature(pbp):
        raise ValueError('This PBP is not a recognized PS1 Classics disc package; '
                         'it will not be converted as a PSP game or renamed blindly')
    document, keys = psn_companions(pbp)
    args = [str(helper.resolve()), '-c', str(pbp.resolve())]
    if document:
        args.append(str(document.resolve()))
        if keys:
            args.append(str(keys.resolve()))
    # PSXtract accepts positional DOCUMENT.DAT then KEYS.BIN; without a
    # document, do not misinterpret a KEYS.BIN as a document. The extractor
    # may use the PBP's internal metadata instead.
    if cancel is not None and cancel.is_set():
        raise InterruptedError('PSN extraction stopped')
    if progress:
        progress('Extracting PS1 Classic into temporary Windows storage', 0, 0)
    from ps1_progress import PSXtractMilestones
    milestone = PSXtractMilestones()
    friendly_events = queue.Queue(maxsize=80)
    # An actively draining reader prevents a noisy converter from deadlocking
    # on an unconsumed stdout pipe. No raw log or decrypted source is persisted.
    proc = subprocess.Popen(args, cwd=output, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, shell=False)

    def read_console():
        try:
            for raw in iter(proc.stdout.readline, b''):
                event = milestone.event(raw.decode('utf-8', errors='replace'))
                if event:
                    try:
                        friendly_events.put_nowait(event)
                    except queue.Full:
                        # Keep output bounded if a third-party helper floods stdout.
                        try:
                            friendly_events.get_nowait()
                            friendly_events.put_nowait(event)
                        except queue.Empty:
                            pass
        finally:
            proc.stdout.close()

    reader = threading.Thread(target=read_console, daemon=True,
                              name='PSXtract-Progress-Reader')
    reader.start()

    def send_friendly_events():
        while True:
            try:
                notice = friendly_events.get_nowait()
            except queue.Empty:
                break
            if progress:
                progress(notice, 0, 0)

    try:
        start = time.monotonic()
        while proc.poll() is None:
            send_friendly_events()
            if cancel is not None and cancel.is_set():
                proc.terminate()
                try: proc.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait(timeout=4)
                raise InterruptedError('PSN extraction stopped; source files are intact')
            if time.monotonic() - start > 2 * 60 * 60:
                proc.kill(); proc.wait(timeout=4)
                raise TimeoutError('PSXtract exceeded two-hour safety limit')
            time.sleep(.2)
        reader.join(timeout=3)
        send_friendly_events()
        if proc.returncode:
            raise RuntimeError('PSXtract could not extract complete PS1 disc images. '
                               'Conversion stopped; original EBOOT and keys unchanged. '
                               f'Helper exit code: {proc.returncode}.')
        if milestone.md5_failed:
            raise RuntimeError('PSXtract reported an MD5 mismatch. No disc images were published.')
        if progress:
            progress('PS1 Classic extracted • checking each disc before CHD conversion', 0, 0)
    finally:
        if proc.poll() is None:
            proc.kill(); proc.wait(timeout=4)
        reader.join(timeout=3)

    from core import safe_walk, MAX_ARCHIVE_BYTES
    files = list(safe_walk(output, cancel=cancel))
    total = sum(p.stat().st_size for p in files)
    if total > MAX_ARCHIVE_BYTES:
        raise ValueError('Extracted PS1 game exceeds 32 GB import safety limit')
    return [p for p in files if p.suffix.lower() == '.cue']


def ordered_psn_cues(cues: list[Path], title: str, *, multi_expected=False) -> list[Path]:
    """Never guess the order of ambiguous extracted discs.

    Re-name only CUE *copies* inside temporary extraction storage, leaving
    track references/BIN bytes in place, so our existing stage_ps1_cues and
    CHDman can verify each independently.
    """
    cues = list(dict.fromkeys(Path(x) for x in cues))
    if not cues:
        raise ValueError('PSXtract produced no CUE sheets. No CHDs were published.')
    parsed = []
    for cue in cues:
        check = inspect_cue(cue)
        if check['errors']:
            raise ValueError(f'Extracted {cue.name} is incomplete: ' + '; '.join(check['errors']))
        m = _NUMBER.search(cue.stem) or _TRAILING_NUMBER.search(cue.stem)
        parsed.append((int(m.group(1)) if m else None, cue))
    if multi_expected and len(cues) < 2:
        raise ValueError('Multi-disc PBP produced fewer than two disc CUE files; '
                         'refusing to publish an incomplete collection')
    if len(cues) == 1:
        parsed = [(1, parsed[0][1])]
    else:
        known = [n for n, _ in parsed if n is not None]
        if len(known) == len(cues) - 1 and set(known) == set(range(2, len(cues) + 1)):
            parsed = [(1 if n is None else n, p) for n, p in parsed]
        numbers = [n for n, _ in parsed]
        if any(n is None for n in numbers) or not disc_numbers_are_contiguous(numbers):
            raise ValueError(
                'Cannot prove the order of the extracted PS1 discs. '
                'No CHDs or playlist were added; review the PSXtract CUE filenames.')
    staged = []
    for n, cue in sorted(parsed):
        name = f'{title} (Disc {n}).cue'
        new = cue.parent / name
        if new.exists() and new != cue:
            raise FileExistsError('Extracted CUE naming conflict; nothing overwritten')
        if new != cue:
            new.write_bytes(cue.read_bytes())
        staged.append(new)
    return staged
