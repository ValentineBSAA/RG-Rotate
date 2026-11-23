"""Read-only CUE inspection. Track data is never repaired or rewritten.

The bounded samples warn about suspicious dumps without treating silence or
padding as proof of corruption. CHDman's own parser remains authoritative.
"""
from __future__ import annotations

import re
from pathlib import Path

FILE = re.compile(r'^FILE\s+(?:"([^"]+)"|(.+?))\s+(BINARY|MOTOROLA|WAVE|AIFF|MP3)\s*$', re.I)
TRACK = re.compile(r'^TRACK\s+(\d+)\s+(\S+)\s*$', re.I)


def cue_references(source: Path) -> list[str]:
    """Lightweight library presentation metadata; call only in the scan worker."""
    with Path(source).open('rb') as stream:
        raw = stream.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        return []
    try: text = raw.decode('utf-8-sig')
    except UnicodeDecodeError: text = raw.decode('cp1252', errors='replace')
    return [str(Path(source).parent / Path((match[1] or match[2]).replace('\\', '/')))
            for line in text.splitlines() if (match := FILE.fullmatch(line.strip()))]


def inspect_cue(source: Path, cancel=None) -> dict:
    source = Path(source)
    report = {'source': str(source), 'files': [], 'tracks': [], 'errors': [], 'warnings': []}
    if source.suffix.lower() != '.cue' or not source.is_file():
        report['errors'].append('Choose an existing .cue sheet, not an individual BIN track.')
        return report
    with source.open('rb') as stream:
        raw = stream.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        report['errors'].append('CUE sheet exceeds 4 MiB. Check that this is a text CUE sheet.')
        return report
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252')
        report['warnings'].append('CUE uses legacy Windows text encoding; CHDman will read the original.')
    current = None
    numbers = set()
    for lineno, line in enumerate(text.splitlines(), 1):
        if cancel is not None and cancel.is_set():
            raise InterruptedError('Disc inspection stopped')
        line = line.strip()
        if not line or line.upper().startswith('REM '):
            continue
        command = line.split()[0].upper()
        if command == 'FILE':
            match = FILE.fullmatch(line)
            if not match:
                report['errors'].append(f'Line {lineno}: malformed FILE entry. Check quotes and file type.')
                current = None
                continue
            name = match[1] or match[2]
            path = source.parent / Path(name.replace('\\', '/'))
            current = {'name': name, 'path': str(path), 'type': match[3].upper(), 'bytes': None}
            report['files'].append(current)
            if not path.is_file():
                report['errors'].append(f'Line {lineno}: missing track "{name}". Put it at {path}; correct the CUE filename only after checking your original dump.')
                continue
            size = path.stat().st_size
            current['bytes'] = size
            if size == 0:
                report['warnings'].append(f'{name}: empty track (0 bytes). Recheck your dump; conversion may fail.')
            else:
                with path.open('rb') as stream:
                    samples = []
                    for offset in sorted({0, max(0, size // 2 - 32768), max(0, size - 65536)}):
                        stream.seek(offset)
                        samples.append(stream.read(65536))
                if all(not any(sample) for sample in samples):
                    qualifier = 'entire file is zero' if size <= 65536 else 'beginning, middle and end samples are zero (not a full scan)'
                    report['warnings'].append(f'{name}: {qualifier}. Audio silence/padding can be valid; check your dump before proceeding.')
                if size < 2352:
                    report['warnings'].append(f'{name}: unexpectedly small track ({size} bytes). Check the source dump.')
        elif command == 'TRACK':
            match = TRACK.fullmatch(line)
            if not match or current is None:
                report['errors'].append(f'Line {lineno}: TRACK needs a valid preceding FILE entry.')
                continue
            number = int(match[1])
            if number in numbers or not 1 <= number <= 99:
                report['errors'].append(f'Line {lineno}: invalid or duplicate track number {number}.')
            numbers.add(number)
            report['tracks'].append({'number': number, 'mode': match[2].upper(), 'file': current['name']})
    if not report['files']:
        report['errors'].append('No FILE entries found. Select the CUE supplied with the complete disc dump.')
    if not report['tracks']:
        report['warnings'].append('No TRACK declarations found. CHDman may reject this sheet; check the dump.')
    return report


def write_playlist(outputs: list[Path], destination: Path) -> str:
    """Explicit opt-in, ordered, relative M3U; exclusive create, never overwrite."""
    destination = Path(destination)
    outputs = [Path(p) for p in outputs]
    if destination.suffix.lower() != '.m3u' or not outputs:
        raise ValueError('Choose an .m3u filename and at least one verified disc.')
    for output in outputs:
        if output.parent.resolve() != destination.parent.resolve() or not output.is_file():
            raise ValueError('Playlist discs must exist in the playlist folder.')
        if '\n' in output.name or '\r' in output.name:
            raise ValueError('Disc filename cannot contain a newline.')
    with destination.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write('\n'.join(p.name for p in outputs) + '\n')
    return str(destination)


def convert_discs(sources, output_dir, binary, progress=None, cancel=None) -> dict:
    """Each disc succeeds independently. A failed disc never hides later results."""
    from chd_convert import convert_cue
    report = {'results': [], 'cancelled': False}
    for index, source in enumerate(sources, 1):
        if cancel is not None and cancel.is_set():
            report['cancelled'] = True
            break
        if progress:
            progress(f'Disc {index}/{len(sources)}: checking {Path(source).name}', index - 1, len(sources))
        try:
            result = convert_cue(Path(source), Path(output_dir), Path(binary), progress=progress, cancel=cancel)
            result['source'] = str(source)
        except InterruptedError:
            report['cancelled'] = True
            break
        except Exception as exc:
            result = {'source': str(source), 'verified': False, 'error': str(exc), 'output': str(Path(output_dir) / (Path(source).stem + '.chd'))}
        report['results'].append(result)
        if result.get('cancelled'):
            report['cancelled'] = True
            break
    return report
