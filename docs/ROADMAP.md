# Living Roadmap · RG Rotate / Retro Library Studio
_Last updated: 2026-11-23 (Arizona time). Status is evidence-based, never assumed._

**Definition of done:** A checked item has met its own acceptance criteria, not just compiled or passed mocked tests. Use **[x]** only for the exact tier verified. Each milestone must have code, regression tests, updated docs, and a real acceptance result where applicable.

## P0 · Arriving device / first working PS1 import

- [x] Windows v1.4.4: Choose/remember an SMB/NAS virtual-card location without allocating a 512 GB image (user verified).
- [x] Windows v1.4.4: Import at least one game to NAS and stop a running import without force-closing (user verified).
- [x] Windows v1.4.x: Import Cocoon APK, PPSSPP APK, RetroArch APK; confirm staged packages (user verified).
- [x] Windows v1.4.x: Library health check completed with 1 game, 0 duplicate groups, 0 broken CUE/M3U references (user screenshot).
- [x] Windows v1.4.4: Practice NAS→Windows copy, 6/6 SHA-256 verified; repeated verification with 0 new files, 6 identical, 6/6 verified (user screenshots).
- [x] Code v1.5.1: Implement automatic CUE/BIN track inspection → CHDman conversion → CHD verification → publication; multi-disc M3U creation; preserve original files; single unified import progress (Linux tests pass).
- [x] Code v1.5.1: Fix CUE-only tiny game-size display to account for full referenced BIN set (Linux tests pass).
- [x] Code v1.5.1: Safe-stop import/CHD worker and report failures without releasing incomplete .chd files (Linux tests pass).
- [x] Code v1.5.1: Artwork matching retries and manual fallback integrated into PS1 preparation (Linux tests pass).
- [ ] **Critical:** On Windows 11, launch v1.5.1 at 125% UI scaling, import user's *Clock Tower: The First Fear* English patch (one CUE, two BINs). Confirm CHDman actually runs and the My Games tile shows **one playable CHD and its correct file size**, not a 226–228-byte CUE.
- [ ] On Windows, test failure handling on a deliberately missing/renamed referenced BIN track; original sources intact, helpful visible error, progress returns Ready, no incomplete playable CHD.
- [ ] On Windows, test a genuine two-disc PS1 title: each disc converted separately, playlist created in correct order, gallery shows one game, changing disc works in emulator.
- [ ] On Windows, verify artwork automatic search returns a cover where available and preserves user-chosen covers/edition names. Confirm unavailable covers show friendly “Search/Choose Cover” action; no wrong cover silently attached.
- [ ] First full external 512 GB card: validate actual free capacity, exFAT compatibility, and capacity reserve; copy from NAS, verify hash, safely eject; **never format automatically**.
- [ ] Real RG Rotate: install supported APKs with consent, configure Cocoon as frontend, set emulator mappings / ROM folders, test PS1/PSP/DS games and return-to-home.

## P1 · Beginner-first workflow and library completeness

- [ ] Replace remaining scattered controls with a clear guided “Add Games → Prepare Apps → Copy to Card” workflow at 100%, 110%, 125%, 140%, 150%; keep advanced screens discoverable.
- [ ] Clearly show “Stage → Inspect → Convert → Verify → Add to Library → Find Artwork” under **one overall task progress bar**, with accurate stage text and cancellation.
- [ ] Show per-game **logical title + disc count + complete file footprint**; list source tracks only in advanced details, not as separate playable games.
- [ ] CHDman actionable failures, missing CUE references, multi-track audio, Unicode/legacy encodings, ZIP/7Z imports and partial file cleanup/retry.
- [ ] Stage APKs vs installed Android state clearly distinguished. Recognize manual Cocoon file alias `cocon-311.apk`; report “user APK ready; publisher unverified” until officially verified.
- [ ] Verify Ninite-like official download and offline resume/skip behavior on Windows. Executable checks for adb.exe/chdman.exe.
- [ ] Test imported CHDs, ZIP/7Z, M3Us and playlist paths when transferred and opened by Cocoon and standalone emulators.
- [ ] Add production-quality artwork retrieval/provider failure messages; prevent repeated NAS scans from locking UI.
- [ ] Verify home-screen browsing, multi-system game organization, favorites, and navigation for the 720×720 screen.
- [ ] Publish **actual tested source files** to this GitHub repo (see SOURCE_PUBLICATION.md), ensure automated tests run in CI, and tag a versioned release.

## P2 · Hardware follow-through

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
