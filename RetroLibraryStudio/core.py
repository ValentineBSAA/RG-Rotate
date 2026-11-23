"""File operations for Retro Library Studio. No Qt dependency."""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable

CAPACITY = 512_000_000_000  # marketed 512 GB, decimal bytes
GIB = 1024 ** 3
COMPANION_BUDGET = 8 * GIB
FREE_RESERVE = 8 * GIB
# Hard cap for game/installer/artwork bytes; no empty 8GiB companion file is created.
GAME_BUDGET = CAPACITY - COMPANION_BUDGET - FREE_RESERVE
MAX_ARCHIVE_BYTES = 32_000_000_000  # explicit safety limit per archive
MAX_ARCHIVE_FILES = 10_000
ROM_EXT = {".chd", ".cue", ".bin", ".img", ".iso", ".cso", ".pbp", ".m3u", ".ccd", ".ecm", ".sub", ".mdf", ".mds", ".nrg", ".gba", ".gb", ".gbc", ".nes", ".sfc", ".smc", ".md", ".gen", ".nds", ".n64", ".z64", ".v64", ".gdi", ".cdi"}
ARCHIVE_EXT = {".zip", ".7z"}
SUPPORTED = ROM_EXT | ARCHIVE_EXT
SYSTEM_DIR = {"PS1": "psx", "PSP": "psp", "GBA": "gba", "GB": "gb", "GBC": "gbc", "NES": "nes", "SNES": "snes", "Genesis": "md", "Nintendo DS": "nds", "Nintendo 64": "n64", "Dreamcast": "dc"}
IGNORED_FOLDERS = {".retro-library", ".retro-tmp"}
Progress = Callable[[str, int, int], None]


@dataclass(frozen=True)
class Entry:
    path: Path
    label: str
    system: str
    size: int
    extension: str


def pretty_bytes(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:,.2f} GB"
    if n >= 1_000_000:
        return f"{n / 1_000_000:,.1f} MB"
    if n >= 1_000:
        return f"{n / 1_000:,.1f} KB"
    return f"{n:,} B"


def within(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def safe_walk(base: Path, cancel=None) -> Iterable[Path]:
    """Walk without following symlinks or directory junctions."""
    if not base.is_dir() or base.is_symlink():
        return
    for directory, dirs, files in os.walk(base, followlinks=False):
        if cancel is not None and cancel.is_set():
            return
        dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS and not (Path(directory) / d).is_symlink()
                   and not (os.name == "nt" and bool(os.stat(Path(directory) / d, follow_symlinks=False).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT))]
        for name in files:
            if cancel is not None and cancel.is_set():
                return
            p = Path(directory) / name
            if p.is_file() and not p.is_symlink() and not p.name.endswith(".retro-part"):
                yield p


def inventory(workspace: Path, cancel=None, progress: Progress | None = None) -> tuple[list[Entry], int, int]:
    entries, total, count = [], 0, 0
    for file in safe_walk(workspace, cancel=cancel):
        if cancel is not None and cancel.is_set():
            break
        try:
            size = file.stat().st_size
        except OSError:
            continue
        total += size
        count += 1
        if progress is not None and count % 200 == 0:
            progress(f'Checking your virtual card: {count:,} files found', count, 0)
        parts = file.relative_to(workspace).parts
        system = next((key for key, value in SYSTEM_DIR.items() if len(parts) >= 2 and parts[:2] == ("ROMs", value)), "Other")
        if file.suffix.lower() in ROM_EXT or system != "Other":
            # A CUE is a tiny text descriptor, not the game's storage size.
            # Only the display entry uses this logical total. The virtual-card
            # usage counter continues counting every physical file exactly once.
            display_size = size
            if file.suffix.lower() in ('.cue', '.m3u'):
                try:
                    components = _cue_companions(file)
                    display_size += sum(p.stat().st_size for p in dict.fromkeys(components))
                except (OSError, ValueError):
                    pass
            entries.append(Entry(file, file.stem, system, display_size, file.suffix.lower()))
    return entries, total, count


def incoming_inventory(folder: Path, limit: int = 30000, cancel=None) -> tuple[list[Entry], int]:
    """Inspect supported existing downloads, not just app-created downloads."""
    out = []
    total = 0
    for f in safe_walk(folder, cancel=cancel):
        if cancel is not None and cancel.is_set():
            break
        if f.suffix.lower() not in SUPPORTED:
            continue
        try:
            size = f.stat().st_size
        except OSError:
            continue
        total += size
        out.append(Entry(f, f.stem, "Unassigned", size, f.suffix.lower()))
        if len(out) >= limit:
            break
    return out, total


def sanitize_archive_member(name: str) -> Path:
    """Reject dangerous path segments on Windows and POSIX, including ADS."""
    normalized = name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if (not normalized or normalized.startswith("/") or "\x00" in normalized
            or re.match(r"^[A-Za-z]:", normalized)):
        raise ValueError(f"Unsafe archive path: {name!r}")
    parts = pure.parts
    if not parts or any(p in {".", "..", ""} for p in parts):
        raise ValueError(f"Unsafe archive path: {name!r}")
    for part in parts:
        if ":" in part or part.rstrip(" .") != part or any(ord(c) < 32 for c in part):
            raise ValueError(f"Unsafe Windows archive name: {name!r}")
        if re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part):
            raise ValueError(f"Reserved Windows filename: {name!r}")
    return Path(*parts)


def verify_zip(z: zipfile.ZipFile) -> int:
    infos = z.infolist()
    if len(infos) > MAX_ARCHIVE_FILES:
        raise ValueError("Archive contains too many files")
    total = 0
    for member in infos:
        sanitize_archive_member(member.filename)
        mode = member.external_attr >> 16
        if stat.S_IFMT(mode) == stat.S_IFLNK:
            raise ValueError("ZIP contains a symbolic link")
        if member.flag_bits & 1:
            raise ValueError("Encrypted ZIP requires password; not supported")
        if member.is_dir():
            continue
        total += member.file_size
        if total > MAX_ARCHIVE_BYTES:
            raise ValueError("Archive would expand beyond the 32 GB safety limit")
        if member.file_size > 50_000_000 and member.compress_size and member.file_size / member.compress_size > 10_000:
            raise ValueError("Suspicious compression ratio; possible archive bomb")
    return total


def verify_7z(z) -> int:
    infos = z.list()
    if len(infos) > MAX_ARCHIVE_FILES:
        raise ValueError("Archive contains too many files")
    total = 0
    for info in infos:
        sanitize_archive_member(info.filename)
        if getattr(info, "is_symlink", False):
            raise ValueError("7Z symbolic links are not allowed")
        if not info.is_directory:
            total += int(info.uncompressed or 0)
        if total > MAX_ARCHIVE_BYTES:
            raise ValueError("Archive would expand beyond the 32 GB safety limit")
    return total


def sha256(file: Path, cancel=None) -> str:
    digest = hashlib.sha256()
    with file.open("rb") as stream:
        while True:
            if cancel is not None and cancel.is_set():
                raise InterruptedError('Hash verification cancelled')
            block = stream.read(4 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def same_file(a: Path, b: Path, cancel=None) -> bool:
    if cancel is not None and cancel.is_set():
        raise InterruptedError('File comparison cancelled')
    return a.stat().st_size == b.stat().st_size and sha256(a, cancel) == sha256(b, cancel)


def copy_atomic(source: Path, dest: Path, progress: Progress | None = None, cancel=None) -> str:
    """Never overwrite an existing different file. Copy through a temporary sibling."""
    if source.is_symlink() or not source.is_file():
        raise ValueError(f"Not a regular file: {source}")
    if dest.exists():
        if not dest.is_file():
            raise FileExistsError(f"Destination occupied: {dest}")
        if same_file(source, dest, cancel):
            return "unchanged"
        raise FileExistsError(f"Conflicting file exists (not overwritten): {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    size = source.stat().st_size
    # Remote SMB free-space queries can hang indefinitely. A prior optional NAS
    # capacity probe is advisory; let the OS report ENOSPC on remote writes.
    from storage_probe import is_network_path
    if not is_network_path(dest.parent) and shutil.disk_usage(dest.parent).free < size:
        raise OSError(f"Insufficient physical disk space for {dest.name}")
    part = dest.parent / (dest.name + ".retro-part")
    if part.exists():
        # A hard-stopped isolated import may leave a partial on the NAS.
        # The same verified-prefix resume algorithm used for card transfers can
        # finish it, but will never overwrite an incompatible partial.
        from sync_engine import _copy_verified
        completed = 0
        def report_more(n: int) -> None:
            nonlocal completed
            completed += n
            if progress:
                progress(source.name, completed, size)
        state, _ = _copy_verified(source, dest, report_more, cancel)
        return state
    copied = 0
    last_reported = 0
    try:
        with source.open("rb") as inp, part.open("xb") as out:
            while True:
                if cancel is not None and cancel.is_set():
                    raise InterruptedError("Operation cancelled")
                block = inp.read(4 * 1024 * 1024)
                if not block:
                    break
                out.write(block)
                copied += len(block)
                if progress and (copied - last_reported >= 32 * 1024 * 1024 or copied == size):
                    progress(source.name, copied, size)
                    last_reported = copied
        if dest.exists():  # defensive race check
            raise FileExistsError(f"Destination appeared during copy: {dest}")
        part.replace(dest)
        return "copied"
    finally:
        part.unlink(missing_ok=True)


def _cue_companions(source: Path, visited: set[Path] | None = None) -> list[Path]:
    """Resolve accompanying cue tracks and m3u playlists without escaping parent."""
    if source.suffix.lower() not in {".cue", ".m3u"}:
        return []
    visited = set() if visited is None else visited
    if source.resolve() in visited:
        return []
    visited.add(source.resolve())
    try:
        raw_bytes = source.read_bytes()
        if len(raw_bytes) > 4 * 1024 * 1024:
            raise ValueError('Disc descriptor is unexpectedly large')
        try:
            raw = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            raw = raw_bytes.decode('cp1252')
    except OSError:
        return []
    if source.suffix.lower() == ".cue":
        names = re.findall(r'^\s*FILE\s+(?:"([^"]+)"|(\S+))', raw, re.I | re.M)
        names = [a or b for a, b in names]
    else:
        names = [x.strip() for x in raw.splitlines() if x.strip() and not x.startswith("#")]
    companions = []
    for name in names:
        rel = Path(name.replace("\\", "/"))
        if rel.is_absolute() or ".." in rel.parts or ":" in name:
            raise ValueError(f"Unsafe reference inside {source.name}: {name}")
        p = (source.parent / rel).resolve()
        if not within(p, source.parent) or not p.is_file() or p.is_symlink():
            raise FileNotFoundError(f"{source.name} references missing/unsafe file {name}")
        companions.append(p)
        companions.extend(_cue_companions(p, visited))
    return companions


def import_candidates(paths: list[Path]) -> list[Path]:
    """Exclude tracks/cues already included by a selected cue or playlist."""
    companions = set()
    errors = set()
    for p in paths:
        if p.suffix.lower() in {".cue", ".m3u"}:
            try:
                companions.update(_cue_companions(p))
            except (OSError, ValueError):
                # Still submit the cue, so its missing companion is surfaced in the import report.
                pass
    return [p for p in dict.fromkeys(paths) if p not in companions]


def expected_import_size(source: Path) -> int:
    """Conservative preflight upper bound, avoiding huge unwanted imports."""
    suffix = source.suffix.lower()
    if suffix == ".zip":
        with zipfile.ZipFile(source) as z:
            return verify_zip(z)
    if suffix == ".7z":
        try:
            import py7zr
            from importlib.metadata import version
            from packaging.version import Version
            if Version(version("py7zr")) < Version("1.1.3"):
                raise RuntimeError("py7zr 1.1.3+ is required for safe 7Z extraction")
        except ImportError as exc:
            raise RuntimeError("Install dependencies: pip install -r requirements.txt") from exc
        with py7zr.SevenZipFile(source, mode="r", max_extract_size=MAX_ARCHIVE_BYTES) as archive:
            return verify_7z(archive)
    companions = _cue_companions(source)
    return sum(x.stat().st_size for x in dict.fromkeys([source] + companions))

def _import_one(source: Path, workspace: Path, system: str, progress: Progress | None, cancel) -> tuple[int, int, int]:
    if system not in SYSTEM_DIR:
        raise ValueError("Choose a recognized system")
    rom_root = workspace / "ROMs" / SYSTEM_DIR[system]
    if not source.is_file() or source.is_symlink():
        raise ValueError("Only regular game files and ZIP/7Z archives are supported")
    if source.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported file: {source.name}")
    if within(source, workspace):
        raise ValueError("Selected file already belongs to the virtual card")
    if source.suffix.lower() in ARCHIVE_EXT:
        # Work outside the counted virtual-card area until extraction passes checks.
        with tempfile.TemporaryDirectory(prefix="retro-import-", dir=workspace.parent) as temp:
            tempdir = Path(temp)
            if source.suffix.lower() == ".zip":
                with zipfile.ZipFile(source) as z:
                    unpacked = verify_zip(z)
                    if shutil.disk_usage(tempdir).free < unpacked:
                        raise OSError("Not enough free space for temporary archive extraction")
                    for member in z.infolist():
                        if cancel is not None and cancel.is_set():
                            raise InterruptedError("Operation cancelled")
                        target = tempdir / sanitize_archive_member(member.filename)
                        if member.is_dir():
                            target.mkdir(parents=True, exist_ok=True)
                            continue
                        target.parent.mkdir(parents=True, exist_ok=True)
                        # stream through bounded buffers
                        with z.open(member) as inp, target.open("xb") as out:
                            while True:
                                if cancel is not None and cancel.is_set():
                                    raise InterruptedError('ZIP extraction cancelled')
                                block = inp.read(1024 * 1024)
                                if not block:
                                    break
                                out.write(block)
            else:
                try:
                    import py7zr
                    from importlib.metadata import version
                    from packaging.version import Version
                    if Version(version("py7zr")) < Version("1.1.3"):
                        raise RuntimeError("py7zr 1.1.3+ is required for safe 7Z extraction")
                except ImportError as exc:
                    raise RuntimeError("Install dependencies: pip install -r requirements.txt") from exc
                with py7zr.SevenZipFile(source, mode="r", max_extract_size=MAX_ARCHIVE_BYTES) as z:
                    unpacked = verify_7z(z)
                    if shutil.disk_usage(tempdir).free < unpacked:
                        raise OSError("Not enough free space for temporary archive extraction")
                    z.extractall(path=tempdir)
            extracted = list(safe_walk(tempdir))
            if not extracted:
                raise ValueError("Archive contained no usable files")
            if any(f.suffix.lower() in ARCHIVE_EXT for f in extracted):
                raise ValueError("Nested archives aren't automatically unpacked")
            if not any(f.suffix.lower() in ROM_EXT for f in extracted):
                raise ValueError("Archive contains no recognized PS1/PSP game files")
            folder = rom_root / source.stem
            copied, skipped, bytes_added = 0, 0, 0
            for f in extracted:
                if cancel is not None and cancel.is_set():
                    raise InterruptedError("Operation cancelled")
                # Extra safety: ensure paths remain inside extracted tree.
                if not within(f, tempdir):
                    raise ValueError("Archive resolved outside extraction directory")
                rel = f.relative_to(tempdir)
                result = copy_atomic(f, folder / rel, progress, cancel)
                copied += result == "copied"
                skipped += result == "unchanged"
                bytes_added += f.stat().st_size if result == "copied" else 0
            return copied, skipped, bytes_added
    if source.suffix.lower() in {".cue", ".m3u"}:
        collection = [source] + _cue_companions(source)
        folder = rom_root / source.stem
    else:
        collection = [source]
        folder = rom_root
    copied, skipped, bytes_added = 0, 0, 0
    for f in dict.fromkeys(collection):
        rel = f.relative_to(source.parent)
        result = copy_atomic(f, folder / rel, progress, cancel)
        copied += result == "copied"
        skipped += result == "unchanged"
        bytes_added += f.stat().st_size if result == "copied" else 0
    return copied, skipped, bytes_added


def import_files(paths: list[Path], workspace: Path, system: str, progress: Progress | None = None, cancel=None) -> tuple[int, int, list[str]]:
    workspace.mkdir(parents=True, exist_ok=True)
    _, occupied, _ = inventory(workspace, cancel=cancel)
    if cancel is not None and cancel.is_set():
        return 0, 0, []
    if occupied > CAPACITY - FREE_RESERVE:
        return 0, 0, ["Virtual card already exceeds the reserved-space limit"]
    copied, skipped, errors = 0, 0, []
    paths = import_candidates(paths)
    for i, source in enumerate(paths, 1):
        if cancel is not None and cancel.is_set():
            break
        if progress:
            progress(f"Importing {i}/{len(paths)}: {source.name}", i - 1, len(paths))
        try:
            estimate = expected_import_size(source)
            # Companion budget is separate; unused companion space is kept available.
            companion_used = sum(p.stat().st_size for p in safe_walk(workspace / "CompanionData", cancel=cancel))
            if cancel is not None and cancel.is_set():
                break
            if occupied + estimate + max(0, COMPANION_BUDGET - companion_used) + FREE_RESERVE > CAPACITY:
                raise OSError("Would violate the 8 GiB companion budget or 8 GiB free-space reserve")
            c, s, bytes_added = _import_one(source, workspace, system, progress, cancel)
            copied += c
            skipped += s
            occupied += bytes_added
            if progress:
                progress("@capacity", occupied, CAPACITY)
        except Exception as exc:
            errors.append(f"{source.name}: {exc}")
    return copied, skipped, errors


def prepare_layout(workspace: Path) -> None:
    for name in ("ROMs/psx", "ROMs/psp", "ROMs/gba", "ROMs/gb", "ROMs/gbc", "ROMs/nes", "ROMs/snes", "ROMs/md", "ROMs/nds", "ROMs/n64", "ROMs/dc", "BIOS", "Media", "CocoonData", "SetupPackages", "CompanionData/Memory", "CompanionData/Settings", ".retro-library"):
        (workspace / name).mkdir(parents=True, exist_ok=True)


def filesystem_name(path: Path) -> str | None:
    """Read the selected volume's Windows filesystem; never format it."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        import ctypes.wintypes
        root = ctypes.create_unicode_buffer(1024)
        fs_name = ctypes.create_unicode_buffer(128)
        kernel = ctypes.windll.kernel32
        if not kernel.GetVolumePathNameW(str(path.resolve()), root, len(root)):
            return None
        if not kernel.GetVolumeInformationW(root.value, None, 0, None, None, None, fs_name, len(fs_name)):
            return None
        return fs_name.value
    except (OSError, AttributeError, ValueError):
        return None


def transfer(workspace: Path, target: Path, progress: Progress | None = None, cancel=None) -> tuple[int, int, list[str]]:
    if not workspace.is_dir() or not target.is_dir():
        raise ValueError("Workspace and target must exist")
    if within(target, workspace) or within(workspace, target):
        raise ValueError("Virtual workspace and target must be separate locations")
    candidates = list(safe_walk(workspace))
    if not candidates:
        raise ValueError("Virtual card is empty")
    total = sum(p.stat().st_size for p in candidates)
    fs = filesystem_name(target)
    if fs and fs.upper() == "FAT32" and any(p.stat().st_size >= (1 << 32) for p in candidates):
        raise OSError("The microSD target is FAT32; files of 4 GiB or larger cannot fit. Use a compatible filesystem such as exFAT after checking device support.")
    if total > CAPACITY:
        raise ValueError("Staged files exceed 512 GB")
    if total > shutil.disk_usage(target).free:
        # Some may already exist; conservative safe preflight.
        raise OSError("Destination does not have enough free space for a full copy")
    # Preserve known empty directories used by launchers/companion without
    # transferring private bookkeeping files or changing existing data.
    for relative in ("ROMs/psx", "ROMs/psp", "BIOS", "Media", "CompanionData/Memory", "CompanionData/Settings"):
        (target / relative).mkdir(parents=True, exist_ok=True)
    copied = skipped = 0
    errors: list[str] = []
    for index, source in enumerate(candidates, 1):
        if cancel is not None and cancel.is_set():
            break
        rel = source.relative_to(workspace)
        if progress:
            progress(f"Transferring {index}/{len(candidates)}: {rel}", index - 1, len(candidates))
        try:
            dest = target / rel
            result = copy_atomic(source, dest, progress, cancel)
            copied += result == "copied"
            skipped += result == "unchanged"
        except Exception as exc:
            errors.append(f"{rel}: {exc}")
    return copied, skipped, errors
