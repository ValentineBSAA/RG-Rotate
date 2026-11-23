"""Conservative Windows SD-card discovery; no formatting operations."""
from __future__ import annotations
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Volume:
    root: Path
    label: str
    filesystem: str
    total: int
    free: int
    removable: bool


def list_windows_volumes() -> list[Volume]:
    if os.name != 'nt':
        return []
    import ctypes
    from ctypes import wintypes
    kernel=ctypes.windll.kernel32
    roots=[]
    mask=kernel.GetLogicalDrives()
    for index in range(26):
        if not mask & (1<<index):continue
        root=Path(chr(ord('A')+index)+':\\')
        kind=kernel.GetDriveTypeW(str(root))
        if kind not in (2,3): continue  # removable or fixed, not network/optical
        try:
            usage=shutil.disk_usage(root)
            volume_name=ctypes.create_unicode_buffer(261)
            fs_name=ctypes.create_unicode_buffer(261)
            ok=kernel.GetVolumeInformationW(str(root),volume_name,261,None,None,None,fs_name,261)
            label=volume_name.value if ok else ''
            fs=fs_name.value if ok else 'Unknown'
            roots.append(Volume(root,label,fs,usage.total,usage.free,kind==2))
        except OSError:
            continue
    return roots


def system_drive_root() -> Path | None:
    if os.name!='nt':return None
    return Path(os.environ.get('SystemDrive','C:')+'\\')


def validate_physical_root(target: Path) -> Volume:
    if os.name!='nt':
        raise ValueError('Physical-card transfers are available only on Windows; use Simulation mode elsewhere')
    if target.resolve()!=Path(target.anchor).resolve():
        raise ValueError('Physical-card destination must be the drive root')
    sysroot=system_drive_root()
    if sysroot and target.resolve()==sysroot.resolve():
        raise ValueError('REFUSED: Windows system drive is not a microSD destination')
    vol=next((x for x in list_windows_volumes() if x.root.resolve()==target.resolve()),None)
    if vol is None:
        raise ValueError('Target is not an available Windows drive')
    if vol.total < 16*1024**3:
        raise ValueError('Target drive is unexpectedly small; verify it is the correct card')
    return vol
