# v1.6.2 · Live PS1 disc progress + duplicate checks for all consoles

## Real user observations (2026-11-23)
- Original v1.6.1 screenshot sequence: FinalFantasyVII(English)(PSN).7z entered the real Windows importer; unpacked into local temporary storage; PSXtract recognized multi-disc PBP; the console identified **Disc 1, 2, 3** (SCES Europe), reconstructed the tracks and printed successful conversion lines; user observed MD5 PASS; GUI subsequently showed **converting Disc 1 to CHD**.
- The user explicitly noted PSXtract progress was invisible without a debug terminal. **Final verification, 3 CHDs, M3U and handheld disc switching were not yet shown.**
- User's direct follow-up: "duplicate detection should work for all consoles not just PlayStation one".

## User-facing progress
- PSXtract stdout is drained in a bounded reader thread inside the isolated import worker. Raw console output is discarded, not written to user logs.
- Only recognized non-sensitive stages become progress messages: PS1 Classic recognized, Disc N identified, rebuilding game data, no separate CD audio tracks, Disc N reconstructed, MD5 status. No source keys, serials, file paths, hashes, offsets or raw stdout are emitted.
- The Windows activity footer displays a concise purple disc-status strip at 125% scaling; detected discs acquire an explicit state. CHD conversion progress continues through the existing friendly status line after extraction. Progress is **indeterminate** for PSXtract since no reliable percentage is provided, rather than a made-up number.
- Cancel still terminates helper and preserves original ZIP/7Z/PBP/KEYS/DOCUMENT files. Previously verified CHDs are not automatically removed.

## Shared duplicate protection
All platform directories listed in `core.SYSTEM_DIR` participate: **PS1, PSP, PS2, GBA, GB, GBC, NES, SNES, Genesis, Nintendo DS, Nintendo 64, Dreamcast, GameCube**.

1. For an incoming single-file game, scan **only its own destination console** for a game file of the same length. An exact SHA-256 content match is safely counted as *already present*, even if the game is renamed or repackaged in a different ZIP/7Z/folder. Cross-platform releases are NOT merged.
2. If no byte-equal match exists and an existing file on that console has the same normalized title but different bytes, do **not** automatically overwrite or merge; report **possible duplicate** and leave both the user's source and original library intact. Distinct region, language and revision tags are preserved, not silently stripped.
3. Archive payloads are inspected **after safe extraction but before publication**, preventing an ambiguous member from partially importing another game. No archive manifest is trusted as proof of identical content.
4. Single-file game checks intentionally exclude `.cue`, `.bin`, `.m3u`, `.gdi`, `.ccd` and track sidecars: duplicate audio/track bytes inside different discs are NOT standalone duplicate game evidence. Existing PS1 CHD/M3U safety checks remain.
5. Common generic names (`EBOOT.PBP`, `GAME.ISO`, `ROM`, `DISC`) are not trusted as title matches because unrelated games can share them. If the content is byte-identical the match still counts.
6. A finished PS1 Classics PBP conversion writes a small **EBOOT SHA-256 receipt** under `.retro-library/psn-sources`. Only after a verified M3U/CHD set exists may an exact EBOOT be skipped before PSXtract/CHDman run. The receipt stores **no source paths, KEYS.BIN data, PSN serial IDs, or personal information**, and lives outside the ROM scanner. A preexisting unproven same-title legacy collection is flagged for manual review instead of copied over.
7. Existing game files, artwork, ROM names, NAS source files and real microSD are not rewritten by the duplicate scanner. Fingerprinting may take time on large games over SMB; the importer remains isolated from the graphical thread.

## Multiple PS1 Classics ZIP/7Z/EBOOT packages
- A separate optional **Batch import PS1 Classics** action can scan a selected folder of ZIP/7Z/PBP packages. Each package has its own game job and numbered progress; one malformed EBOOT is reported without combining its disc files with another title.
- Standalone PBP sidecars KEYS.BIN and DOCUMENT.DAT stay in place; they are not separate games. Loose CUE/BIN sets remain grouped as a complete disc set rather than treated as individual archives.
- Batch summary includes imported, already present, and needs-attention counts with per-package statuses. No item is silently erased, and cancellation prevents starting the next package.
- Batch includes only PS1 package formats: the shared general game import still supports the other 12 console families.

## Acceptance on Windows 11 and RG Rotate
- [ ] V162-01 Launch new beta and repeat a PS1 Classic 3-disc test; confirm disc-by-disc live activity in the GUI without opening the debug console.
- [ ] V162-02 Import then re-import an identical PSP game, PS2 ISO, NDS game, GBA ROM and GameCube game from different folder or ZIP/7Z name. Only one file per console should remain.
- [ ] V162-03 Import same bytes as two different console selections, and confirm they remain **separate system libraries**.
- [ ] V162-04 Import same title with different bytes, or different region/revision; confirm no silent overwrite, clear review state for uncertain duplicates and no mistaken suppression of distinct editions.
- [ ] V162-05 Verify PS1 CUE/BIN tracks, RE2 M3U and CHDs, Final Fantasy VII disc order, and original PSN EBOOT + KEYS.BIN untouched.
- [ ] V162-06 Repeat a PSN EBOOT across differently named archives after the *first v1.6.2 verified import*. Confirm it skips conversion and does not generate a second game tile or extra .json game tile. Older v1.6.1 sets without receipts must report ambiguity instead of guessing.
- [ ] V162-07 Run Windows/Linux automated tests; verify the exact merged source, build ZIP integrity, and local clean-extract tests.
- [ ] V162-08 Real 512 GB microSD USB identity and first physical transfer, then PSP/PS1 actual launch and FFVII disc swapping remain separate hardware acceptance items.

## Constraints / limits
- Byte-equality proves only identical **files**, not that differently encoded ISO/CSO/CHD images are equivalent. Such files may require manual confirmation.
- An existing title with different contents might be a version/edition or an actual duplicate. We choose preservation over destructive guessing.
- Old PS1 collections lacking original EBOOT receipt may be flagged for review even if they are in fact the same game. No forced bulk migration/deletion.
- No copyrighted game image, BIOS, PSN key, or Sony EBOOT is in this repository or test suite.


## Batch importing PS1 Classics that were distributed for PSP

- From **My Games → More import options → Batch import PS1 Classics (PSN ZIP/7Z/EBOOT)**, select a folder containing several ZIP/7Z PSN archives and/or individual EBOOT.PBP packages in game folders. The folder is scanned in the isolated worker, not the UI.
- The other **Add Game Files** chooser already supports choosing multiple archives. When two or more ZIP/7Z/PBP inputs are selected, the importer now queues them as separate games, with its own title hint and temporary extraction directory. This fixes the old multi-archive path where multiple EBOOTs could share one archive title.
- The progress footer says **GAME 2/15** (etc) and shows each current PS1 disc reconstruction stage; completion reports a readable per-game result: **imported**, **already present**, **needs attention**. One broken package does not abort unrelated packages.
- Source SHA-256 fingerprints are calculated on EBOOT.PBP only. A repeated archive, a renamed ZIP or a differently-compressed 7Z containing that *exact same EBOOT* is skipped as an already imported PS1 Classic once a verified CHD/M3U receipt exists. Existing unproven PS1 same-title collections are held for review rather than overwritten. No KEYS.BIN contents are ever hashed, logged, or staged.
- **Native PSP games are different.** A non-PS1-Classics EBOOT.PBP in the batch is flagged for review; it is not forced through PSXtract/CHDman. Native PSP ISO/CSO/homebrew import through the normal PSP option and the same all-console game-file duplicate checks.
- Archive extraction stays local, bounded and disposable; no automatic deletion of originals, existing CHDs, existing playlists, or other ROMs.
- Batch tests use two synthetically-generated PSN packages and real ZIP/7Z archives, include a broken archive and native PSP EBOOT, and assert failure isolation and no duplicate tiles. Real Sony PSN encryption remains a user-controlled acceptance test, not proven by synthetic fixtures.

### Additional batch acceptance checks
- [ ] V162-B01 Select a folder of 3–10 PSN games in ZIP/7Z and EBOOT.PBP form; verify game count and that one bad archive does not stop the others.
- [ ] V162-B02 Confirm GAME N / TOTAL and per-disc stages are readable at 125% with a one-page imported/skipped/attention summary.
- [ ] V162-B03 Import the same PS1 Classic once in ZIP and once in 7Z with identical EBOOT payload; no second PSXtract/CHDman run and only one M3U/gallery tile.
- [ ] V162-B04 Confirm two different PS1 Classics in the same queue have distinct game titles, disc numbering and folder paths.
- [ ] V162-B05 Include one native PSP EBOOT and confirm safe rejection in PS1 Classics batch; import native PSP files separately in PSP mode.
