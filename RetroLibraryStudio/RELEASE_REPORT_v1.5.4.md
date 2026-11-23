# v1.5.4 Windows Source Beta — 2026-11-23

- Added selected-result automatic artwork preview in existing Search for Cover dialog.
- Added styled right-click game context menu in cover gallery **and file list**.
- Existing PS1 CUE/BIN and safe standalone IMG converted by MAME CHDman, confirmed by second verify, then original tracks moved from current PSX folder to an adjacent recovery folder outside virtual card. No deletion.
- CloneCD CCD/IMG/SUB and ambiguous IMG are blocked rather than converted without metadata.
- Existing CHD + original CUE is reverified; old sources can be tidied without recompression.
- Local test suite: **240 passed / 15 skipped**. Main new regression tests in `tests/test_v154_organizer.py`.
- Windows source launch is via `Start_Retro_Library_Studio.bat`. No prebuilt signed executable. Actual Qt GUI, live artwork server, true CHDman binary and Synology SMB user acceptance **pending**.

Known user screenshot baseline v1.5.3: Clock Tower BIN/CUE 118.0 MB and cover retrieved from Libretro. The previous conversion checkbox did not retroactively convert the already imported Clock Tower set.
