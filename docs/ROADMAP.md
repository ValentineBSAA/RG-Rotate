# Living Roadmap · RG Rotate / Retro Library Studio
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
