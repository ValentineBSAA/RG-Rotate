# RG Rotate / Retro Library Studio · Full regression & hardware test checklist

## H · v1.5.8 new PS1 multi-disc collection gate

Complete [new M01–M10 acceptance checklist](MULTIDISC_ACCEPTANCE.md) before claiming the one-game grouping feature is Windows-verified: folder import; real CHDman each CUE; RE2 Disc1+Disc2 one CHD per disc, M3U and cover tile; FFVII/FFVIII separate; Disc3 incremental; old custom playlists preserved; corrupted/missing tracks refused; 125% UI and Synology NAS protection; actual Cocoon disc switching later.

- [ ] H01: Real Windows folder import and two-disc Resident Evil 2 CHDman conversion/verification.
- [ ] H02: One My Games tile and title/cover with **2 DISCS** badge, File List retains disc detail.
- [ ] H03: Incremental extra discs, album edition separation, no playlist corruption.
- [ ] H04: NAS originals, prior recovery backups, CompanionData remain untouched.
- [ ] H05: Actual RG Rotate Cocoon M3U disc swap when hardware arrives.

_Last organized: 2026-11-23. Current source: **v1.5.7 merged into main** (PR #11); no dedicated Windows source ZIP/EXE packaged yet. **Source CI passed: [run 45155293003](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45155293003), 279 Windows passed; 278 Linux passed, 1 skipped.** Do not treat source CI as actual user Windows, Synology NAS or physical RG Rotate acceptance._

**Evidence key:** [x] = explicit user-observed real Windows result (with version) or other stated tier; [ ] = outstanding acceptance. Tests below must be repeated when changing relevant code. Log app version, Windows scale, screenshots/error text, original/virtual/destination paths (redacted if shared), file size/hash and actual outcome.

## A. Console shelves · new v1.5.7 UI (all need Windows confirmation)
- [ ] A01: Extract/run candidate **in a new program folder**, leaving the known-good install and NAS virtual card intact. Confirm v1.5.7 in window title and no startup crash.
- [ ] A02: With All systems selected, game library shows **full-width, visually distinct system headers** and cover tiles under PSP / PS1 / DS / GBA / PS2 / GameCube wherever games exist.
- [ ] A03: Scrollable top console pills show count of **logical games**, not individual BIN tracks, artwork files or double-counted PS1 discs; console sections reflect actual library inventory.
- [ ] A04: Click PSP, PS1, Nintendo DS, PS2, GameCube and All. The **dropdown, tiles, counts and file list** stay synchronized; clicking an empty console shows zero matches, not another console's games.
- [ ] A05: Search title while All is selected and while filtered to a system; counts and headers update without stale tiles; clear search restores all games.
- [ ] A06: Cover gallery scrolls naturally; 48-game Show More paging displays further sections and titles exactly once. Existing favorites/covers/titles remain unchanged.
- [ ] A07: Switch to File list and back, right-click a tile and a table row, open format details, update title, preview/change cover, navigate to folder.
- [ ] A08: Test Windows display scaling at **100, 110, 125, 140, 150%**, including 900×620 minimum and maximized. No clipped controls, overlaps, unusable horizontal scroll, unreadable tab text or wrong section width.
- [ ] A09: Close/relaunch: chosen gallery/file mode, screen size/position, existing library and artwork survive; no NAS scan or network operation starts merely from clicking a shelf.
- [ ] A10: Import one disposable PS2 ISO by explicitly choosing PS2, one GameCube GCM by format, and one ambiguous ISO choosing GameCube; verify separate `ROMs/ps2` and `ROMs/gc` library entries with **no compatibility promise**. Existing PS1 .cue and PSP .cso routing unchanged.
- [ ] A11: Confirm test/reference metadata explains **PS2/GameCube are experimental on the T618 RG Rotate**; mere import/cover art is not a launch or FPS pass.

## B. Windows 11 / Synology NAS safety
- [x] B01: Earlier v1.4.x selected and remembered user-chosen Synology virtual-card workspace without allocating 512 GB.
- [x] B02: Earlier v1.2.3+ real NAS Stop operation returned control, no need to kill the app.
- [x] B03: Earlier Windows imported Resident Evil Gore Edition and manual local cover; own original source was preserved.
- [x] B04: Earlier Windows Library Check completed with zero broken references in small sample.
- [ ] B05: Fresh **v1.5.7** launch remembers correct NAS folder and does not silently scan Downloads, probe offline network storage or reset the workspace.
- [ ] B06: Small ordinary import reaches Ready; after Stop no incomplete .chd/ROM is published as complete; cancel, revisit another page, and retry normally.
- [ ] B07: Disconnect/share temporarily unavailable: error/status is readable, Stop remains responsive, no Qt freeze, no fake completed import.
- [ ] B08: ZIP/7Z import and source-file groupings; malformed archive, path traversal, duplicate filename, corrupt/truncated file, unicode/long names are handled without overwriting originals.
- [ ] B09: Library Check after new work: CHD/CUE/M3U references, duplicate groups, no stale completed progress or duplicate game tiles.

## C. PS1 lossless conversion and backups
- [x] C01: User-verified v1.5.4 Clock Tower: The First Fear CHDman conversion/verification: **55.4 MB CHD**, cover and CHD badge.
- [x] C02: User-verified v1.5.4 Resident Evil Gore Edition CHDman conversion/verification: **311.9 MB CHD**, cover and badge.
- [ ] C03: Preserve actual converted CHDs, original NAS source copies, artwork, prior recovery directories and existing saves when upgrading.
- [ ] C04: On **disposable virtual-card copies only**, v1.5.5+ batch two complete CUE/BIN games; one stage/progress workflow (Inspect → Convert → Verify → Finalize), responsive Stop, CHDman verifies each.
- [ ] C05: Batch `Keep recovery backups`: source tracks moved to a **separate recovery folder outside virtual card**, visible through Open conversion backups, and not silently erased.
- [ ] C06: Batch `Remove verified working copies`: second confirmation; only in-card **working** BIN/CUE/IMG files deleted *after* CHDman verify + recheck. Original NAS archive and prior backup folders untouched. Confirm independently before using on any real archive.
- [ ] C07: Known standalone raw IMG sample converts; ambiguous IMG, CloneCD CCD/IMG/SUB and incomplete descriptor refused safely.
- [ ] C08: Missing/renamed BIN, shared CUE tracks, CHDman error, mid-conversion Stop and disconnection all preserve recoverable originals and do not advertise partial CHD as playable.
- [ ] C09: CHD remains **lossless** at file-data level; inspect game in emulator for audio, video, FMV, subtitles, loading and saves, because CHDman verify alone is not gameplay confirmation.
- [ ] C10: Genuine **two-disc** PS1 title: two individually verified CHDs + ordered M3U, a single logical gallery tile, and successful in-emulator disc switch (not one merged disc).
- [ ] C11: Compare NAS before/after used bytes to confirm moving to an adjacent recovery folder **does not free NAS space**; never auto-purge historical backups.

## D. Artwork and display polish
- [x] D01: v1.5.3 Windows: online fallback returned Clock Tower cover choices; user selected and applied a cover.
- [x] D02: v1.5.4 Windows: verified CHD tiles kept their approved covers.
- [ ] D03: v1.5.5+ online selection previews at 125%, auto-preview before confirmation, clean aspect-fit after resizing, no clipping or silent cover swap.
- [ ] D04: Offline/provider-down and edition-specific title cases retain **Search / Choose from PC**; existing cover never overwritten automatically.
- [ ] D05: Cover preview, custom titles and file format badges persist across console filter, view change, refresh and app restart.
- [ ] D06: Cover thumbnails arrive under virtual card Media/BoxArt; Cocoon's Android library independently displays correct covers after its own scan.

## E. Software setup / transfer
- [x] E01: Earlier Windows setup displayed staged `cocon-311.apk`, PPSSPP and RetroArch packages; this was **not** Android installation.
- [x] E02: Prior NAS→Windows practice transfer: **6/6 SHA-256** verified, 1.21 GB; repeat: 0 new copied, 6 identical, 6/6 verified.
- [ ] E03: Run live PPSSPP/RetroArch authorized downloads; record source, hash and successful APK staging. `cocon-311.apk` stays labeled publisher unverified.
- [ ] E04: Real Windows installed `chdman.exe` help/version and verified known-disc workflow; ADB `adb version` works; clearly identify failed tool, retry/skip without locking GUI.
- [ ] E05: v1.5.6+ 512 GB nominal capacity meter correct: 512,000,000,000 bytes ≈476.84 GiB before overhead; staged bytes + 8 GiB AI allowance + 8 GiB free reserve, without writing a fake 512 GB file.
- [ ] E06: Meter/Exact sizes… remains readable at 125% and accurate after adding/deleting *disposable* files, scanning again and changing location; no blocking NAS stat in paint path.
- [ ] E07: Practice preflight/preview/copy/repeat SHA-256 verification/Stop/resume. No stale 100% or misleading size-only verification; no silent overwrite.
- [ ] E08: Destination selector retains practice vs physical-card mode between launches. Unplug/choose wrong destination should refuse unsafe transfer rather than guessing.
- [ ] E09: Preserve `CompanionData`, Cocoon metadata, Media, BIOS, saves and unrelated files during any import, verified cleanup and incremental transfer.

## F. Physical 512 GB microSD and first RG Rotate boot (blocked until hardware available)
- [ ] F01: Inspect actual card manufacturer/size, mounted drive, filesystem, Windows formatted bytes and free bytes. No automatic formatting.
- [ ] F02: Verify actual-card preflight budget uses measured capacity + existing files + transfer bytes and preserves 8 GiB free; AI allowance remains a budget, not an allocated partition/file.
- [ ] F03: Copy selected NAS game set with throughput/ETA and SHA-256, repeat 0-new-files verification, safely eject/reinsert, verify again.
- [ ] F04: Internal 32 GB remains Android OS/apps; 512 GB microSD holds games, artwork and CompanionData persistent memory without overwriting existing data.
- [ ] F05: Install/authorize Cocoon, PPSSPP, selected PS1 emulator, DS emulator/RetroArch with user's consent; staging APK alone is not installed.
- [ ] F06: Configure ROM roots, scoped storage permissions, emulator associations, Cocoon launcher/default Home and reliable return-to-Home.
- [ ] F07: Test closed/open display layouts, 720×720 touchscreen, cover legibility, scroll, button navigation, volume/sleep/resume, long-play stability.
- [ ] F08: PS1 CHD launch and gameplay (Clock Tower, Resident Evil): video/audio/FMV, controller, save/load, performance, titles/box art; then test multi-disc M3U swap.
- [ ] F09: PSP PPSSPP: SOCOM Tactical Strike, Syphon Filter, Gran Turismo, Pursuit Force Extreme Justice; proper input mapping, analog limitations, FPS/audio/save states.
- [ ] F10: Nintendo DS Yu-Gi-Oh! GX Spirit Caller: touch targeting, single-screen top/bottom hotkey switch, legible display and save.
- [ ] F11: GBA/older-system sample launch, save/load and return-to-Cocoon; verify titles and controls.
- [ ] F12: PS2 and GameCube: **individual optional experiments only**, document which emulator, game, frame rate, input/analog limits and whether playable. No blanket compatibility assertion.
- [ ] F13: Test built-in Anbernic AI versus custom gaming companion first: speech, game guidance, screenshots, persistence, CPU/RAM/FPS/battery, offline/online needs and permissions.
- [ ] F14: If custom companion needed, store persistent AI memory on microSD CompanionData, temporary screenshots only, test backup/restore and never let cleanup delete memories.

## Exit criteria before calling a public stable build
- [x] G01: **Merged main source CI passed**: [run 45155602315](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45155602315), **279 Windows / 278 Linux passed, 1 skipped**. This does not imply real Windows/NAS acceptance.
- [ ] G02: v1.5.7 user Windows screenshots show new console-shelf visual and scale/filter acceptance.
- [ ] G03: v1.5.5+ destructive batch safety verified on disposable NAS test copies (if enabled for release).
- [ ] G04: Actual card and representative handheld game launches pass before claiming RG Rotate-ready.
- [ ] G05: Roadmap, handoff, verification matrix, release notes reflect the exact evidence tier.

**Testing sequence:** first **A + B05 + E05/E06** (visual-only, safe), then **D**, then **C with disposable copies**, then **E transfers**, then **F after device arrives**. Do not risk personal originals to validate a new visual feature.

## I · v1.5.9 virtual SDXC/exFAT format profile + disc details

- [ ] I01: At 125% verify existing nominal 512 GB meter and second virtual exFAT meter; no overlap, correct labels and combined budget.
- [ ] I02: Open simulated exFAT details and Exact sizes; identify model vs real measured byte counts and original 8 GiB companion + 8 GiB reserve.
- [ ] I03: Resident Evil 2 M3U renders exactly one cover tile with **2 DISCS**, popup names playlist + both CHDs, File List still includes all 3 files.
- [ ] I04: Old NAS workspace, covers, sources, M3U, backups, saves and CompanionData all unchanged; no disk image, hidden 512 GB file, reformat or movement.
- [ ] I05: Connect actual 512 GB card; inspect filesystem and Windows measured formatted capacity/free bytes. Keep the measured values authoritative. Do not assume Windows automatically reformats it.
- [ ] I06: Verify copy preflight, 8 GiB reserve, FAT32 >4 GiB check and SHA-256 verification on actual removable card; test RG Rotate emulator only afterward.

[Detailed v1.5.9 acceptance](VIRTUAL_EXFAT_PLAN.md).
