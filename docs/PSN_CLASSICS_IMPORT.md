# v1.6.1 · PS1 Classics EBOOT/PBP + 7Z acceptance

**User evidence (2026-11-23):** Windows Explorer inside `Final Fantasy VII (English)(PSN)/NPEF00069` shows `EBOOT.PBP`, `KEYS.BIN` and `DOCUMENT.DAT`. This is a PlayStation Network PSOne Classics package, **not** three raw PS1 discs and **not** a PSP ISO. Number of physical PS1 discs cannot be established from a screenshot alone. The standard original Final Fantasy VII has three discs.

## Conversion workflow

1. Existing **Add game files** and **Add folder** read `.zip`/`.7z` into guarded, disposable **local** Windows temporary storage, with no source archive modification, 32 GB limit and no nested archive unpacking.
2. Recognize PSOne Classics by the PBP's **PSISOIMG/PSTITLEIMG** PSAR signature; `KEYS.BIN` is **key material**, and `DOCUMENT.DAT` is an electronic manual. They must never be treated as a disc or sent to CHDman.
3. When a PS1 Classics package is detected, request the external **PSXtract** tool installed under `Documents/Retro Library Studio/WindowsTools/psxtract/psxtract.exe`. CHDman itself **cannot** reverse a PSN EBOOT. No program will manufacture keys, download games or copy the key/material to the virtual microSD.
4. PSXtract generates temporary CUE/BIN discs; each CUE must pass existing completeness checks, and explicit disc numbering must be unique/consecutive (1..N). If the actual order cannot be proven, stop with an actionable error rather than guessing.
5. Each valid disc goes through **existing CHDman createcd + verify** then original hashed copy workflow, into `ROMs/psx/Final Fantasy VII/`, with `Final Fantasy VII.m3u` and one artwork tile. All original EBOOT/KEYS/DOCUMENT/7z files remain untouched.
6. Multi-disc **M3U emulator switching** and extraction of a real encrypted FFVII package still require real Windows and RG Rotate checks. Synthetic PSXtract/CHDman tests **do not** validate actual PSN decryption.

## Optional extractor

Upstream project: https://github.com/has207/psxtract-2; release page: https://github.com/has207/psxtract-2/releases/tag/v3.0. The package is a third-party helper. Review its source/trustworthiness and install it manually into the WindowsTools/psxtract directory; the app should show a clear dependency error if absent. PSXtract is not an official Sony tool. It can fail for supported, encrypted, damaged, or incomplete packages.

## Acceptance

- [ ] P161-01 Extract a real `.7z` containing three regular PS1 CUE/BIN discs: 3 verified CHDs, one game M3U and artwork; archive unchanged.
- [ ] P161-02 Confirm user's `NPEF00069/EBOOT.PBP` header is a recognized PS1 Classic without disclosing or uploading user keys.
- [ ] P161-03 If PSXtract is missing, show clear friendly error; no fake PSP entry or partial CHD.
- [ ] P161-04 Install trusted PSXtract helper, confirm it can extract real user's PS1 Classics EBOOT. Validate every CUE + track; failures are reported.
- [ ] P161-05 Final Fantasy VII: 3 distinct CHDs, M3U order correct, one cover with `3 DISCS` badge (if 3 discs actually extract).
- [ ] P161-06 Replay same import: no duplicate content, no overwrites and no loss of source data. Missing or ambiguous numbers refuse unsafe playlist.
- [ ] P161-07 Real RG Rotate launches PS1 M3U and switches discs/saves correctly.
- [ ] P161-08 Existing Resident Evil 2 collection / Clock Tower / PSP games, NAS virtual card, 512 GB/planned exFAT, artwork and CompanionData remain unchanged.
