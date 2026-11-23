# Source publication and continuing development
_Last updated 2026-11-23._

## Publication status

**COMPLETE for text source:** The original v1.5.1 Python modules, Windows launch scripts, requirements, README/changelog, tool setup code, and test suite are now committed as **64 UTF-8 files** under [RetroLibraryStudio/](../RetroLibraryStudio/) in GitHub commit [b458028](https://github.com/ValentineBSAA/RG-Rotate/commit/b458028436426d859c7847da2fb8129b3b556661).

The source is browsable and cloneable, so **Codex and future chats can work against GitHub directly**. The optional generated *Resident Evil: Gore Edition* example cover (PNG) was excluded from the public source upload. Commercial ROMs, BIOS, downloaded APKs, saves, settings and personal NAS credentials were not pushed.

### Source archive provenance
- Full ChatGPT build ZIP: `RetroLibraryStudio_v1.5.1_Automatic_CHD_M3U_Artwork_Windows_Source.zip`.
- Original ZIP SHA-256: `abc1fb3496826357e27aebf463c26453d381b6fba3f275f6bffba70e7e464001`
- Original ZIP: 3,074,882 bytes and 65 archive members. This includes the optional example cover.
- GitHub code is a text-source-only equivalent, without that optional cover. Do **not** expect its ZIP checksum to match the original binary archive.
- `python -m pytest -q --disable-warnings --maxfail=1` run on Linux: **225 passed, 15 skipped**.
- [GitHub Actions v1.5.1 CI](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45138220982) passed: **241 Windows tests; 240 Linux tests with 1 skip**. These use mocked CHDman conversions.
- v1.5.1 **real Windows CHDman / Synology NAS / physical RG Rotate acceptance remains pending**.

## Clone on Windows

1. Clone `https://github.com/ValentineBSAA/RG-Rotate.git` in GitHub Desktop.
2. Open the `RetroLibraryStudio` folder.
3. Run `Start_Retro_Library_Studio.bat` to install required Python packages and launch, or `RUN_TESTS_Windows.bat` to test.
4. **Do not overwrite the existing working app folder or virtual NAS card.** Use a separate application checkout and point it to the already selected NAS workspace only after confirming the path.
5. Verify actual CHDman installation and conversion on Windows before importing an entire PS1 library.

## Required update process

1. Start from **GitHub main**, reading README → PROJECT_HANDOFF → ROADMAP → VERIFICATION_MATRIX.
2. Make modifications via an issue/branch/PR or a clearly described main commit.
3. Run tests and document which passed on Linux, Windows with the Synology NAS, or actual hardware.
4. Update **ROADMAP.md + PROJECT_HANDOFF.md + VERIFICATION_MATRIX.md + app CHANGELOG.md** with the code change. Never leave the new features untracked.
5. Test the **full ZIP distribution** separately from the source tree if packaging a release.
6. Do not check “Complete” for anything not verified at its stated acceptance level.

“Continuously update the roadmap” means updating it whenever development or tests change the project. This is not a background service that commits on its own between conversations.

## License and user files

The repository is public. No license has yet been selected explicitly; do not assume the code is open-source licensed simply because it is visible. Discuss and add an appropriate LICENSE before inviting redistribution. Do not commit games, copyrighted BIOS, downloaded proprietary APKs, keys, personal passwords or device-specific private files. Keep large user assets on their own storage.

## v1.5.3 build and source update

- GitHub source updated with clickable format badges and official Libretro-GitHub artwork fallback. New test file: `RetroLibraryStudio/tests/test_v153_badges_artwork.py`.
- Local ZIP: `RetroLibraryStudio_v1.5.3_Windows_Test_Beta.zip`, **3,088,444 bytes**, SHA-256 `d33da5e5c182f63c8baf99a988fe492fdaf3ea1d742315a861ce30542ecf7312`. ZIP self-check passed. Clean extracted local test: **230 passed / 15 skipped**.
- Source/package is **not an independently tested Windows binary EXE**; install dependencies via launcher; test against existing NAS workspace in separate folder.

## v1.5.4 publication

- Source files and tests published to main [b0c02214](https://github.com/ValentineBSAA/RG-Rotate/commit/b0c02214917e0356d6c00645a40b7ef26090ac30).
- Windows test ZIP: `RetroLibraryStudio_v1.5.4_Windows_Test_Beta.zip`, **3,094,825 bytes**, SHA-256 `86687bdf34c69a33cd93733311b36b2c86f6ca9ee81a2f82bd853caf99d4cc15`.
- Local tests: 240 passed, 15 skipped. Physical Windows CHDman and user NAS acceptance remains pending.

- **CI for v1.5.4 source:** [run 45144304702](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45144304702) succeeded, Windows 255 pass; Linux 254 pass / 1 skip. Real CHDman and original-image compatibility pending.


## v1.5.5 source sync pending (2026-11-23)

**A newer local source ZIP has been prepared and verified:** `RetroLibraryStudio_v1.5.5_Windows_Test_Beta.zip` (73 members, SHA-256 `e1a00b4f0147353ffdc37f47bb49e69a87afd5bfc23a9839968232834d441350`). The zip includes the runnable v1.5.5 source, Windows batch launchers, tests, README and release report. Local Linux tests: **248 passed, 16 skipped**.

**Important:** The repository's `RetroLibraryStudio/` code has **not yet been fully synchronized to v1.5.5**. To ensure GitHub is an authoritative code handoff, clone the repo with GitHub Desktop, replace the `RetroLibraryStudio/` folder contents with the ZIP's extracted source, review the staged changes and push. Do not copy `Example_Covers` if licensing is uncertain; never upload the user's ROMs, BIOS, APKs, saves, settings or NAS addresses. The next chat should check whether this upload happened before working from GitHub code.

Until sync is confirmed, do not claim GitHub CI checks validate v1.5.5. The last verified published source remains v1.5.4.
