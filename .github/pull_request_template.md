## What changed?
<!-- Explain what was changed and why, linking the GitHub issue. -->

## Behavior and data safety
- [ ] No change silently deletes, overwrites, reformats, or moves ROMs, BIOS, saves or user artwork.
- [ ] NAS work remains cancellable / GUI-responsive; incomplete CHDs and .retro-part files never show as playable.
- [ ] M3U is generated only for **multi-disc** titles; each disc gets its own CHD.
- [ ] New game import uses the **single visible progress workflow** and shows complete game size, not just CUE size.
- [ ] GUI actions remain discoverable at **125% display scale**.

## Evidence
- [ ] Tests run locally: environment, command, pass/fail count included.
- [ ] Windows/Synology acceptance separately recorded if performed.
- [ ] Real RG Rotate/microSD acceptance separately recorded if performed.
- [ ] I have **not** called untested Windows/hardware behavior complete.

## Roadmap and handoff
- [ ] Updated `docs/ROADMAP.md`.
- [ ] Updated `docs/PROJECT_HANDOFF.md`.
- [ ] Updated `docs/VERIFICATION_MATRIX.md`.
- [ ] Updated `RetroLibraryStudio/CHANGELOG.md` and version if user-facing.
- [ ] Updated README/test checklist when workflow changed.
