# Project handoff · read this before working

**IMPORTANT v1.6.7 enhancement after original diagnosis:** Confirmed against has207/psxtract-2 v3 source: its command-line `psxtract_main` guards a missing optional document, so `-c EBOOT.PBP "" KEYS.BIN` is safe on the receipt-verified v3 helper, letting it use the **actual adjacent** key rather than defaulting to derived-key mode. Added `verified_psxtract_v3_key_only` to `ps1_psn.py` and tests covering v3-only arguments, key privacy and conservative fallback for any unverified/custom older binary. This MAY resolve the Clock Tower II PGD MAC error but cannot be called successful until real EBOOT conversion verifies; never invent DOCUMENT or substitute keys. [v1.6.7 checklist](PSXTRACT_PGD_AND_PICKER_POLISH_v167.md).


## v1.6.7 critical handoff · Clock Tower II PGD failure in successful title-aware picker

User's actual Windows v1.6.6 photo shows the custom PS1 chooser **WORKS**: 30 packages identified by EBOOT metadata, game names and Sony folder IDs visible, with Clock Tower II - The Struggle Within (SLUS00695) selected. The imported game failed before CHDman: console after PBP unpacking says `Single disc game detected`, `Decrypting ISO header`, `PGD: Invalid 0x80 MAC hash!`, `ERROR: ISO header decryption failed!`. Final summary: 1 checked, **0 imported / 0 already present / 1 needs attention / 0 verified CHDs**. This is PSXtract encrypted-header authentication failure, not the artwork or title picker. Actual helper outcome for Clock Tower II remains unverified despite other Crash Bandicoot imports succeeding. The app's old generic negative exit message is bad UX.

v1.6.7 source branch `fix/v1.6.7-psxtract-header-diagnostics-picker-polish`: PSXtractMilestones maps the exact PGD/ISO error to privacy-safe UI statuses, describe_extractor_failure explains no CHD conversion and possible matching companion/unsupported source, and the chooser header/results copy is now shorter (source folder basename, full NAS path in tooltip, 30 found). **Important potential source issue:** current positional helper only passes KEYS.BIN when DOCUMENT.DAT exists; if KEYS only, built-in derivation is used. This is not proven the sole cause, and inventing fake manual/key data is unsafe. Don't claim Clock Tower fixed without real successful extraction. See [acceptance checklist](PSXTRACT_PGD_AND_PICKER_POLISH_v167.md). Preserve original packages, older generic PS1 entries and verified CHDs.


**v1.6.6 completion (November 23, 2026):** [PR #24](https://github.com/ValentineBSAA/RG-Rotate/pull/24) merged into main (squash `23ce722`). Exact branch-head [CI run 45280723949](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45280723949) passed **398 Windows tests, 397 Linux tests with 1 skipped**. [Windows source ZIP](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45280714622) at tested commit `2a778d5` packaged successfully (123 internal entries; ZIP CRC good), downloaded as `RetroLibraryStudio_v1.6.6_Windows_Source_Beta.zip`. **Still pending:** physical Windows 11 NAS test of the v1.6.6 single/multi PS1 title picker, real automatic cover after CHDman verify, and real repeat EBOOT skip; do not mark those passed from synthetic CI. v1.6.4 user-tested Crash Bandicoot CHD conversion and Stop are the baseline. Native Windows picker showing NPEE codes is intentionally replaced *inside the app* by a title-aware chooser when last folder is PS1; cannot actually rename Windows file-dialog folders. Verified CHDs remain valid if cover download fails. Old anonymous v1.6.2 PS1 entries remain untouched. [Exact v1.6.6 acceptance checklist](PS1_UNIFIED_PICKER_AND_POST_CHD_ART_v166.md).


## v1.6.6 Beta handoff · Fix native file picker trap and post-CHD cover ordering

**2026-11-23 real user follow-up:** With v1.6.5, **Add Game Files** still displayed native Windows `NPEE00001` / `NPEE00008` folders, not game titles; user picked EBOOT+KEYS inside a Sony ID subfolder and successfully imported another Crash Bandicoot game to CHD. Manual cover workflow returned the right USA cover and applied it after confirmation, but the desired automatic cover step did NOT. User explicitly requires the automatic cover workflow to start **only AFTER CHD conversion/verification**. A native Windows OS picker cannot rename source folders; route the app entry point into the custom PBP-title dialog instead.

v1.6.6 source branch: `fix/v1.6.6-unified-picker-cover-automation`. `pick_files` now uses `psn_picker.ps1_parent_from_last_location` to open the same custom selection dialog for one or many PS1 titles; its "Browse other ROM files" action retains standard native ROM file selection. Automatic artwork root cause: `key_title('Crash Bandicoot™')` didn't match Libretro catalog `Crash Bandicoot (USA)` because `™` was extra punctuation word. `key_title` now strips legal glyphs only from normalized artwork lookup. `guided_import` now reports verified CHD publication, performs exact automatic cover lookup only after verified CHD, and, on proven duplicate SHA receipt, may fill a previously missing cover WITHOUT re-extracting/converting the game. Artwork/network errors are not CHD failures. All original EBOOT/KEYS and old generic v1.6.2 PS1 entries preserved.

Synthetic post-CHD tests and full Windows/Linux regression required before merge. Real Windows NAS artwork success, new picker and post-success duplicate skip **NOT YET VERIFIED**. See [v1.6.6 acceptance](PS1_UNIFIED_PICKER_AND_POST_CHD_ART_v166.md).


**v1.6.5 completion update (November 23, 2026):** [PR #23](https://github.com/ValentineBSAA/RG-Rotate/pull/23) merged into main (squash `b8fe446`) after [Windows/Linux CI](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45278366622) passed **394 Windows, 393 Linux with one skip** on source commit `96c02a7`. [Windows 1.6.5 source ZIP](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45278357384) passed packaging/CRC and includes new PS1 title picker and tests; this is **source beta, not an EXE**. User's proven physical Windows baseline is still v1.6.4 Crash Bandicoot™ CHD conversion + Stop task working. **v1.6.5 real NAS PS1 folder selection, automatic artwork, duplicate retry, and physical RG Rotate launch NOT YET TESTED.** The new UI reads actual EBOOT title from public PBP metadata instead of guessing Sony NPEE product IDs; the user can select a subset and EBOOT companions are found automatically. Browse PS1 Classics, Add Folder, Add Files remember the last game folder. Existing anonymous PS1 CHDs from v1.6.2 should NEVER be automatically deleted/renamed. [Exact acceptance checklist](PSN_GAME_PICKER_AND_ARTWORK_v165.md).


## v1.6.5 Beta user testing handoff · selectable EBOOT titles + automatic artwork

On November 23, 2026, user reported that **v1.6.4 successfully extracted/converted Crash Bandicoot™ to CHD** and that Stop intentionally canceled an in-progress extraction; restarting the import was successful. The user is keeping ROMs on a Synology NAS under `PSTV/PSP/GAME/PS1/NPEE00001/EBOOT.PBP` with `KEYS.BIN` next to it. User needs to choose a subset of 30 code-folder PSN games, not import everything; default native file picker is opaque, remembers wrong folder and requires manual EBOOT+KEYS selection. User also wants genuine in-app MD5/CHD progress and automatic covers (USA when unknown, original region respected), with no redundant dialog for confident matches across all console platforms. Correct source identity is from PBP public metadata; **do not hardcode guessed code mappings**.

v1.6.5 candidate branch: `feature/v1.6.5-psn-game-picker-artwork`. Added isolated `psn_picker.py`, `scan_psn_catalog` worker mode, selectable `batch_psn_selected` worker mode, searchable/checkable title grid, last game folder `QSettings`, main UI named PS1 progress, MD5 event, exact-cover region handling, trademark-stripped cover *lookup only*, and synthetic tests. **Add Folder** invokes PS1 picker when EBOOT evidence is found, otherwise preserves normal multi-console import. A single selected PBP discovers KEYS sidecar itself. [Acceptance checklist](PSN_GAME_PICKER_AND_ARTWORK_v165.md). Do not claim beta tests complete before CI. Existing generic PS1 tile(s) from v1.6.2 are untrusted; no automatic renaming/deletion. A canceled and restarted PSN game is not yet a proven post-success duplicate skip.


**STATUS UPDATE 2026-11-23:** [PR #22](https://github.com/ValentineBSAA/RG-Rotate/pull/22) for v1.6.4 Unicode CUE fix merged into main (squash `21c2b5a`). Source CI run [45272838436](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45272838436) **384 Windows passed; 383 Linux passed, 1 skipped**. The exact branch-head source ZIP [45272820961](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45272820961) packaged successfully (commit `8d755754`; subsequent merge was squash of same source). Real Windows user **Crash Bandicoot™** CHDman createcd + verify, duplicate retry, and Stop acceptance are **still pending**. v1.6.3 had recognized title correctly but imported zero files because CHDman reported Unicode CUE filename missing. User should use v1.6.4 source ZIP from GitHub Actions, install in new program folder, start with one Crash Bandicoot™ EBOOT, inspect named CHD after verification, then repeat same EBOOT. No big 30-game batch until passes. Retain anonymous v1.6.2 PS1 CHDs untouched. Full [v1.6.4 checklist](PSN_UNICODE_CHDMAN_v164.md).


## CRITICAL v1.6.4 handoff · Crash Bandicoot™ real CHDman failure

On November 23, 2026, user physically ran v1.6.3 Beta Windows single-file PSN EBOOT import. App correctly recognized **Crash Bandicoot™** but CHDman 0.289 exited 1 during createcd: Error parsing input file `...\\rgl-psn-extract-...\\Crash Bandicoot™ (Disc 1).cue: No such file or directory`. Final dialog: **Added 0 file(s), 0 already present**. No valid converted CHD was observed, so **do not claim success or test duplicate yet**. Likely Unicode (™) unsupported in CHDman CLI path; input CUE may be present to Python but not CHDman. Implemented fix in v1.6.4 branch `fix/v1.6.4-unicode-psn-chdman`: `ps1_chd_bridge.ascii_psn_cue` alias of CUE in disposable local PSXtract temp, ASCII hardlinks for Unicode BIN track names, cleanup in finally. PSN pipeline passes ASCII alias to CHDman and publishes the originally identified Unicode filename AFTER verification; normal hand-picked CUE imports untouched. New tests include synthetic Windows legacy-CLI failure surrogate. **Real Windows CHDman verification is still required.** See [v1.6.4 checklist](PSN_UNICODE_CHDMAN_v164.md). Preserve old anonymous v1.6.2 output for manual inspection.


**STATUS UPDATE · 2026-11-23:** v1.6.3 fix was merged to main in [PR #21](https://github.com/ValentineBSAA/RG-Rotate/pull/21) (squash commit f3ec0e8). [Windows/Linux source CI](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45269373105) passed **379 Windows / 378 Linux and one skipped**. The exact tested code was [packaged successfully](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45269530914) as RetroLibraryStudio_v1.6.3_Windows_Test_Beta.zip from branch head 788853f (workflow-only change after successful source CI). **The old user NAS batch was defective; REAL v1.6.3 Windows Stop/PSXtract/CHDman acceptance is still PENDING.** Do not delete or relabel the existing generic PS1 CHDs automatically. New-chat first step: test Stop and named imports on a disposable workspace, then review old NAS files. See [v1.6.3 checklist](PS1_BATCH_IDENTITY_AND_STOP_v163.md).


## CRITICAL handoff 2026-11-23 · v1.6.3 stop/title regression

Real user imported a folder of 30 PS1 Classics with v1.6.2. Main GUI showed GAME 1/30 • PS1 and later GAME 2/30 • PS1, PS1 extraction/CHD conversion. User reports converted files were published with a generic PS1 cover and PS1/Disc 1.chd instead of actual game identity, and Stop task did not reliably stop. **v1.6.2 real NAS acceptance FAILED.** The root cause was package_title trusting wrapper stem PS1 as a valid title. v1.6.3 fix branch: fix/v1.6.3-psn-title-stop-safety. Source changes: bounded PBP PARAM.SFO TITLE fallback, generic-name rejection, batch relabel, verified result folders, direct Open game folder, Stop escalation, single-disc duplicate receipts, new tests/docs and 1.6.3 source ZIP workflow. **Do not claim verified until CI AND actual Windows Stop test.** Do not automatically delete/relabel existing generic PS1 CHDs because their source identity is unproven. The safest next step is to stop the old running v1.6.2 batch, inspect originals and generic output, test 1.6.3 on disposable workspace. Exact steps: [v1.6.3 acceptance](PS1_BATCH_IDENTITY_AND_STOP_v163.md).


**Additional user requirement:** user has many PSN PS1 Classics packaged for PSP and wants a **one-folder batch import**, no duplicates, in addition to the all-console duplicate guard. Implemented `ps1_batch.py` with per-archive/PBP isolated `guided_import` calls, source receipt duplicate skip, per-game errors/queue counts, and an existing-games-first rule. `import_worker.py` exposes `batch_psn_folder` and routes multiple selected archives/PBPs to the batch queue. `app.py` adds **Batch import PS1 Classics (PSN ZIP/7Z/EBOOT)**, GAME N/TOTAL status, and a friendly end-of-batch summary; native PSP EBOOTs remain separate from PS1 Classics. Synthetic ZIP/7Z and per-package failure-isolation tests are in `tests/test_v162_psn_batch.py`. Never pretend PSP-native EBOOTs can be blindly converted into PS1 CHDs. Real user FFVII final CHD conversion, physical handheld acceptance, and actual batch screenshots remain pending.


## v1.6.2 branch handoff | all-console duplicate guard + user-friendly disc extraction

User real v1.6.1 Windows screenshots show **7Z extracting**, PSXtract multi-disc identified, Final Fantasy VII SCES Europe discs 1-3 reconstructing data tracks, PSXtract MD5 pass reported, then CHDman converting Disc 1. Final 3 CHDs/M3U/gameplay **not yet observed**. User requests one clear PS1 disc 1/2/3 extraction stage, and adds **IMPORTANT: duplicate detection must cover every console, not PS1 alone**.

**v1.6.2 merged:** [PR #20](https://github.com/ValentineBSAA/RG-Rotate/pull/20), commit `053909f`; CI [45261322930](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45261322930) passed **364 Windows, 363 Linux, 1 skipped**. Feature branch feature/v1.6.2-disc-progress-and-duplicate-guard. ps1_progress.py safely parses PSXtract console text for brief live disc stages. ps1_psn.py now drains stdout in background while sending only safe milestones; app.py shows compact PS1 disc chips in the activity footer during import. library_duplicates.py deduplicates exact SHA-256 contents across **all 13 supported systems**, for individual game files and archives, while refusing different-source same-title collisions without deleting. core.py wires shared guard before file copy and after ZIP/7Z extraction. PS1 title/receipt extension in ps1_duplicates.py + ps1_pipeline.py only processes EBOOT.PBP SHA-256, never KEYS.BIN; metadata lives in hidden .retro-library/psn-sources, not visible ROMs. Legacy CHDs lacking provenance require review.

No current game files, CHDs, M3U, artworks, app installer, microSD, or NAS source data deleted/rewritten by code. Real user physical card and final FFVII outcome pending. [Full acceptance](LIBRARY_DEDUP_AND_PS1_PROGRESS.md).


## v1.6.1 source candidate · PSOne Classics EBOOT and 7Z

New real Windows screenshot shows `Final Fantasy VII (English)(PSN)/NPEF00069/EBOOT.PBP`, `KEYS.BIN`, `DOCUMENT.DAT`. This is a PS1 Classics PSN package, *not* a 3-disc CUE/BIN dump or normal PSP ISO. v1.6.0 had proper .7z archive handling but no PSN-to-CHD bridge and risked treating KEYS.BIN as a standalone PS1 BIN track.

Branch `feature/v1.6.1-psn-eboot-and-7z-verification`: `ps1_psn.py` recognizes signatures and optional same-directory companions, extracts with separately installed PSXtract into disposable LOCAL Windows temp, validates ordered CUE/BIN set; `ps1_pipeline.guided_import` routes this to **existing CHDman conversion + M3U**, never directly converts `KEYS.BIN` or manual. Archive basename is used for game title when nested NPEF game-code would otherwise hide it. New `test_v161_psn_and_7z.py` has real 7Z archive and synthetic PSXtract test. Source CI and real Windows/PSXtract user acceptance **pending**; no real Sony decryption claimed.

Do not change existing verified Resident Evil 2, its 2-DISCS UI, PSP games, 512 GB virtual card, NAS or backups. Acceptance: [PSN_CLASSICS_IMPORT.md](PSN_CLASSICS_IMPORT.md).


## v1.6.1 source candidate | PSN PS1 Classics + 7Z

Real user photo shows Final Fantasy VII (English)(PSN)/NPEF00069 with EBOOT.PBP, KEYS.BIN and DOCUMENT.DAT. It is an official PS1 Classics PSN-style package, not a native PSP ISO. KEYS.BIN is companion key material; DOCUMENT.DAT is a manual. They should never become CHD files or be stored in the virtual ROMs. Final Fantasy VII original PS1 = 3 discs.

Branch feature/v1.6.1-psn-eboot-and-7z-verification, **PR #17 merged into main (commit 94a1bc5)**, [main CI 45251934269](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45251934269) **326 Windows passed; 325 Linux passed/1 skipped**, exact packaged ZIP CRC verified and clean local extract **292 tests passed/34 skipped** (local Qt/7z dependencies absent). Files: ps1_psn.py new PSAR signature/classification, optional PSXtract bridge and careful disc naming; ps1_pipeline.py new PSN extraction stage and .7z document forwarding; tool_setup.py pinned upstream v3.0 PSXtract ZIP+SHA-256 safe install; batch_setup.py and app.py optional checkbox (off by default), proper binary path forwarding; tests/test_v161_psn_and_7z.py creates REAL .7z archives with fake disc contents; tests/test_v161_psxtract_setup.py covers ZIP safety.

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
