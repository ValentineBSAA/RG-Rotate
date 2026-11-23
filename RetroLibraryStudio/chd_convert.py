"""Conservative CHD conversion helper using official MAME chdman on Windows.

No automatic source deletion, no shell invocation, no overwrites. Output files
are only published after successful conversion *and* chdman verify.
"""
from __future__ import annotations
import subprocess
import tempfile
import time
import os
from pathlib import Path
from typing import Callable


def verify_tool(binary: Path, runner=subprocess.run) -> tuple[bool, str]:
    if not Path(binary).is_file():
        return False, 'CHDman has not been installed yet'
    try:
        result = runner([str(binary)], capture_output=True, text=True,
                        timeout=15, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f'CHDman did not start: {exc}'
    combined = ((result.stdout or '') + '\n' + (result.stderr or '')).strip()
    # CHDman exits nonzero when run without a command; a recognizable usage
    # message, not the return code alone, indicates an executable program.
    if 'chdman' not in combined.lower() and 'chd manager' not in combined.lower():
        return False, 'CHDman did not return its expected usage information'
    return True, 'Executable responds to usage check'


def convert_cue(input_cue: Path, output_dir: Path, binary: Path,
                progress: Callable | None = None, cancel=None,
                runner=subprocess.Popen) -> dict:
    input_cue, output_dir, binary = Path(input_cue), Path(output_dir), Path(binary)
    if input_cue.suffix.lower() != '.cue' or not input_cue.is_file():
        raise ValueError('Choose an existing PS1 .cue file')
    if not output_dir.is_dir():
        raise ValueError('Choose an existing output folder')
    if not binary.is_file():
        raise FileNotFoundError('Install CHDman in Install Apps first')
    finished = output_dir / (input_cue.stem + '.chd')
    temporary = output_dir / (input_cue.stem + '.retro-converting.chd')
    if finished.exists() or temporary.exists():
        raise FileExistsError('Output already exists. Rename or choose another folder. Nothing overwritten.')
    if cancel is not None and cancel.is_set():
        return {'cancelled': True, 'verified': False, 'output': str(finished)}
    from disc_sets import inspect_cue
    inspection = inspect_cue(input_cue, cancel=cancel)
    if inspection['errors']:
        raise ValueError('Disc files need attention:\n' + '\n'.join(inspection['errors']))
    def execute(args, stage):
        if progress: progress(stage, 0, 0)
        # Redirect output to disk, not an unconsumed PIPE. CHDman can print
        # thousands of progress updates, which otherwise deadlock a pipe.
        with tempfile.TemporaryFile(mode='w+t', encoding='utf-8', errors='replace') as output:
            process = runner(args, stdout=output, stderr=subprocess.STDOUT,
                             text=True, shell=False)
            started = time.monotonic()
            while process.poll() is None:
                if cancel is not None and cancel.is_set():
                    process.terminate()
                    try: process.wait(timeout=4)
                    except subprocess.TimeoutExpired:
                        process.kill(); process.wait(timeout=4)
                    raise InterruptedError('CHD conversion cancelled')
                if time.monotonic() - started > 4*60*60:
                    process.kill(); process.wait(timeout=4)
                    raise TimeoutError('CHD conversion exceeded the four-hour safety limit')
                time.sleep(0.2)
            if process.returncode != 0:
                output.seek(0)
                message = output.read()[-12000:]
                raise RuntimeError(f'{stage} failed (exit {process.returncode}): {message}')
    try:
        execute([str(binary), 'createcd', '-i', str(input_cue), '-o', str(temporary)], 'Converting PS1 disc to CHD')
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError('CHDman did not produce a non-empty disc image')
        execute([str(binary), 'verify', '-i', str(temporary)], 'Verifying converted CHD')
        if finished.exists():
            raise FileExistsError('Another output file appeared; cannot overwrite it')
        # Windows rename refuses an existing destination. POSIX rename replaces
        # it, so use an exclusive hard link there to retain no-overwrite safety.
        if os.name == 'nt':
            temporary.rename(finished)
        else:
            os.link(temporary, finished)
            temporary.unlink()
        return {'cancelled': False, 'verified': True, 'source': str(input_cue),
                'output': str(finished), 'bytes': finished.stat().st_size,
                'warnings': inspection['warnings']}
    except InterruptedError:
        temporary.unlink(missing_ok=True)
        return {'cancelled': True, 'verified': False, 'output': str(finished)}
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def verify_existing_chd(source: Path, binary: Path, cancel=None) -> None:
    """Verify an already-staged CHD before reusing or adding it to an M3U."""
    import subprocess
    if not Path(source).is_file() or not Path(binary).is_file():
        raise FileNotFoundError('Cannot verify the existing CHD without CHDman')
    process = subprocess.Popen([str(binary), 'verify', '-i', str(source)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               shell=False)
    try:
        started = time.monotonic()
        while process.poll() is None:
            if cancel is not None and cancel.is_set():
                process.terminate()
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=3)
                raise InterruptedError('Verification stopped')
            if time.monotonic() - started > 4*60*60:
                process.kill(); process.wait(timeout=3)
                raise TimeoutError('CHD verification timed out')
            time.sleep(.15)
        if process.returncode != 0:
            raise ValueError('An existing CHD failed CHDman verification; not added to the playlist')
    finally:
        if process.poll() is None:
            process.kill(); process.wait(timeout=3)
