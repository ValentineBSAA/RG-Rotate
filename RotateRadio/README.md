# RotateRadio 0.1.0 — hardware alpha
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
