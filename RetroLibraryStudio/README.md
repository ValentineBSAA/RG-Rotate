# Retro Library Studio 1.5.4 Beta — Artwork Previews, Right-click CHD Conversion

**Windows 11 / PySide6 · RG Rotate · Cocoon Shell default**

This version builds on the user-tested NAS import, verified practice copy and
safe-stop fixes. The virtual microSD folder is **not** a 512 GB disk image;
it grows only as games and software are staged. Your NAS remains supported.

## The simple PS1 workflow

1. In **My Games**, leave **Automatically convert PS1 CUE/BIN to CHD** enabled
   (it is enabled by default).
2. Open **Install Apps**, and make sure **CHDman** is ready on Windows.
3. Choose **Add Game Files** and select the **CUE** file, or **Add Folder** to
   select the complete game's folder. If selecting the folder, both BIN tracks
   are discovered automatically. ZIP/7Z sets are unpacked safely first.
4. Watch the SAME progress bar move through checking disc tracks, creating the
   CHD, verifying it with CHDman, copying the finished CHD to the virtual card,
   and looking up artwork. Because CHDman's progress cannot be measured
   reliably, the bar animates during conversion instead of inventing a percent.
5. A single-disc game becomes **one verified `.chd`** in the virtual PS1 library.
   Multi-disc games get **one CHD per disc**, plus a small `.m3u` playlist that
   lists those discs in order. M3U doesn't contain game data; it points to CHDs.

**Important:** The originals are never deleted. For a *new* import, the original
CUE/BIN tracks remain only where you selected them; the virtual ROM folder gets
the verified CHD. If CHDman is missing, the new PS1 CUE import reports an error
rather than silently importing incomplete BIN tracks. CUE/BIN names with
legacy Windows accents (CP1252) are supported. Bare BIN files aren't assumed
to be complete disc images. Files without CUE descriptors (such as raw IMG)
are not automatically converted by this pipeline.

### Existing Clock Tower and other previously imported discs

Choose **Convert earlier PS1 imports…** in My Games. This non-destructively
optimizes existing PS1 CUE/BIN folders on your virtual card. A verified CHD is
added, and the gallery prefers it over its CUE; **the originals are still in
that folder** and will also be copied to the real card until you explicitly
review/relocate them later. Do not delete your only working disc source.

The CUE's displayed size is now the **total of its referenced tracks**, not
just the tiny text-descriptor size. The total physical card usage counter still
counts actual files only once.

### Cover art

After a new import, the same worker tries the official Libretro cover catalog;
if an index cannot be retrieved, it attempts a few exact canonical title/region
names. Uncertain or modified editions are **not** automatically assigned a
potentially incorrect cover. Use **Search for a game cover** to review results
or choose your own PNG/JPG/WEBP. Covers are stored in `Media/BoxArt` and
previewed from a local Windows cache. Online artwork requires internet access.

## Start / safe usage

Extract to a **new application folder**. Run `Start_Retro_Library_Studio.bat`.
Keep your existing NAS workspace selected. The previous v1.5.0 or v1.4.4
application folders can remain as backups. Don't extract the update directly
into the NAS virtual-card directory.

This build includes the GitHub CI-tested Windows ZIP/CUE track-path fix. It is still a **source beta**; real CHDman and Android game launching require your tests.

The 512 GB planning profile, 8 GiB companion budget, 8 GiB always-free reserve,
Cocoon APK workflow, Ninite-style downloader, disk health checker and verified
incremental microSD transfer remain supported. Nothing formats the card.

## Testing scope

Run `RUN_TESTS_Windows.bat` and follow `WINDOWS_TEST_CHECKLIST.md`. Tests in the
packaged source cover the PS1 conversion orchestration with a simulated CHDman.
They do **not** establish that actual MAME CHDman conversion, Android emulator
launch, live cover retrieval, Windows GUI layout or physical-card transfer
passed in this environment. Validate these on Windows before importing the full
collection or copying your physical card.

---

## Original 1.5.0 documentation (historical)

# Retro Library Studio 1.5.0 Beta — Guided Setup & PlayStation Discs

Windows 11 / PySide6 source release, based on the supplied v1.4.4 project.
Extract into a **new application folder**. Keep your existing PC/NAS library
folder selected; no re-import, library reset or artwork migration is required.
The existing QSettings organization, application name and saved paths are kept.

## Start

1. Install a normal Windows Python 3.11+ distribution with its Python launcher.
2. Run `Install_Dependencies.bat`, or let `Start_Retro_Library_Studio.bat` prepare
   its private `.venv` automatically. Use `Start_Debug.bat` for startup messages.
3. Choose your existing library folder in the top strip. Use **Add My Games**,
   **Prepare My RG Rotate**, or **Copy to My microSD** from Start.

The sidebar uses shorter names: Add games, Prepare apps, Copy to card.
The current page's main actions remain below its scrolling content. Extra import
and artwork options expand when selected. The gallery remains the default;
File list shows the actual individual files. Display-title edits save in Windows
settings and do not rename files or change artwork identity. Multi-disc/region
variants in the same folder share a gallery tile with their original paths in
its tooltip. CUE-referenced tracks remain in File list, rather than separate game tiles.

## PlayStation Disc Converter

Open Prepare apps → **Convert PS1 discs…** in the fixed action bar.
Select one or more complete `.cue` sheets, then an output folder. Never select
an individual BIN track as a complete disc. The worker checks FILE references,
relative subfolders, multiple files, declared tracks and audio tracks before
showing a review. Missing filenames show their expected paths; the app does not
repair CUE sheets or rename original tracks.

Empty and suspicious zero-filled samples produce warnings, not automatic
rejection. For large tracks only beginning/middle/end samples are examined;
silence and padding can be legitimate. CHDman's parser and verification decide
whether a conversion succeeds. The report includes source, output, bytes,
verification and actual CHDman errors (up to the last 12,000 characters).
Each disc stays separate. Failed conversions never publish a completed CHD.
Original CUE/BIN files are never deleted. Existing output names are refused.

When multiple discs verify, optionally create an M3U, **only for discs of the
same game**. Drag the paths into Disc 1 / Disc 2 order before saving. Playlists
use relative CHD filenames, must live beside those CHDs, and cannot overwrite
an existing playlist. Conversion does not automatically import the output;
use Add My Games to add the CHD/M3U when ready.

Stop first requests cancellation. The worker is force-stoppable if NAS I/O hangs.
A Windows job object also ends its CHDman child when that worker exits. A forced
stop can leave `.retro-converting.chd`; inspect/remove only that generated
temporary output before retrying. Completed verified discs are preserved.

## Preparing apps and copying safely

The batch setup and its status messages run in the isolated worker. Existing
manual APK receipts and matching hashes are retained, including `cocon-311.apk`.
These remain **publisher unverified**. APK ready never means installed on Android.
ADB and CHDman are prepared under WindowsTools and checked as executable. Older
ADB files need one setup run for the new version-check receipt; no duplicate
download is required when the existing executable passes.

Select a practice folder or physical card, preview, then copy/verify. The transfer
worker checks capacity, overlap, conflicting files, resumable partials and the
protected reserve again. Live progress includes current file, bytes, speed, ETA,
hash-verification stage and completed verified-file counts. New previews reset
the current result; previous runs remain explicitly labeled history. Destination
capacity/availability checks run in the preview worker, rather than during navigation.

The 512 GB profile, 8 GiB companion budget, 8 GiB protected card reserve, NAS
workspace, artwork, APK import, BIOS tools, health checks, device setup and
practice-copy workflows remain available. Nothing formats your card or moves
your original ROMs.

## Validation and building

Run `RUN_TESTS_Windows.bat`. See `RELEASE_REPORT.md` for exact test scope and
`WINDOWS_TEST_CHECKLIST.md` for the remaining live checks. This is a source beta,
not a signed or hardware-certified release. Optional `Build_Windows_EXE.bat`
builds the same five executables; keep them together in `dist`.

The sections below are historical v1.4.4 and earlier notes. Their statements
about tests and layout refer to those releases, not to 1.5.0.

---

## v1.4.4 practice-folder fix

v1.4.3 saved the practice destination path, but did not save the Practice Mode checkbox. This caused the real-card drive-root restriction to reject an ordinary practice folder after restarting. v1.4.4 remembers both, restoring the old default `Documents\Retro Library Studio\PracticeTransfer` as a practice location when it is already selected. New folder selections automatically enter Practice Mode; root drive selections use real-card mode. Unexpected old custom folders require confirmation before copying.

**Retest:** Keep the existing NAS virtual card and already-copied Windows practice folder. Open Copy to Card, verify the chosen destination reads **PRACTICE MODE**, preview, click **Verify Existing Files (SHA-256)**, and confirm. Expected for the unchanged six-file example: **0 newly copied, 6 existing identical, 6/6 verified**. Close and reopen and confirm PRACTICE MODE stays selected. No re-import or clearing the folder is necessary.

# Retro Library Studio v1.4.4: Practice Mode Persistence (November 22, 2026)

**Why this release:** The real Windows test successfully copied and SHA-256 verified 6/6 files (1.21 GB) from a Synology NAS to a Windows practice folder. On the next preview, the program estimated **0 B of new data**, but incorrectly left the previous **100% / Copied 6 files** result visible. That screenshot proves the incremental *preflight*, not a new SHA-256 verification. This release makes that distinction explicit.

**New behavior:**
- Preflight counts files already present **by name and size only** and prominently says that a preview does NOT verify hashes.
- If all staged files already exist and 0 B needs copying, the next action becomes **Verify N existing files (SHA-256)**.
- Starting a new preview or changing the destination resets the *current* progress bar to 0, instead of inheriting an old 100% result.
- The previously completed run is retained in a **separately labeled** history line; it cannot be mistaken for a current verification.
- After preview, the application automatically scrolls to the next transfer action.
- A second successful run clearly reports **0 new files copied, N existing files identical, N/N SHA-256 verified**.
- Practice-folder success dialogs no longer tell you to eject a card that does not exist. Real-card success dialogs still advise safe ejection.
- A corrupt existing file of the *same size* is **not** counted as verified by the preview. A repeat verification detects its different hash and refuses to overwrite it.

**Preserved:** Cocoon Shell default; NAS virtual-card workspace; 512 GB planning limit, 8 GiB companion budget, 8 GiB protected physical-card free space; game and APK import, Cocoon filename recognition, gallery and manual covers; CHDman and Android tools; background subprocess transfers, Stop/force-stop, safe resume and no-overwrite behavior.

**Re-test in Windows:** Extract this version to a fresh application folder, run `Start_Retro_Library_Studio.bat`, and keep your existing Synology workspace. In **Copy to Card**, use the previously populated **PracticeTransfer** destination, and **Check what would be copied**. Expect `0 B new` and a warning that the files are *not yet hash-verified by this preview*. The progress bar should reset to **0**, with a button labeled **Verify 6 existing files (SHA-256)** (the number may differ if you added files). Click it, approve the *practice* path, and let the verification finish. Expected for an unchanged practice folder: **0 copied, 6 already identical, 6/6 verified**. Save a screenshot of that *new completion* result. If files were changed since the previous run, the outcome will differ appropriately.

**Limitations:** Automated tests run the real Python transfer worker and cover the incremental/corruption paths, but this environment does not have PySide6/Windows or access to your NAS and real microSD hardware. Windows layout, live NAS verification, and physical RG Rotate setup still need on-device testing. This is a source beta, not a prebuilt signed Windows EXE. Nothing in the application installs APKs on Android merely by placing them on the card.

---

# v1.4.1 APK Import Repair (November 22, 2026)

## v1.4.2 Cocoon installer recognition correction

The user-tested `cocon-311.apk` (single "o") can now be recognized as a **manually imported Cocoon Shell candidate**, as well as APK filenames beginning with `Cocoon`. This requires the existing safe import receipt and its matching SHA-256, plus basic APK integrity checks. The app will label it **My APK ready • publisher unverified**, never "officially verified" or "installed on Android". The Ninite-style setup will skip re-downloading it by default. Unrelated names such as `coconut-tools.apk` do not match.

**Next tests:** Open **Install Apps** and check the Cocoon row; it should say `My APK ready • publisher unverified` while PPSSPP/RetroArch, ADB and CHDman retain their statuses. Then **Library Check → Scan my virtual card**. A successful file-integrity scan is *not* proof that the game will run in an emulator. Finally use **Copy to Card → Try a safe practice copy first**, perform preflight, copy and hash verification using a disposable folder. Do not use the real card until those pass.

The **Choose a PS1 CUE and convert** dialog selects a `.cue` sheet (not `.q`). Opening it only verifies the CHDman GUI is connected; actual disc conversion and verification are a separate test. A standalone `.img` file is not a CUE/BIN set and must not be mislabeled convertible through that picker.


This update corrects the failed Cocoon APK import acceptance test on a Synology NAS workspace.

**What was broken:** Selecting an APK repeatedly navigated to Install Apps. That navigation started a NAS readiness scan, set the program as busy, and rejected the actual import. In addition, the APK importer used a background Qt thread and scanned the whole virtual card again for each APK; its completion action refreshed game files instead of the Android installer list.

**Fixed:**
- Import does **not** begin an unrelated app-status scan. An active task is clearly reported instead of silently dropping your selection.
- APK staging runs in the same isolated Stop-capable child process used by the proven game importer. The app stays navigable when a NAS read stalls, and Stop can terminate the stalled child.
- Workspace usage is checked only once per batch; importing an identical existing APK does not trigger an unnecessary full-card scan.
- Completion explicitly reports the number copied/skipped/errors, the exact saved path and filename, and explains that Android installation is still pending. If zero APKs were added, an error is displayed, not a success.
- The installer list refreshes after a successful import (using a stoppable read-only NAS scan).
- A partial `.retro-part` file is never displayed as an installed/ready APK. Retrying is safe when the existing partial matches the source.

**Test Cocoon 3.11:** Open Install Apps -> scroll to **Already downloaded an Android app?** -> **Add APK Files** -> choose your existing `Cocoon*.apk`. Watch the active task indicator. You should see **APK import completed** with a destination such as `\\Joes-Plex\G Drive\Gaming RG Rotate\RG Rotate Virtual Card\SetupPackages\Cocoon-3.11.apk`. Click **Open Android installers folder** and verify the file is present. The Cocoon status should become **My APK ready • publisher unverified**, not **installed on Android**.

**Important:** A valid APK is a ZIP archive with an `AndroidManifest.xml` entry. Renamed HTML pages and unsupported bundle formats (`.apkm`/`.xapk`/`.apks`) are not accepted as single APKs. The app can test structure and integrity, but **cannot verify the publisher identity of user-provided APKs**.

# Retro Library Studio v1.4.0 Day-One Beta: NAS-to-microSD Copy Safety

**Windows 11 + Python/PySide6 | RG Rotate | Cocoon Shell default | Source beta**

This is a guided Windows application for preparing game files, authorized Android app installers, artwork, and an eventual verified transfer to a real microSD card. It **never allocates an empty 512 GB image**. Your virtual microSD is a normal folder that occupies space only as content is imported.

## v1.4.0: focused arrival-day transfer upgrade

**The most important change:** card transfer **preview AND verified copy** run in a separate `RetroLibraryTransfer` child process rather than in a Qt worker thread. This protects the GUI when Windows waits for a mapped Synology NAS. First Stop is cooperative. If a network I/O call does not return, after six seconds the bottom button offers **Force stop stalled copy…**, requiring another explicit confirmation. A forced termination may leave an incomplete `.retro-part` on the card; the next run validates that partial against the source before resuming. Finished files are published only after SHA-256 validation, and neither the original games nor unrelated destination files are deleted.

- An independent subprocess re-checks folder overlap, actual SD space and 8 GiB reserve when copying. A GUI preflight cannot override its safety checks.
- Transfer progress shows data copied, speed, ETA, plus a **Verifying SHA-256** stage. ETA is an estimate, not a guarantee over SMB.
- The Windows EXE build now has **five** binaries that must stay together, including `RetroLibraryTransfer.exe`.
- The **Day-one readiness** button on Start Here shows which PC-side steps are done and which still require your actual handheld. It is deliberately a cached snapshot, not another blocking network scan.
- `Example_Covers/Resident Evil Gore Edition.png` is included from the cover artwork created in this chat. In My Games → Search for cover → **Choose image from PC instead**, select that PNG to assign it manually. This does not change or rename the ROM.

**Not yet verified:** Windows execution of the new PySide6 flow, physical RG Rotate transfers, actual SMB stop under load, Cocoon/emulator installation on Android, and live Ninite-style downloads. The automated suite exercises the Python helper and core engine; it does not replace a real Windows/SD test.

See `DAY_ONE_QUICK_START.md` and the shortened top section of `WINDOWS_TEST_CHECKLIST.md` before transferring a large library.

## Manual game-artwork search (introduced in 1.3.1)

You can choose **your own search query**, even when the game has an unofficial or modded edition name.

1. Open **My Games** and choose **Search for cover** on a game tile. In **File list**, click **Search for a game cover…**, then select the imported game.
2. In the search window, edit the title (for example, search for **Resident Evil** when the file is named `Resident Evil Gore Edition.img`). Click **Search** or press Enter.
3. Select the proper result. Click **Preview selected** to see the actual online image before deciding.
4. Click **Use selected cover** and confirm. Only the artwork is saved under `Media/BoxArt`; the original game file is unchanged. You can also choose an image from your PC instead.

Searching and previewing do not add or download games. Online artwork is fetched from Libretro's thumbnail library. An internet connection and a matching entry are required; otherwise use **Choose image from PC instead**. Search/preview can be cancelled with **Stop task**; on a NAS, the final artwork write is done in a separate cancellable helper process. Previously saved covers and original ROMs are protected from automatic replacement.

## New in v1.3.1: your My Games cover gallery

**Your Synology virtual-card location stays the same. No need to rebuild or reimport games.** The app is still a source beta, not a verified Windows executable.

- Open **My Games** and select **Cover gallery** (default) or **File list**. Search and filter systems; scroll within the gallery and use **Show more games** for larger collections.
- Games show their own cover (if available), readable title, system and size. PS1 CUE/BIN companions are treated as a single game for cover lookup. Your actual game filenames and folders are NOT renamed.
- **Automatic covers:** the first scan of an existing workspace starts a visible, stoppable artwork lookup once. After successful new imports, missing-cover lookup runs automatically while the checkbox remains enabled. Uncheck it in My Games to disable automatic artwork queries.
- Matching uses Libretro's `Named_Boxarts` catalog. Only normalized exact-title matches are downloaded automatically. Region tags such as `(USA)` can be ignored, but special edition words remain meaningful. For `Resident Evil Gore Edition`, do **not** assume the regular Resident Evil cover is correct. The tile will offer **Find / add cover** for review.
- **Per-game correction:** click the tile's **Find / add cover**, then either search online and choose one of several suggestions, or choose a PNG/JPG/WEBP image from your PC. Explicit confirmation is required before replacing a previously saved cover. A bad or ambiguous match never silently overwrites a manual image.
- The full cover is saved under `VirtualCard/Media/BoxArt/<system>/<game>.png`, and the GUI uses an additional **Windows-local preview cache**. A fast gallery therefore doesn't repeatedly open full-size images over SMB. If that cache is missing on a different PC, use **Find missing covers** to reconstruct it from covers already on the virtual card, even offline.
- Cover downloads and writes happen in `artwork_worker.py`, a **separate stoppable subprocess**. Hard stop can leave a `.retro-art-part` temporary *artwork* file, never a fake completed game. Original ROMs remain untouched.
- The optional Windows EXE builder now produces **four** files that must stay together: `RetroLibraryStudio.exe`, `RetroLibraryScan.exe`, `RetroLibraryImport.exe`, and `RetroLibraryArtwork.exe`.

**Important Cocoon distinction:** this prepares artwork for Retro Library Studio and saves it alongside the virtual card. It **does not guarantee Cocoon Shell will automatically display those images**. Cocoon has its own Android-side artwork scraper and game artwork editor (https://cocoon-shell.com/wiki/scraping/). Test Cocoon's import/assignment once the RG Rotate is physically available.

**Artwork data:** the lookup is from the community Libretro thumbnail service, https://thumbnails.libretro.com/ . Covers may have their own rights and licensing. Do not redistribute them without permission. Catalog availability and metadata matches require a live internet connection and are **not** verified in the automated offline test suite.

### Windows test: previously imported Resident Evil Gore Edition

1. Extract v1.3 into a new application folder; run `Start_Retro_Library_Studio.bat` and keep your existing NAS workspace. Avoid moving the actual ROMs folder.
2. Open **My Games**. Existing `Resident Evil Gore Edition.img` should appear as a PS1 tile with the correct size. The first artwork lookup should be visible in the bottom task bar and should be cancellable.
3. If no automatic cover is assigned, click **Find / add cover → Search artwork online** and review the possible title matches. If none is correct, choose your own PNG/JPG/WEBP image.
4. Check `Media/BoxArt/psx/Resident Evil Gore Edition.png` on the NAS after a successful artwork selection. Switch from **Cover gallery** to **File list**, then back.
5. Reopen the app. The cover preview should persist through the local Windows cache, and the original IMG should still be present and unchanged.
6. If you need to check cancellation, start a cover search, click **Stop task**, and confirm the status returns to Ready with navigation available. Use a small disposable collection for the first test.

## The 3 most important things

1. **Pick a folder on your PC OR your mapped Synology NAS drive.** Use `Choose location…` in the top strip. An example is `L:\RG Rotate\RG Virtual Card` or `R:\RG Rotate Virtual Card` if R: is a mapped NAS share. You can also select a reachable UNC folder such as `\\NAS\Shared\RG Rotate`. The app creates its own `ROMs`, `BIOS`, `Media`, `SetupPackages`, `CocoonData`, and `CompanionData` structure.
2. **Add your files, without moving originals.** In My Games, import owned game files, folders and ZIP/7Z archives. In Install Apps, import existing APKs, run the official-source batch setup, add your own cover art, or use CHDman if you choose to convert a PS1 disc. Imported Cocoon APKs are identified as *user-supplied* and are NOT publisher-verified.
3. **Copy & verify the real card only when you have it.** First use Copy to Card → Try a safe practice copy. Later select the physical SD drive and run its preflight and SHA-256 verification. Windows-side APK staging is NOT Android APK installation.

## Why your free-space numbers differed

The old application could continue displaying the **previous drive's** free space while it recursively inspected an empty card. In v1.2:

- A freshly empty workspace switches immediately, without the full file-count operation.
- Local-drive free-space lookup runs in a background task. **NAS/SMB free-space lookup is optional**, so a sleeping NAS cannot keep the screen stuck at Checking. Click **Check storage** to request its capacity with a six-second timeout. The app remains usable without that figure; old results cannot overwrite newly selected locations.
- The main screen distinguishes **backing storage free** (what your PC/NAS has), **remaining simulated capacity** (512 GB marketed profile), and **how much more you can stage right now** (the smaller limit).
- If Windows reports 461 GB free at the new location, the program should show that location's 461 GB (subject to decimal/binary display), not the previous drive's 289.16 GB.
- You do NOT need to delete files to pre-allocate 512 GB. You can import gradually until you need more free space. NAS storage is a valid location for the virtual card, but scanning and large transfers are limited by your network speed and the NAS's available space.

The marketed 512 GB microSD is about 476.8 **GiB** before filesystem overhead. The app reserves an **8 GiB AI companion budget** plus an **8 GiB always-free buffer on the real card**, so about 460.8 GiB is planned for games and other library content. These are accounting limits, not empty files. Actual hardware capacity and file sizes determine the precise final transfer allowance.

## v1.2 software setup (retained)

Install Apps is the Ninite-style setup center. Leave wanted items checked, then click **Install Recommended Setup** (it now honors every checked/unchecked item). The app attempts official downloads sequentially and reports per-item successes and failures. The default selections are Cocoon Shell, PPSSPP, RetroArch, Android Platform Tools and CHDman. DuckStation remains optional and compatibility-sensitive; selecting it reports a manual compatibility review instead of auto-installing an uncertain beta.

| Component | Destination / verification |
|---|---|
| Cocoon, PPSSPP, RetroArch | APKs staged under `VirtualCard/SetupPackages/`, **not yet installed on Android** |
| Your manually imported Cocoon APK | Same folder; the batch setup will recognize its matching saved import receipt, report "publisher unverified", and avoid redownloading it by default |
| Android Platform Tools | Windows `Documents/Retro Library Studio/WindowsTools/platform-tools/adb.exe` |
| CHDman | Windows `Documents/Retro Library Studio/WindowsTools/chdman/chdman.exe`; tests actual executable response before reporting Ready |
| PS1 CUE → CHD | Choose the CUE file and output directory under Install Apps, keeping your originals. Conversion runs CHDman `createcd`, then `verify` before publishing output. |
| Box art | `VirtualCard/Media/BoxArt/<system>/`; choose a local image or run a best-effort Libretro lookup from the new gallery (batches up to 80 games). It does **not** guarantee cover matches, and Cocoon may require Android-side art assignment. |

**Copyright:** The program never fetches commercial ROMs or proprietary BIOS images. Obtain commercial software only through lawful sources and provide any required BIOS yourself. Artwork is from user-selected PNG files or an optional public Libretro thumbnail lookup; check licensing requirements before redistributing images.

## Launch on Windows

Extract the ZIP into a **new** folder. Do not extract on top of older versions. Run `Start_Retro_Library_Studio.bat`. First startup installs required Python dependencies (internet required). `Start_Debug.bat` also runs dependency checks and writes a startup log if necessary. The optional `Build_Windows_EXE.bat` is provided for building a Windows EXE locally; the ZIP contains **source**, not a prebuilt EXE.

The application uses Windows QSettings to remember the chosen workspace and window position and the view size including **125%**. Your old virtual-card files are never overwritten or deleted during normal updates. If the previous workspace has content and you choose a new one, you can perform a verified copy or switch without copying; the original remains untouched. An incomplete `.retro-part` file blocks switching until it's recovered so an interrupted import isn't silently abandoned.

**Mapped NAS drives:** Keep the NAS connected and ensure your Windows user has read/write access. Mapped drives may not be visible to programs run under another Windows account or elevated privileges. Run the app normally, not as Administrator. Some network shares may disconnect during sleep; the application will report an unavailable path rather than silently move the library. An SMB drive isn't itself a physical microSD destination.

## How verified transfer works

The separate source directory may be on a PC SSD/HDD or NAS. The destination must be a different directory/device. The transfer preflight checks target free space, incompatible FAT32 single-file sizes, and filename conflicts. Confirmed transfers are incremental, SHA-256 verified, cancellable and resumable (where the partial prefix still matches the source). Files already on the destination are never silently overwritten, and no card formatting is performed.

**Status and limitations:** Automated *pure-Python* tests pass. PySide6 appearance, Windows mapped-NAS behavior, live official downloads, executable CHDman validation on Windows, exact-title artwork lookup, and physical SD transfers still require Windows acceptance testing. See `WINDOWS_TEST_CHECKLIST.md`. Do not use the real microSD until practice transfer succeeds.

## v1.2.1 NAS storage responsiveness fix

- On a Windows UNC / mapped network drive, the location panel immediately says **NAS workspace selected • Capacity check optional**. It does not auto-query the NAS on startup or when changing the workspace.
- **Check storage** queries capacity in a disposable process with a six-second timeout; a busy or disconnected NAS cannot keep an endless spinner. On local drives, this remains an automatic background check.
- Failure to read NAS capacity is **not** evidence that the workspace is full. It is a warning only. Writes still require sufficient real free space, and the app must not claim to have verified capacity until it has.
- No 512 GB disk image is created. The physical 512 GB card remains the final transfer destination.
- NAS transfers are limited by network throughput. Do the test import and practice copy with a small, lawfully obtained game first.

The capacity check is non-destructive. Because the PySide6 UI and SMB network cannot be exercised here, verify the optional-check flow on Windows before relying on the result.

## v1.2.2: Safe Stop on a Synology NAS

**Start with this release in a new folder.** It remembers the same virtual-card workspace from Windows settings; do not delete or move your NAS library. When you open the app, a **Checking Virtual Card** task is now handled by a disposable read-only helper (`readonly_scan.py`). Clicking **Stop task** should return the status to **Ready** without waiting for a NAS file-listing call to complete. This mechanism also handles a long **Checking Existing Card Before Location Change** scan and network-side **Install Apps** status inspection.

- Clicking Stop for a **read-only scan** first requests the helper to quit, then terminates it after a short grace period if needed. Your source files are never modified by those checks.
- Clicking Stop for a **write** requests cooperative cancellation. File imports, ZIP extraction, verification and transfer planning now poll the cancel flag more often, but an individual slow Windows/SMB write may still take time to return. The app displays this explicitly after several seconds. Do not unplug the card or power off the NAS during a write.
- If you click the window's X during a task, the app can cancel and close automatically when the task ends. It no longer requires an endless cycle of closing the window again. A blocked network write must still return first.
- No remote storage-capacity probe or directory existence check is required before the initial window opens. The optional **Check storage** button from v1.2.1 remains.
- If you build a Windows EXE, keep the two generated executables `dist/RetroLibraryStudio.exe` and `dist/RetroLibraryScan.exe` together. The source launcher automatically invokes `readonly_scan.py` via its Python environment.

**Windows acceptance tests still needed:** Stop the automatic NAS card scan while it is active, navigate between sections, stop an app-status check, and then test cancelling a small game import. Confirm the app returns to Ready, originals are untouched, and previously staged files remain intact. See `WINDOWS_TEST_CHECKLIST.md`.

## v1.2.3: NAS game-import Stop repair

**Your screenshot identified the remaining issue:** `Stopping: Importing Selected Games` stayed active because the import was running in a Qt worker thread blocked inside Windows SMB I/O. The earlier v1.2.2 child-process fix covered *scans*, not game *imports*.

- Game file and entire-folder imports now run in a separate `import_worker.py` process, not in a GUI worker thread. The main window can navigate while the import is active.
- Stop first sends a cooperative `STOP` to the helper. If that worker is still blocked after a brief grace period, the GUI can end **that import worker only**, without terminating the app.
- Files are copied to `.retro-part` temporary siblings and are renamed to the finished ROM filename only after a complete copy. A forced stop might leave a `.retro-part`; an attempted retry verifies its bytes against the source and resumes only a matching partial. Conflicts remain untouched. Original game files are never moved or deleted.
- The GUI does **not** report a forced stop as completed until the import child has actually exited. If Windows delays termination, navigation is still available but new writes stay disabled to avoid races.
- Both regular **Add Game Files** and **Add Folder** use the isolated helper. It scans folders off the UI thread too.
- For building an EXE, keep `RetroLibraryStudio.exe`, `RetroLibraryScan.exe`, and **`RetroLibraryImport.exe`** together. The source `.bat` launcher uses the Python import helper automatically.

**Windows acceptance test:** close the stuck old app if necessary, then launch v1.2.3 from a new folder, keeping the same NAS workspace. Import only one small, nonessential homebrew/test game from a local PC folder. Press Stop while the import is active. It should return to Ready after the child exits. Retry that same file and confirm it completes, then verify that the original remains intact and the NAS has no falsely completed partial. Next test a slow NAS import. Do not start with a huge library or the real microSD.

**Limitations:** The Windows Qt GUI and Synology SMB calls cannot be executed in this container. A subprocess hard-stop is tested locally but still requires a real Windows/NAS acceptance test. Other file-writing operations (APKs, CHD conversion, SD transfer) remain cooperatively cancellable; this change specifically isolates **game imports**. When Windows itself delays process termination, no software can promise an instantaneous OS-level stop. Never disconnect the NAS or unplug media during writes.

## v1.5.3: clear game formats and resilient cover search

Click the **CHD**, **BIN/CUE**, **M3U** or other format badge on any cover tile to see what file exists and what still needs verification. Artwork search now falls back to the official Libretro thumbnail catalog on GitHub and shows a manual browse option when online search cannot complete.

## v1.5.4: Visual cover previews and right-click conversion

Clicking an artwork search result automatically loads a preview below the matching titles, without applying it until you confirm. The separate Preview button also remains available. This uses a cancellable background artwork helper.

Right-click a PS1 game tile or file-list entry for a styled context menu: Rename, Search/Preview Cover, File Format Details, Convert to verified CHD and tidy the PSX folder, or Open Folder. BIN/CUE and safely identifiable single-track IMG are supported. CloneCD CCD/IMG/SUB and ambiguous IMG sets are **rejected instead of guessed**. If the original CUE/BIN still exists beside a CHD, right-click the CHD to verify it and move legacy tracks to a recoverable location.

**Original source safety:** CHDman must first create and verify a CHD, then reverify the completed destination. Only after success does the program move the CUE/BIN or IMG into a sibling folder named `<virtual card> - Conversion Backups`, outside the virtual microSD. No permanent deletion; original files remain recoverable. The app never silently formats a drive. Keep backups until play-tested on RG Rotate.

**Test scope:** Local 240 passed, 15 skipped. GUI and genuine MAME chdman conversion on the user's Windows NAS remain for acceptance testing.

## v1.5.4: Visual cover previews and right-click conversion

Clicking an artwork search result automatically loads a preview below the matching titles, without applying it until you confirm. The separate Preview button also remains available. This uses a cancellable background artwork helper.

Right-click a PS1 game tile or file-list entry for a styled context menu: Rename, Search/Preview Cover, File Format Details, Convert to verified CHD and tidy the PSX folder, or Open Folder. BIN/CUE and safely identifiable single-track IMG are supported. CloneCD CCD/IMG/SUB and ambiguous IMG sets are **rejected instead of guessed**. If the original CUE/BIN still exists beside a CHD, right-click the CHD to verify it and move legacy tracks to a recoverable location.

**Original source safety:** CHDman must first create and verify a CHD, then reverify the completed destination. Only after success does the program move the CUE/BIN or IMG into a sibling folder named `<virtual card> - Conversion Backups`, outside the virtual microSD. No permanent deletion; original files remain recoverable. The app never silently formats a drive. Keep backups until play-tested on RG Rotate.

**Test scope:** Local 240 passed, 15 skipped. GUI and genuine MAME chdman conversion on the user's Windows NAS remain for acceptance testing.
