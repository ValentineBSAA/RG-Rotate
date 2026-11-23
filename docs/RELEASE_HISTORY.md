# Release history / regression ledger

This is a **historical summary**, not a claim that all archived builds are on GitHub. Source archives were produced through ChatGPT and tested on the user's Windows PC at various milestones. Latest packaged Windows source beta: **v1.5.8** with one-tile PS1 multi-disc collections; v1.5.7 console shelves are included. Real Windows multi-disc and RG Rotate gameplay still require testing. Real-device and batch cleanup acceptance remain pending.

| Version | Major milestone or repair | State |
| --- | --- | --- |
| 0.1.0 | Virtual 512 GB card concept, PS1/PSP folders, ZIP/7Z import, non-destructive copy, Windows PySide6 | Prototype |
| 1.0.0 | Combined software setup, importer, capacity reserve, card copy and SHA-256 checks | Source beta |
| 1.1.0 | Beginner-guided UI, big import actions, 125% scale, window persistence | Initial GUI had launch dependency problems |
| 1.1.1 | Startup/bootstrap repair, PySide6 dependency check and logging | User confirmed GUI launches |
| 1.1.2–1.1.3 | APK library and Ninite-like batch download workflow | Iterative development |
| 1.1.4 | Visible task monitor, no hidden auto-Downloads scan, CHDman extraction stages | Source beta |
| 1.1.5 | Choose virtual workspace on Start page; safe copy/migration, no silent default | User confirmed folder structure/location |
| 1.2.0 | NAS location and storage planning, CHD/cover tools, actual-vs-virtual capacity | NAS capacity lookup initially stalled |
| 1.2.1 | Optional/time-limited NAS free-space check | User confirmed responsive |
| 1.2.2 | Read-only NAS scans in cancellable subprocesses | Import Stop still stuck |
| 1.2.3 | NAS game imports isolated from GUI; atomic temp file and safe Stop | **User confirmed Stop and import work** |
| 1.3.0 | Cover gallery, local thumbnail cache, list/grid view | User confirmed cover tile works |
| 1.3.1 | Manually search, preview and apply a game cover | Source beta |
| 1.4.0 | Day-one readiness, isolated transfer and better verification feedback | Source beta |
| 1.4.1 | APK importer restored to a real isolated action, completion feedback | **User verified Cocoon APK import** |
| 1.4.2 | Recognize user-imported `cocon-311.apk` as “my APK ready” | Automated; real GUI retest incomplete |
| 1.4.3 | Differentiate preview and complete transfer, incremental verification | Practice-mode lost on restart |
| 1.4.4 | Remember Practice/Real Card destination type, safe preflight | **User verified 6-file repeated SHA-256 check, 0 recopy** |
| 1.5.0 | Codex redesign, improved disc checks/converter/manual M3U, user customization, front-end layout | Source inspected; real Clock Tower library CUE size reported incorrectly |
| 1.5.8 | One parent folder/cover for verified per-disc PS1 CHDs, ordered M3U and later-disc updates | CI 289 Windows / 288 Linux + 1 skip; user Windows and handheld pending |
| 1.5.7 | Visual console shelves/count tabs; PS2/GameCube folders | User verified filters, 125% UI, gallery/list, NAS and capacity meter; handheld pending |
| 1.5.6 | 512 GB virtual/real capacity meter; measured card preflight and 8 GiB budgets | CI 274 Windows/273 Linux + 1 skipped; actual Windows meter and real microSD pending |
| 1.5.5 | Batch CUE/IMG-to-CHD, verified-only virtual-card working-copy deletion or recovery backup choice, backup-folder navigation and artwork preview resizing | Source and tests published; CI passed 264 Windows / 263 Linux (1 skipped); real Windows batch acceptance pending |
| 1.5.4 | Artwork result auto-previews, polished right-click game menus, verified CHD conversion/tidy from CUE/BIN and safe IMG with off-card recovery backups | Linux 240/15 local; Windows CHDman and UI acceptance pending |
| 1.5.5 | Batch lossless CHD conversion, explicit verified working-copy cleanup, direct recovery-folder access, responsive artwork preview | Source beta, Linux 248/16; Windows batch test pending |
| 1.5.4 | User confirmed Clock Tower (55.4 MB) and Resident Evil Gore Edition (311.9 MB) CHDman verification + artwork preserved | Windows user-observed pass for individual conversion only |

| 1.5.5 | Batch CUE/IMG→CHD with verified-only virtual-card cleanup, source preservation, recovery folder navigation, and cover preview fit | **Local ZIP 248 passed / 16 skipped; Windows batch acceptance pending; GitHub source sync pending** |
| 1.5.3 | Clickable actual file-format badges (CHD / BIN-CUE / M3U etc), detailed format popup, Libretro artwork catalog GitHub fallback, resilient cover fetch | Source beta; Linux 230/15, Windows user acceptance pending |
| 1.5.2 | First Windows acceptance build incorporating v1.5.1 automatic PS1 pipeline and CI fixes | User screenshot: Clock Tower 118 MB; artwork search unavailable |
| 1.5.1 | Auto PS1 CUE/BIN → verified CHD → staged game; multi-disc M3U; combined game size and artwork in unified import task | **225 Linux passed / 15 skipped, Windows/live CHDman pending** |

## Avoid repeating the old problems

- **Don't hide crucial actions in Preferences**: choose the NAS virtual-card location first.
- **Don't fill an entire 512 GB image**: the disk budget is virtual and tracked dynamically.
- **Don't block GUI on SMB filesystem calls**: use bounded helpers, not direct synchronous network probes.
- **Don't rely on cancellation flags for blocked Windows I/O**: isolate and safely terminate read-only helpers; atomic temp files and cancellation-aware writers.
- **Don't treat SetupPackages APK as installed Android app**.
- **Don't report “Completed” merely after a transfer preview**.
- **Don't mix old result bars with new previews**.
- **Don't conflate a CUE descriptor with its complete BIN-track game footprint**.
- **Don't combine separate physical CD discs into one CHD**; one CHD per disc, M3U references them.
- **Don't replace edition-specific covers automatically** based on a loose match.
- **Don't claim automated tests equal the real-device acceptance test**.

## Next release criteria

v1.5.1 can be called Windows-accepted only after converting a real full CUE/BIN disc, generating and testing a multi-disc playlist, confirming one logical game in My Games with correct size, showing artwork, and completing the NAS practice copy workflow. Physical RG Rotate readiness is a separate gate.

Keep earlier v1.4.4 folder as a known-good fallback until these v1.5.1 Windows tests pass.
