# v1.5.3 Beta — File format badges and artwork fallback (2026-11-23)

- My Games cover tiles show actual **CHD, BIN/CUE, M3U, ISO, PBP**, etc. file-format badges. Click for the stored filename, type and truthful verification limits. A CHD extension is **not** proof of CHDman verification or successful game launch.
- Legacy CUE/BIN imports display BIN/CUE until a CHD is actually present. M3U indicates a playlist of separate discs, not a combined CHD.
- Artwork catalog now falls back from the Libretro thumbnail site to the official Libretro per-platform GitHub tree when the primary index fails. PNG download/preview also falls back to the official GitHub raw mirror. User can still browse or import their own cover. These paths are tested with simulated outages but real network availability is external.
- A new regression suite covers badge classification, artwork fallback, and unsafe redirects.
- Local clean-extraction: **230 passed, 15 skipped**. Actual Windows artwork/CHDman/NAS acceptance remains pending.

# v1.5.2 Beta — Windows acceptance candidate (2026-11-23)

- Packaged the GitHub CI-tested v1.5.1 PS1 CUE/BIN → CHD import pipeline into a Windows launchable source distribution.
- Canonicalized Windows ZIP/CUE companion paths so referenced BIN tracks do not reappear as standalone game imports, with regression coverage.
- Preserved tested NAS import/cancellation, verified practice copy, CHD/M3U, artwork and one unified import progress workflow.
- Local clean-extraction source test: **226 passed, 15 skipped**; matching GitHub CI core: **241 Windows passed; 240 Linux passed, 1 skipped**.
- **Release gate still open:** real Windows CHDman conversion of Clock Tower with its two BIN tracks, online artwork, mapped NAS behavior for v1.5.2, and RG Rotate device testing.

# v1.5.1 Beta — Automatic PS1 CHD/M3U Import (November 23, 2026)

- Connected existing CUE inspection, CHDman create/verify, M3U generation and safe staging to the **normal Add My Games import**. The game enters My Games as a verified CHD, not an individual CUE/BIN track, when conversion succeeds.
- One unified progress flow now reports inspection, conversion, verification, staging and cover retrieval. Originals remain unchanged; interruptions cannot release partial .chd output as playable.
- Fixed My Games' misleading CUE-only 226–228-byte display by accounting for referenced BIN tracks when still in the legacy format.
- Supports importing complete CUE/BIN sets from ZIP/7Z through local temporary extraction. Disc 1/Disc 2 remain independent CHD files and an M3U references them in order.
- Improved artwork fallback for English patches while keeping ambiguous edition covers user-reviewable.
- **GitHub Actions CI:** initially exposed Windows ZIP/CUE companion aliases, fixed by comparing canonical file paths and adding a regression test. [Run 45138220982](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45138220982) passed: **Windows 241 tests; Linux 240 tests with 1 skip**.
- Real CHDman execution, live artwork providers, user Synology SMB, physical card and Android Cocoon setup still require acceptance testing.

# v1.5.0 Beta — Guided setup and PlayStation disc conversion (November 22, 2026)

- Reorganized Start around Add My Games, Prepare My RG Rotate and Copy to My microSD.
- Added fixed primary actions, expandable secondary options, keyboard-focus
  highlights, compact navigation and optional system-controlled reveal motion.
- Gallery responds to available width, supports saved display-title overrides,
  groups same-title disc variants and hides CUE-referenced tracks from tiles.
  All actual files remain in File list.
- Added read-only CUE validation for multiple FILE entries, relative paths,
  quoted filenames, track declarations and audio. Missing references explain
  the expected path; empty/zero samples warn without rewriting sources.
- Added independent per-disc conversion reports, actual CHDman failure detail,
  verified-only CHD publication and opt-in ordered M3U creation without overwrites.
- Reused the import-worker protocol for disc checks, conversion, playlist writes
  and batch software preparation. Windows job containment stops CHDman children
  on worker force-stop. No new executable is needed by the EXE builder.
- ADB setup performs a harmless executable version check and caches readiness
  against size/mtime. Permission-denied tool status checks no longer crash the
  app-status scanner. Manual APK publisher-unverified labels remain intact.
- Removed synchronous destination stat/disk-space probes from navigation and
  preview entry points. The transfer worker retains its actual safety checks.
- Added live completed-file verification counts without changing copy safety.
- Retained the 180 baseline test cases; updated UI wiring assertions, explicit
  UTF-8 test reads and stricter ADB expectations. Replaced the test that attempted
  a real 512 GB truncate on NTFS with simulated inventory capacity.
- Added Windows dependency installer, release report and updated acceptance checks.

# v1.4.4 • Remember Practice Mode (November 22, 2026)

- Fixed a Windows acceptance-test failure: after restarting, the saved `PracticeTransfer` folder was treated as a real microSD destination and rejected for not being a drive root.
- Saved destination mode alongside destination path, with migration for the exact old default practice folder.
- Ordinary folders chosen as destinations are explicitly marked Practice; drive roots remain Real Card destinations and must pass Windows drive checks.
- New preview preflight validates the destination mode BEFORE saying the preview succeeded. Unknown old folder choices must be confirmed as practice instead of silently bypassing real-card safeguards.
- Changing destination or mode resets stale transfer progress; no previous run can masquerade as the current run.
- Added 6 regression tests for remembered practice mode, known-folder migration, physical-drive safety, and verified second copies.
- Existing NAS imports, Cocoon installer, artwork, verification, original-file preservation and 8 GiB real-card reserve are unchanged.
- No live Windows GUI test of this version has been performed here; requires user acceptance test.

# v1.4.3 • Incremental Transfer Clarity (November 22, 2026)

- Confirmed user-reported result: first NAS-to-practice transfer copied and hash-verified 6/6 files; repeat preview estimated 0 B, but **did not** prove a second hash verification.
- Fixed stale 100% transfer bar and previous run results displayed after a new preview.
- Added explicit size-match file count and preview-only warning. Exact 0 B preview now offers one-click SHA-256 verification of existing files.
- Distinct practice-folder and real-card completion messages, with last-run history separated from current progress.
- Reset and re-label progress when selecting a different destination, improve scrolling to next action.
- Added tests for 6-file first copy, second copy with 0 new/6 identical and hash verification, same-size corruption rejection, and cancelled/empty result reporting. Preserved all 168 prior tests.
- Windows Qt and actual Synology/physical microSD remain separate acceptance tests.

---

# v1.4.2 Cocoon APK Recognition Fix

- Recognize the user-tested `cocon-311.apk` name, with a strict checked user-import receipt and matching SHA-256; report the APK as **publisher unverified**, not as officially sourced.
- Preserve the existing Cocoon official-download workflow and skip an unnecessary duplicate download when a matching user-supplied APK is present.
- Prevent unrelated similar names such as `coconut-tools.apk` from being assigned as Cocoon.
- Keep the existing Windows/NAS import, artwork, copy/verification, CHDman and responsive UI implementation unchanged.
- Add dedicated regression tests covering the exact user-reported APK name and preparation statuses.

# v1.4.1: Cocoon APK import and installer-status repair

- Fix a repeat-navigation bug: opening Install Apps while choosing an APK launched a background NAS status scan that consumed the sole operation slot, preventing the import and producing no clear confirmation.
- APK imports now use the isolated import helper (same Stop-capable architecture as game imports), rather than a Qt worker thread that could block on NAS I/O.
- APK capacity accounting is checked once per batch, and identical existing APKs avoid the full inventory.
- Success dialog names the exact `SetupPackages` destination and added files; errors and zero imports produce explicit failure dialogs.
- Installer status is refreshed on completion without a second scan at import start.
- Added six targeted APK subprocess/duplicate/failure/cancellation/UI-race regression tests; 164 automated tests passed in Linux source environment.
- No claim of actual Synology network I/O or Windows GUI verification. No changes to ROM files, artwork, verified SD transfer logic, or the 8 GiB budgets.

---

# v1.4.0 Day-One Beta: Verified Card Transfer

- Converted microSD **preflight and verified copy** from main-process QThread to isolated, cancellable `RetroLibraryTransfer` subprocess, matching the already tested NAS import architecture.
- Added cooperative Stop and a separately confirmed Force Stop fallback when the copy is stalled in Windows/SMB file I/O. Original files are not deleted. Partial `.retro-part` files must be reverified before resume.
- Added clear SHA-256 verification phase feedback instead of leaving an unexplained 100% copy progress bar while hashes are still running.
- Recheck real-card destination and size before final confirmation, while retaining existing capacity, free-space, overwrite and filesystem safeguards.
- Added instant day-one readiness summary (cached, no synchronous NAS scan) and example Resident Evil Gore Edition cover for manual artwork assignment.
- Windows EXE build now produces **five** files, including `RetroLibraryTransfer.exe`.
- Extended automated tests: transfer-worker preview/copy/conflict/retry/cancel and GUI packaging assertions; **158 passing tests**, but no live Windows Qt or physical-card test here.

---

# Retro Library Studio v1.3.1 - Manual Game Artwork Search

## Added
- **Search for a game cover** on My Games works in gallery and list modes. Pick an imported game, type any alternate search title, and see catalog matches.
- Per-game search dialog shows a list of results, a **Preview selected** action (downloaded only to the Windows thumbnail cache), and an explicit **Use selected cover** confirmation.
- For special editions such as `Resident Evil Gore Edition`, the user may search `Resident Evil` manually; the ROM's filename and binary content remain unchanged.
- **Choose image from PC instead** remains available if the online artwork index has no appropriate title.
- Search, preview and save reuse the isolated stop-capable artwork helper. Only final approved cover goes to `Media/BoxArt` on the virtual card. Local previews are cached on Windows.

## Preserved
- Existing artwork gallery, automatic matching with conservative edition handling, NAS import and stop, virtual 512 GB accounting, Cocoon default, Ninite-style setup, verified copy engine, and 8 GiB companion plus 8 GiB free-space limits.

## Validation
- 151 automated regression tests, including manual query sorting, shortened title search, offline cached catalog, NAS-safe preview, host restrictions and subprocess search.
- Real Windows GUI rendering, live Libretro downloads, mapped Synology NAS, and RG Rotate hardware are **not** validated in this environment.

---

# Retro Library Studio Changelog

## v1.3.0 Guided Beta · Artwork Gallery (November 21, 2026)

- **My Games:** cover gallery is the default view, with local thumbnail caching, readable names, platform/size labels, text search, per-system filtering, a file-list toggle, and paged batches of 48 tiles to limit memory use. The window's existing 100–150% scaling remains available.
- **Automatic artwork after imports:** background cover lookup starts after successful imports. Existing v1.2.3 workspaces also receive a one-time lookup. An opt-out checkbox is on My Games; the bottom task bar shows current work.
- **Conservative matches:** online Libretro directory index used for suggestions; only names identical after normalization of common region/disc tags are downloaded without review. Special-edition titles are not stripped. Resident Evil Gore Edition is intentionally a review case, not silently mapped to plain Resident Evil.
- **Fix wrong cover:** per-game online candidate picker or local PNG/JPG/WEBP. Explicit permission is required for replacements. Covers are staged atomically into `Media/BoxArt` and Windows-local previews are cached for fast NAS scrolling.
- **NAS robustness:** `artwork_worker.py` isolates slow catalog retrieval, NAS file presence checks, image reads and art writes from the main Qt thread. Stop can terminate it without stopping the application. Game ROMs are never edited, renamed or deleted by artwork tasks.
- **Offline reuse:** if a cover exists on the NAS but its Windows thumbnail cache has been cleared, Find missing covers can restore the local preview without needing a network download.
- **Windows EXE build:** added a fourth `RetroLibraryArtwork.exe` helper. All four EXEs must remain together.
- **Tests:** 143 pure-Python tests pass, including artwork matching, atomic cover saves, subprocess helper, simulated forced termination and all prior import/transfer tests.
- **Not verified here:** live Libretro download, Synology SMB artwork I/O, Windows PySide6 rendering, Cocoon Android art integration and actual RG Rotate hardware.

## v1.2.3 Guided Beta · Isolated NAS Imports (November 21, 2026)

- **Fix:** My Games imports ran as Qt worker threads and could remain stuck on "Stopping: Importing Selected Games" when Windows was waiting on Synology SMB I/O. Both Add Game Files and Add Folder now run in a disposable `import_worker.py` subprocess.
- **Stop sequence:** request cooperative cancellation, then end the import helper if it remains blocked. Never report a stopped task as finished while the child is still running; preserve GUI navigation and the original files.
- **Incomplete-file recovery:** copied game data is published only after full file completion. An unexpected hard-stop can leave a `.retro-part`; importing that same source again checks its existing bytes and resumes a matching partial, refusing conflicting ones.
- **Windows EXE packaging:** new `RetroLibraryImport.exe` helper accompanies `RetroLibraryStudio.exe` and `RetroLibraryScan.exe`.
- **Regression coverage:** local subprocess success, folder import, overlapping-folder rejection, forced-stalled-worker termination, and matching/mismatching `.retro-part` resume safety. Windows Qt and the real NAS still require acceptance testing.
- Kept v1.2.2 software setup, virtual-card location and read-only scans, Cocoon default, artwork, CHD conversion, and physical-card transfer behavior.


## v1.2.2 Guided Beta · Safe Stop (November 21, 2026)

### Fixed / improved
- **Cancellable NAS scans:** checking the virtual card, counting files before a location change, and inspecting APK status now use a dedicated, disposable **read-only child process**. The Stop button requests graceful termination and forcibly ends only that read-only child if Windows/SMB won't respond. It does **not** kill an active writer.
- **No stuck card-location chooser:** when a scan is stopped to change workspace, the folder chooser can open after the scan exits. Closing during a scan requests cancellation and closes when the child has finished.
- **No repeated close dialogs:** when the user confirms "stop and close", the app closes automatically after the running operation acknowledges stop. Original files are never deleted by cancellation.
- **More cooperative import/transfer stops:** interrupted transfers check cancellation during SHA-256 verification and planning; ZIP extraction checks cancellation per 1 MiB block; imports check cancellation during their initial inventory. Existing original files remain intact. Interrupted transfer partials remain for verification/resume.
- **NAS-friendly behavior:** remote virtual-card existence checks no longer block first-window startup, remote APK readiness inspection no longer runs on the Qt UI thread, and remote file imports do not block on a synchronous SMB free-space query (actual write errors still apply).
- **Readable cancellation feedback:** the Stop button clearly distinguishes a stoppable read-only scan from a cooperative file-writing operation and warns when Windows is still servicing a network I/O request.
- **Windows EXE build:** optional PyInstaller script now builds `RetroLibraryStudio.exe` together with `RetroLibraryScan.exe` so the GUI can capture the helper's scan results. Both must remain in the same folder.
- Preserved v1.2.1 workspace, Cocoon default, 512 GB planning profile, 8 GiB companion budget, 8 GiB physical-card free-space reserve, installers, CHD conversion, and safe transfer logic.

### Verification
- **117 automated tests passed**, including 10 cancellation/worker-specific tests and the 107 existing tests.
- Read-only helper was executed as a real subprocess against a local test card; child termination was tested with a deliberately stalled worker.
- **Not verified here:** native Windows PySide6 lifecycle, a live mapped Synology SMB share, real APK downloads, production `.exe` builds, and physical microSD transfers.

### Important limitation
A Python thread cannot safely interrupt an already-blocked Windows network **write**. The application does not forcibly kill writers, because that can leave unverified files. Stop is cooperative for imports, downloads, conversions and transfers; if Windows is blocked inside SMB, it may take time for the OS call to return. The new immediate/forced stop applies to **read-only scans only**. If a `.retro-part` file remains after an unexpected crash, the transfer engine verifies it before resuming; do not manually rename it to a completed game.
