# RG Rotate · Retro Library Studio

**Project home and development handoff** for the Anbernic RG Rotate (Android 12, 720×720, Unisoc T618, 3 GB RAM, 32 GB internal storage) and **Retro Library Studio**, a Windows 11 / PySide6 virtual-microSD preparation utility.

> **Current working milestone: v1.5.2 Windows PS1 Acceptance (source beta).** The **full text source and tests** are now published under [RetroLibraryStudio/](RetroLibraryStudio/). The optional generated Resident Evil cover image is not in GitHub. See [Source publication](docs/SOURCE_PUBLICATION.md).

## Project at a glance

- **Default Android frontend:** Cocoon Shell. Keep emulator selection, first-run permissions, and Android Home configuration as *on-device* tasks; staging APKs does not install them.
- **Primary systems:** PSP, PlayStation 1, Nintendo DS, Game Boy Advance; additional older systems as appropriate. PS2 and GameCube are **experimental**, not guaranteed on T618 or without analog sticks.
- **Windows virtual card:** User-chosen local directory or Synology NAS SMB/mapped drive. No 512 GB preallocation or sparse disk image; actual files consume real space only when added.
- **Card plan:** 512 GB marketed capacity (about 476.8 GiB before filesystem overhead); **8 GiB protected free-space headroom** plus **8 GiB budget for AI companion data**. Recalculate against the real card's formatted capacity. Android OS/apps primarily reside on 32 GB internal storage.
- **Import:** existing lawful game files, folders, ZIP and 7Z archives, PS1 CUE/BIN multi-track sets, CHD, and Android APK setup packages. Preserve originals, paths, metadata, save data, and NAS content.
- **Software setup:** Ninite-like official/authorized-source setup for Cocoon, PPSSPP, RetroArch, ADB Platform Tools and CHDman; clearly distinguish “APK staged” from “installed on Android.” Windows tools are **not** copied to the microSD as Android apps.
- **Copy and verification:** preview, practice folder or physical microSD, live speed/ETA, hash verification, incremental repeat transfers, cancellation/recovery and no silent overwrite.
- **UX:** Beginner-first **Add Games → Prepare Apps → Copy to Card**; adjustable 100–150% UI scale including 125%, saved window geometry, visible status, large cover-gallery and manual artwork search.

## Start here in a new conversation or Codex session

1. Read [Project Handoff](docs/PROJECT_HANDOFF.md) for the latest known state, decisions, paths and safety rules.
2. Read the **living [Roadmap](docs/ROADMAP.md)** for current priorities and stop conditions.
3. Read [Verification Matrix](docs/VERIFICATION_MATRIX.md) to avoid claiming an untested feature passed.
4. Read [Release History](docs/RELEASE_HISTORY.md) to understand why earlier regressions occurred.
5. Before changing code, obtain the actual source ZIP or the published source branch, run existing tests, keep the NAS workspace intact, then update **roadmap + handoff + tests + changelog in the same change**.

### Current PS1 first-game test

**Clock Tower: The First Fear (English patched)** has a CUE with two BIN tracks. The old importer staged all three, but **My Games displayed only the tiny ~226–228-byte CUE size**. v1.5.1 aims to convert complete CUE/BIN sets to a verified single CHD *before* publishing them in My Games, count the complete size, and generate an ordered M3U for multi-disc sets. This behavior is **code/test-verified only**, not Windows/real CHDman-verified.

## Important data/safety policies

- Never put commercial ROMs, proprietary BIOS, or keys in the public repository. Source code and documentation only. Do not bundle unlicensed games.
- Never rewrite source BIN/CUE tracks or delete ROMs on import. Broken or unsupported CUE files must report explicit errors, not publish an incomplete game.
- Never silently format a real card, delete user data, replace a conflicting file, or treat a size-only match as an integrity check.
- Keep actual device status separate from desktop preparation and backend unit-test results.
- A 512 GB profile is a **planning budget**, not a demand for 512 GB available on the Windows or NAS drive.

## Key documents

| Document | Purpose |
| --- | --- |
| [ROADMAP.md](docs/ROADMAP.md) | Living priorities, statuses, acceptance criteria |
| [PROJECT_HANDOFF.md](docs/PROJECT_HANDOFF.md) | Cross-chat project context and workflow |
| [VERIFICATION_MATRIX.md](docs/VERIFICATION_MATRIX.md) | Real PC passes vs simulated / pending |
| [RELEASE_HISTORY.md](docs/RELEASE_HISTORY.md) | Version milestones and regressions |
| [GAME_LIBRARY_PLAN.md](docs/GAME_LIBRARY_PLAN.md) | Systems, titles, controller cautions, Cocoon favorites |
| [SOURCE_PUBLICATION.md](docs/SOURCE_PUBLICATION.md) | How to add the ZIP's actual code and keep it current |

**Maintenance rule:** Every meaningful project change must update the roadmap status and tests; report whether it was unit-tested, Windows-tested, or RG Rotate-tested. No silent completion claims.
