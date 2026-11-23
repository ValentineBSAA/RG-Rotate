"""Opt-in setup of OFFICIAL Windows helper binaries in a per-user folder.

Does not execute installers, modify PATH or require administrator privileges.
Does not download ROMs/BIOS, flash firmware, or run chdman on user files.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from core import sanitize_archive_member
from chd_convert import verify_tool

ADB_URL = 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip'
MAME_API = 'https://api.github.com/repos/mamedev/mame/releases/latest'
ADB_DOCS = 'https://developer.android.com/tools/releases/platform-tools'
CHDMAN_DOCS = 'https://www.mamedev.org/release.html'
PSXTRACT_DOCS = 'https://github.com/has207/psxtract-2/releases/tag/v3.0'
PSXTRACT_ZIP = 'https://github.com/has207/psxtract-2/releases/download/v3.0/psxtract-2.zip'
PSXTRACT_SHA256 = '7bca7a8d982f7503a0d9348a3cc043385ee22264eb59ef7edf7fac9388b72013'
MAX_PSXTRACT_ARCHIVE = 50 * 1024**2
MAX_ADB_ARCHIVE = 100 * 1024**2
MAX_MAME_ARCHIVE = 240 * 1024**2


def tools_root() -> Path:
    return Path.home() / 'Documents' / 'Retro Library Studio' / 'WindowsTools'


def _verified_chd(root: Path) -> bool:
    binary = root / 'chdman' / 'chdman.exe'
    record = root / 'chdman' / '.checked.json'
    if not binary.is_file() or not record.is_file():
        return False
    try:
        data = json.loads(record.read_text(encoding='utf-8'))
        statinfo = binary.stat()
        return (data.get('size') == statinfo.st_size and data.get('mtime_ns') == statinfo.st_mtime_ns
                and data.get('executable_test_passed') is True)
    except (OSError, ValueError, TypeError):
        return False


def _check_and_mark_chd(binary: Path) -> None:
    ok, reason = verify_tool(binary)
    if not ok:
        raise RuntimeError('CHDman did not pass its executable test: ' + reason)
    statinfo = binary.stat()
    (binary.parent/'.checked.json').write_text(json.dumps({
        'size':statinfo.st_size, 'mtime_ns':statinfo.st_mtime_ns,
        'executable_test_passed': True, 'meaning':'Executable responded to a harmless usage check'
    }), encoding='utf-8')



def validate_installed_chdman(root: Path | None = None) -> tuple[bool, str]:
    """Perform a harmless real executable test, then persist ready state."""
    root = root or tools_root()
    exe = root / 'chdman' / 'chdman.exe'
    if not exe.is_file():
        return False, 'CHDman is not installed. Use Install Recommended Setup first.'
    try:
        _check_and_mark_chd(exe)
    except (OSError, RuntimeError) as exc:
        return False, str(exc)
    return True, 'CHDman.exe starts successfully and the ready status has been saved.'

def tool_status(root: Path | None = None) -> dict[str, dict]:
    root = root or tools_root()
    adb = root / 'platform-tools' / 'adb.exe'
    chd = root / 'chdman' / 'chdman.exe'
    def present(path):
        try: return path.is_file()
        except OSError: return False
    try: chd_ready = _verified_chd(root)
    except OSError: chd_ready = False
    adb_ready = False
    try:
        data = json.loads((adb.parent / '.checked.json').read_text(encoding='utf-8'))
        info = adb.stat()
        adb_ready = (data.get('size') == info.st_size and data.get('mtime_ns') == info.st_mtime_ns
                     and data.get('executable_test_passed') is True)
    except (OSError, ValueError, TypeError): pass
    psx = root / 'psxtract' / 'psxtract.exe'
    receipt = psx.parent / '.checked.json'
    psx_ready = False
    try:
        record = json.loads(receipt.read_text(encoding='utf-8'))
        psx_ready = (psx.is_file() and record.get('size') == psx.stat().st_size
                     and record.get('mtime_ns') == psx.stat().st_mtime_ns
                     and record.get('release_sha256') == PSXTRACT_SHA256)
    except (OSError, ValueError, TypeError):
        pass
    return {
        'Android Platform Tools': {'installed': adb_ready, 'file_present': present(adb), 'path': str(adb), 'source': ADB_DOCS},
        'CHDman': {'installed': chd_ready, 'file_present': present(chd),
                   'path': str(chd), 'source': CHDMAN_DOCS},
        'PSXtract': {'installed': psx_ready, 'file_present': present(psx),
                     'path': str(psx), 'source': PSXTRACT_DOCS},
    }


def _request(url: str):
    return urllib.request.Request(url, headers={
        'User-Agent': 'RetroLibraryStudio/1.1', 'Accept': 'application/vnd.github+json' if 'api.github.com/' in url else '*/*'})


def official_mame_release() -> tuple[str, str]:
    """Get current official upstream Windows x64 release, never use an arbitrary mirror."""
    with urllib.request.urlopen(_request(MAME_API), timeout=35) as result:
        data = json.load(result)
    assets = [a for a in data.get('assets', [])
              if re.fullmatch(r'mame\d+b_x64\.exe', a.get('name', ''), re.I)]
    if not assets:
        raise RuntimeError('Official MAME release does not provide the expected Windows x64 package')
    asset = assets[0]
    url = asset.get('browser_download_url', '')
    parts = urllib.parse.urlparse(url)
    if parts.scheme != 'https' or parts.hostname != 'github.com' or not parts.path.startswith('/mamedev/mame/releases/download/'):
        raise RuntimeError('Unexpected MAME download location')
    return url, asset['name']


def _download(url: str, dest: Path, max_bytes: int, progress=None, cancel=None) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    try:
        with urllib.request.urlopen(_request(url), timeout=90) as response:
            final = urllib.parse.urlparse(response.geturl())
            allowed = {'dl.google.com', 'github.com', 'release-assets.githubusercontent.com',
                       'objects.githubusercontent.com'}
            if final.scheme != 'https' or final.hostname not in allowed:
                raise RuntimeError(f'Unapproved download redirect: {final.hostname}')
            total = int(response.headers.get('Content-Length') or 0)
            if total > max_bytes:
                raise RuntimeError('Package exceeds download safety limit')
            received = 0
            with dest.open('xb') as file:
                while True:
                    if cancel is not None and cancel.is_set():
                        raise InterruptedError('Download cancelled')
                    data = response.read(1024 * 1024)
                    if not data:
                        break
                    received += len(data)
                    if received > max_bytes:
                        raise RuntimeError('Package exceeds download safety limit')
                    file.write(data)
                    digest.update(data)
                    if progress:
                        progress(f'Downloading {dest.name}', received, total or received)
        if not received:
            raise RuntimeError('Empty package')
        return digest.hexdigest()
    except Exception:
        dest.unlink(missing_ok=True)
        raise


def _extract_platform_zip(archive: Path, destination: Path) -> None:
    """Restrict archive extraction to the documented platform-tools directory."""
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist()) > 3000:
            raise ValueError('Unexpected number of files in Platform Tools')
        total = 0
        for info in z.infolist():
            name = sanitize_archive_member(info.filename)
            if not name.parts or name.parts[0].casefold() != 'platform-tools':
                raise ValueError('Unexpected path in official Platform Tools archive')
            mode = info.external_attr >> 16
            if stat.S_IFMT(mode) == stat.S_IFLNK:
                raise ValueError('Refusing symlink inside Platform Tools')
            total += info.file_size
            if total > 500 * 1024**2:
                raise ValueError('Platform Tools expanded size is unexpectedly large')
        z.extractall(destination)
    if not (destination / 'platform-tools' / 'adb.exe').is_file():
        raise RuntimeError('The downloaded package did not include adb.exe')


def install_adb(root: Path, progress=None, cancel=None) -> dict:
    if (root / 'platform-tools' / 'adb.exe').is_file():
        _verify_adb(root / 'platform-tools' / 'adb.exe')
        return {'name': 'Android Platform Tools', 'ok': True, 'state': 'already ready'}
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='retro-adb-', dir=root) as tmp:
        temporary = Path(tmp)
        archive = temporary / 'platform-tools.zip'
        digest = _download(ADB_URL, archive, MAX_ADB_ARCHIVE, progress, cancel)
        if cancel is not None and cancel.is_set(): raise InterruptedError('Setup stopped')
        if progress: progress('Extracting ADB Platform Tools', 0, 0)
        _extract_platform_zip(archive, temporary)
        if progress: progress('Finishing ADB Platform Tools', 0, 0)
        if (root / 'platform-tools').exists():
            raise FileExistsError('Platform Tools destination appeared during installation; nothing replaced')
        (temporary / 'platform-tools').rename(root / 'platform-tools')
    _verify_adb(root / 'platform-tools' / 'adb.exe')
    _write_receipt(root, 'platform-tools', ADB_URL, digest)
    return {'name': 'Android Platform Tools', 'ok': True, 'state': 'downloaded and unpacked'}


def _verify_adb(binary: Path, runner=None):
    import subprocess
    result = (runner or subprocess.run)([str(binary), 'version'], capture_output=True,
                                        text=True, shell=False, timeout=15)
    if result.returncode != 0 or 'Android Debug Bridge' not in (result.stdout or ''):
        raise RuntimeError('ADB executable check failed. Check WindowsTools/platform-tools and retry setup. '
                           + (result.stderr or '')[-600:])
    info = binary.stat()
    (binary.parent / '.checked.json').write_text(json.dumps({
        'size': info.st_size, 'mtime_ns': info.st_mtime_ns, 'executable_test_passed': True,
        'meaning': 'ADB responded to a harmless version check; no device installation attempted'
    }), encoding='utf-8')


def _find_seven_zip_stream(sfx: Path, output: Path) -> None:
    """MAME distributes a 7z self-extracting EXE, which py7zr cannot open directly.
    Carve the embedded 7z payload without ever executing the package.
    """
    signature = b'7z\xbc\xaf\x27\x1c'
    offset = -1
    with sfx.open('rb') as f:
        while f.tell() < 8 * 1024**2:
            start = f.tell()
            data = f.read(1024 * 1024 + len(signature))
            index = data.find(signature)
            if index >= 0:
                offset = start + index
                break
            if not data or len(data) < len(signature):
                break
            f.seek(start + 1024 * 1024)
        if offset < 0:
            raise RuntimeError('Official MAME package does not contain the expected 7z archive payload')
        f.seek(offset)
        with output.open('xb') as out:
            shutil.copyfileobj(f, out, 4 * 1024**2)


def _extract_chdman(archive: Path, temp: Path) -> Path:
    try:
        import py7zr
    except ImportError as exc:
        raise RuntimeError('Install the bundled Python requirements for secure 7Z extraction') from exc
    from importlib.metadata import version
    from packaging.version import Version
    if Version(version('py7zr')) < Version('1.1.3'):
        raise RuntimeError('Patched py7zr 1.1.3 or newer is required')
    with py7zr.SevenZipFile(archive, mode='r', max_extract_size=1_000_000_000) as z:
        entries = z.list()
        matches = []
        for item in entries:
            name = sanitize_archive_member(item.filename)
            if getattr(item, 'is_symlink', False):
                raise RuntimeError('Unexpected symbolic link in MAME package')
            if name.name.lower() == 'chdman.exe':
                matches.append(item.filename)
        if len(matches) != 1:
            raise RuntimeError('CHDman executable not uniquely found inside official MAME package')
        # CHDman may use shared MAME DLLs. Extract only DLLs alongside its EXE.
        parent = Path(matches[0]).parent
        targets = [matches[0]]
        for item in entries:
            name = sanitize_archive_member(item.filename)
            if name.parent == parent and name.suffix.lower() == '.dll' and (item.uncompressed or 0) <= 200 * 1024**2:
                targets.append(item.filename)
        z.extract(path=temp, targets=targets)
    chd = temp / Path(matches[0])
    if not chd.is_file():
        raise RuntimeError('CHDman not extracted')
    return chd.parent


def install_chdman(root: Path, progress=None, cancel=None) -> dict:
    if (root / 'chdman' / 'chdman.exe').is_file():
        if not _verified_chd(root):
            _check_and_mark_chd(root / 'chdman' / 'chdman.exe')
        return {'name': 'CHDman', 'ok': True, 'state': 'already ready and executable verified'}
    root.mkdir(parents=True, exist_ok=True)
    url, package_name = official_mame_release()
    with tempfile.TemporaryDirectory(prefix='retro-chd-', dir=root) as tmp:
        temporary = Path(tmp)
        package = temporary / package_name
        digest = _download(url, package, MAX_MAME_ARCHIVE, progress, cancel)
        if cancel is not None and cancel.is_set(): raise InterruptedError('Setup stopped')
        if progress: progress('Locating CHDman inside MAME release', 0, 0)
        archive = temporary / 'mame_archive.7z'
        _find_seven_zip_stream(package, archive)
        unpack = temporary / 'unpacked'; unpack.mkdir()
        if progress: progress('Extracting CHDman from MAME', 0, 0)
        source = _extract_chdman(archive, unpack)
        if cancel is not None and cancel.is_set(): raise InterruptedError('Setup stopped')
        if progress: progress('Finalizing CHDman installation', 0, 0)
        if (root / 'chdman').exists():
            raise FileExistsError('CHDman destination appeared during installation; nothing replaced')
        source.rename(root / 'chdman')
    if not (root / 'chdman' / 'chdman.exe').is_file():
        raise RuntimeError('CHDman was not actually installed into WindowsTools')
    _check_and_mark_chd(root / 'chdman' / 'chdman.exe')
    _write_receipt(root, 'chdman', url, digest)
    return {'name': 'CHDman', 'ok': True, 'state': 'downloaded, unpacked and executable verified'}



def _extract_psxtract_zip(archive: Path, destination: Path) -> Path:
    """Extract a PINNED upstream PSXtract release, rejecting unsafe ZIP entries.

    No downloaded binary or installer is executed by this function.
    """
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        if len(infos) > 3000:
            raise ValueError('PSXtract release contains too many files')
        size, unique = 0, set()
        for info in infos:
            name = sanitize_archive_member(info.filename)
            if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
                raise ValueError('Unsafe symlink in PSXtract release')
            key = str(name).replace('\\', '/').casefold()
            if key in unique:
                raise ValueError('Duplicate case-insensitive path in PSXtract release')
            unique.add(key)
            size += info.file_size
            if size > 250 * 1024**2:
                raise ValueError('PSXtract release exceeds extraction safety limit')
        z.extractall(destination)
    exact = list(destination.rglob('psxtract.exe'))
    if len(exact) != 1:
        matches = [p for p in destination.rglob('*.exe') if p.stem.casefold().startswith('psxtract')
                   and 'gui' not in p.stem.casefold()]
        if len(matches) != 1:
            raise RuntimeError('Expected one PSXtract command-line executable in pinned release')
        executable = matches[0]
    else:
        executable = exact[0]
    if executable.is_symlink() or not executable.is_file():
        raise RuntimeError('PSXtract executable missing or linked')
    return executable


def install_psxtract(root: Path, progress=None, cancel=None) -> dict:
    """Opt-in pinned third-party helper for PSN EBOOT conversion (never auto-run)."""
    dest = Path(root) / 'psxtract'
    if dest.exists():
        state = tool_status(root).get('PSXtract', {})
        if state.get('installed'):
            return {'name': 'PSXtract', 'ok': True,
                    'state': 'Pinned helper installed; real game extraction not yet verified'}
        raise FileExistsError('Existing unverified PSXtract folder; no overwrite. Review manually first.')
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='retro-psxtract-', dir=root) as directory:
        temp = Path(directory)
        archive = temp / 'psxtract-2.zip'
        digest = _download(PSXTRACT_ZIP, archive, MAX_PSXTRACT_ARCHIVE, progress, cancel)
        if digest.casefold() != PSXTRACT_SHA256:
            raise RuntimeError('PSXtract upstream SHA-256 checksum mismatch; download refused')
        if cancel is not None and cancel.is_set():
            raise InterruptedError('PSXtract setup stopped')
        if progress: progress('Checking PSXtract release archive', 0, 0)
        unpack = temp / 'unpacked'; unpack.mkdir()
        exe = _extract_psxtract_zip(archive, unpack)
        # Keep sibling DLLs, CUE lookup data and resources with the executable.
        package_dir = exe.parent
        if exe.name.casefold() != 'psxtract.exe':
            renamed = package_dir / 'psxtract.exe'
            if renamed.exists():
                raise FileExistsError('Ambiguous PSXtract executables; nothing installed')
            exe.rename(renamed)
        if cancel is not None and cancel.is_set():
            raise InterruptedError('PSXtract setup stopped')
        if dest.exists():
            raise FileExistsError('PSXtract installation folder appeared unexpectedly')
        package_dir.rename(dest)
    binfile = dest / 'psxtract.exe'
    if not binfile.is_file():
        raise RuntimeError('PSXtract executable was not installed')
    info = binfile.stat()
    (dest / '.checked.json').write_text(json.dumps({
        'size': info.st_size, 'mtime_ns': info.st_mtime_ns,
        'release_sha256': PSXTRACT_SHA256,
        'meaning': 'Official release ZIP SHA-256 checked. Actual EBOOT extraction still untested.'
    }), encoding='utf-8')
    _write_receipt(root, 'psxtract', PSXTRACT_ZIP, digest)
    return {'name': 'PSXtract', 'ok': True,
            'state': 'Checksum-verified helper installed; PSN extraction awaits real test'}


def _write_receipt(root: Path, name: str, url: str, digest: str) -> None:
    (root / (name + '.json')).write_text(json.dumps({
        'source': url, 'sha256_of_downloaded_package': digest,
        'note': 'SHA-256 is for local integrity only; does not establish publisher signature.'
    }, indent=2), encoding='utf-8')


def install_selected(names: list[str], root: Path | None = None, progress=None, cancel=None) -> list[dict]:
    root = root or tools_root()
    functions = {'Android Platform Tools': install_adb, 'CHDman': install_chdman,
                 'PSXtract': install_psxtract}
    results = []
    for idx, name in enumerate(names, 1):
        if cancel is not None and cancel.is_set():
            break
        if name not in functions:
            results.append({'name': name, 'ok': False, 'state': 'Unknown utility'})
            continue
        if progress:
            progress(f'Preparing {idx}/{len(names)}: {name}', idx - 1, len(names))
        try:
            results.append(functions[name](root, progress, cancel))
        except Exception as exc:
            results.append({'name': name, 'ok': False, 'state': str(exc)})
    return results
