# v1.4.4 focused retest: remembered practice destination

1. Extract this source ZIP into a **new program folder**. Leave the NAS virtual card and old practice transfer destination untouched.
2. Start `Start_Retro_Library_Studio.bat`.
3. Open **Copy to Card**. Your saved `Documents\Retro Library Studio\PracticeTransfer` target should say **PRACTICE MODE**. If you had previously selected a *different* practice folder, confirm Practice Mode explicitly when prompted.
4. Click **Check what would be copied**. If nothing has changed, the preview shows 6 staged files, 0 B new and 6 same-size existing files (not yet hash-verified).
5. Click **Verify 6 existing file(s) (SHA-256)**, confirm Practice Copy, and allow verification to finish.
6. Expected completion for your unchanged practice folder: 0 copied, 6 already identical, 6/6 SHA-256 verified. Then restart and confirm Practice Mode remains selected.
7. Only choose your **real** microSD root after inserting the physical card into its reader. Real Card mode retains all physical destination restrictions and 8 GiB safety reserve.

Windows GUI and real RG Rotate are still awaiting acceptance tests.

# v1.4.3 quickest retest: incremental copy

1. Start `Start_Retro_Library_Studio.bat`. Your existing NAS workspace stays selected; do **not** re-import games.
2. **Copy to Card** → keep the Windows **PracticeTransfer** folder as the destination, with **Practice mode** checked. Do not choose the actual SD card for this retest.
3. Click **Check what would be copied**. If the previous six-file copy is intact, expect **0 B** new and **6 files already present by name/size**. This is a *preview*, not a new verification.
4. The current transfer progress bar should be reset to **0%**. Click **Verify 6 existing files (SHA-256)**, confirm the path, then let it finish.
5. Expect **0 files copied · 6 identical · 6/6 verified** in the *new completion* dialog. No instruction to eject a practice folder.
6. Open the Windows test folder if desired; your source NAS files must remain unchanged. After that, you're ready to test the actual 512 GB microSD once inserted, with Windows checking real capacity and the 8 GiB free-space reserve.

If the practice destination changed or the files were altered, the counts will differ. A same-size but different file should be reported as a conflict, not silently overwritten.

---


## v1.4.2 Cocoon installer recognition correction

The user-tested `cocon-311.apk` (single "o") can now be recognized as a **manually imported Cocoon Shell candidate**, as well as APK filenames beginning with `Cocoon`. This requires the existing safe import receipt and its matching SHA-256, plus basic APK integrity checks. The app will label it **My APK ready • publisher unverified**, never "officially verified" or "installed on Android". The Ninite-style setup will skip re-downloading it by default. Unrelated names such as `coconut-tools.apk` do not match.

**Next tests:** Open **Install Apps** and check the Cocoon row; it should say `My APK ready • publisher unverified` while PPSSPP/RetroArch, ADB and CHDman retain their statuses. Then **Library Check → Scan my virtual card**. A successful file-integrity scan is *not* proof that the game will run in an emulator. Finally use **Copy to Card → Try a safe practice copy first**, perform preflight, copy and hash verification using a disposable folder. Do not use the real card until those pass.

The **Choose a PS1 CUE and convert** dialog selects a `.cue` sheet (not `.q`). Opening it only verifies the CHDman GUI is connected; actual disc conversion and verification are a separate test. A standalone `.img` file is not a CUE/BIN set and must not be mislabeled convertible through that picker.


# RG Rotate: Day-One Setup (v1.4.0)

## Tonight, before your handheld arrives

1. Unzip the application **into a fresh PC folder** and run `Start_Retro_Library_Studio.bat`. An internet connection and Python 3.11+ (64-bit) are required for the source launcher. `Start_Debug.bat` writes a log if startup fails.
2. Confirm the virtual-card location is your existing Synology share. You **do not need 512 GB free** until you actually stage that much game data. A virtual card is a normal folder, not a disk image.
3. Open **My Games** and confirm your original game(s) still appear. If you want the new Gore Edition artwork, use the manual image picker and select `Example_Covers/Resident Evil Gore Edition.png` shipped in this package.
4. Open **Install Apps** → select Cocoon Shell (default), PPSSPP, RetroArch, ADB Platform Tools and CHDman, then choose the recommended setup. Existing local Cocoon APKs can be staged instead. Download successes must be tested on your Windows PC; an APK on the card is not yet installed on Android.
5. Open **Start Here → What is ready for my RG Rotate?**, then go to **Copy to Card → Try a safe practice copy first**. Transfer and verify a small disposable set. Restart and verify again. NEVER use a real device card for the first test.

## When the card and RG Rotate arrive

1. Put the new microSD into the reader. Check Windows recognizes the correct drive and confirm actual capacity. No formatting is performed by this app. Back up any pre-existing card files before making changes.
2. Under **Copy to Card**, click **Find inserted card** or carefully choose the **root** of the actual microSD. Do not choose C:, an unrelated disk, or your NAS share. Verify the destination name and size.
3. Click **Check what would be copied**. Review new bytes, conflicts, filesystem limitations and 8 GiB minimum reserve. Then choose **Copy & Verify microSD** and confirm the physical destination.
4. During copy, the status displays speed/ETA and a distinct SHA-256 verification phase. For a stuck NAS copy, press **Stop**. If it remains stuck, the application offers an explicit **Force stop stalled copy…** button. This can leave an incomplete `.retro-part`; retry verifies before resuming. Never yank the card mid-write.
5. When completed with all files verified, **Eject** the card in Windows. Insert in the RG Rotate.
6. Install approved APKs from the setup folder or use optional USB-assisted Android installation; authorize USB and storage permissions. Set **Cocoon Shell** as Home. In Cocoon select the `ROMs` parent, choose a data folder and add emulator associations. Cocoon's first-run setup is on-device, per its official instructions.
7. Launch representative PS1/PSP titles, test input, sound, saves, UI visibility, and scan cover art inside Cocoon itself. Windows covers are *not* automatically registered with Cocoon.

## Storage policy

Marketed 512 GB ≈ 476.8 GiB before filesystem overhead. Reserve 8 GiB for companion data and maintain 8 GiB free on the REAL card. The virtual-card planning budget is roughly 460.8 GiB for all other staged content. These budgets do **not** allocate empty storage blocks on Windows or NAS.

## Release limitations

- This is a source **beta**, not a tested standalone Windows EXE. You can use `Build_Windows_EXE.bat` on Windows, keeping **all five EXEs** together.
- No unattended ROM/BIOS acquisition; only authorized software downloads, user-imported media, and artwork matching.
- Live NAS SMB transfers, Windows UI rendering, native Android app install, emulator mapping and hardware card checks require user acceptance testing.
- In case of failure use `Start_Debug.bat` and the included Windows acceptance checklist. Never erase the working NAS library to troubleshoot.
