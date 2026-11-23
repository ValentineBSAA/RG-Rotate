# Retro Library Studio v1.5.8 Windows source beta

**Candidate date:** 2026-11-23. **Source CI:** [GitHub Actions 45162684438](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45162684438) passed **289 tests Windows** and **288 tests Linux + 1 skip**. Local extract with PySide6 unavailable passed **266 tests, 25 skipped**.

## New functionality
- Complete PS1 game-folder import, verified per-disc CHDs in one game title directory
- Ordered M3U, safe incremental playlist extension, one gallery cover tile with N DISCS badge
- Existing disc-numbered CHDs verified and organized without recompression
- Strict CUE track integrity, no automatic guesses, no source deletion
- Final Fantasy VII/Final Fantasy VIII separate titles; Resident Evil 2 Leon/Claire disc roles recognized when editions match

## Verification boundary
This suite uses mocked CHDman samples and headless PySide6 tests. It **does not prove** a real Windows 11/Synology import from user discs, live CHDman on a multi-disc game, Cocoon scraping, actual RG Rotate gameplay or disc switching. Use [the new acceptance checklist](../docs/MULTIDISC_ACCEPTANCE.md) and report real outcomes before closing issue #2.

## First user test
Extract to **new folder**; launch `RetroLibraryStudio/Start_Retro_Library_Studio.bat` and keep previous working install. Under **Add games**, choose **Import complete PS1 game folder…** with a disposable complete original Resident Evil 2 (USA) two-disc CUE/BIN collection. Expect two actual verified CHDs and one M3U under a common parent folder; one tile with 2 DISCS and one cover. Do not run old batch-delete workflow as part of this test.
