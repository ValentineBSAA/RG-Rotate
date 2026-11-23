# v1.6.4 Beta: Crash Bandicoot™ / CHDman Unicode path fix

## Real Windows 11 evidence (2026-11-23)
During a **single** v1.6.3 PSN PlayStation Classics EBOOT import, the user observed a progress bar and correct **Crash Bandicoot™** game title, followed by:

> Crash Bandicoot™ (Disc 1).cue: Converting PS1 disc to CHD failed (exit 1)...
> Error parsing input file (...\\rgl-psn-extract-...\\Crash Bandicoot™ (Disc 1).cue: No such file or directory)

The result reported **Added 0 file(s), found 0 already present**. No verified Crash Bandicoot CHD was demonstrated, so a duplicate reimport cannot be considered tested. This is a real Windows acceptance failure, not a pass.

## Probable root cause
The importer explicitly renames a temporary, otherwise valid PSXtract CUE from a generic disc name to the PBP's correctly identified Unicode game title **before launching the Windows CHDman executable**. Some Windows CHDman builds use filesystem arguments in a legacy code page and fail to open filenames with symbols such as U+2122 (™). A valid CUE can pass Python's inspect_cue and still cause CHDman to report "no such file". The exact CHDman limitation is suspected from this log, not independently proven on the user's machine.

## Fix
- Add `ps1_chd_bridge.ascii_psn_cue` **only** for disposable PSN extraction. Create an ASCII-only temporary CUE alias in the same local directory so all relative BIN track references remain valid.
- If a track filename is itself non-ASCII, make an NTFS hardlink alias and rewrite only the temporary CUE's FILE reference, without copying gigabytes of track data. All aliases are removed in finally blocks, even on cancellation/failure.
- CHDman receives the ASCII alias, writes to its existing local temporary ASCII output directory, and independently verifies the CHD. The app publishes the verified CHD under the true Unicode title, e.g. `ROMs/psx/Crash Bandicoot™/Crash Bandicoot™ (Disc 1).chd`, retaining artwork and title identification.
- No files in the original EBOOT/KEYS.BIN/DOCUMENT.DAT, original CUE, external NAS source folders or prior incomplete/anonymous library entries are modified.
- If the local TEMP directory itself contains characters incompatible with CHDman, fail with a clear explanation rather than silently modifying files.
- Existing direct hand-picked CUE/BIN import remains unchanged. No Unicode aliases are written into the user's own source library.

## Acceptance
- [ ] GitHub Windows and Linux synthetic regression tests pass on exact v1.6.4 SHA.
- [ ] Package ZIP passes manifest and CRC check.
- [ ] Windows 11 real Crash Bandicoot™ EBOOT: PSXtract, CUE inspection, CHDman conversion, CHDman verify, final named CHD in correct game folder.
- [ ] My Games shows one Crash Bandicoot™ tile with correct title and usable **Open game folder**.
- [ ] Repeat exact same EBOOT. Verify deduplication before extraction with **0 new files**, not the existing failure-state zero.
- [ ] Test Stop task during an active disposable import; no second game starts and app unlocks only after worker exits.
- [ ] Verify old generic PS1/Disc 1.chd output remains untouched pending manual identity inspection.
- [ ] Only after single-game and Stop verification, run a small multi-game PSN batch.

CI uses synthetic fixtures; it cannot validate the actual installed Windows CHDman binary, SMB behavior, or the RG Rotate hardware. Real Windows verification is required.
