# v1.6.5 Beta: selective PlayStation Classics, smart cover automation and useful progress

## Real user acceptance that led to this work
- The user tested v1.6.4 on Windows 11 against PS1 EBOOT.PBP files located on a Synology NAS under `PSTV/PSP/GAME/PS1/NPEE00001/`, with `KEYS.BIN` beside `EBOOT.PBP`.
- The app successfully converted Crash Bandicoot™ into CHD after the v1.6.4 Unicode-ASCII bridge; the user also canceled an extraction with Stop and restarted it. Those real-world observations are not proof of duplicate protection, 30-game batch success or every Windows corner case.
- Source packages are in Sony product-code folders (e.g. `NPEE00001`), so Windows' native file picker does not identify the actual game without opening the EBOOT. The user wants to choose *some* games, not blindly import 30.
- The native picker starts in Downloads instead of the most recently chosen folder, forcing unnecessary NAS navigation. The user wants the previously browsed folder remembered.
- User had to select both `EBOOT.PBP` and `KEYS.BIN`, although the import pipeline already detects the sidecar. The new UI should select games, not keys or individual tracks.
- The GUI was less informative than PSXtract console logs; MD5/CHD conversion stages should be visible.
- The user's preferred cover region when unknown is **USA**. They want automatic exact-match cover downloads for all consoles, with no confirmation dialog for safe matches. A known source region must take precedence over the default; special editions should not be silently assigned standard-edition art.
- Old generic `PS1` tiles/CHDs from the failed v1.6.2 batch remain untrusted. Never automatically merge or delete them; an additional generic tile is not proof of duplication of the latest successful game.

## Implementation
- New `psn_picker.py` scans the selected parent folder for recognized PS1 Classics EBOOT and ZIP/7Z packages in an isolated, stoppable worker. It reads public bounded EBOOT title metadata. **It does not infer titles from Sony product-code databases**, which would risk false identity; unnamed archives are labeled honestly until import inspects them. No need to decrypt/extract an archive just to preview.
- New custom PySide6 game selector: title, folder/code, package type and size, scrollable grid, text search, checkboxes, Select visible, Clear visible. No game preselected for a multi-game parent; a single-item folder is prechecked. The user chooses exactly the games they want.
- A selected `EBOOT.PBP` automatically uses its *same-directory* companion `KEYS.BIN`/`DOCUMENT.DAT` through the existing importer. These files are never treated as independent games, manually selected, modified or published on the virtual card.
- `Add Folder` also uses this picker when a recognized PS1 EBOOT is found, but preserves ordinary non-PS1 ZIP/SNES/GBA/PSP folder imports when no EBOOT evidence exists. The dedicated PS1 Classics action can inspect a folder of PS1 archives even before discovering each individual archive's title.
- The last browsed folder is saved in `QSettings` under `last_game_folder`. Both Add Files and Add Folder begin there on subsequent use.
- Existing CHD verification, duplicate receipts and per-disc M3Us are retained; Stop in the scan/import worker is cancellable.
- Progress title now shows the actual discovered PBP title, MD5 integrity-check milestones, CHD conversion and verification stages. Conversion percentages remain indeterminate when the helper does not provide an honest percentage.
- Automatic artwork uses exact normalized title matching across all supported cover systems, choosing USA when region is unknown, respecting an explicit region when known, stripping PSN trademark glyphs **only for cover filename lookups**, and leaving fuzzy/ambiguous editions for manual review. Existing manual artwork is never overwritten. Internet/catalog failures report an outcome rather than inventing a result.

## Required test gates
- [ ] Windows and Linux automated tests pass on exact v1.6.5 source commit.
- [ ] ZIP manifest/CRC pass and Windows source ZIP downloadable.
- [ ] On actual Windows 11, open PS1 parent folder containing NPEE/NPUJ code folders. The titles come from EBOOT metadata; none are guessed from code.
- [ ] Select only one of multiple packages; other EBOOTs, KEYS and source folders remain untouched.
- [ ] In Add Folder, select a *single* `EBOOT.PBP + KEYS.BIN` folder and verify it imports with no explicit KEYS selection.
- [ ] After closing/relaunching the program, Add Files/Add Folder opens in the last selected directory.
- [ ] Confirm a standard non-PS1 folder still imports as its actual system, not PS1.
- [ ] See Crash Bandicoot™ and valid PSXtract MD5, CHD conversion/verify status in the main GUI; no invented percentage or disc count.
- [ ] A verified Crash Bandicoot (USA) Libretro cover is assigned automatically when online and confident, no dialog. Missing network, region ambiguity and different editions must not silently overwrite.
- [ ] Reimport the *same successfully converted* Crash Bandicoot EBOOT from the PS1 chooser and verify a duplicate skip, no repeated CHDman conversion and one game tile. The earlier canceled-then-restarted test does not establish duplicate detection.
- [ ] After selecting a multi-disc title, confirm every disc's CHD and one validated M3U with correct title.
- [ ] Stop the PS1 picker and import task; verify no additional game is started.
- [ ] Inspect legacy anonymous PS1 tile manually, keep it intact until linked conclusively to a source. No automatic cleanup.
- [ ] Later, physical RG Rotate mounted microSD transfer and emulator launch testing; NAS staging alone is not physical card testing.

## Release status
Source candidate only until CI + ZIP packaging succeed. CI cannot establish the actual NAS, installed CHDman/PSXtract, artwork network access or physical handheld acceptance.
