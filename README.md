# RG Rotate · Retro Library Studio

## v1.6.4 Beta candidate · Crash Bandicoot™ / Unicode CHDman path

**Real Windows failure:** v1.6.3 recognized Crash Bandicoot™ from a PSN EBOOT, but CHDman reported that the Unicode-named temporary CUE did not exist and imported **0 files**. No successful duplicate verification occurred.

- The PSN extractor's disposable CUE is now passed to CHDman using a same-folder ASCII-only alias. Unicode track references can use temporary NTFS hardlinks, avoiding a second multi-GB copy. Cleanup is automatic and original PBP/CUE/BIN/KEYS files are never rewritten.
- The final verified CHD still uses the proper original Unicode game title. Other original PS1 disc imports are unchanged.
- **Real Windows conversion is pending.** [v1.6.4 acceptance checklist](docs/PSN_UNICODE_CHDMAN_v164.md). Stop old 30-game batch, do not bulk delete generic v1.6.2 PS1 CHDs, and test one Crash Bandicoot import before a new batch.


## v1.6.3 fix candidate · PS1 Classics real titles, reliable Stop, game folder access

- **Real 30-package Windows batch exposed v1.6.2 failure:** archive name PS1 was used as game identity, creating generic PS1/Disc 1 CHDs and cover tiles; Stop task reportedly failed to stop reliably. **Do not rerun the v1.6.2 batch** on the existing virtual card.
- Fix candidate rejects generic PS1/PSX/PlayStation labels, tries bounded public PBP PARAM.SFO TITLE metadata, and flags unknown titles without publishing anonymous CHDs. The batch queue displays the resolved title and final folder, My Games tiles expose Open game folder.
- Stop now escalates from a cooperative command to worker termination/kill while locking new imports until process exit. Exact-byte duplicates for completed single-disc PSN imports also have receipts.
- **Already mislabeled legacy files are not renamed, merged or deleted automatically.** Review the actual CHDs and original source before deciding what to reimport; use a disposable workspace for first tests.
- **Source candidate only; actual Windows NAS Stop, PSXtract/CHDman and RG Rotate gameplay not yet verified.** [Required v1.6.3 tests](docs/PS1_BATCH_IDENTITY_AND_STOP_v163.md).


## v1.6.2 source beta · PS1 disc-by-disc progress + all-console duplicate prevention

- A live PlayStation Classics extraction strip now shows each detected disc and its stage; CHDman verification retains its own progress, without pretending to know extractor percentages.
- **All 13 supported consoles** share strict game-file SHA-256 duplicate detection (PS1, PSP, PS2, DS, GB, GBC, GBA, NES, SNES, Genesis, N64, Dreamcast, GameCube). This works on direct files and inside .zip/.7z archives, not just on PlayStation titles. Scans are limited to the destination console, preserving intentional multi-platform releases.
- Byte-identical renamed/repackaged game files are skipped. Different payload with the same title is held for review; regions, editions and revisions remain separate. CUE/BIN track companions are excluded from independent file-level deduplication.
- PS1 Classics import additionally fingerprints EBOOT.PBP so a completed CHD/M3U collection can be recognized across renamed/repacked ZIP/7Z/PBP sources. Small receipts are written under **.retro-library/psn-sources** (ignored by the game scanner); key files are never hashed or copied into ROMs. Existing legacy PS1 collections with no receipt are preserved and flagged, never silently claimed identical.
- The previous real Windows Final Fantasy VII PSN screenshots show 7Z extraction, three reconstructed discs and CHD conversion started. Actual final three-CHD/M3U user acceptance and on-device play remain pending.

[Full v1.6.2 test checklist](docs/LIBRARY_DEDUP_AND_PS1_PROGRESS.md).


## v1.6.1 PS1 Classics package recognition & 7Z verification (source candidate)

- A Windows FFVII PSN folder can contain `EBOOT.PBP`, `KEYS.BIN` and `DOCUMENT.DAT` rather than per-disc CUE/BIN. The importer now recognizes PS1 Classics PBP signatures and keeps the key and manual as **companions**, never standalone discs or PSP titles.
- A separately installed PSXtract helper can produce temporary CUE/BIN discs, which enter our **existing CHDman createcd+verify** and safe CHD/M3U collection pipeline. If missing or unable to extract, the import reports the blocker without fake success or source deletion.
- Existing ZIP/7Z unpacking remains intact and receives real archive regression tests. **Real PSN EBOOT decryption and RG Rotate playback have not yet passed.**
- See [PSN/7Z acceptance guide](docs/PSN_CLASSICS_IMPORT.md). Keep v1.6.0 until Windows and CI checks complete.


## v1.6.1 source beta · PS1 Classics EBOOT and real 7-Zip validation

- New PSN PS1 Classics path recognizes EBOOT.PBP with KEYS.BIN / DOCUMENT.DAT; keys/manual are companion material, never CHD discs. A valid PS1 Classics disc signature prevents confusing PS1 with native PSP games.
- An optional, unchecked PSXtract selection in Prepare apps installs a pinned GitHub v3.0 release after user consent and SHA-256 verification. It is not included in our ZIP, does not execute during installation, and is required for the encrypted PSN path.
- Once the helper extracts full PS1 CUE/BIN discs, the existing verified CHDman conversion, ordered M3U, parent folder and single cover process continues automatically. The original archive, keys, manual and NAS library are preserved.
- Added tests that actually create and extract .7z archives with three synthetic discs. Synthetic PSN PBP tests mock decryption. **Actual PSN EBOOT extraction and gameplay are unverified until the user tests their file.**
- [PS1 Classics/7Z test checklist](docs/PS1_CLASSICS_7Z_ACCEPTANCE.md).


## v1.6.0 · Readable details and verified microSD adapter identification

- Game File Format, Exact Sizes and exFAT details are now premium **summary-first dialogs** with easy-to-read grouped facts, member files and optional *Show exact bytes and technical details*. No existing game, folder or artwork is modified.
- On **Copy to card**, Windows volumes are scanned in a background worker. A newly plugged USB microSD reader is suggested for review, never silently chosen. Some adapters report a 512 GB SD card as a **fixed** drive, which is clearly marked as uncertain.
- A physical copy requires an exFAT card identity (Windows volume GUID or volume serial) from a fresh Preview, a repeat match before copying, an exact typed drive-letter confirmation, and another identity check before each file. **No automatic formatting or deletion.**
- Your Windows 11/512 GB microSD needs real capacity and filesystem verification after arrival. Simulated 512 GB and exFAT estimates remain separate from measured card data.
- [v1.6.0 acceptance steps](docs/CARD_DETECTION_AND_READABLE_DIALOGS.md). v1.5.9 Resident Evil 2 two-CHD + M3U grouping was user verified; physical RG Rotate game-launch tests still pending.


## v1.5.9 · Non-destructive exFAT preview + multi-disc details

- Fixed the **real Windows v1.5.8 Resident Evil 2** gallery detail defect. Read-only scan previously discarded M3U-to-CHD membership and hid the member CHDs before grouping. The new scan retains them and presents a **2 DISCS** badge with both verified file paths, **without modifying the game folder or playlist**.
- Added a second **SIMULATED Windows 11 SDXC/exFAT** capacity bar *under* the previously tested 512 GB nominal planner. The overlay models a 128 KiB cluster-size assumption, estimated exFAT metadata, file-allocation rounding, existing staged bytes, companion allowance and protected 8 GiB free reserve. It creates, formats and deletes **nothing**.
- **Not exact physical capacity:** Real card sector count, allocation unit and partition overhead are unknown until Windows measures the connected microSD. **Copy to card → Preview** already reads that measurement and uses it for physical transfer safety. Windows does not automatically reformat a properly readable card.
- [Full virtual-format acceptance and rationale](docs/VIRTUAL_EXFAT_PLAN.md). Keep v1.5.8 until you confirm the new UI; RG Rotate hardware setup and real M3U disc-switching remain pending.


## v1.5.8 Windows source beta · One Game, Multiple Discs

- New **Import complete PS1 game folder…** action inspects all CUE/BIN tracks, converts and verifies each disc as its own CHD, and puts CHDs under one parent game folder. Existing CHDs are verified and organized without recompressing.
- A strict, ordered M3U playlist can be created or safely extended as later discs arrive. **One cover-gallery tile** represents valid multi-disc playlists, with an N DISCS badge; raw File List still shows physical files for troubleshooting.
- Editions, regions, Resident Evil 2 Leon/Claire disc tags, Final Fantasy VII vs VIII, and disc order are kept separate. Missing tracks, gaps, duplicates or conflicting M3Us do not silently merge, overwrite or destroy sources.
- The desktop uses background scan-worker M3U membership; no network work in Qt painting. This is not a claim that Cocoon disc swapping has been tested on a physical RG Rotate.
- Full new acceptance: [Multi-disc Windows tests](docs/MULTIDISC_ACCEPTANCE.md). Older acceptance still open: [Full checklist](docs/FULL_TEST_CHECKLIST.md).

**Status:** v1.5.8 is merged into main ([PR #13](https://github.com/ValentineBSAA/RG-Rotate/pull/13)). CI: 289 Windows tests passed, 288 Linux passed/1 skipped. The GitHub-packaged ZIP passed an integrity check and 264 clean-extraction tests locally (25 Qt tests skipped). Actual Windows CHDman/Synology multi-disc and RG Rotate gameplay acceptance remain pending. Keep your working v1.5.7 folder.


**Project home and development handoff** for the Anbernic RG Rotate (Android 12, 720×720, Unisoc T618, 3 GB RAM, 32 GB internal storage) and **Retro Library Studio**, a Windows 11 / PySide6 virtual-microSD preparation utility.

> **Latest packaged Windows source beta: v1.5.8**, including v1.5.7 console shelves, the 512 GB planner and new one-game PS1 multi-disc collections. Real NAS and device acceptance are not guaranteed by automated tests. Read the [complete testing checklist](docs/FULL_TEST_CHECKLIST.md). Real v1.5.5 batch verified-cleanup, v1.5.6 Windows capacity UI and physical RG Rotate still need acceptance.

## Project at a glance

- **Default Android frontend:** Cocoon Shell. Keep emulator selection, first-run permissions, and Android Home configuration as *on-device* tasks; staging APKs does not install them.
- **Primary systems:** PSP, PlayStation 1, Nintendo DS, Game Boy Advance; additional older systems as appropriate. PS2 and GameCube are **experimental**, not guaranteed on T618 or without analog sticks.
- **Windows virtual card:** User-chosen local directory or Synology NAS SMB/mapped drive. No 512 GB preallocation or sparse disk image; actual files consume real space only when added.
- **Card plan:** 512 GB marketed capacity (about 476.8 GiB before filesystem overhead); **8 GiB protected free-space headroom** plus **8 GiB budget for AI companion data**. Recalculate against the real card's formatted capacity. Android OS/apps primarily reside on 32 GB internal storage.
- **Import:** existing lawful game files, folders, ZIP and 7Z archives, PS1 CUE/BIN multi-track sets, CHD, and Android APK setup packages. Preserve originals, paths, metadata, save data, and NAS content.
- **Software setup:** Ninite-like official/authorized-source setup for Cocoon, PPSSPP, RetroArch, ADB Platform Tools and CHDman; clearly distinguish “APK staged” from “installed on Android.” Windows tools are **not** copied to the microSD as Android apps.
- **Copy and verification:** preview, practice folder or physical microSD, live speed/ETA, hash verification, incremental repeat transfers, cancellation/recovery and no silent overwrite.
- **UX:** Beginner-first **Add Games → Prepare Apps → Copy to Card**; adjustable 100–150% UI scale including 125%, saved window geometry, visible status, large cover-gallery and manual artwork search.

## Start here in a new conversation or Codex session

1. Read [Project Handoff](docs/PROJECT_HANDOFF.md) for the latest known state, decisions, paths and safety rules.
2. Read the **living [Roadmap](docs/ROADMAP.md)** for current priorities and stop conditions.
3. Read [Verification Matrix](docs/VERIFICATION_MATRIX.md) and [Full Test Checklist](docs/FULL_TEST_CHECKLIST.md) to distinguish passed tests from pending acceptance.
4. Read [Release History](docs/RELEASE_HISTORY.md) to understand why earlier regressions occurred.
5. Before changing code, obtain the actual source ZIP or the published source branch, run existing tests, keep the NAS workspace intact, then update **roadmap + handoff + tests + changelog in the same change**.

### Current PS1 first-game test

**Clock Tower: The First Fear (English patched)** has a CUE with two BIN tracks. The old importer staged all three, but **My Games displayed only the tiny ~226–228-byte CUE size**. v1.5.1 aims to convert complete CUE/BIN sets to a verified single CHD *before* publishing them in My Games, count the complete size, and generate an ordered M3U for multi-disc sets. This behavior is **code/test-verified only**, not Windows/real CHDman-verified.

## Important data/safety policies

- Never put commercial ROMs, proprietary BIOS, or keys in the public repository. Source code and documentation only. Do not bundle unlicensed games.
- Never rewrite source BIN/CUE tracks or delete ROMs on import. Broken or unsupported CUE files must report explicit errors, not publish an incomplete game.
- Never silently format a real card, delete user data, replace a conflicting file, or treat a size-only match as an integrity check.
- Keep actual device status separate from desktop preparation and backend unit-test results.
- A 512 GB profile is a **planning budget**, not a demand for 512 GB available on the Windows or NAS drive.

## Key documents

| Document | Purpose |
| --- | --- |
| [ROADMAP.md](docs/ROADMAP.md) | Living priorities, statuses, acceptance criteria |
| [PROJECT_HANDOFF.md](docs/PROJECT_HANDOFF.md) | Cross-chat project context and workflow |
| [VERIFICATION_MATRIX.md](docs/VERIFICATION_MATRIX.md) | Real PC passes vs simulated / pending |
| [RELEASE_HISTORY.md](docs/RELEASE_HISTORY.md) | Version milestones and regressions |
| [GAME_LIBRARY_PLAN.md](docs/GAME_LIBRARY_PLAN.md) | Systems, titles, controller cautions, Cocoon favorites |
| [SOURCE_PUBLICATION.md](docs/SOURCE_PUBLICATION.md) | How to add the ZIP's actual code and keep it current |

**Maintenance rule:** Every meaningful project change must update the roadmap status and tests; report whether it was unit-tested, Windows-tested, or RG Rotate-tested. No silent completion claims.

**Latest Windows testing:** [v1.5.4 right-click CHD & cover-preview acceptance issue](https://github.com/ValentineBSAA/RG-Rotate/issues/8). Source published under `RetroLibraryStudio/`; real CHDman conversion and RG Rotate device testing still pending.

### Current Windows results (2026-11-23)

The user confirmed **Clock Tower: The First Fear** (55.4 MB CHD) and **Resident Evil Gore Edition** (311.9 MB CHD) converted and CHDman verified successfully in v1.5.4, with cover artwork preserved. v1.5.5 adds batch PS1 CUE/BIN and selected IMG conversion, optional verified cleanup only within the virtual card, an **Open conversion backups** action, and artwork preview fitting. Batch-delete acceptance on the user's NAS remains **pending**.
