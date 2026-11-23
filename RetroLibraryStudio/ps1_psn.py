"""PSOne Classics package recognition and optional PSXtract extraction bridge.

PSN EBOOT.PBP is not a PSP ISO and KEYS.BIN is key material, NOT a disc.
The helper must be installed by the user separately. This bridge never embeds
keys or DRM material, writes to the original package, or publishes unverified
disc images. Temporary CUE/BIN output flows into existing CHDman verification.
"""
from __future__ import annotations

import re
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


def package_title(pbp: Path, title_hint: str | None = None) -> str:
    """Do not name the game 'NPEF00069' or lose distinct FFVII/FFVIII names."""
    choices = [str(title_hint or ''), pbp.parent.name, pbp.parent.parent.name]
    for raw in choices:
        name = raw.strip()
        while True:
            new = _STRIP_STORE_TAGS.sub('', name).strip()
            if new == name:
                break
            name = new
        if not name or name.casefold() in ('eboot', 'psp', 'game', 'content'):
            continue
        if _GAME_CODE.fullmatch(name) or name.casefold().startswith('rgl-archive-'):
            continue
        return folder_title(name)
    raise ValueError(
        'Cannot determine a safe game title from this PSN package. '
        'Place the EBOOT inside a named game folder or select a named archive.')


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
    with tempfile.TemporaryFile(mode='w+t', encoding='utf-8', errors='replace') as log:
        proc = subprocess.Popen(args, cwd=output, stdout=log,
                                stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, shell=False)
        try:
            start = time.monotonic()
            while proc.poll() is None:
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
            if proc.returncode:
                raise RuntimeError(
                    'PSXtract could not extract complete PS1 disc images. '
                    'Conversion stopped; the source EBOOT and key files are unchanged. '
                    f'Helper exit code: {proc.returncode}.')
        finally:
            if proc.poll() is None:
                proc.kill(); proc.wait(timeout=4)
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
