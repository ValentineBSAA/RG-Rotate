"""Ninite-style, opt-in setup queue for *official* RG Rotate software.

Android APKs are staged, never installed on an absent device. Windows binaries
are unpacked inside the app's private WindowsTools folder. No ROM downloads.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable
import json
import hashlib

import software
import tool_setup

RECOMMENDED = ('Cocoon Shell', 'PPSSPP', 'RetroArch', 'Android Platform Tools', 'CHDman')
OPTIONAL = ('DuckStation',)
DESCRIPTION = {
    'Cocoon Shell': 'Default RG Rotate launcher',
    'PPSSPP': 'PlayStation Portable games',
    'RetroArch': 'Retro console emulation',
    'Android Platform Tools': 'USB setup utility for Windows',
    'CHDman': 'PS1 disc-image utility for Windows',
    'DuckStation': 'Optional PS1 emulator; Cocoon launch compatibility warning',
}
ANDROID = ('Cocoon Shell', 'PPSSPP', 'RetroArch')
WINDOWS = ('Android Platform Tools', 'CHDman')



def manual_apk_for(workspace: Path, app_name: str) -> Path | None:
    """Recognize an *explicitly user-imported* matching APK, not arbitrary APK names.

    This is content-integrity validation only, not verification of publisher
    identity. The UI clearly labels these imports as unverified.
    """
    # User files do not always follow upstream naming.  In particular,
    # Cocoon 3.1.1 is sometimes saved as `cocon-311.apk` (single 'o').
    # Recognize only these narrow aliases *and* require a user-import receipt
    # with a matching SHA-256 below.  A name alone never proves publisher.
    accepted_prefixes = {
        'Cocoon Shell': ('cocoon', 'cocon-'),
        'PPSSPP': ('ppsspp',),
        'RetroArch': ('retroarch',),
    }
    aliases = accepted_prefixes.get(app_name)
    if aliases is None: return None
    receipts = Path(workspace) / '.retro-library' / 'receipts'
    matches = []
    for receipt in sorted(receipts.glob('local_*.json')):
        try:
            data = json.loads(receipt.read_text(encoding='utf-8'))
            if 'user imported' not in data.get('source',''):
                continue
            name = data.get('filename','')
            if not Path(name).name.lower().startswith(aliases) or not name.lower().endswith('.apk'):
                continue
            file = Path(workspace) / 'SetupPackages' / name
            if file.is_symlink() or not file.is_file(): continue
            software._apk_ok(file)
            with file.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            if digest == data.get('sha256'):
                matches.append(file)
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return matches[0] if len(matches) == 1 else None

def readiness(workspace: Path, host_tools: Path) -> dict[str, str]:
    """Local readiness only; *never* represents APKs as installed on Android."""
    result = {name: 'Not prepared' for name in (*RECOMMENDED, *OPTIONAL)}
    local_status = tool_setup.tool_status(host_tools)
    for name in WINDOWS:
        if local_status[name]['installed']:
            result[name] = 'Ready on Windows'
        elif local_status[name].get('file_present'):
            result[name] = 'Needs attention: run setup to verify the existing Windows executable'
    for name in ANDROID:
        receipt = workspace / '.retro-library' / 'receipts' / (name.replace(' ', '_') + '.json')
        if receipt.is_file():
            try:
                import json
                data = json.loads(receipt.read_text(encoding='utf-8'))
                source = Path(data['file'])
                if (source.is_file() and source.resolve().is_relative_to((workspace / 'SetupPackages').resolve())
                        and data.get('url', '').startswith('https://') and data.get('sha256')):
                    software._apk_ok(source)
                    import hashlib
                    with source.open('rb') as f:
                        actual = hashlib.file_digest(f, 'sha256').hexdigest()
                    if actual == data['sha256']:
                        result[name] = 'APK ready • Android install pending'
            except (OSError, ValueError, KeyError, TypeError):
                pass
    for name in ANDROID:
        if result[name] == 'Not prepared' and manual_apk_for(workspace, name):
            result[name] = 'My APK ready • publisher unverified'
    result['DuckStation'] = 'Optional • manual compatibility review'
    return result


def prepare_batch(
    names: list[str], workspace: Path, host_tools: Path,
    progress: Callable[[str, int, int], None] | None = None,
    cancel=None,
    on_state: Callable[[str, str], None] | None = None,
    prefer_local: bool = True,
) -> dict:
    """Run selected installs sequentially with per-item status and safe retries.

    A failure on one package does not prevent later packages from being tried.
    The caller owns user confirmation, and no Android install is attempted here.
    """
    if len(set(names)) != len(names):
        raise ValueError('Duplicate installer names')
    unexpected = set(names) - set(RECOMMENDED) - set(OPTIONAL)
    if unexpected:
        raise ValueError('Unknown packages: ' + ', '.join(sorted(unexpected)))
    workspace = Path(workspace)
    host_tools = Path(host_tools)
    report = {'results': [], 'cancelled': False}
    for number, name in enumerate(names, 1):
        if cancel is not None and cancel.is_set():
            report['cancelled'] = True
            break
        if on_state:
            on_state(name, f'Checking ({number}/{len(names)})…')
        if progress:
            progress(f'Checking {name} ({number}/{len(names)})', number - 1, len(names))
        try:
            if name in ANDROID:
                local = manual_apk_for(workspace, name) if prefer_local else None
                if local:
                    item = {'name': name, 'ok': True,
                            'state': 'My APK ready • publisher unverified • Android install pending',
                            'path': str(local)}
                    if on_state: on_state(name, item['state'])
                    report['results'].append(item)
                    continue
                if on_state:
                    on_state(name, 'Downloading official APK / checking existing copy…')
                def apk_progress(label, done, total):
                    if progress:
                        progress(f'{name}: {done / 1048576:.1f} MiB downloaded', done, total)
                    if on_state:
                        percent = min(100, round(done / total * 100)) if total and total >= done else None
                        on_state(name, f'Downloading {percent}%' if percent is not None else 'Downloading…')
                receipt = software.download_apk(name, workspace, progress=apk_progress, cancel=cancel)
                detail = 'Already downloaded • ready for Android' if receipt.get('status') == 'already downloaded' else 'APK ready • Android installation pending'
                item = {'name': name, 'ok': True, 'state': detail, 'path': receipt.get('file')}
            elif name in WINDOWS:
                if on_state:
                    on_state(name, 'Downloading / preparing on Windows…')
                def tool_progress(label, done, total):
                    if progress:
                        progress(f'{name}: {label}', done, total)
                    if on_state:
                        if total == 0:
                            on_state(name, label + '…')
                        else:
                            percent = min(100, round(done / total * 100)) if total >= done else None
                            on_state(name, f'Downloading {percent}%' if percent is not None else 'Downloading…')
                if name == 'Android Platform Tools':
                    answer = tool_setup.install_adb(host_tools, progress=tool_progress, cancel=cancel)
                else:
                    answer = tool_setup.install_chdman(host_tools, progress=tool_progress, cancel=cancel)
                item = {'name': name, 'ok': bool(answer['ok']),
                        'state': 'Ready on Windows' if answer['ok'] else answer['state']}
            else:
                item = {'name': name, 'ok': False,
                        'state': 'Needs compatibility review • use official download page'}
            if on_state:
                on_state(name, item['state'])
        except InterruptedError:
            report['cancelled'] = True
            if on_state:
                on_state(name, 'Stopped safely • retry later')
            break
        except Exception as exc:
            item = {'name': name, 'ok': False, 'state': f'Needs attention: {type(exc).__name__}: {exc}'}
            if on_state:
                on_state(name, item['state'])
        report['results'].append(item)
    if report['cancelled'] and on_state:
        remaining = set(names) - {r['name'] for r in report['results']}
        for name in remaining:
            on_state(name, 'Not completed • retry later')
    if progress:
        progress('Installer queue finished' if not report['cancelled'] else 'Installer stopped',
                 len(report['results']), max(1, len(names)))
    return report
