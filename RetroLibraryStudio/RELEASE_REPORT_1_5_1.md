# v1.5.1 release verification report · 2026-11-23

**Source published** in GitHub under `RetroLibraryStudio/`. This is a **source beta**, not a hardware-verified release.

## Main changes
- Automatic PS1 CUE/BIN import through CHDman createcd and verification, independent CHD per game disc, M3U only for distinct multi-disc sets, artwork lookup, and unified visible progress.
- Correct complete logical size for legacy CUE/BIN games; safer Windows ZIP companion path normalization and regression test.
- Original source files, existing NAS files and user artwork not deleted or silently overwritten.

## Evidence
- Windows GitHub Actions **241 passed**; Linux **240 passed, 1 skipped**: [successful CI run](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45138220982).
- Local prepublication source on Linux **225 passed, 15 skipped** without Qt dependencies.
- CHDman conversion in automated tests is mocked; **actual CHDman and the user's Clock Tower disc have not been tested on Windows in this version**.
- Previous Windows v1.4.4 user acceptance: 6/6 copied and verified, repeated 0 new + 6 SHA-256 verified, successful NAS import Stop and APK staging. This is prior-version evidence, **not a v1.5.1 acceptance claim**.

## Release gate
Before calling v1.5.1 ready for the RG Rotate: real Windows Clock Tower CUE+two-BIN → one verified CHD, multi-disc M3U emulator test, automatic artwork fallback, NAS safe Stop, actual card copy and verified Android/Cocoon launch.

See `WINDOWS_TEST_CHECKLIST.md` and repository `docs/VERIFICATION_MATRIX.md`.
