# Project handoff · read this before working

**Snapshot date:** 2026-11-23, America/Phoenix. **Latest source artifact:** Retro Library Studio **v1.5.1** (automatic PS1 CHD/M3U/artwork beta). **Last broadly user-verified Windows transfer baseline:** **v1.4.4**.

## Why this exists

The user bought an **Anbernic RG Rotate** with a **512 GB microSD** for PSP, PS1, Nintendo DS, GBA and selected other systems. The main software is **Retro Library Studio**, a friendly Windows 11 PySide6 app that stages a console-organized library in a user-selected **Synology NAS** directory, installs/prepares useful software, and ultimately verifies a transfer to the real card. The Windows app should be deliberately beginner-friendly, not a developer utility. The user dislikes needless manual game-file reorganization and release after release of avoidable GUI problems.

This GitHub repository was newly created with only an 11-byte placeholder README. On 2026-11-23 the **64 UTF-8 text source and test files for v1.5.1** were committed under `RetroLibraryStudio/` (commit `b458028`). The optional generated cover image is not published. Cloning the repo now provides Python/Windows source; the user still must install dependencies and perform Windows acceptance tests.

## GitHub source + CI status

- v1.5.1 text source and tests published under `RetroLibraryStudio/`.
- [CI run 45138220982](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45138220982): **241 passed on Windows; 240 passed / 1 skipped on Linux**.
- GitHub CI uncovered a ZIP/CUE-BIN path alias issue on Windows. Canonical path comparison fixed (`89b1b6c`), regression test added (`e51d25a`). The user still needs to run genuine CHDman on Windows before we say Clock Tower import is fully accepted.

## Current engineering baseline

- **v1.4.4:** User ran Windows 11 GUI against real Synology NAS. Verified app launch and workspace selection; PS1 import; artwork tile; imported Cocoon APK to `SetupPackages`; PPSSPP and RetroArch APK staging; ADB and CHDman showed Ready (actual program execution not fully acceptance-tested). Library check reported 1 game, no duplicate groups, no broken CUE/M3U references. NAS→Windows practice transfer: **6/6 files SHA-256 verified** (roughly 1.21 GB); repeat run: **0 copied, 6 already identical, 6/6 verified**. Previously unresponsive Stop for NAS imports was repaired and user confirmed Stop now worked. Source file preservation was a top priority.
- **v1.5.0:** Guided UX rewrite, better PS1 disc inspection, manual CHD conversion/M3U generation, cover gallery. User's upload of v1.5.0 source tested in Linux with **205 passed / 15 skipped**; its release report claims 220 tests on Windows, not independently reproduced here.
- **v1.5.1:** Automatic PS1 import pipeline added to preceding source: inspect CUE and companions; convert with CHDman; verify resulting CHD; stage playable CHD, optional M3U for correctly identified multi-disc titles; integrate artwork lookup and single unified progress; calculate full original CUE+BIN footprint correctly when still in legacy format. Preserve originals and avoid falsely marking partials as playable. **Latest local independent test: 225 passed / 15 skipped under Linux with pytest**; CHDman executions simulated, Qt/Windows-specific tests skipped. Actual Windows conversions have not been observed.

## Specific bug report: Clock Tower (active)

User imported `Clock Tower: The First Fear` English-patched. It has a `.cue` (~226–228 bytes) plus `Track 1.bin` and `Track 2.bin`. The prior importer copied all three into a game-named NAS folder, **but My Games incorrectly displayed only the tiny CUE size**. The user's goal is no manual track management: **one displayed game**, automatically converted to verified single-disc CHD *before* showing in My Games. A PS1 single game with multiple BIN tracks is **one disc**, not an M3U case. **M3U applies to a title with multiple separate game discs**, each separately converted to CHD. Stop the conversion safely on NAS stalls; don't alter original files. User wants a single progress bar across inspect, convert, verify, stage, artwork.

Another reported example: **Resident Evil 2**, where one disc's CHD conversion failed and another succeeded. Actual source CUE and CHDman error must be collected to know why. Do not assume format labels mean the files are equivalent. Preserve any audio tracks and inspect exact CUE file references.

## Known user-facing problems previously fixed

1. First GUI lacked a clear location selector; now location is obvious and persistent. If previous workspace exists, copy/verify explicitly, never silently move.
2. Startup used to scan Downloads automatically and lock tasks; now Downloads scan is opt-in. NAS disk-capacity probe is optional to prevent indefinite waiting.
3. Safe Stop was initially only a thread flag; read-only scans, imports, and transfers were moved to isolated workers to preserve GUI responsiveness with SMB stalls. Never regress this.
4. APK import was blocked by status scan; repaired by isolating APK importer and returning clear success path.
5. Cocoon manual APK `cocon-311.apk` wasn't recognized by status matcher; aliases handled, still label **publisher unverified**.
6. Transfer preview displayed stale previous 100% progress; cleared. 2nd-run hash verification must be distinct from size-only preview.
7. Practice-transfer path retained after restart but mode wasn't; corrected v1.4.4 to remember practice-vs-real destination and preflight it early.
8. Artwork lookup exact filename matching failed on unusual editions. Preserve manual result selection and avoid mismatched cover auto-assignments.
9. My Games CUE entry appeared as ~226 bytes; v1.5.1 source intended to fix.

## Hardware / architecture decisions

- RG Rotate: Android 12, square 720×720 touchscreen, Unisoc T618, 3 GB RAM, 32 GB onboard storage. The SD is mostly ROMs, covers, metadata, companion storage; do not copy Android system into it.
- Use **Cocoon Shell** as default frontend, but first-run Android configuration, emulator association, library folder permissions and app installation require on-device work or authorized ADB; staging an APK on card is not installation.
- Primary emulators: PPSSPP for PSP; compatible PS1 player (DuckStation beta may have third-party launcher issues); DS player to enable full-screen **top/bottom toggle** via physical key for Spirit Caller; RetroArch for selected older systems. PS2/GameCube performance is experimental.
- UI: premium dark interface, simple three-button navigation, 100–150% scaling including 125%, remembered size/position; small 3.5-inch square Cocoon layouts should prioritize readable covers.
- Storage: virtual target 512 decimal GB ≈476.8 GiB nominal before filesystem overhead. Budget 8 GiB for voice companion + leave 8 GiB free; remaining card allocation is dynamic, checked against actual formatted card. No empty reserved files and no requirement to preallocate 512 GB on NAS.
- Protected user data: microSD `CompanionData` for persistent AI memory; don't delete/overwrite during game management. Evaluate built-in Anbernic AI before custom development.
- User wants to **review/import PlayStation 1 games one at a time** with guidance; after PS1 move to PSP, GBA, DS. Start with Clock Tower, not automated giant bulk import.
- Copyright: user-supplied lawful game images; no commercial ROM downloader or proprietary BIOS files bundled.

## Operating rules for every future chat or Codex change

1. Start by reading README + ROADMAP + this handoff + VERIFICATION_MATRIX.
2. Identify **latest actual code** (GitHub branch or user ZIP); do not rebuild from descriptions alone.
3. Preserve the source NAS workspace, all imported files, user-selected artwork, receipts, and Windows settings. Use new build folder/version; don't overwrite a user's known-good install.
4. Run existing regression tests and add focused tests; distinguish Linux/mock/Windows/physical-device evidence.
5. Update docs/ROADMAP.md, this handoff, VERIFICATION_MATRIX, version/changelog **with the code change**, and link exact issue/commit/PR.
6. Give user one compact Windows checklist with expected pass/fail, not an endless cascade of tiny patches.
7. Publish a validated full ZIP or EXE only when verified to exist; no invented download links.

## Fresh CI evidence (2026-11-23)

The latest GitHub workflow run [45138220982](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45138220982) **passed on both platforms** after a Windows ZIP-import bug was detected and fixed: **241 passed Windows; 240 passed, 1 skipped Linux**. This does **not** prove conversion via real CHDman on the user's Windows PC or test against the Synology NAS; retain P0 Clock Tower acceptance as open.

## Next actions in order

1. **DONE:** Publish the actual v1.5.1 text source and tests (commit `b458028`). Next: establish CI, no ROMs, keys or personal NAS addresses.
2. On Windows, exercise v1.5.1 with the real Clock Tower CUE/BIN set, verify CHDman output, single game tile, true game size, artwork, one progress bar, preserved originals, and safe Stop.
3. Test one genuine multi-disc title and M3U disc-switching.
4. Validate live Ninite downloads / installed tools and missing-artwork handling.
5. Once the 512 GB microSD arrives: actual card discovery, preflight, copy, SHA-256 verification, safe eject, Android/Cocoon setup, play a game.
