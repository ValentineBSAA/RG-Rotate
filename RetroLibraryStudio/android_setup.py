"""Conservative optional USB-assisted installation. Never flashes, roots or formats."""
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path


def adb_binary() -> str | None:
    # Prefer Platform Tools installed by this application, then an existing system ADB.
    from tool_setup import tool_status
    status = tool_status().get('Android Platform Tools', {})
    if status.get('installed'):
        return status['path']
    return shutil.which('adb')


def connected_devices() -> list[tuple[str, str]]:
    adb = adb_binary()
    if not adb:
        raise FileNotFoundError('ADB Platform Tools not found on PATH; install them from Google.')
    proc = subprocess.run([adb, 'devices'], capture_output=True, text=True, timeout=20, check=True)
    lines=[]
    for ln in proc.stdout.splitlines()[1:]:
        fields=ln.strip().split()
        if len(fields)>=2:
            lines.append((fields[0],fields[1]))
    return lines


def install_local_apks(workspace: Path, serial: str, names: list[str], progress=None, cancel=None) -> list[dict]:
    adb = adb_binary()
    if not adb:
        raise FileNotFoundError('ADB not installed')
    devices = connected_devices()
    if (serial,'device') not in devices:
        raise PermissionError('Selected USB device not authorized or disconnected')
    root = workspace/'SetupPackages'
    results=[]
    for idx, basename in enumerate(names,1):
        if cancel is not None and cancel.is_set():
            break
        if Path(basename).name != basename or not basename.lower().endswith('.apk'):
            raise ValueError('Only local APK basenames supported')
        source=root/basename
        if not source.is_file() or source.is_symlink():
            raise ValueError('Missing or unsafe local APK')
        if progress:
            progress(f'Installing {idx}/{len(names)}: {basename}',idx-1,len(names))
        try:
            # No -r or -d: no silent replacement/downgrade of installed packages.
            cp=subprocess.run([adb,'-s',serial,'install',str(source)],capture_output=True,text=True,timeout=240)
            results.append({'name':basename,'ok':cp.returncode==0 and 'Success' in cp.stdout,
                            'detail':(cp.stdout+' '+cp.stderr).strip()[:300]})
        except subprocess.TimeoutExpired:
            results.append({'name':basename,'ok':False,'detail':'ADB install timed out'})
    return results
