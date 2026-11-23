# v1.6.6 Beta · Unified PS1 single/multi-select and artwork strictly after CHD

## Actual Windows observations (November 23, 2026)
- User tested v1.6.5 and showed the **native Windows Add Game Files dialog** displaying only Sony code folders `NPEE00001`, `NPEE00008`, etc. It cannot replace the folder labels with game metadata; the custom app title-aware picker must handle these paths instead.
- A single EBOOT + KEYS selection for a known Crash Bandicoot sequel imported correctly to CHD. User had to open manual art search, choose `Crash Bandicoot (USA)` artwork and confirm it. This manual success **does not count as automatic cover success**.
- User requires the same named game picker for one PS1 title or several, with automatic same-directory KEYS selection.
- **New explicit ordering requirement:** Auto cover retrieval/assignment happens only **after CHD conversion, verification, and publication**, never before a verified game exists.

## Root cause and fix
1. The prior v1.6.5 custom PS1 title picker was reachable through Add Folder or the dedicated PS1 button, but the ordinary **Add Game Files** control still opened native Windows file selection. v1.6.6 routes Add Game Files into the named PS1 picker when the remembered location is the PS1 parent or a Sony PS1 code subdirectory. The chooser includes Browse other ROM files for normal individual ROM selection. Single-game and multi-game checkboxes use the same screen.
2. `artwork_gallery.key_title` had treated Unicode ™ (and ®) in a PBP TITLE as extra meaningful text, so `Crash Bandicoot™` and `Crash Bandicoot (USA)` did **not** compare equal. The manual user-entered title omitted ™ and worked. v1.6.6 strips only legal glyphs for comparison, preserving the real game title and all meaningful game edition text.
3. `guided_import` explicitly reports verified CHD publication before cover lookup. `process_batch` labels the cover's searching/saved/review/unavailable status and only downloads exact artwork with USA preference when original region is unknown, respecting a specified region and never overriding existing manual art. A cover outage is non-fatal for verified CHDs.
4. If the SHA-256 duplicate receipt proves an earlier import completed successfully, retrying the same EBOOT skips PSXtract/CHDman but may still fill in a **missing** cover after confirming the CHD collection. It never replaces a cover already selected manually.
5. No legacy generic PS1 files from v1.6.2 are renamed or deleted automatically.

## Source / CI checks
- [ ] Exact current source SHA Windows + Linux tests pass, including new synthesized CHD→cover ordering, matched USA cover with trademark, duplicate backfill without conversion, and source folder selection.
- [ ] Windows beta ZIP manifests, integrity checks, start script and regression tests pass.
- [ ] New v1.6.6 beta merged only after CI passes.

## Real Windows acceptance
- [ ] Open **Add Game Files / PS1 Titles** from a remembered `.../PS1/NPEE00008` path: see custom title picker containing parent-folder titles. Select just one Crash title, no need to check KEYS.
- [ ] Search and select two titles simultaneously with the same picker, verify both game folders and no added anonymous PS1 game.
- [ ] Verify the main UI first shows extraction, then CHD conversion and verification, **then** "Artwork after conversion"; no art lookup during extraction.
- [ ] With automatic covers enabled, convert a title that does not yet have a cover, verify USA exact cover gets saved to `Media/BoxArt/psx` with **no manual confirm dialog**.
- [ ] Confirm CHD survives an artwork outage and status says needs attention.
- [ ] Reimport an already verified EBOOT. No extraction/CHDman, only missing-cover check; one tile remains.
- [ ] Confirm ordinary non-PS1 Add Game Files / Add Folder still functions.
- [ ] Stop during a disposable batch and verify no next title starts.
- [ ] Physical RG Rotate card transfer and launch pending, not inferred from NAS workspace.
