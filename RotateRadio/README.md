# RotateRadio 0.3.0 — Android Studio alpha
Standalone ARM64 Android app for GTA LCS/VCS on PPSSPP. No ISO, emulator configuration or game save modification. Pick music folder and PPSSPP PSP or SAVEDATA folder once; select target(s); convert and install additively. One folder is one station pack; nested music is scanned recursively. Existing files are never intentionally overwritten. Existing custom tracks remain active alongside newly added tracks. GTA exposes its native custom soundtrack mode, not multiple distinct in-game radio slots.

Encoder candidate: https://github.com/liangchunn/atracdenc-rs (LGPL-2.1, standalone CLI, build workflow includes matching source in artifact). ATRAC3 LP4 RIFF is experimental until tested on device. Android MediaCodec decodes supported source formats and resamples to stereo PCM16 44.1 kHz. Unsupported, corrupt and short tracks fail individually. No cloud uploads. Copy music wirelessly using PairDrop and extract ZIPs using Android Files before selecting the folder. No built-in wireless server, ZIP unpacker, true station switching, or ISO-based automatic region detection in this alpha. Region suggestions are based on recognized existing save folders; user confirms the selection. If no saves exist or multiple regions are present, choose manually. On Android use PPSSPP Settings > System > PSP Memory Stick > Show Memory Stick folder; select its PSP or SAVEDATA folder. If private storage is inaccessible, stop and do not migrate without backup. Close GTA before installing; enable Custom Soundtracks in Audio after launching. Test 2 tracks first.

Sources: https://www.ppsspp.org/docs/reference/custom-background-music/ and https://github.com/liangchunn/atracdenc-rs. Debug APK only; not physically tested. APK and matching encoder source are in GitHub Actions artifact if build succeeds. To uninstall music, disable custom soundtrack in GTA; remove only RR-prefixed files you recognize from CUSTOMTRACKS, never delete SAVEDATA or save folders. Future: managed undo, station pack activation, persistent cache, direct wireless upload, resume.

## Hardware acceptance checklist
- Install APK only after successful CI, on RG Rotate ARM64 Android 12.
- Launch GTA and save once; close PPSSPP completely.
- Transfer a small folder with two original or licensed tracks over PairDrop; choose music folder and the existing PSP/SAVEDATA folder. Verify region suggestion.
- Test an MP3 or M4A and a preencoded ATRAC3+ sample, each longer than 5 seconds. Verify progress and copy integrity; repeat import and confirm duplicates skipped.
- Launch GTA and turn on Custom Soundtracks; test driving, dialogue and sound effects. Disable custom soundtrack and verify original radio returns.
- Check game saves and ISO unchanged; cancel a second batch and verify previously installed tracks remain. Test microSD folder permissions.
- Do not call this production-ready until the encoder executes on Android and playback succeeds in LCS/VCS.

## Plex Connect (0.2.0)
1. Select the existing PPSSPP PSP/SAVEDATA directory and correct GTA region in Setup. Keep PPSSPP 1.20.3 for testing. Close GTA.
2. Tap Plex Connect, Link Plex. On your iPhone visit https://plex.tv/link and enter the displayed device code. Return to RotateRadio and Check authorization.
3. Select a discovered Plex server with a reachable HTTPS connection. Browse music libraries, artists, albums, tracks, playlists, or search by track title. Select songs individually or select all tracks of a collection (up to 1000). Choose Install selected. Confirm the destination.
4. The app requests the original authorized Plex media part, downloads one track at a time, converts it using the existing encoder, validates and installs into CUSTOMTRACKS. Temporary downloads are deleted; installed files remain offline. No modifications are sent to Plex. Mobile data charges may apply.

Security: Plex device code flow; account token encrypted using Android Keystore AES-GCM, server token session-only, TLS certificate validation, no HTTP fallback or redirects. Only Plex-discovered HTTPS plex.direct/plex.tv servers accepted. Sign out clears local credentials. No passwords or tokens needed in GitHub. Remote server must be reachable and permit authorized original file downloads; no bypass of access controls. Shared servers, relay, custom domains, unusual formats and live authentication have not been hardware-tested. One source part per track. Batch limit 1000, file limit 512 MB, track limit 30 minutes. Local folder import still available. Existing game files and music untouched.

Build signing: CI debug keys may change between runs. If Android reports signature conflict, uninstall only the RotateRadio application (NOT PPSSPP or any game data), then install 0.3.0 and select folders again. Existing CUSTOMTRACKS outside app private storage stay intact. No production signing yet.

Plex API reference: https://developer.plex.tv/pms/. Test with two tracks first, then one album/playlist, cancel a download, repeat to test duplicates, and verify offline playback in GTA. Plex live login and download cannot be validated without a real user session on the handheld.


## Android Studio redesign (0.3.0)
- Music, Queue and Setup navigation with fixed bottom tabs, larger touch targets, high-contrast dark cards and scrollable content for the square RG Rotate display.
- Setup retains existing folder permissions and game selection on a signature-compatible update. Choose Setup first on fresh installations.
- Plex track pages use multi-selection without a network reload per tap; select or clear a page, select whole collection, review and install. Existing secure Plex backend unchanged.
- Queue shows download, conversion, verification/install, processed track totals and final installed/skipped/failed counts. Activity log is collapsible. Screen stays awake during a batch. Cancellation preserves completed tracks. No persistent background service or resume yet.
- Hardware QA: finish the currently active 0.2.0 batch before upgrading. Verify the 720×720 display, Plex multi-select, local source, retained settings, cancellation, duplicate handling and actual GTA playback. Do not uninstall PPSSPP. CI debug signing may require reinstalling RotateRadio only; app-private preferences would then be lost.


## 0.3.1 destination verification
Requires a matching normal in-game save containing PARAM.SFO for each selected target before writing any tracks. Select the actual PPSSPP memory stick folder (see PPSSPP Settings > System > PSP Memory Stick > Show Memory Stick folder). Setup > Inspect installed tracks shows provider, actual SAVEDATA document ID, matching save and .gta filenames/readability without writing files. Every newly installed track is re-listed and SHA-256 checked after the final rename. Successful storage verification does not guarantee playback. A copied save in an unused PSP directory can still pass preflight; compare against PPSSPP's actual location. No automatic migration or deletion of previous music. If final verification fails, inspect the folder; a renamed file may remain. Finish existing conversions before updating.


## 0.3.2 SD auto discovery
Setup > Find PPSSPP automatically scans persisted read/write external storage directory grants, including nested PSP/PSP/SAVEDATA. Grant SD card / folder access opens the Android picker on a removable mounted volume when available; select an allowed PSP/PPSSPP parent directory (not necessarily the SD root, restricted by Android). Search is bounded to 250 directories and five levels, skips common unrelated folders, and requires matching GTA PARAM.SFO. If a unique fully searched candidate is found, remember its tree permission and exact SAVEDATA document ID separately; ambiguous or incomplete searches require user selection. First launch with no destination scans previous grants. Existing destinations are preserved until user requests discovery. This cannot determine PPSSPP's private active preference, so compare the detected path against PPSSPP if playback fails. No broad all-files permission or storage migration. Test multiple folders, revoked grant, removable media, nested PSP/PSP, and incorrect target before hardware acceptance.
