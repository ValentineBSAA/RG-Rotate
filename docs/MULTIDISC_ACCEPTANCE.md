# v1.5.8 · One artwork tile, multiple PS1 discs

**Status:** Source beta candidate. Automated tests use synthetic CHDman fixtures. No user Windows 11 / Synology batch import or actual RG Rotate/Cocoon disc swapping has been verified for this version.

## What the software should do

1. User selects **Add games → Import complete PS1 game folder…**, then the folder containing the game’s CUE/BIN discs (or existing CHDs). Existing generic Add Folder / Add Game Files continue working.
2. A child worker reads all CUEs, checks each referenced BIN, uses real CHDman to convert each **complete physical disc** losslessly and verify it, copies verified CHDs to a single parent game folder and hashes the copy. Existing numbered CHDs are verified and copied without recompression.
3. Recognizes explicit Disc/Disk/CD numbers **without removing region, edition or game number**. The **Resident Evil 2 (USA)** discs are one game; **Resident Evil 2 Dual Shock Ver. (USA)** is a different game and should not be silently mixed. FFVII (3 discs) and FFVIII (4 discs) are two separate game folders and covers.
4. Only once Disc 1..N form a consecutive, unique set, writes an ordered `.m3u` file of relative CHD filenames. Later disc imports can extend an **exact, safe subset** of the existing playlist. Never overwrite a conflicting/custom playlist, guess missing tracks, or publish a partial M3U.
5. Example destination:
   ```text
   ROMs/psx/Resident Evil 2 (USA)/
       Resident Evil 2 (USA) (Disc 1).chd
       Resident Evil 2 (USA) (Disc 2).chd
       Resident Evil 2 (USA).m3u
   ```
6. **My Games Cover Gallery** shows **one tile** for the M3U, with the normal game title, one cover and a **2 DISCS** badge. Search can match a referenced disc; File List remains deliberately detailed. The inventory scanner caches M3U membership **off the GUI thread**, with no new NAS operations during painting. A broken or incomplete M3U must never conceal playable standalone CHDs.
7. No original user CUE/BIN/CHD file is deleted or modified. Neither protected NAS source archive nor older conversion backups nor CompanionData is cleaned by this import. Existing batch cleanup remains **opt-in** and requires separate disposable Windows acceptance.

## User-facing acceptance tests (real Windows 11 + Synology)

- [ ] **M01** Launch v1.5.8 in a new folder, remember prior NAS virtual-card workspace, confirm already-imported PS1/PSP artwork, other game systems and 125% layout survive.
- [ ] **M02** Use the new **Import complete PS1 game folder…** button for a *disposable complete copy* of Resident Evil 2 (USA), with Disc 1 and Disc 2 CUE/BIN. Confirm each CUE references the *exact* BIN filename(s) in its own disc folder.
- [ ] **M03** Confirm real CHDman verify outputs **two CHDs** and exactly **one M3U** in `ROMs/psx/Resident Evil 2 (USA)/`, with M3U Disc 1 before Disc 2. No source CUE/BIN deleted.
- [ ] **M04** Refresh My Games: PS1/all game count reflects **one RE2 tile**, artwork correct, **2 DISCS** badge opens details naming both CHDs; File List can still show each physical file.
- [ ] **M05** Simulate Disc 3 later on a *throwaway* three-disc game: one initial CHD, then two CHDs + playlist, then playlist safely adds Disc 3 in order with one tile. Re-import should not overwrite/duplicate.
- [ ] **M06** Separate FFVII vs FFVIII names and regions/editions. For known complete test fixtures expect 3- and 4-disc sets separately, not a combined seven-disc playlist.
- [ ] **M07** Missing Track 1 / wrong CUE filename / duplicate disc number / Disc 1+3 gap / corrupted CHD / cancelled conversion => intelligible errors, **no incomplete playlist**, originals intact and recoverable. Never rename BINs automatically.
- [ ] **M08** An old unrelated/custom M3U is not clobbered. An M3U with missing CHD references must not hide existing disc tiles. Legacy Clock Tower and Resident Evil Gore Edition CHDs untouched.
- [ ] **M09** Check 125% cover preview fit, no duplicate genre/console tabs, responsive NAS operations, one progress workflow, correct staged GB and protected 8 GiB + 8 GiB budgets.
- [ ] **M10** Once physical RG Rotate arrives, map the resulting M3U as one Cocoon title and verify emulator disc swap and save/playback. **Not yet a device pass.**

**Note:** Original PlayStation CDs have tracks *within each disc*, not extra game discs. CUE + BIN track files make **one CHD per disc**. An M3U references separate CHDs; it is not one merged disc image. For user-supplied licensed game images only.
