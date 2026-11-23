# Living Roadmap · RG Rotate / Retro Library Studio

## v1.6.7 · Real PSXtract encrypted-header failure, not CHDman

- [x] User's v1.6.6 custom PS1 title chooser displayed 30 games including Clock Tower II (SLUS00695); selection worked. Keep title chooser.
- [x] Diagnose actual Clock Tower failure from screenshot: PGD invalid 0x80 MAC hash, ISO header decryption failed; 0 imported / 0 CHDs. Not CHDman.
- [x] Identify possible PSXtract CLI integration constraint: KEYS.BIN requires preceding DOCUMENT.DAT positional argument in legacy format. Do not make a fake document or assume the exact cause.
- [x] Add public safe error explanation for PGD/MAC, key/manual presence, no CHD started; original files unchanged.
- [x] Simplify picker header, label source by PS1 folder with full NAS path tooltip; tighten import results wording.
- [x] Synthetic tests for PGD failure and no key-byte disclosure.
- [ ] Full Windows/Linux CI; new v1.6.7 Windows ZIP/CRC and startup.
- [ ] Real Windows screenshot and Clock Tower error checks after v1.6.7.
- [ ] Only mark Clock Tower conversion fixed when the actual EBOOT completes PSXtract, CHD verify and artwork; no invented keys or workaround.
- [ ] Continue proven-working Crash Bandicoot and other games; preserve all original files and legacy generic CHDs.
[Acceptance](PSXTRACT_PGD_AND_PICKER_POLISH_v167.md).


**v1.6.6 completion (November 23, 2026):** [PR #24](https://github.com/ValentineBSAA/RG-Rotate/pull/24) merged into main (squash `23ce722`). Exact branch-head [CI run 45280723949](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45280723949) passed **398 Windows tests, 397 Linux tests with 1 skipped**. [Windows source ZIP](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45280714622) at tested commit `2a778d5` packaged successfully (123 internal entries; ZIP CRC good), downloaded as `RetroLibraryStudio_v1.6.6_Windows_Source_Beta.zip`. **Still pending:** physical Windows 11 NAS test of the v1.6.6 single/multi PS1 title picker, real automatic cover after CHDman verify, and real repeat EBOOT skip; do not mark those passed from synthetic CI. v1.6.4 user-tested Crash Bandicoot CHD conversion and Stop are the baseline. Native Windows picker showing NPEE codes is intentionally replaced *inside the app* by a title-aware chooser when last folder is PS1; cannot actually rename Windows file-dialog folders. Verified CHDs remain valid if cover download fails. Old anonymous v1.6.2 PS1 entries remain untouched. [Exact v1.6.6 acceptance checklist](PS1_UNIFIED_PICKER_AND_POST_CHD_ART_v166.md).


## v1.6.6 Beta · Unified PS1 game selection + artwork AFTER CHD

- [x] Diagnose native Windows Add Game Files picker bypass of v1.6.5 PBP-title chooser.
- [x] Route remembered PS1/NPEE locations to the searchable title-aware picker for single and multiple game selection; preserve Browse other ROM files.
- [x] Find automatic artwork mismatch due to literal trademark symbol in PBP title; normalize legal glyphs ONLY during cover lookup.
- [x] Enforce/report sequence: PSXtract → CHDman → verified output folder → exact region artwork; cover outage never invalidates a good CHD.
- [x] On proven duplicate receipt, avoid re-conversion but allow missing artwork backfill after recognizing verified CHD.
- [x] Synthetic tests including CHD-before-cover event ordering, USA exact artwork, duplicate skip and folder picker path.
- [ ] Exact SHA Windows/Linux CI and ZIP manifest/CRC.
- [ ] Real Windows NAS test: native picker bypass absent; known Crash game automatically gets correct USA cover after CHD; duplicate skip without extraction; Stop.
- [ ] Keep prior anonymous PS1 CHDs untouched until independently identified.
[Full v1.6.6 acceptance](PS1_UNIFIED_PICKER_AND_POST_CHD_ART_v166.md).


**v1.6.5 completion update (November 23, 2026):** [PR #23](https://github.com/ValentineBSAA/RG-Rotate/pull/23) merged into main (squash `b8fe446`) after [Windows/Linux CI](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45278366622) passed **394 Windows, 393 Linux with one skip** on source commit `96c02a7`. [Windows 1.6.5 source ZIP](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45278357384) passed packaging/CRC and includes new PS1 title picker and tests; this is **source beta, not an EXE**. User's proven physical Windows baseline is still v1.6.4 Crash Bandicoot™ CHD conversion + Stop task working. **v1.6.5 real NAS PS1 folder selection, automatic artwork, duplicate retry, and physical RG Rotate launch NOT YET TESTED.** The new UI reads actual EBOOT title from public PBP metadata instead of guessing Sony NPEE product IDs; the user can select a subset and EBOOT companions are found automatically. Browse PS1 Classics, Add Folder, Add Files remember the last game folder. Existing anonymous PS1 CHDs from v1.6.2 should NEVER be automatically deleted/renamed. [Exact acceptance checklist](PSN_GAME_PICKER_AND_ARTWORK_v165.md).


## v1.6.5 · Selective EBOOT imports, remembered locations and reliable artwork

- [x] Scan PS1 Classics parent folder from a cancellable process; read bounded public EBOOT title metadata; never invent Sony NP code/name associations.
- [x] Select any subset of games by actual name with search, checkboxes and select-visible controls. Import only checked EBOOT/ZIP/7Z packages, automatically include same-folder KEYS when PSXtract needs it.
- [x] Remember last game-picker folder for Add Game Files, Add Folder, and PS1 chooser.
- [x] Keep ordinary multi-console Add Folder behavior when there is no recognized PS1 EBOOT.
- [x] Show resolved game title, PSXtract MD5 stages, CHD conversion and verify in main UI.
- [x] Enable strict auto-cover matching for supported consoles, USA default if region unspecified, respect explicit region, preserve user art, never guess on uncertain editions.
- [x] Synthetic tests for Sony-code titles, select subset, no KEYS as game, cover region and safe cancellation.
- [ ] Exact source CI (Windows/Linux), source ZIP verification, then real Windows UI.
- [ ] Windows NAS selection of some of the ~30 PS1 games with previews, normal folder import regression, remembered location after restart.
- [ ] Real art downloaded automatically without user dialog, and manual fallback only if needs review.
- [ ] Test same Crash Bandicoot EBOOT **after successful CHD conversion** is skipped as duplicate before PSXtract/CHDman.
- [ ] Audit extra generic PS1 tile against old v1.6.2 imports, without deletion or guessing.
- [ ] Copy to physical RG Rotate microSD and verify game launches (later).
[Acceptance and evidence](PSN_GAME_PICKER_AND_ARTWORK_v165.md).


**STATUS UPDATE 2026-11-23:** [PR #22](https://github.com/ValentineBSAA/RG-Rotate/pull/22) for v1.6.4 Unicode CUE fix merged into main (squash `21c2b5a`). Source CI run [45272838436](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45272838436) **384 Windows passed; 383 Linux passed, 1 skipped**. The exact branch-head source ZIP [45272820961](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45272820961) packaged successfully (commit `8d755754`; subsequent merge was squash of same source). Real Windows user **Crash Bandicoot™** CHDman createcd + verify, duplicate retry, and Stop acceptance are **still pending**. v1.6.3 had recognized title correctly but imported zero files because CHDman reported Unicode CUE filename missing. User should use v1.6.4 source ZIP from GitHub Actions, install in new program folder, start with one Crash Bandicoot™ EBOOT, inspect named CHD after verification, then repeat same EBOOT. No big 30-game batch until passes. Retain anonymous v1.6.2 PS1 CHDs untouched. Full [v1.6.4 checklist](PSN_UNICODE_CHDMAN_v164.md).


## v1.6.4 · Crash Bandicoot™ conversion failure

- [x] Real Windows 11 v1.6.3 single EBOOT import identified title **Crash Bandicoot™**, then CHDman createcd exited 1: Windows reported temporary `Crash Bandicoot™ (Disc 1).cue` as nonexistent. **Added 0 files**. Exact duplicate test NOT possible yet.
- [x] Suspected Unicode path handling in Windows CHDman; introduced disposable ASCII-only CUE alias and temporary hardlinked Unicode track aliases, cleaned on cancellation. Original game title preserved in final CHD folder.
- [x] Added synthetic regression tests for trademark names, Unicode tracks, no-extra-alias ASCII source, cancellation, end-to-end named CHD.
- [ ] CI Windows and Linux source regression passes on v1.6.4 commit.
- [ ] Packaging ZIP and manifest integrity pass.
- [ ] **Critical real-device acceptance**: real CHDman verify, actual named Crash Bandicoot™ CHD, correct tile, same EBOOT duplicate skip, real Stop testing.
- [ ] Confirm existing generic PS1 folders are unchanged and not assumed to be Crash Bandicoot.
- [ ] Small multi-game batch only after all above tests pass.

[Full v1.6.4 checklist](PSN_UNICODE_CHDMAN_v164.md).


**v1.6.3 source status (2026-11-23):** [PR #21 merged](https://github.com/ValentineBSAA/RG-Rotate/pull/21); [CI 379 Windows / 378 Linux passed, 1 skipped](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45269373105); [Windows source ZIP packaged and integrity-checked](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45269530914). Unchecked Windows NAS items below remain pending. Preserve all anonymous v1.6.2 CHDs for manual identification; do not bulk-clean.


## v1.6.3 · Real 30-game batch failure: highest priority

- [x] Diagnose the generic PS1 source-label regression from user's Windows screenshots and source path: a wrapper stem of PS1 was accepted as a game title, yielding PS1/Disc 1 CHD and anonymous cover.
- [x] Add safe title resolver using PBP PARAM.SFO and meaningful archive/inner folder names. Fail closed on unknown identities, never silently merge games in PS1 directory.
- [x] Update queue labels as actual game title becomes known; improve batch result status/folder details, add Open game folder on gallery tiles.
- [x] Make Stop request visible and escalate cooperative STOP -> terminate -> kill, no new job until worker exits.
- [x] Record receipts for complete PSN single-disc CHDs. Keep all existing CHDs, EBOOTs, artwork and backups untouched.
- [x] Add synthetic regression fixtures for generic PS1 wrappers, distinct titles, stop at game 1 and reimport.
- [ ] GitHub Windows/Linux CI for exact v1.6.3 commit.
- [ ] Physical Windows 11 125% disposable-workspace tests: two generic PS1 archives, correct titles, CHD/M3U, Stop during ZIP/7Z/PSXtract/CHDman, gallery and safe legacy audit.
- [ ] Confirm v1.6.3 package can replace the old test *program folder*, not automatically rename any files in the virtual NAS workspace.
- [ ] Inspect legacy PS1/Disc 1 file identity manually; no automated cleanup until evidence is conclusive.

[Acceptance and recovery](PS1_BATCH_IDENTITY_AND_STOP_v163.md).


- [x] **Batch PS1 Classics:** choose a directory of ZIP/7Z/EBOOT packages; isolated per-game queue with GAME N/TOTAL, readable summary and continuation after a bad archive.
- [x] Multiple archives selected in Add Game Files are processed individually, not pooled into one potentially mislabeled PSN extraction.
- [x] Repeat PSN EBOOT content checks prevent extra CHDs/M3Us even across renamed/repacked ZIP/7Z; non-PS1 PSP EBOOTs are not misconverted.
- [ ] Batch real PSN archive acceptance at 125% after Windows/Linux CI.

## v1.6.2 · Live PS1 disc extraction + cross-console deduplication

- [x] Live PSXtract output drain with bounded memory; translate only non-sensitive disc/milestone lines into user-facing progress. Do not expose keys, offsets, PSN IDs or stdout logs.
- [x] Game import SHA-256 identity checks across all 13 platform roots, for both ordinary files and ZIP/7Z members.
- [x] Exact duplicates skipped; same title with different data held for review; different regions/revisions preserved; ignore CUE/BIN/M3U companions to protect multi-track discs.
- [x] PSN EBOOT source fingerprint receipt under ignored .retro-library metadata (no spurious extra ROM tile); old and unproven same-title CHD sets preserved.
- [x] Added synthetic tests: all-platform duplicate handling, 7Z/ZIP, game formats, safe read-only receipts, PSXtract console milestones.
- [x] [PR #20](https://github.com/ValentineBSAA/RG-Rotate/pull/20) merged to main; [source CI 45261322930](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45261322930) **364 Windows passed; 363 Linux passed / 1 skipped**.
- [ ] User 125% screenshots of per-disc extraction, skipped duplicates, no new tiles for reimports.
- [ ] Actual real FFVII triple-CHD/M3U gallery and RG Rotate gameplay verification.

[Full v1.6.2 checklist](LIBRARY_DEDUP_AND_PS1_PROGRESS.md).


## v1.6.1 · Final Fantasy VII PSN EBOOT and real 7Z import

- [x] Source: PS1 Classics PBP header detection including multi-disc signatures; `KEYS.BIN` and `DOCUMENT.DAT` are PSN companions, not convert-to-CHD inputs.
- [x] Source: optional installed PSXtract bridge for PS1 CUE/BIN extraction in local temp, followed by verified CHDman+M3U pipeline; refuse bad disc numbering, incomplete output or missing helper.
- [x] Source: archive folder title hint survives NPEF-series directory IDs and 7Z extraction; preserve all original files, reject nested/oversize archives.
- [x] Added synthetic PSN fixture + real py7zr archive regression tests; **GitHub CI pending**.
- [ ] Real Windows installation and executable test of PSXtract v3.0 from reviewed upstream release.
- [ ] Real user's FFVII PSN EBOOT conversion into verified CHDs, one M3U, correct artwork/disc count; manual user acceptance, not inferred from mocks.
- [ ] Real RG Rotate disc swapping and saves after safe card transfer.

[Full PS1 Classics / 7Z checklist](PSN_CLASSICS_IMPORT.md).


## v1.6.1 · PSN EBOOT/KEYS and validated 7-Zip import

- [x] Source: distinguish PS1 Classics PSN EBOOT from PSP native EBOOT. Treat KEYS.BIN and DOCUMENT.DAT as companion files, not independent BIN tracks or CHDs.
- [x] Source: optional PSXtract v3.0 pinned SHA-256 checked installer with user opt-in; no automatic format or unapproved executable download.
- [x] Source: extracted CUE/BIN goes through prior CHDman verify, ordered M3U and one artwork tile; fail closed for missing tool, incomplete tracks, invalid disc order or unsupported PBP.
- [x] Source: actual .7z creation/extraction tests (synthetic three-disc files), mocked PSXtract package handoff and unsafe extraction tests.
- [x] PR #17 merged to main. [Main CI 45251934269](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45251934269) passed **326 Windows** and **325 Linux with 1 skipped**. GitHub-built v1.6.1 source ZIP checksum/CRC checked; clean extraction locally **292 passed, 34 skipped** without optional Qt/7z dependencies.
- [ ] User confirms real 7z archive with Final Fantasy VII PSN EBOOT, KEYS.BIN, DOCUMENT.DAT safely extracts three actual disc CUE/BIN pairs.
- [ ] User confirms actual CHDman produces three verified CHDs, one Final Fantasy VII.m3u, one artwork tile with 3 DISCS, originals unchanged.
- [ ] RG Rotate emulator disc switching and saves verified on physical device.

[Full acceptance](PS1_CLASSICS_7Z_ACCEPTANCE.md). Actual Sony PSN decryption is not proven by fake fixtures.


## v1.6.0 · Friendly details + safe USB microSD discovery

- [x] Three dense details popups replaced by premium summary cards with expandable raw paths/bytes and Copy details.
- [x] Copy to card scans candidate removable and plausible 512 GB fixed-looking USB reader drives on a background worker, never automatically selecting or copying.
- [x] Physical transfer preview captures Windows volume GUID/serial, capacity, filesystem and letter. Copy blocked without fresh identity, exFAT and explicit typed drive letter.
- [x] Worker rechecks card identity before copying and transfer engine verifies again before each file; existing non-overwrite/8 GiB reserve/SHA-256 stays in place.
- [x] [Merged main CI](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45246376971) passed **311 Windows tests, 310 Linux passed with 1 skipped**; exact final v1.6.0 package CRC verified and clean-extracted (279 local tests passed, 32 skipped without Qt).
- [ ] User verifies refreshed dialog UI at 125% and connected USB card candidate.
- [ ] Actual card identity, exFAT, volume capacity and first small verified copy.
- [ ] Actual RG Rotate emulators/Cocoon and M3U disc swap/saves.
- [ ] No automatic formatting; protect Synology NAS sources and prior v1.5.9 release.

[Full acceptance checklist](CARD_DETECTION_AND_READABLE_DIALOGS.md).


## v1.5.9 · Virtual exFAT card profile / Multi-disc detail follow-up

- [x] Source: pass validated M3U members through read-only worker JSON into Qt; do not prematurely hide CHD members. Gallery owns one playlist tile with **N DISCS** badge and lists each member in Format Details.
- [x] Source: second simulated exFAT meter below the **unchanged nominal 512 GB** card meter; pure 128 KiB cluster, partition/FAT/bitmap/boot estimate; actual scanned file allocation slack and existing 8 GiB + 8 GiB budgets.
- [x] Source: `exFAT details…` labels estimates, does not format/delete/allocate; Windows physical card Preview remains authoritative.
- [x] Source and Qt regression passed [main CI 45242023081](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45242023081): Windows 301 passed; Linux 300 passed/1 skipped.
- [x] [PR #14](https://github.com/ValentineBSAA/RG-Rotate/pull/14) merged; exact main Windows/Linux CI green. [Packaging run 45242022687](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45242022687) succeeded; clean-extracted ZIP 273 passed/28 skipped locally (PySide6 not available).
- [ ] User Windows 125% screenshot showing **2 DISCS**, format details lists both CHDs, and both capacity meters are readable.
- [ ] Physical microSD formatted capacity, filesystem and free-space verification after arrival; never auto-format or destroy NAS/SD card data.
- [ ] Actual RG Rotate Cocoon/emulator disc switching, save/load and cover recognition after transfer.

**Detail plan:** [Virtual exFAT plan](VIRTUAL_EXFAT_PLAN.md). Preserve v1.5.8 successful CHDman outputs and every previously imported game.


## v1.5.8 · Smart PlayStation multi-disc collections

**Goal:** One Game/One Cover/One Parent Folder, with a verified CHD per actual physical disc and one safe ordered M3U. Related to existing [multi-disc issue #2](https://github.com/ValentineBSAA/RG-Rotate/issues/2).

- [x] Code: dedicated full PS1 folder import action; conservative Disc/Disk/CD identity; preserve edition/region/Resident Evil 2 character tags; never join FFVII with FFVIII.
- [x] Code: create CHDs from complete CUE/BIN via CHDman and preserve original NAS/source, or verify and organize existing CHDs without recompression.
- [x] Code: consecutive 1..N ordered M3U; safe incremental extension with conflict checks; reject ambiguous/duplicate/missing tracks, playlist clashes, unsafe CUE paths.
- [x] Code: one My Games gallery tile/cover and N DISCS badge using scan-worker M3U members; do not hide discs behind broken playlist; raw File List remains detailed.
- [x] Synthetic Python/optional Qt tests added in `tests/test_v158_collections.py` (pending GitHub CI evidence).
- [x] v1.5.8 [PR #13](https://github.com/ValentineBSAA/RG-Rotate/pull/13) merged; [GitHub CI run 45162967417](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45162967417) passed 289 Windows / 288 Linux with 1 skipped. GitHub packaging and clean extracted local source tests also passed; **not** Windows/NAS gameplay acceptance.
- [ ] Physical Windows 11 / Synology acceptance M01–M09 from [MULTIDISC_ACCEPTANCE.md](MULTIDISC_ACCEPTANCE.md), starting with a disposable complete Resident Evil 2 (USA) two-disc set.
- [ ] Real RG Rotate/Cocoon game-launch and disc-swap acceptance M10, only after hardware arrives.
- [ ] v1.5.5 destructive cleanup / v1.5.6 capacity meter regression acceptance remains separate, never silently inferred.

**Build policy:** Source release only after CI; no claim that mocked CHDman verifies real user disc data. See [complete checklist](FULL_TEST_CHECKLIST.md).


## v1.5.7 · Console shelves and system-aware library (source candidate)

**Implementation merged into `main` via [PR #11](https://github.com/ValentineBSAA/RG-Rotate/pull/11), squash commit `6515dba`.** display-only system sections with full-width headers, colored console pills and logical game counts; matching gallery/file-list filters; conservative explicit PS2/GameCube folders and experimental-use warnings. No actual RG Rotate support claim or new OS/app installation.
- [x] Source logic and offline Qt regression cases committed for console group ordering, 100/125/150% scaling, filter synchronization, import folder classification.
- [x] GitHub Actions [PR run 45155293003](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45155293003) **and merged main run 45155602315** passed **279 Windows** and **278 Linux + 1 skipped** source tests. **Real Windows/NAS/handheld acceptance remains pending.**
- [ ] Real Windows v1.5.7 screenshot at 125%, tabs, grouping, search, file list, artwork and no duplicate discs.
- [ ] Validate PS2/GameCube isolated test imports with original NAS sources untouched.
- [ ] Preserve v1.5.5 batch CHD pending verification, v1.5.6 capacity meter pending Windows UI/hardware verification.
- [ ] Physical RG Rotate gameplay, system cover mapping and emulation tests after device arrives.

**Complete acceptance plan:** [FULL_TEST_CHECKLIST.md](FULL_TEST_CHECKLIST.md) covering A01–G05; do not replace older real results with inferred passes.

_Last updated: 2026-11-23 (Arizona time). Status is evidence-based, never assumed._

**Definition of done:** A checked item has met its own acceptance criteria, not just compiled or passed mocked tests. Use **[x]** only for the exact tier verified. Each milestone must have code, regression tests, updated docs, and a real acceptance result where applicable.

## P0 · Arriving device / first working PS1 import

Tracked: [#1 Clock Tower CHD](https://github.com/ValentineBSAA/RG-Rotate/issues/1), [#2 multi-disc M3U](https://github.com/ValentineBSAA/RG-Rotate/issues/2), [#3 artwork](https://github.com/ValentineBSAA/RG-Rotate/issues/3), [#4 physical RG Rotate](https://github.com/ValentineBSAA/RG-Rotate/issues/4).

- [x] Windows v1.4.4: Choose/remember an SMB/NAS virtual-card location without allocating a 512 GB image (user verified).
- [x] Windows v1.4.4: Import at least one game to NAS and stop a running import without force-closing (user verified).
- [x] Windows v1.4.x: Import Cocoon APK, PPSSPP APK, RetroArch APK; confirm staged packages (user verified).
- [x] Windows v1.4.x: Library health check completed with 1 game, 0 duplicate groups, 0 broken CUE/M3U references (user screenshot).
- [x] Windows v1.4.4: Practice NAS→Windows copy, 6/6 SHA-256 verified; repeated verification with 0 new files, 6 identical, 6/6 verified (user screenshots).
- [x] Code v1.5.1: Implement automatic CUE/BIN track inspection → CHDman conversion → CHD verification → publication; multi-disc M3U creation; preserve original files; single unified import progress (Linux tests pass).
- [x] Code v1.5.1: Fix CUE-only tiny game-size display to account for full referenced BIN set (Linux tests pass).
- [x] Code v1.5.1: Safe-stop import/CHD worker and report failures without releasing incomplete .chd files (Linux tests pass).
- [x] Code v1.5.1: Artwork matching retries and manual fallback integrated into PS1 preparation (Linux tests pass).
- [ ] **Critical:** On Windows 11, launch v1.5.2 at 125% UI scaling, import user's *Clock Tower: The First Fear* English patch (one CUE, two BINs). Confirm CHDman actually runs and the My Games tile shows **one playable CHD and its correct file size**, not a 226–228-byte CUE.
- [ ] On Windows, test failure handling on a deliberately missing/renamed referenced BIN track; original sources intact, helpful visible error, progress returns Ready, no incomplete playable CHD.
- [ ] On Windows, test a genuine two-disc PS1 title: each disc converted separately, playlist created in correct order, gallery shows one game, changing disc works in emulator.
- [ ] On Windows, verify artwork automatic search returns a cover where available and preserves user-chosen covers/edition names. Confirm unavailable covers show friendly “Search/Choose Cover” action; no wrong cover silently attached.
- [ ] First full external 512 GB card: validate actual free capacity, exFAT compatibility, and capacity reserve; copy from NAS, verify hash, safely eject; **never format automatically**.
- [ ] Real RG Rotate: install supported APKs with consent, configure Cocoon as frontend, set emulator mappings / ROM folders, test PS1/PSP/DS games and return-to-home.

## P1 · Beginner-first workflow and library completeness

Tracked: [#5 app installer](https://github.com/ValentineBSAA/RG-Rotate/issues/5), [#6 UX/reliability/CI](https://github.com/ValentineBSAA/RG-Rotate/issues/6).

- [ ] Replace remaining scattered controls with a clear guided “Add Games → Prepare Apps → Copy to Card” workflow at 100%, 110%, 125%, 140%, 150%; keep advanced screens discoverable.
- [ ] Clearly show “Stage → Inspect → Convert → Verify → Add to Library → Find Artwork” under **one overall task progress bar**, with accurate stage text and cancellation.
- [ ] Show per-game **logical title + disc count + complete file footprint**; list source tracks only in advanced details, not as separate playable games.
- [ ] CHDman actionable failures, missing CUE references, multi-track audio, Unicode/legacy encodings, ZIP/7Z imports and partial file cleanup/retry.
- [ ] Stage APKs vs installed Android state clearly distinguished. Recognize manual Cocoon file alias `cocon-311.apk`; report “user APK ready; publisher unverified” until officially verified.
- [ ] Verify Ninite-like official download and offline resume/skip behavior on Windows. Executable checks for adb.exe/chdman.exe.
- [ ] Test imported CHDs, ZIP/7Z, M3Us and playlist paths when transferred and opened by Cocoon and standalone emulators.
- [ ] Add production-quality artwork retrieval/provider failure messages; prevent repeated NAS scans from locking UI.
- [ ] Verify home-screen browsing, multi-system game organization, favorites, and navigation for the 720×720 screen.
- [x] Publish the full **v1.5.1 text source and tests** in this GitHub repo under `RetroLibraryStudio/` (commit `b458028`).
- [x] GitHub Actions regression CI is green on v1.5.1 source after a Windows ZIP/CUE companion path fix: **Windows 241 passed**, **Linux 240 passed / 1 skipped** ([run](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45138220982)).
- [ ] Tag a versioned source release after genuine Windows CHDman and artwork acceptance tests.

## P2 · Hardware follow-through

Tracked: [#7 built-in vs custom AI companion](https://github.com/ValentineBSAA/RG-Rotate/issues/7).

- [ ] Choose a DS emulator and map single-screen top/bottom toggle to a spare button for *Yu-Gi-Oh! GX: Spirit Caller*; check touchscreen accuracy.
- [ ] Test PSP favorites in PPSSPP, especially SOCOM Tactical Strike, Syphon Filter Dark Mirror / Logan's Shadow, Gran Turismo, and Pursuit Force Extreme Justice with RG Rotate's controls.
- [ ] Test Cocoon's launcher/home default, opening apps, returning from an emulator, and rotating the display; establish easy recovery to stock Android.
- [ ] Test and document performance/controls of PS2/GameCube **individually only**. Do not assume Most Wanted 2005 runs at full speed on the T618.
- [ ] Compare Anbernic's built-in AI game assistant to planned voice-first companion. Only implement missing capabilities after on-device evaluation.
- [ ] Plan companion's data area with an 8 GiB **budget** on card, not an empty allocation; persistent memory on microSD, temporary screenshots, optional NAS backup.

## Decisions locked unless user changes them

- **Cocoon Shell** is the default frontend.
- **Windows PySide6** is the management UI; window position/size and 125% scale persist.
- **Synology NAS via mapped drive/SMB** is the allowed virtual-card workspace; 512 GB is virtual budget, not preallocated.
- **8 GiB always-free safety margin** + **8 GiB AI companion budget** on the eventual card, recalculated from actual formatted capacity.
- **No silent formatting, deletion, moving originals, conflicting-file overwrite, or bypass of verification.**
- Auto convert complete PS1 CUE/BIN sets to verified **single-disc CHDs before library display**; generate an **M3U only for multi-disc games**, referencing the separate CHDs. M3U is a tiny playlist, **not an image combining multiple discs**.
- All potentially blocking NAS work runs off the GUI; cancellation must leave incomplete outputs non-playable and recoverable.
- Artwork searches should be automatic but conservative; uncommon editions get a manual result picker.

## Roadmap maintenance rule

When you or Codex make a change: (1) link an issue/commit/PR, (2) update the relevant check here, (3) update VERIFICATION_MATRIX.md with exact test environment + evidence, (4) update PROJECT_HANDOFF.md with new blockers/current version, (5) record release notes. Never mark physical Windows/Android acceptance complete merely because unit tests pass. When opening a new chat, begin with README → PROJECT_HANDOFF → ROADMAP → latest code.

There is no unattended GitHub update running. “Continuously update” means update this file **with each development change**, not invent scheduled automatic commits.

### v1.5.2 packaging milestone · 2026-11-23

- [x] Built source ZIP with Windows startup launcher, included GitHub CI-tested Windows track-path fix and new source tests; clean extract: **226 passed, 15 skipped** locally.
- [ ] User confirms actual Windows v1.5.2 launch and Clock Tower two-track CUE conversion with real CHDman.
- [ ] User confirms cover search, single progress workflow and no tiny-CUE size display in My Games.

### v1.5.3 · Format transparency / artwork catalog fallback (2026-11-23)

- [x] Add clickable format badges on My Games tiles from **actual scanned file extensions** (CHD / BIN-CUE / M3U / ISO / PBP etc), and file details popup. CHD badge does **not** claim integrity verification.
- [x] Add offline-tested Libretro catalog fallback to official platform-specific GitHub tree; image download fallback to raw.githubusercontent.com; manual browser and PC-image options remain.
- [x] Package source-based Windows test ZIP `RetroLibraryStudio_v1.5.3_Windows_Test_Beta.zip`; clean-extract local Linux test: **230 passed, 15 skipped**; [GitHub CI run 45141431778](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45141431778): **245 passed Windows / 244 passed + 1 skipped Linux**.
- [ ] **User acceptance:** Confirm Clock Tower shows BIN/CUE until an actual CHD is stored, then CHD after Refresh. A 118.0 MB reported size alone is not proof of CHD.
- [ ] **User acceptance:** Perform live artwork search on Windows; if both public providers fail, capture exact network status/error.
- [ ] User confirms genuine CHDman conversion and verified card transfer with the real files.

### v1.5.4 · Artwork previews + contextual PS1 CHD organizer (2026-11-23)

Tracked by [#8](https://github.com/ValentineBSAA/RG-Rotate/issues/8), committed as [b0c02214](https://github.com/ValentineBSAA/RG-Rotate/commit/b0c02214917e0356d6c00645a40b7ef26090ac30).

- [x] Code: Automatically preview selected Libretro artwork in the search dialog; keep explicit confirmation before using a cover, and make double-click preview rather than apply.
- [x] Code: Context menu on game tiles and file-list entries with title edit, cover search/preview, format details, PS1 CHD/tidy and open folder.
- [x] Code: CUE/BIN disc and safe recognizable raw IMG → verified CHD **in the existing PSX folder**. Reverify CHD on NAS; only then move source tracks into a sibling recovery folder **outside the virtual card**. Originals are preserved, not deleted.
- [x] Code: Reject ambiguous IMG, CloneCD CCD/IMG/SUB, and shared-disc track references when safe reconstruction/cleanup cannot be established.
- [x] Package `RetroLibraryStudio_v1.5.4_Windows_Test_Beta.zip`; local regression tests **240 passed, 15 skipped** (Qt OS-specific tests skipped locally).
- [ ] User Windows acceptance: browse/select covers and observe full preview **before applying**; confirm attractive context menu at 125%.
- [ ] User Windows acceptance: Convert Clock Tower real CUE + two BINs with CHDman and NAS, confirm CHD badge, only CHD in PSX directory, recovery outside virtual card, and preserved artwork.
- [ ] User Windows acceptance: IMG raw-track test, verification failure rollback, incremental NAS practice transfer, and physical microSD/Cocoon later.

- [x] v1.5.4 GitHub source CI: [run 45144304702](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45144304702) **255 passed on Windows**, **254 passed / 1 skipped on Linux**. These tests still do not establish real CHDman/NAS/handheld acceptance.

### v1.5.5 · lossless PS1 batch conversion and safe cleanup (2026-11-23)

- [x] **User-observed v1.5.4 Windows pass:** Clock Tower CHD **55.4 MB** and Resident Evil Gore Edition CHD **311.9 MB**; CHDman verification succeeded, both CHD badges and chosen artwork displayed.
- [x] Implement code-only v1.5.5 batch conversion for CUE/BIN and safe standalone IMG sources under the selected virtual-card `ROMs/psx` tree, using MAME's default **lossless** CD codecs and per-disc CHDman verification.
- [x] Offer explicit **Keep recovery backups** or **Remove verified virtual-card working copies** with double confirmation for deletion. No deletion of separately stored NAS source originals or old recovery backups.
- [x] Add **Open conversion backups** action and single conversion dialog buttons linking output/recovery folders.
- [x] Cover previews now scale the entire image to available space preserving aspect ratio on resize, using an in-memory pixmap (not NAS reads).
- [x] Linux clean-extracted v1.5.5 package: **248 passed / 16 skipped**, ZIP integrity check passed. [GitHub CI run 45148569884](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45148569884): **Windows 264 passed; Linux 263 passed and 1 skipped**.
- [ ] **CRITICAL user acceptance:** On Windows, batch convert 2 disposable PS1 discs (with both cleanup choices) and confirm only virtual-card working files are removed after genuine CHDman verification, not external NAS originals.
- [ ] Verify right-click recovery folder opens, cover preview remains inside frame at 125%, and an interrupted batch preserves failed/unprocessed source tracks.
- [ ] Review old v1.5.4 conversion backups manually; do **not** auto-delete them from the NAS because provenance is unknown.


### v1.5.5 · Batch lossless PS1 conversion and safe cleanup (2026-11-23)

- [x] **Local source beta:** Add batch PS1 CUE/BIN and unambiguous IMG → verified CHD conversion, one progress task, per-game failure summary, and conversion cancellation. **248 passed, 16 skipped locally**.
- [x] **Local source beta:** Offer explicit **Keep recovery backups** or **Remove verified working copies**. Deletion is limited to the active virtual card's `ROMs/psx` files and only follows two completed verification steps. Files outside the virtual card, including the user's separate NAS ROM collection, are untouched. Previously generated recovery backups are not deleted automatically.
- [x] **Local source beta:** Add **Open conversion backups** and cover-preview fit-to-window behavior.
- [x] Package `RetroLibraryStudio_v1.5.5_Windows_Test_Beta.zip` (73 members; SHA-256 `e1a00b4f0147353ffdc37f47bb49e69a87afd5bfc23a9839968232834d441350`); ZIP integrity passed and local Linux tests passed **248/16 skipped** after sanitizing personal NAS/example-user paths.
- [x] **GitHub source and CI:** v1.5.5 source and tests published. [CI run 45149019365](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45149019365): **264 Windows passed; 263 Linux passed / 1 skipped**. Real Windows NAS batch cleanup still pending.
- [ ] **Windows acceptance:** Run v1.5.5 batch on disposable test PS1 discs with CHDman. Confirm all CHDs verified, each disc stays in its expected `ROMs/psx` location, the `CHD` badge and covers persist, and all source originals outside the virtual card remain intact.
- [ ] **Windows cleanup acceptance:** Choose **Remove verified working copies** for disposable card copies only. Failed or cancelled conversions must retain their source tracks; user confirms no deletion of source collection or earlier recovery backups.
- [ ] **Windows preview acceptance:** Confirm artwork selection previews preserve aspect ratio while resizing; test bad network / timeouts and safe Stop.

### v1.5.6 · Card visualization and real capacity (2026-11-23)

- [x] Source code: persistent 512 GB virtual-card capacity strip on all pages, with exact-byte details, staged files, unused companion budget and 8 GiB protected free space.
- [x] Source code: Copy to Card actual formatted-capacity preview (only after a real physical destination is selected and measured), currently used space, proposed new data, estimated free after transfer.
- [x] Transfer preflight: block when formatted capacity is smaller than staged library + protected budgets, or when free-space safety reserve would be violated.
- [x] Automated model tests (local 255 passed / 19 skipped). No background NAS scan added.
- [ ] Windows PySide6 CI & visual acceptance at 125% scaling.
- [ ] User verifies bar against Windows card Properties and staged CHD/APK/cover totals; capture screenshot.
- [ ] First physical-card verified transfer, no unexpected formatting/deletion and 8 GiB free after transfer.

### v1.5.6 acceptance build packaged (2026-11-23)

- [x] Windows test ZIP built: `RetroLibraryStudio_v1.5.6_Windows_Test_Beta.zip` (3,107,017 bytes; SHA-256 `1bf62b798111f9d621ee5fffb07ba37ecfbcc854b1f3c186dc8495cac1efe36f`). ZIP CRC and clean-extraction checked.
- [x] GitHub [CI run 45152416169](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45152416169): **274 passed Windows**, **273 passed + 1 skipped Linux**.
- [x] Downloadable ZIP cleanroom local suite: **255 passed / 19 skipped**.
- [ ] User tests persistent 512 GB planning bar, Exact sizes details, and read-only measured physical-card preview on real Windows + microSD.
