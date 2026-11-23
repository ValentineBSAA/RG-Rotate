"""ASCII-only CHDman CUE bridge for disposable extracted PSN discs.

Some Windows CHDman builds parse CLI filenames through a legacy code page.
A PBP title can contain characters such as the trademark sign (™), causing
CHDman to report "no such file" for an existing Unicode-named CUE.

NEVER change the original PBP, source user CUE/BIN, or published game title.
This helper is only called on files in a disposable PSN extraction directory.
It creates a small ASCII CUE alongside the original so relative track names
still resolve. Temporary aliases/hardlinks are cleaned on exit/cancellation.
"""
from __future__ import annotations

import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path

from disc_sets import FILE, inspect_cue


@contextmanager
def ascii_psn_cue(source: Path, *, cancel=None):
    """Yield a CHDman-readable alias without changing real game identity.

    Only use this on the app's own disposable extracted PSN CUE files. The
    normal user-managed PS1 CUE import must not create aliases in source
    libraries. The source and its track data remain untouched.
    """
    cue = Path(source)
    if not cue.is_file() or cue.is_symlink():
        raise ValueError('Extracted PS1 CUE is missing or unsafe')
    if cancel is not None and cancel.is_set():
        raise InterruptedError('PS1 conversion stopped')
    inspection = inspect_cue(cue, cancel=cancel)
    if inspection['errors']:
        raise ValueError('PSN disc references need attention: ' +
                         '; '.join(inspection['errors']))
    needs_alias = not str(cue).isascii() or any(
        not entry['name'].isascii() for entry in inspection['files'])
    if not needs_alias:
        yield cue
        return
    if not str(cue.parent).isascii():
        raise ValueError('CHDman cannot safely open this non-ASCII temporary '
                         'Windows folder. Configure TEMP/TMP with an ASCII-only '
                         'local path and retry; original files were preserved.')

    aliases: list[Path] = []
    try:
        # The CUE is small (max 4 MiB as checked by inspect_cue).
        data = cue.read_bytes()
        if any(not entry['name'].isascii() for entry in inspection['files']):
            # File aliases use hardlinks inside disposable LOCAL extraction
            # storage. This does not duplicate potentially gigabyte-sized BIN
            # tracks and never renames or modifies PSXtract's output.
            try:
                text = data.decode('utf-8-sig')
            except UnicodeDecodeError:
                text = data.decode('cp1252')
            referenced: dict[str, str] = {}
            updated = []
            for line in text.splitlines(keepends=True):
                match = FILE.fullmatch(line.strip())
                if match and not (match[1] or match[2]).isascii():
                    name = match[1] or match[2]
                    if name not in referenced:
                        track = cue.parent / Path(name.replace('\\', '/'))
                        if track.is_symlink() or not track.is_file():
                            raise ValueError('PSN CUE refers to an unavailable track')
                        suffix = track.suffix if track.suffix.isascii() else '.bin'
                        with tempfile.NamedTemporaryFile(prefix='rgl-track-', suffix=suffix,
                                                         dir=cue.parent, delete=False) as temp:
                            alias_track = Path(temp.name)
                        alias_track.unlink()
                        # NTFS local temporary extraction; no network writes.
                        os.link(track, alias_track)
                        aliases.append(alias_track)
                        referenced[name] = alias_track.name
                    ending = '\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else ''
                    updated.append(f'FILE "{referenced[name]}" {match[3]}{ending}')
                else:
                    updated.append(line)
            data = ''.join(updated).encode('utf-8')
        with tempfile.NamedTemporaryFile(mode='wb', prefix='rgl-disc-', suffix='.cue',
                                         dir=cue.parent, delete=False) as temp:
            alias_cue = Path(temp.name)
            aliases.append(alias_cue)
            temp.write(data)
        if cancel is not None and cancel.is_set():
            raise InterruptedError('PS1 conversion stopped')
        # Inspect the alias after rewrites so CHDman does not receive an
        # unreadable / incomplete source. Relative BIN paths are preserved.
        checked = inspect_cue(alias_cue, cancel=cancel)
        if checked['errors']:
            raise ValueError('Temporary ASCII CUE alias is invalid: ' +
                             '; '.join(checked['errors']))
        yield alias_cue
    finally:
        for alias in reversed(aliases):
            alias.unlink(missing_ok=True)
