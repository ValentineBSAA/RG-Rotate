# Retro Library Studio 1.5.0 Beta — release report

## Delivered

Complete Windows source package based on the supplied v1.4.4 archive. Includes
launcher, dependency installer, debug launcher, test runner and optional five-EXE
builder. This release is source; an EXE build/signing test was not performed.

## What changed

- Three-action Start page; fixed page actions; compact sidebar; expandable import,
  converter and artwork options; keyboard selection/focus styling and a short
  expand reveal that respects Qt's system animation hint. Long headings wrap.
- Responsive cover columns, saved user display titles, same-folder multi-disc
  variant grouping, and CUE companion metadata gathered in the scan subprocess.
  Gallery hides referenced track files; File list keeps every actual entry.
- Complete CUE-set review, missing-reference explanations, multi-file/audio
  support, conservative empty/zero-sample warnings, independent disc conversions,
  actual CHDman error details, verified-only final CHDs and optional ordered M3U.
- Disc inspection/conversion, playlist writes and batch setup reuse the isolated
  worker protocol. Windows job containment ends conversion child processes when
  their worker is killed. Forced stops can leave generated temporary output.
- ADB version-check receipt, executable readiness tied to file size/mtime,
  graceful tool-status permission errors, and preserved manual APK trust labels.
- Destination path display no longer probes NAS storage synchronously. Preview
  and copy retain worker-side destination validation and reserve checks. Transfer
  progress now explicitly reports the number of hash-verified completed files.
- Updated README, changelog, version, Windows checklist and dependency installer.

Existing import, archive, resume, SHA-256, no-overwrite, practice-mode and reserve
algorithms were retained. The storage accounting, NAS folder layout, QSettings
identity, artwork paths and receipts were retained. No user ROMs, existing
workspace configuration or imported artwork were modified during this work.

## What actually ran

**220 automated tests passed on Windows using Python 3.12 and PySide6 6.12.**
The 180 original test cases remain, with compatibility updates to UI assertions,
an explicit UTF-8 read, stricter ADB readiness expectations and a simulated
inventory-capacity fixture replacing an unsafe 512 GB truncate on NTFS. Forty
additional cases cover disc validation/conversion, playlists, executable probing,
Qt UI behavior, worker isolation and transfer feedback.

Tests include real local subprocess imports/scans/transfers, fresh and repeated
practice copies, same-size destination corruption, cancellation/resume, preserved
sources, manual APK recognition, installer queue failures/retries, CUE/BIN/audio
fixtures, verification failures and exclusive playlist creation. CHDman calls
and package downloads are mocked; these tests are not actual disc conversions.

Windows Qt widgets were instantiated/rendered with the native Windows platform
plugin, isolated settings and hidden test windows. All six pages were checked
at 100%, 110%, 125%, 140%, 150% app scales with 1240×805 and 900×620 requested
window sizes. Tests check main-action bounds, saved scale, title preferences and
saved/restored geometry. Native renders were visually inspected; an additional
render probe checked all six pages at every scale. This was an automated widget
and rendering check, not a human click-through or a Windows monitor-DPI matrix.

The real Windows job-object lifecycle test launched a CHDman-like child process,
force-killed its worker and confirmed that the child also exited.

Baseline comparison: the unmodified source produced 177 passes and two failures
in this sandbox (an inaccessible existing WindowsTools path and an implicit
Windows text-codepage read); its capacity-truncate case was stopped and excluded
from that comparison. The new package resolves those issues and runs all 220
cases without that exclusion. No baseline application behavior is claimed to be
hardware-validated by these tests.

## Still unverified

- The actual Resident Evil 2 Disc 1/Disc 2 dumps and the cause of Disc 1's failure.
  Neither those disc files nor an actual CHDman conversion log was supplied.
- Real CHDman image creation/verification and emulator M3U disc switching.
- Live authorized software downloads, package-source availability and real ADB
  or CHDman executable installation. Test dependency downloads did run.
- Your Synology SMB behavior, force-stop under a real network stall, physical
  microSD detection/capacity/copy, RG Rotate APK installs and game operation.
- Human GUI acceptance, your monitor's Windows DPI/driver behavior, first-run
  launcher/dependency setup on a clean PC and optional PyInstaller EXE output.

## Real-device checks to do next

1. Extract into a new app folder, launch, retain your current NAS library, and
   check settings/artwork/geometry and 125% layout. Do not reset or re-import.
2. Confirm `cocon-311.apk` is ready but publisher unverified; test selected-app
   preparation and the real Windows helper probes.
3. Convert the actual RE2 CUE sets. Review exact missing paths/warnings and save
   CHDman errors if Disc 1 fails. Check original hashes; create a same-game M3U
   in explicit disc order and test it in your emulator.
4. Repeat the known six-file NAS→Windows practice copy, then repeat verification:
   for unchanged fixtures expect 0 new files, 6 identical, 6/6 verified. Test stop,
   resume and a conflicting same-size file in a disposable destination.
5. Perform the physical-card preview/verified copy, eject safely, then test APK
   installation, Cocoon artwork, emulators, CHDs and disc switching on RG Rotate.

Use the full WINDOWS_TEST_CHECKLIST.md included in the package.
