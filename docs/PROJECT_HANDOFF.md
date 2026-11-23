# Project handoff · read this before working

## v1.6.1 source candidate | PSN PS1 Classics + 7Z

Real user photo shows Final Fantasy VII (English)(PSN)/NPEF00069 with EBOOT.PBP, KEYS.BIN and DOCUMENT.DAT. It is an official PS1 Classics PSN-style package, not a native PSP ISO. KEYS.BIN is companion key material; DOCUMENT.DAT is a manual. They should never become CHD files or be stored in the virtual ROMs. Final Fantasy VII original PS1 = 3 discs.

Branch feature/v1.6.1-psn-eboot-and-7z-verification, PR #17. Files: ps1_psn.py new PSAR signature/classification, optional PSXtract bridge and careful disc naming; ps1_pipeline.py new PSN extraction stage and .7z document forwarding; tool_setup.py pinned upstream v3.0 PSXtract ZIP+SHA-256 safe install; batch_setup.py and app.py optional checkbox (off by default), proper binary path forwarding; tests/test_v161_psn_and_7z.py creates REAL .7z archives with fake disc contents; tests/test_v161_psxtract_setup.py covers ZIP safety.

Windows release user must opt in to downloading a THIRD-PARTY helper with pinned SHA-256. Helper is not bundled, not run on install. The exact real Sony encrypted EBOOT was not provided, so real extraction/audio quality are UNVERIFIED. Once extracted CUE/BIN are complete, existing real user verified CHDman + M3U + artwork stage runs. Originals and old RE2 untouched. [Acceptance](PS1_CLASSICS_7Z_ACCEPTANCE.md).


## v1.6.0 candidate · Clear dialogs and USB card identity gates

User-supplied **real v1.5.9 screenshots verified** one Resident Evil 2 M3U cover tile with 2 DISCS badge, correct two CHD entries in the detail popup, and two distinct capacity bars at 125%. The dialog was deemed too text-heavy. A real branded 512 GB microSD is arriving and will be inserted into Windows 11 via microSD-to-USB adapter.

**v1.6.0 branch** `feature/v1.6.0-friendly-details-and-card-identity`: `friendly_dialogs.py` contains the styled scannable, selectable grouped cards and expandable technical detail panel. Only `show_game_format`, `show_virtual_exfat_details` and `show_card_plan_details` were replaced; existing layouts, importing, conversion and artwork remain untouched.

`drives.py` includes Windows volume GUID/volume serial via Win32 API; `card_identity.py` defines candidate detection and strict comparisons. `app.py` polls candidate volumes asynchronously **only on Copy to card**, leaves selection to user, flags Windows-fixed USB adapters as uncertain, requires fresh preview and typed drive-letter confirmation; `transfer_worker.py` refuses copy without an expected identity and revalidates; `sync_engine.py` revalidates identity **before every file**. Keep legacy practice-folder behavior unchanged. **Volume ID is not a cryptographic physical card proof**; user must still check Explorer/Disk Management. Protect NAS originals, verified CHDs/M3U and CompanionData, and never format.

[Testing plan](CARD_DETECTION_AND_READABLE_DIALOGS.md). [PR #15](https://github.com/ValentineBSAA/RG-Rotate/pull/15) merged to main. GitHub source CI passed 311 Windows / 310 Linux + 1 skip; final packaged v1.6.0 ZIP 99 files CRC verified, extracted source passed 279 tests / 32 skipped locally due missing GUI dependencies. Actual USB adapter and real card verification remain pending.


## v1.5.9 source candidate · Resident Evil 2 detail repair + virtual exFAT overlay

From user real Windows 11 v1.5.8 screenshots: verified Resident Evil 2 Disc 1/Disc 2 CHDs in one parent folder, correctly ordered two-line M3U and artwork; the gallery only showed an `M3U` badge and the details popup only showed the playlist. **Root cause:** read-only `readonly_scan.py` omitted `Entry.members` in JSON, `app.py` reconstructed five-column entries without membership, and `disc_tracks` prematurely hid referenced M3U CHDs. **Fix:** worker transmits six fields including members, CHD files survive until validated grouping in `library_presentation.py`, app restores members, old 5-column JSON tolerated. This is *not* a gameplay or live-device pass.

User also requested a non-destructive virtual Windows 11 512 GB exFAT format simulation **on top** of current NAS workspace. `virtual_exfat.py` models advertised nominal capacity vs estimated formatted capacity with assumed 128 KiB clusters, exFAT metadata/alignment, and cluster slack computed in **existing single read-only scan** via `core.inventory(..., metrics=...)`. `app.py` adds second labeled exFAT bar under original nominal bar, `exFAT details…` and enhanced Exact sizes. No real formatting, partition, preallocation or new NAS file. Real physical card `shutil.disk_usage` from the existing Preview remains authoritative once connected. **Exact formatted bytes cannot be predicted without the physical card.**

New automated regression: `tests/test_v159_exfat_and_playlist.py` including real read-only scan roundtrip and optional Qt at 100/125/150%. Source branch `feature/v1.5.9-exfat-preview-and-disc-details`. [Details](VIRTUAL_EXFAT_PLAN.md), [full checklist](FULL_TEST_CHECKLIST.md). [PR #14](https://github.com/ValentineBSAA/RG-Rotate/pull/14) merged to main (`e69d55c`); [main CI 45242023081](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45242023081) passed 301 Windows, 300 Linux/1 skipped. Packaged ZIP CRC verified; clean extract 273 passed/28 skipped without PySide6 locally. User Windows v1.5.9 screenshot and physical-card acceptance still pending. No original CHDs, CUE/BIN, playlists, artwork or CompanionData modified by this feature.


## v1.5.8 packaged source beta · Multi-disc collection workflow (2026-11-23)

Merged to main as [PR #13](https://github.com/ValentineBSAA/RG-Rotate/pull/13), commit `c063450`; developed on `feature/v1.5.8-multidisc-collections` from v1.5.7. The user successfully tested v1.5.7 console pills/gallery-list toggling, 125% scaling, NAS location persistence and 512 GB virtual meter, then requested a full PS1 collection workflow: **one cover, one library entry, one parent game folder, CHD per disc and one ordered M3U**. RE2 Disc 1/2 should be one game; FFVII's 3 and FFVIII's 4 remain distinct.

Implementation: `ps1_collections.py` supplies conservative explicit disc numbering, folder/title validation, scan-worker-only valid playlist membership and atomic subset-only M3U extension. `ps1_pipeline.py` routes CUE/BIN conversion via CHDman and direct pre-existing CHD verification into per-title folders; each disc has its own .chd. `core.Entry.members` stores verified references during worker inventory to avoid GUI-thread NAS reads. `library_presentation.py` hides member CHD tiles ONLY when an M3U references a validated consecutive disc set, while retaining raw file-list visibility. `app.py` adds a dedicated folder import and N DISCS badge and displays the main game cover. `disc_sets.py` refuses escaping/unsafe CUE references.

Original BIN/CUE/CHD archives, existing virtual-card CHDs, backups, CompanionData and custom artwork are protected; corrupted or incomplete sources are never automatically repaired/renamed. Conversion cleanup is separately opt-in. **Source CI is green**: Windows 289 passed, Linux 288 passed/1 skipped; downloaded ZIP clean-extract local tests 264 passed/25 skipped. **Real Windows/Synology M01–M09 and RG Rotate emulator disc switching M10 are still pending.** [Acceptance](MULTIDISC_ACCEPTANCE.md), [Full checklist](FULL_TEST_CHECKLIST.md), [Verification matrix](VERIFICATION_MATRIX.md).


## 2026-11-23 · v1.5.7 source candidate: system shelves

Now **merged to `main`** from branch `feature/v1.5.7-system-shelves` in `ValentineBSAA/RG-Rotate` ([PR #11](https://github.com/ValentineBSAA/RG-Rotate/pull/11), squash commit `6515dba`). v1.5.6 was the previous code baseline (512 GB staged capacity meter, Windows CI 274 passed / Linux CI 273 passed, 1 skipped). This branch adds visual **console tabs/pills** with live logical game counts and strong grouped headings in My Games, preserving existing cover and game-format badges, title edits, contextual CHD actions, gallery paging, filtering, file-list view and 512 GB meter. Primary sections PSP, PS1, Nintendo DS, GBA, PS2, GameCube; other known systems follow. The shelf system is display-only: it never scans NAS to build visual groups and does not touch ROM files.

`core.SYSTEM_DIR` now has explicit `ROMs/ps2` and `ROMs/gc` directories for **user-selected legal game image organization**; GameCube `.gcm` infers GameCube; ambiguous `.iso`, `.rvz`, `.gcz` use selected system or parent folder. **PS2 and GameCube are experimental on this T618/3 GB RG Rotate, not guaranteed playable.** Artwork catalogs are merely best-effort. The new comprehensive [test checklist](FULL_TEST_CHECKLIST.md) includes all remaining Windows/NAS, batch verified-cleanup, card and handheld tests. PR [#11](https://github.com/ValentineBSAA/RG-Rotate/pull/11) CI [run 45155293003](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45155293003) passed **279 Windows tests, 278 Linux passed + 1 skipped**. Real Windows user acceptance remains required before calling a release verified. No new ZIP is claimed.

Do not regress prior user-observed v1.5.4 Clock Tower 55.4 MB and Resident Evil 311.9 MB CHDman-verified Windows conversions, v1.4.x NAS Stop and practice 6/6 SHA-256 verification. **v1.5.5 batch-delete/backup modes and v1.5.6 Windows capacity-bar UI remain pending user acceptance.** Preserve originals on Synology, historical backup folders, existing virtual card and CompanionData. Do not touch physical card until actual device arrives.


**Snapshot date:** 2026-11-23, America/Phoenix. **Latest packaged source beta:** Retro Library Studio **v1.5.8** (multi-disc collections, source tests passed; real NAS and handheld still pending). **Last broadly user-verified Windows transfer baseline:** **v1.4.4**.

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

## v1.5.2 source test package (2026-11-23)

- User-facing ZIP prepared: `RetroLibraryStudio_v1.5.2_Windows_Test_Beta.zip`; Windows launcher `Start_Retro_Library_Studio.bat` inside.
- Fixed canonical CUE-referenced BIN path matching for Windows ZIP imports; regression test in the repository.
- Clean extracted ZIP local Linux pytest: **226 passed / 15 skipped**. Matching GitHub Windows CI for v1.5.1 core: **241 passed**. Real Clock Tower CHDman on user PC remains pending; this is not a hardware pass.
- First test: import/convert user's Clock Tower complete CUE + two BIN tracks (or optimize prior import), verify **one CHD, full size, single tile, preserved originals**. Avoid multi-disc testing until single disc succeeds.

## v1.5.3 update / Clock Tower screenshot review (2026-11-23)

- **Observed:** User's v1.5.2 My Games gallery showed `Clock Tower - The First Fear` at **118.0 MB** rather than 226–228 bytes. This confirms better logical size display, **not** CHD conversion. Cover search dialog returned `The online artwork catalog is unavailable` and no entries.
- **Implemented v1.5.3:** Actual file-type badge on tile (CHD, BIN/CUE, M3U, ISO, PBP), clickable read-only explanation. Never label a CHD verified just because filename ends in .chd. GUI avoids NAS stat on the paint path.
- **Artwork:** Libretro catalog is primary. If it fails, try official `api.github.com/repos/libretro-thumbnails/<platform>/git/trees/master?recursive=1`, with limited response size and cached index. Cover retrieval can fall back to official `raw.githubusercontent.com` image. Manual browser/PC image fallback remains.
- **Build:** `RetroLibraryStudio_v1.5.3_Windows_Test_Beta.zip`, clean extraction tests **230 passed / 15 skipped** on Linux; real online provider and actual Windows UI still require user acceptance.
- **Next:** Have user click Clock Tower's file-type badge. If BIN/CUE, conversion still pending; run the existing CHDman action on source CUE/track pair with no source-file deletion. Then test artwork search. Do not treat reported size as evidence of successful CHD conversion.

- **CI after v1.5.3 badge/artwork changes:** [run 45141431778](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45141431778) passed **245 tests on Windows**, **244 pass and 1 skip on Linux**; unit tests use mocked artwork endpoints, so user screenshot verification is still required.

## v1.5.4 (2026-11-23) · artwork preview + contextual CHD organization

- **Actual observed v1.5.3 Windows passes:** Clock Tower `BIN/CUE` badge showed **118.0 MB**; online artwork search returned USA/Japan/Ghost Head results and user successfully applied selected cover. Empty preview section was the new bug.
- **v1.5.4 implementation:** result selection automatically starts an async artwork preview after 260 ms debounce, before apply. Double-click previews rather than blindly applies. Styled right-click menu on gallery and file list supports format/details/title/cover and conversion.
- **Conversion:** For in-card PS1 CUE/BIN and safe single-track IMG, do CHDman createcd → verify → reverify CHD in existing game folder → move legacy original tracks into adjacent `<virtual card name> - Conversion Backups` **outside card**. No file is deleted; existing CHD can be reverified and tidied. Invalid/ambiguous IMG or CloneCD CCD/IMG/SUB is refused rather than guessed. The action runs in isolated import worker to protect Qt and NAS Stop.
- **Current code:** commit `b0c02214`; local tests 240 passed, 15 skipped; source ZIP `RetroLibraryStudio_v1.5.4_Windows_Test_Beta.zip`. Actual Windows conversion acceptance still **pending**. See [issue #8](https://github.com/ValentineBSAA/RG-Rotate/issues/8).
- **Important:** Backups are outside the virtual card (same parent NAS folder). If user wants to reclaim their NAS disk later, provide a separate carefully verified recovery cleanup workflow, never auto-delete original source files.

- **CI confirmed for v1.5.4:** [Windows 255 tests passed and Linux 254 passed / 1 skipped](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45144304702). Real conversion on user's NAS remains the next gate.

## v1.5.5 live handoff (2026-11-23)

**User Windows pass:** v1.5.4 Clock Tower: The First Fear converted/CHDman verified to 55.4 MB CHD; Resident Evil Gore Edition to 311.9 MB CHD. Both CHD badges and covers visible in user's screenshots. Original tracks moved into NAS sibling `RG Rotate Virtual Card - Conversion Backups` after verification, so they still use NAS storage.

**v1.5.5 code:** Batch scans ONLY the selected `<virtual card>/ROMs/psx` tree, converts each safe CUE/BIN or standalone unambiguous IMG using ordinary lossless CHDman createcd, re-verifies CHD. User explicitly chooses either backup outside card or deletion of virtual-card **working copies** only after each verification, with a second destructive confirmation. Elsewhere-on-NAS original ROM archives are never touched; preexisting recovery backups are not automatically purged. Adds Open conversion backups and direct links from individual completion dialog; artwork preview uses aspect-fit in memory.

**Local package**: `RetroLibraryStudio_v1.5.5_Windows_Test_Beta.zip`, 3,097,042 bytes, SHA-256 `5ef63fd138d6b5fc285d7b0448427b36188b24d36b9ee670aa3fc65c8166691d`, ZIP test passed; clean extracted Linux suite **248 passed, 16 skipped**. No real v1.5.5 Windows batch deletion acceptance yet. Use disposable test folders FIRST and preserve v1.5.4 fallback.

**Final v1.5.5 GitHub source CI:** [run 45148569884](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45148569884) passed **264 Windows tests** and **263 Linux tests / 1 skip**. README/release package updated with matching source and a clean-extraction test report.


## v1.5.5 package handoff · 2026-11-23

The user reported **real v1.5.4 Windows success**: Clock Tower CHD displayed as **55.4 MB**, Resident Evil Gore Edition as **311.9 MB**, green CHD badges, both covers retained, actual CHDman verification reported, and converted files kept in the appropriate PSX folder. Earlier source tracks moved to `<virtual card sibling> - Conversion Backups`, which was **outside the virtual card but on the same NAS share**, not automatically freed NAS space.

**New v1.5.5 local source beta:** batch convert `.cue` and safe standalone `.img` candidates; sequential CHDman create/verify; report per-item errors and remaining work; one progress workflow; clickable **Open conversion backups**; cover preview scales proportionally to dialog dimensions. Two cleanup policies: preserve originals in a recovery directory or delete only the **virtual-card working tracks** after CHD verification with explicit confirmation. Does not delete the user's separate NAS originals. Old recovery folders are not purged. CHDman uses normal **lossless CD compression**. CloneCD `.ccd/.img/.sub` and other ambiguous IMG files are intentionally refused.

**Evidence:** new ZIP `RetroLibraryStudio_v1.5.5_Windows_Test_Beta.zip`; local clean test on Linux **248 passed, 16 skipped**; archive 73 entries, hash `e1a00b4f0147353ffdc37f47bb49e69a87afd5bfc23a9839968232834d441350`. Real v1.5.5 Windows, NAS batch/delete and UI acceptance are **not yet tested**. **v1.5.5 source is now published to GitHub**, including `app.py`, `ps1_organizer.py`, `import_worker.py` and `tests/test_v155_batch_cleanup.py`. [GitHub CI run 45149019365](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45149019365) passed **264 Windows tests** and **263 Linux tests with 1 skip**. Those are automated tests; the new batch-delete workflow remains untested on the user's actual NAS.

## v1.5.6 implementation handoff (2026-11-23)

User requested visual indication of filling the planned 512 GB card while importing games, and precise physical capacity preview when real card arrives. Source now contains `RetroLibraryStudio/card_capacity.py` for pure accounting, `CardFillMeter` for a read-only segmented Qt bar, a persistent bar near the top of all pages and a real card size comparison in Copy to Card after isolated preview. `Exact sizes…` shows all figures in bytes and decimal/binary units. This reads the existing virtual inventory from NAS worker results, not a new GUI-thread NAS scan. It does NOT preallocate or format a card.

The **512 GB nominal** capacity is 512,000,000,000 bytes or 476.84 GiB; actual formatted card size must come from Windows' destination preview. Stage and protected budgets remain (8 GiB AI allowance + 8 GiB free reserve), with used CompanionData counted only once. In `sync_engine.py`, physical preflight now rejects impossible real capacity and insufficient free-space headroom. Local pytest 255 pass / 19 skipped (GUI tests skipped where PySide6 unavailable). Await Windows GUI CI, real card transfer and the user's confirmation.

### v1.5.6 delivered beta

Windows source ZIP `RetroLibraryStudio_v1.5.6_Windows_Test_Beta.zip` created, ZIP self-check and clean extracted test passed: **255 passed, 19 skipped**. SHA-256 `1bf62b798111f9d621ee5fffb07ba37ecfbcc854b1f3c186dc8495cac1efe36f`. [CI run](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45152416169) Windows **274 passed**, Linux **273 passed / 1 skipped**. The user has not yet tested 1.5.6 GUI or actual card capacity. Keep the old program folder as backup.
