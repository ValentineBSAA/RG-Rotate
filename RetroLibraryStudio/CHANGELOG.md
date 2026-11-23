## v1.5.6 Beta · Live 512 GB Card Planner (2026-11-23)

## v1.5.9 candidate · exFAT Simulation + 2 DISCS Details

- Fixed scan serialization: the gallery now receives verified `Entry.members` from background inventory and keeps referenced CHDs until a playlist is validated. Expected Resident Evil 2 behavior is **one cover + 2 DISCS**, with all three files in the details popup. Original verified CHDs/M3U are never changed.
- Added an optional, safe **virtual Windows 11 SDXC/exFAT format estimate** below the existing 512 GB nominal meter, modeling 128 KiB file clusters and exFAT metadata. The scan computes file slack without a second NAS walk. Existing 8 GiB AI allowance and 8 GiB protected free reserve remain.
- New `exFAT details…` explains exactly which bytes are modeled; already-measured real physical card capacity/free space remains the transfer authority. There is **no formatting, partitioning, file creation or deletion**.
- Added empty library, playlist roundtrip, malformed playlist, pure storage math and optional Qt tests. New v1.5.9 user Windows/Synology evidence and real microSD measurement remain pending.


## v1.5.8 packaged source beta · Smart Multi-disc Collections (2026-11-23)

- One new button **Import complete PS1 game folder…** to inspect complete CUE/BIN disc sets in an isolated worker, verify each lossless CHD, and stage into `ROMs/psx/<Game Title>/`.
- Disc tags and editions handled conservatively. Resident Evil 2 (USA) Disc 1 and 2 join their edition, Final Fantasy VII (3 discs) and VIII (4 discs) remain separate; track files are not discs.
- Existing disc-numbered CHDs are verified then staged without conversion. Partial/incomplete tracks, out-of-order/missing/duplicate disc numbers and unsafe CUE references are rejected.
- M3U creation requires consecutive discs; later additions can extend only a non-conflicting ordered subset by atomic replacement. Custom/alternate playlists are preserved.
- My Games shows one gallery tile for a complete scanned M3U collection, with N DISCS badge, file details and artwork fallback to prior disc cache. Individual disc entries remain visible in advanced File List; broken playlists do not hide discs.
- Added regression tests `test_v158_collections.py`; real Windows/Synology and RG Rotate disc swap are **pending**. Existing PS1 conversion cleanup remains opt-in; originals and memory unaffected.


## v1.5.7 source candidate · Console Shelves (2026-11-23)

- Added scrollable premium console pills with **logical game counts**, synchronizing My Games cover gallery and file list filters. Gallery displays distinct full-width console headers and organizes games by PSP, PS1, Nintendo DS, GBA, PS2, GameCube, then remaining supported systems. Existing game cards keep artwork, title edits, CHD format badges, contextual actions and Show More paging.
- Explicit PS2 and GameCube destination folders support sorting user-supplied game images. GCM is unambiguous; ISO/RVZ/GCZ remain selected-system/folder inferred. PS2/GameCube are **experimental** for RG Rotate gameplay, not emulation promises.
- No new NAS I/O in visual shelf sorting; no conversion, backup deletion or physical card preallocation. v1.5.6 capacity meter retained.
- Offline Python and optional Qt tests added, [FULL_TEST_CHECKLIST.md](../docs/FULL_TEST_CHECKLIST.md) provides full future acceptance.
- **Not yet a Windows beta ZIP or real-device acceptance.** Record CI and screenshots before declaring this candidate tested.


- Added an always-visible **512 GB advertised-capacity virtual microSD bar** near the top of Start, Add Games and every other page. It shows actual staged file bytes, future AI companion budget and the 8 GiB protected free-space reserve without allocating a 512 GB file.
- Added **Exact sizes…** to display the staged library byte count (including CHDs/artwork/APKs) and GB/GiB conversion.
- After **Copy to card → Check what would be copied**, the real-card section displays **measured formatted capacity**, existing space used, estimated unique new transfer bytes and estimated free space afterward. Practice folders are explicitly excluded. Previously previewed card numbers are invalidated after workspace or destination changes and after a verified transfer.
- Added transfer preflight conflicts for cards whose real formatted capacity cannot hold the staged library plus budgets, or whose free space cannot accommodate new bytes and reserve.
- Pure capacity computations never query the NAS from the GUI paint path. NAS free-space lookup remains opt-in, bounded and separate from card planning.
- **512,000,000,000 bytes = 512 GB = approximately 476.84 GiB.** Real formatted capacity may differ and is not claimed until the Windows card preview measures it.
- Source beta, not a verified physical microSD release. Initial clean extracted local tests: **255 passed / 19 skipped** (PySide6 not available locally). Windows CI and on-device test are separately tracked.

# v1.5.5 Beta — Lossless Batch CHD & Verified Cleanup (2026-11-23)

- User-observed v1.5.4 Windows results: Clock Tower CHDman verified (55.4 MB); Resident Evil Gore Edition verified (311.9 MB); cover art retained.
- New batch CUE/BIN and safe standalone IMG conversion using standard MAME CD lossless codecs, CHDman verify per disc, one overall progress bar.
- Two explicit cleanup policies: keep recoverable tracks off-card, or delete ONLY verified virtual-card working copies after double confirmation. Never touch outside original NAS archives; old backups aren't deleted automatically.
- Open conversion backups from gallery/context menu and open exact backup folder from completion dialog.
- Fix artwork preview clipping by responsive in-memory aspect-fit scaling.
- Local clean extraction: 248 passed / 16 skipped on Linux. GitHub CI: **264 Windows passed**, **263 Linux passed + 1 skipped** ([run](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45148569884)). Real Windows batch confirmation pending.

# v1.5.4 Beta — Artwork Previews & Context-Menu CHD Organization (2026-11-23)

- Automatic **selected cover preview** in the artwork results dialog, with a short debounce to avoid rapid repeated downloads. Double-click previews instead of applying an unseen cover. The explicit Preview selected button remains available.
- Game-gallery cards now have a themed right-click menu: Edit Title, Preview/Change Cover, File Details, Convert to verified CHD + tidy PSX folder, and Open Game Folder.
- An existing PS1 BIN/CUE set can be converted **in its current PSX folder**. After CHDman verifies the CHD on the NAS, the CUE and referenced BINs are moved to a separate recovery folder **alongside, but outside, the virtual microSD**. No permanent deletion.
- Already-converted CUE/BIN sets with matching CHD show the cleanup option on the CHD tile, with verification before moving source files.
- Single-track raw IMG conversion supported only for identifiable CD sectors (MODE1/2352, MODE2/2352 or recognized MODE1/2048). Ambiguous IMG and CloneCD CCD/IMG/SUB sets are rejected with clear guidance to avoid silently losing track/subchannel metadata.
- Conversion, verification, backup and refresh run in isolated worker under one progress area. Partial conversion or failed verification never moves original sources.
- Tests cover conversion/rollback and format detection; **real CHDman, live cover preview and Windows UI require user acceptance**.

# Retro Library Studio v1.5.3 Beta — Format Badges and Artwork Fallback (2026-11-23)

- Game tiles now show a **clickable, high-contrast file-format badge**: CHD, BIN/CUE, M3U, ISO, PBP, and other actual extensions, based on the scanned library file. Badges NEVER claim conversion or integrity verification by extension alone. Clicking opens a concise file-format explanation and the available library path/file list.
- Legacy CUE/BIN sets say BIN/CUE until a real .chd is staged. Multi-disc M3U entries are playlists pointing to separate disc images, not a CHD themselves.
- Missing-artwork search now attempts the Libretro thumbnail catalog first and its officially maintained platform-specific GitHub tree when the first catalog is unavailable. Preview and cover download can use the corresponding GitHub raw mirror when the main thumbnail endpoint fails. Cached indexes are reused. Online availability remains conditional on the user's network and both services.
- Added direct “Browse Libretro covers” escape hatch for provider outages and retained “Choose image from PC instead.” Existing user covers and game files remain untouched.
- **Tests:** 230 passed, 15 skipped (Linux, no real CHDman or live network); actual Windows UI, live artwork, NAS and RG Rotate still require physical user acceptance.

## First test

1. Extract to a NEW folder; double-click `Start_Retro_Library_Studio.bat`. Verify v1.5.3 title and remembered NAS library.
2. Open **Add games / My Games**. The Clock Tower tile should show **BIN/CUE** if its underlying file is still `.cue`, or **CHD** only if a `.chd` exists and is selected. Click the badge for file details; this does not read/modify ROMs.
3. Press **Search for cover** on Clock Tower. The catalog now retries via the official GitHub source; look for candidates and choose/preview/apply one. If both sources are unreachable, use Browse Libretro covers or Choose image from PC.
4. Only then run the real Windows CHD conversion with the original CUE + both BIN tracks in their existing folder. Verify a genuine `.chd` is produced and reappears as a CHD badge after refreshing. The original source tracks must remain untouched.
5. Report errors verbatim. We will not assume a successful conversion or artwork download from tests alone.

---
# 1.5.2 Beta — Windows PS1 acceptance candidate (2026-11-23)

- Packaged Windows-launchable source based on the latest GitHub v1.5.1 CI-tested PS1 pipeline.
- Fixed CUE-referenced BIN tracks with equivalent/aliased Windows paths being incorrectly interpreted as standalone game files during archive import.
- Added a regression test for this path alias case; preserved the preexisting CHD, M3U, NAS Stop, artwork, and verified-transfer behavior.
- UI geometry test handles clamped screen sizes on GitHub Actions runners; this does not constitute real 125% DPI acceptance.
- This is a testable **source beta**, not a compiled EXE. Real CHDman conversion, online artwork and RG Rotate still require user acceptance.

# v1.5.1 Beta — Automatic PS1 import and artwork progress

- Added default-on conversion of complete PS1 CUE/BIN disc sets to verified CHD
  **during game importing**, including safely unpacked ZIP/7Z sets.
- Automatic M3U playlists for imported multi-disc CHD sets, with correct disc
  ordering, no overwrite, and an incremental Disc 2 later workflow.
- Added Convert earlier PS1 imports option. Old BIN/CUE files are preserved.
- Corrected displayed CUE/M3U logical sizes; no double-counted storage usage.
- M3U playlists are the single gallery entry for multi-disc games, while CHD
  is preferred over an older CUE with the same name.
- Integrated artwork lookup and review statuses into the same import-worker
  progress flow. Added exact region fallback if the Libretro catalog is offline.
- Fixed CP1252 CUE companion-name decoding and better standalone BIN guidance.
- One global task bar shows indeterminate animation during CHDman processing,
  rather than a fake percentage. Cancellation stays in the isolated worker.
- No change to user's saved NAS path, existing artwork, imported games or
  previous practice-card transfers.

---

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
