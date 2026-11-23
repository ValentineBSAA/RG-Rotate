# v1.5.5 first Windows acceptance (do not run on valuable source originals)

1. Launch the new extracted folder; confirm v1.5.5 and both earlier CHD tiles still present.
2. **Open conversion backups** and verify it opens the sibling NAS recovery folder; no files deleted.
3. In cover search, select a cover and resize the dialog. Entire image must fit; no cropped or stretched preview.
4. Import a disposable copy of one PS1 CUE/two BINs into a test folder on virtual card, keeping a separate original outside the card.
5. Batch → **Keep recovery backups**. Confirm CHDman verified, CHD badge, source moved to recovery, external original untouched.
6. Another disposable disc: Batch → **Remove verified working copies**, acknowledge the second confirmation. Confirm CHD exists, old tracks within virtual card removed, external original and old recovery backups untouched.
7. Broken missing track and manual Stop tests: never remove incomplete/failed/unprocessed source files.
8. Review results and run Library Check before copying to real microSD.

# v1.5.4 priority Windows acceptance

1. [ ] Open My Games at 125% and RIGHT-CLICK Clock Tower cover tile. Styled context menu should show the conversion action. Test right-click on File List as well.
2. [ ] Search Clock Tower artwork, select USA and Japan entries: image **previews automatically** in the dialog before applying. No cover should change until `Use selected cover`.
3. [ ] Right-click Clock Tower BIN/CUE, choose `Convert to verified CHD + tidy PSX folder`. Note the confirmation shows recovery location OUTSIDE the virtual card. Confirm and monitor single task progress.
4. [ ] After completion, Clock Tower tile should show CHD; only its CHD should remain in original PSX game directory. Original CUE/BIN files present in adjacent `... - Conversion Backups` recovery folder. Artwork unchanged.
5. [ ] On a *copy* of invalid CUE, verify conversion fails without moving original tracks or leaving a playable fake CHD.
6. [ ] If an IMG game has CCD/SUB metadata, verify action refuses unsafe conversion. For single-track raw IMG, verify format detection works and conversion succeeds when supported.
7. [ ] After conversion, run Library Check and NAS-to-Windows practice transfer; verify incremental SHA-256 results. Do not format microSD.

---
# v1.5.4 priority Windows acceptance

1. [ ] Open My Games at 125% and RIGHT-CLICK Clock Tower cover tile. Styled context menu should show the conversion action. Test right-click on File List as well.
2. [ ] Search Clock Tower artwork, select USA and Japan entries: image **previews automatically** in the dialog before applying. No cover should change until `Use selected cover`.
3. [ ] Right-click Clock Tower BIN/CUE, choose `Convert to verified CHD + tidy PSX folder`. Note the confirmation shows recovery location OUTSIDE the virtual card. Confirm and monitor single task progress.
4. [ ] After completion, Clock Tower tile should show CHD; only its CHD should remain in original PSX game directory. Original CUE/BIN files present in adjacent `... - Conversion Backups` recovery folder. Artwork unchanged.
5. [ ] On a *copy* of invalid CUE, verify conversion fails without moving original tracks or leaving a playable fake CHD.
6. [ ] If an IMG game has CCD/SUB metadata, verify action refuses unsafe conversion. For single-track raw IMG, verify format detection works and conversion succeeds when supported.
7. [ ] After conversion, run Library Check and NAS-to-Windows practice transfer; verify incremental SHA-256 results. Do not format microSD.

---
# v1.5.1: Focused Windows acceptance check

Use a **copy** of a small, lawfully obtained PS1 disc set for initial testing.

- [ ] Open v1.5.1. Confirm existing NAS workspace and 125% scale are retained.
- [ ] Confirm CHDman says Ready on Windows in Install Apps.
- [ ] On My Games, confirm automatic CUE/BIN → CHD is enabled by default.
- [ ] Add a NEW PS1 folder with `Game.cue`, `Game (Track 1).bin` and
      `Game (Track 2).bin`. It should appear as **one** verified CHD, not
      three entries. Both original tracks should remain unchanged.
- [ ] Confirm the same activity bar reports **inspection → conversion →
      verification → copying → artwork**, with Stop available. Conversion
      can be indeterminate while CHDman is running.
- [ ] Import two discs of one game (Disc 1 and Disc 2). Confirm there are two
      verified CHDs and one correctly ordered M3U. A new Disc 2 imported later
      should also create the playlist.
- [ ] Open Cover gallery. A converted single disc appears once with its true
      CHD size. A multi-disc title appears once via its M3U. File list can
      still show the underlying disc files for troubleshooting.
- [ ] If auto-artwork didn't find a confident match, confirm a visible review
      state and use manual cover search. Never assign an unrelated edition.
- [ ] For your ALREADY IMPORTED Clock Tower folder, choose **Convert earlier
      PS1 imports…** and confirm it adds a verified CHD while preserving CUE
      and BIN tracks. Original tracks are still on the virtual card.
- [ ] Stop a disposable PS1 conversion while it is running. No incomplete CHD
      should appear in the game library. Your original tracks stay intact.
- [ ] Run Library Check. Preview then verify a disposable incremental transfer.
- [ ] If any test fails, capture the exact operation, error, and Windows log.

**Still unverified here:** Real Windows CHDman, live Libretro art, Windows Qt,
Synology SMB timing, Cocoon recognition on Android and the actual RG Rotate.
Do not delete any existing source disc files as part of this test.

---

# v1.5.0 Windows / NAS / RG Rotate acceptance checks

Automated Qt widget checks are not a substitute for these interactive and
hardware checks. Use a small legally owned test collection and a practice
destination first. Keep your existing library and artwork.

- [ ] Extract to a new folder; run dependency installer and launcher with a normal
  installed Python. Confirm startup logs and the existing NAS location/settings.
- [ ] Inspect all six pages at app scales 100%, 110%, 125%, 140%, 150% on your
  actual monitor and Windows DPI setting. Test maximized/restored windows,
  keyboard focus and scrolling; confirm main actions remain accessible.
- [ ] Close/reopen after moving and resizing; confirm geometry, scale, source,
  destination, practice mode and a manually edited display title persist.
- [ ] Add individual games, a folder, ZIP and 7Z; drag/drop mixed games and APKs.
  Check originals, imported files, per-item errors and cancellation.
- [ ] Browse gallery and File list. Search/edit titles and covers. Check that
  special editions keep their names; multi-disc variants group without losing
  files. Referenced data/audio BINs should not be separate game tiles.
- [ ] Import `cocon-311.apk`; confirm My APK ready / publisher unverified and no
  claim of Android installation. Prepare selected software; verify individual
  states and retry without redundant downloads. Test ADB version and CHDman usage.
- [ ] Convert the actual Resident Evil 2 Disc 1 AND Disc 2 CUE/BIN sets separately
  and together. Review every reference and warning. Record actual CHDman errors
  if Disc 1 fails; compare track names, sizes and completeness of the dumps.
  No definitive diagnosis of your Disc 1 is possible without those files/logs.
- [ ] Check a multi-FILE/audio CUE, a missing filename, an empty track, an existing
  output name and a cancelled conversion. Only successful verified CHDs should
  appear under final output names. Original source hashes must be unchanged.
- [ ] Generate a same-game M3U in explicit Disc 1/Disc 2 order; load it in your
  actual emulator and test switching discs. Do not combine unrelated games.
- [ ] Repeat the proven six-file NAS → Windows practice transfer, then preview
  and verify existing files. Expect 0 new copies, 6 identical, 6/6 verified for
  the unchanged fixture. Preview alone must not claim hash verification.
- [ ] Test Stop during NAS scan, import, setup and conversion; simulate an
  unavailable NAS and confirm navigation remains responsive. Review any generated
  partials after force-stop; do not delete original games.
- [ ] Test transfer interruption/resume, same-size conflicting destination,
  duplicate detection and protected free-space checks on disposable fixtures.
- [ ] On the physical microSD: detect the right drive, confirm capacity, preview,
  approve transfer and verify hashes. Safely eject, then test the card in RG Rotate.
- [ ] On RG Rotate: install authorized APKs, configure Cocoon/emulators, test
  artwork assignment, games, CHDs, M3U disc switching and USB/ADB device setup.
- [ ] Optionally build all five EXEs and test from a clean folder / Windows PC.

Historical acceptance checklists follow.

---

# v1.4.4 practice-mode acceptance checklist

- [ ] Opens with the existing NAS source and Windows practice destination intact.
- [ ] Copy to Card clearly shows `PRACTICE MODE` even after restarting.
- [ ] Preview shows 0 B new, 6 existing same-size files (not yet SHA verified).
- [ ] Clicking **Verify Existing Files (SHA-256)** proceeds without `Physical-card destination must be the drive root`.
- [ ] Repeat verification ends: 0 copied; 6 already identical; 6/6 hash verified; no errors.
- [ ] Close and reopen; destination and mode remain saved.
- [ ] Choosing an actual card root switches to real-card mode, without weakening physical-card safeguards.

# v1.4.3 incremental transfer acceptance test

- [ ] v1.4.3 starts on Windows and remembers the existing NAS workspace and 125% scale.
- [ ] Choose existing *practice folder* (not the real card) and run preflight: 6 files, 0 B new if unchanged.
- [ ] Preview says **not hash-verified**; old 100% completion bar is cleared and next action is visible without hunting through the page.
- [ ] Rerun verification: status says Verifying SHA-256, then **0 newly copied / 6 identical / 6 of 6 verified** (assuming source and destination unchanged).
- [ ] Practice success dialog does not tell you to eject a microSD.
- [ ] NAS source games, artwork and APKs remain intact.
- [ ] Optional: a fresh disposable practice folder copies the files normally. Keep real microSD untested until arrival.

Do not mark a second transfer passed based only on the 0 B *preview*; save its actual completion result.

---


## v1.4.2 Cocoon installer recognition correction

The user-tested `cocon-311.apk` (single "o") can now be recognized as a **manually imported Cocoon Shell candidate**, as well as APK filenames beginning with `Cocoon`. This requires the existing safe import receipt and its matching SHA-256, plus basic APK integrity checks. The app will label it **My APK ready • publisher unverified**, never "officially verified" or "installed on Android". The Ninite-style setup will skip re-downloading it by default. Unrelated names such as `coconut-tools.apk` do not match.

**Next tests:** Open **Install Apps** and check the Cocoon row; it should say `My APK ready • publisher unverified` while PPSSPP/RetroArch, ADB and CHDman retain their statuses. Then **Library Check → Scan my virtual card**. A successful file-integrity scan is *not* proof that the game will run in an emulator. Finally use **Copy to Card → Try a safe practice copy first**, perform preflight, copy and hash verification using a disposable folder. Do not use the real card until those pass.

The **Choose a PS1 CUE and convert** dialog selects a `.cue` sheet (not `.q`). Opening it only verifies the CHDman GUI is connected; actual disc conversion and verification are a separate test. A standalone `.img` file is not a CUE/BIN set and must not be mislabeled convertible through that picker.


# v1.4.1 APK Import Acceptance (Windows + Synology)

1. Extract this release to a **new** program folder and run `Start_Retro_Library_Studio.bat`. The saved NAS virtual-card location should remain the same.
2. Go to **Install Apps** and scroll to **Already downloaded an Android app?**.
3. Select **Add APK Files** and pick your existing Cocoon `.apk` from Downloads. It must not silently start a different NAS status scan and ignore your selection.
4. Watch the bottom task area identify **Adding Android APKs**. Wait for **APK import completed**. If it fails, record the exact error. Do not click the full recommended installer yet.
5. The confirmation dialog should show the **full `SetupPackages` path**. Click **Open Android installers folder**, and ensure the APK exists there with the same size as the original. Check that the original download is still present.
6. Wait for the separate app-status refresh to finish. Cocoon should show **My APK ready • publisher unverified** (not installed on Android).
7. Import the **same file again**. Expect **0 added; 1 already present**, no extra copies.
8. Press **Stop task** during a deliberately slow/disposable import if safe to do so. The app must return to Ready after the worker exits, and incomplete files must not look ready.
9. Verify **My Games** still shows your Resident Evil game and artwork. Don't attempt a real microSD transfer until the practice transfer passes.

No Android app has been installed just by copying an APK to the virtual card.

---

# v1.4.0 Arrival-Day Acceptance: Start Here

Use a **new extracted application folder** and keep your existing NAS virtual-card workspace untouched. First verify these with a disposable sample, not your full 512 GB card.

- [ ] Start the program on Windows. Version reads **1.4.0 Day-One Beta**. Your previously selected NAS path remains selected, and the UI remains responsive.
- [ ] Open My Games: existing Resident Evil IMG remains shown. Choose **Search for cover → Choose image from PC instead** and select `Example_Covers/Resident Evil Gore Edition.png` from the app folder. Confirm it shows on the tile without touching the game file.
- [ ] Open Start Here → **What is ready for my RG Rotate?**. The checklist should open instantly, with Android still clearly pending.
- [ ] Open Install Apps. Stage Cocoon 3.11 manually or try official software downloads. Confirm all APKs are marked **ready to install**, never already installed on the RG Rotate. Confirm CHDman is **executable verified** and ADB is located under WindowsTools if setup succeeds.
- [ ] Copy to Card → **Try a safe practice copy first** → Preview → Copy. Confirm progress, verification, complete file hash matches and a final success notification.
- [ ] Rerun the same practice copy: unchanged data should be recognized and skipped, with the same verification success.
- [ ] Begin a disposable larger practice transfer from the NAS and click Stop. Confirm navigation still works; if Stop is stuck, the UI should offer **Force stop stalled copy…** after ~6 seconds, requiring confirmation. Check `.retro-part` is NOT reported as a complete file, then retry and resume safely.
- [ ] Insert the physical microSD only after the practice transfer passes. Select the root of the correct drive, check exFAT/fat32 limits, actual usable capacity and 8 GiB free reserve. Confirm the card again before copying. Start with a small transfer rather than the entire NAS library.
- [ ] After copying, use Windows **Eject** before removal. On the RG Rotate install/authorize Cocoon and emulators, scan `ROMs` with platform folders, and test game controls and saves. The Windows program cannot prove this stage until the device is present.

**DO NOT format or delete old copies to free space during testing. Do not assume the card is verified because the source tests passed.**

---

# Manual artwork search acceptance (v1.3.1)

- [ ] The program opens on Windows and remembers the Synology NAS workspace.
- [ ] Under **My Games**, existing `Resident Evil Gore Edition.img` remains visible; no reimport is needed.
- [ ] Click **Search for cover**. Change the title from `Resident Evil Gore Edition` to `Resident Evil` and click **Search**.
- [ ] Results appear, including region variants when offered by the catalog. List selection visibly highlights the selected result at 100% and 125% UI scaling.
- [ ] Select a result and click **Preview selected**; image is visible, with no game or NAS file change from preview alone.
- [ ] Confirm **Use selected cover**, and verify its thumbnail appears in **My Games** and the file exists under `Media/BoxArt/psx` on the virtual card.
- [ ] Confirm the original game `.img` is unchanged. Re-run search and decline the replacement to verify the cover stays the same.
- [ ] Switch to File list and use **Search for a game cover…**; same dialog works.
- [ ] Search nonsense text, press Stop during a search, and use **Choose image from PC instead** to verify each fallback is clear.

# Retro Library Studio v1.3.1 | Windows acceptance checklist

**Run the tests in this order.** Use harmless files, a disposable card/practice folder, and ordinary user privileges. Never delete your original files to make an empty 512 GB workspace.

## Priority A: v1.3.1 artwork gallery on your existing NAS workspace

Use your already-imported `Resident Evil Gore Edition.img`. No need to copy or re-import the game just to test the gallery.

- [ ] Launch v1.3.1 and verify it remembers your existing Synology workspace and shows the correct PS1 game/size.
- [ ] Open My Games: **Cover gallery** appears by default; **File list** restores the detailed table and switching back works.
- [ ] An initial cover lookup runs visibly with a working **Stop task**, rather than blocking all navigation. If there is no internet, the app shows a retriable failure, not fabricated artwork.
- [ ] For Resident Evil Gore Edition, **no unrelated regular Resident Evil cover is silently chosen**. Click Find / add cover; inspect online suggestions and select manually if correct, or choose a local cover image.
- [ ] For a clearly named game with an official catalog cover, a correct match downloads automatically and appears in the gallery. A miss is visibly marked for review.
- [ ] Confirm `Media/BoxArt/psx/<game>.png` exists on NAS after artwork is applied, while the original game IMG remains byte-for-byte unchanged.
- [ ] Try a local PNG and a JPG or WEBP. Select a different image again; an explicit replacement confirmation should appear. No original local image is changed.
- [ ] Close/reopen; check artwork remains visible through the Windows local preview cache. Test 125% scale and narrowing/searching a gallery.
- [ ] Test offline gallery: previously downloaded cover previews are visible without a NAS image-read per tile; **Find missing covers** restores a missing local preview from an existing NAS cover.
- [ ] Start an artwork task and click Stop. The status must return to **Ready**, navigation must work, and no partially downloaded `.retro-art-part` is treated as a complete cover.
- [ ] Try 50+ games (use harmless test files) and Show more. No all-at-once rendering stall or frozen UI.
- [ ] **Cocoon on actual RG Rotate remains separate:** verify the Android scraper/edit art workflow before claiming these Windows covers appear inside Cocoon.

## B. Storage location and NAS

- [ ] Launch v1.2.1, confirm the correct UI version and your last chosen virtual-card path.
- [ ] Choose a brand-new empty location on a different Windows drive. No long **Checking Existing Card** spinner should appear; the location should change immediately.
- [ ] Confirm `VIRTUAL CARD LOCATION` shows the newly selected path, and a local drive free-space figure updates to that new drive, NOT the previous 289.16 GB reading. For a NAS location, the free-space check should be optional.
- [ ] Check Windows Explorer → Properties for the same location. The two free-space displays should agree after allowing for GB/GiB rounding and changes from other programs.
- [ ] Check `Start Here`: storage shows **backing storage free**, **how much more can be staged**, and your virtual card's game space. No giant 512 GB file is created.
- [ ] If your Synology is reachable, select a dedicated folder on its mapped network drive. Confirm folder structure, the **NAS workspace selected • Capacity check optional** message, and persistence after app restart. Then click Check storage; it should either show capacity or report a timeout within about six seconds, without freezing navigation. Do not use the root of the NAS share for this test.
- [ ] Try selecting a local folder with unrelated files: the app proposes a dedicated subfolder and does not disturb your existing data.
- [ ] Confirm that simply selecting/reopening a NAS workspace does not start a NAS capacity lookup.
- [ ] Disconnect the NAS (only if safe to do so), click Check storage, and confirm the app reports a capacity error without an endless spinner. Reconnect and try again.
- [ ] Import one small harmless supported file into the NAS virtual card, then verify it from Windows Explorer. (The NAS copy will likely be slower.)
- [ ] If a workspace has files, switching away should still offer **Copy my card** or **Use new folder without copying**, preserving old content.

## B. Ninite-style installer

- [ ] Open **Install Apps**. Cocoon, PPSSPP, RetroArch, ADB and CHDman are checked by default.
- [ ] Uncheck one of them, run **Install Recommended Setup**, and confirm the unchecked program is not downloaded. No second competing installer button should be necessary.
- [ ] Manually import your existing Cocoon 3.11 APK via **Add APK Files**. It appears in SetupPackages.
- [ ] Its row says **My APK ready • publisher unverified**, not **Not prepared** or **installed on Android**.
- [ ] Re-run setup with Cocoon selected: its manually imported APK is recognized and not downloaded again. Its provenance remains unverified.
- [ ] Confirm failed downloads show **Needs attention**, while independent downloads can complete.
- [ ] Confirm ADB is under WindowsTools/platform-tools, NOT under the virtual SD.
- [ ] Confirm CHDman is unpacked under WindowsTools/chdman and responds to **Test CHDman executable**; a downloaded archive alone MUST NOT be marked Ready.
- [ ] Optional DuckStation selection is acknowledged as compatibility review, not silently ignored.

## C. CHD and artwork

- [ ] Choose a small legal PS1 CUE+BIN set from a disposable test folder.
- [ ] Use **Convert a PS1 game to CHD**; choose an output directory. Confirm a non-empty `.chd` exists and CHDman verifies it. Original `.cue` and `.bin` remain.
- [ ] Try again with the same output filename: refusal without overwrite.
- [ ] Add one small PNG cover to an imported game and check `Media/BoxArt/<system>/`.
- [ ] Run optional Libretro artwork lookup for a small collection; misses are reported, never fabricated. No artwork is claimed installed in Cocoon.

## D. Library and safe copy

- [ ] Import one small PS1, PSP or GBA file directly into My Games. The original must remain unchanged.
- [ ] Check My Games and Library Check: correct game count and no unexpected errors.
- [ ] Use Copy to Card → **Try a safe practice copy first**, then preview and start transfer.
- [ ] Verify the copied files match the source (app SHA-256 verification). Ensure the source remains untouched.
- [ ] Repeat the practice copy: unchanged files are skipped. Add a file and try again: only that new file is copied.
- [ ] Set the scale to 125%, move/resize the window, close, reopen, and confirm position and scale persist.

## Still pending on real hardware

- [ ] Physical 512 GB card detection, filesystem, real formatted capacity and free-space reserve verified.
- [ ] Physical copy progress, actual ETA, cancellation and safe resume tested.
- [ ] Android/USB device authorization and APK installation confirmed on the RG Rotate.
- [ ] Cocoon default Home selection, launcher folder permissions, emulator associations and controller mapping tested on device.

**A Python test suite PASS is not the same as a physical Windows/NAS or RG Rotate test PASS.**

## v1.2.2 Safe Stop acceptance (new, highest priority)

**Use only small expendable test files at first. Do not use the real microSD during this test.**

- [ ] Start `Start_Retro_Library_Studio.bat` with the existing NAS location saved. The GUI opens without waiting for a remote existence/capacity query.
- [ ] On **Start Here**, click **Check files in my virtual card**, immediately click **Stop task**. Status returns to **Ready** without force-closing the application. Scanned file counts are not falsely reset to zero.
- [ ] Begin another scan, select **Choose location** while it runs. The old scan stops, then the folder chooser appears. Cancel the chooser. Old workspace remains selected.
- [ ] Open **Install Apps**, let the app-status read-only scan begin, click **Stop task**. The app remains responsive and navigation continues to work.
- [ ] Import a **small** game from Windows to the NAS and press Stop while copying. The task should acknowledge cancellation when Windows completes its current SMB I/O step. Confirm the original file is intact. Inspect the NAS for an incomplete `.retro-part` if the operation was interrupted.
- [ ] Run a safe practice transfer. Stop once and confirm no completed destination file has failed verification or been overwritten. Retry to verify resumability.
- [ ] Click X while a **read-only** scan is still running, approve Stop and close. The program closes automatically, without requiring another X click.
- [ ] Reopen the app. Your NAS location, window geometry, and UI scale remain saved.

If read-only Stop is still stuck, use `Start_Debug.bat` and provide its log plus the **exact task name** shown at the bottom. If a **writing** task remains stuck, record whether the NAS is accessible in Windows Explorer, as Windows may be waiting on an uninterruptible SMB call.

## v1.2.3: Priority import Stop regression test

- [ ] Open the rebuilt program, confirm title says **1.2.3**, and the existing NAS virtual-card path is still selected. **Do not delete the card**.
- [ ] Import one very small expendable local file (e.g., your own homebrew `.gba` sample) to the NAS using My Games → Add Game Files. If the copy completes too quickly to press Stop, test a larger *expendable* file separately.
- [ ] Press **Stop task** during Importing Selected Games. The app should request stop, then end the isolated helper if SMB doesn't cooperate. You should regain the UI without force-closing the main window.
- [ ] Verify no incomplete source file was deleted or altered. The destination must not contain a finished game filename with truncated content.
- [ ] If a `.retro-part` is left after hard stop, retry the same source file. It should verify the matching prefix and finish. A deliberately different partial should NOT be overwritten; it should report a conflict instead.
- [ ] Repeat with **Add Folder** (which now also uses the isolated import child).
- [ ] Stop a read-only card scan and confirm v1.2.2's scan stop continues to work.
- [ ] Perform a small practice microSD transfer, but **do not use the physical microSD yet**.

**Report the status text and whether navigation works** if it still shows a stuck import. Other writing operations have separate cancellation paths and are not automatically covered by this import fix.
