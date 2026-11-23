# v1.6.3 Beta: PS1 Classics batch identity, Stop task, and safe recovery

## Why v1.6.2 failed real Windows acceptance
In a real 30-package PS1 Classics batch on the user's Synology-backed virtual card, the GUI displayed "GAME 1/30 • PS1" rather than the game title and published a generic PS1 cover and PS1/Disc 1 CHD. The user reports Stop task did not reliably end the work. This is an acceptance failure; previous CI did **not** test generic outer archive names or a real multi-game NAS stop.

Do not run the old v1.6.2 batch again against the same workspace. Do not delete, move, bulk-rename, or automatically merge existing generic PS1 CHDs. They cannot be tied to particular games without checking against the original source. An "Edit display title" setting only changes the tile caption, **not** the identity of the disc image.

## Implemented in source
- The PS1 title resolver rejects PS1/PSX/PlayStation/Disc 1, generic storage folders and PSN product codes as game identity. It reads the bounded, public TITLE field from PBP PARAM.SFO when archive/folder names do not identify a game; no keys, PSAR data or entire PBP are read.
- The batch queue updates from "Unidentified PS1 package" to the resolved title after inspecting the EBOOT, and displays the discovered title and verified collection folder in the end-of-batch summary.
- Unidentified packages stop at **Needs attention**, without silently publishing anonymous PS1 CHDs; errors do not block unrelated packages. A filename like PS1.zip is never, by itself, a title.
- CHD conversion still uses verified per-disc outputs, one ordered M3U for multidisc sets and one library tile. A verified single PSN disc can now get an EBOOT fingerprint receipt to skip identical reimports.
- The gallery has a direct **Open game folder** action. Legacy generic tiles show a review message; nothing is auto-renamed or deleted.
- Stop sends STOP over the worker control channel, closes it for reliable delivery, then escalates from terminate to kill if necessary. The UI remains locked against starting another import until the actual worker exits. The Windows Job Object contains converter subprocesses. A killed worker may leave .retro-part working files to inspect: no arbitrary deletion or claim that a file was verified.
- User-facing PSXtract progress no longer asserts "0 discs reconstructed" when the helper did not provide a recognized count.

## Real Windows acceptance checklist
- [ ] V163-01 Install v1.6.3 into a *new* program folder; open existing virtual card in read-only view and verify originals, artwork, CHDs and NAS paths were not touched just by opening.
- [ ] V163-02 **Before resuming a 30-game batch**, inspect erroneous ROMs/psx/PS1 entries. Open game folders and verify what files exist, leaving them intact. Never guess their titles by file order.
- [ ] V163-03 On a disposable test workspace, import two **different** PSN packages named PS1.zip or PS1.7z with valid PBP TITLE metadata. They must become **two distinct named folders**, with named CHDs, correctly ordered M3Us and two cover tiles; no ROMs/psx/PS1 result.
- [ ] V163-04 Import a generic-name package with no reliable inner title; it must say Needs attention and publish no anonymous CHD.
- [ ] V163-05 During a disposable ZIP/7Z extraction, click Stop once. Verify STOPPING appears, no second package starts, and the UI unlocks only after the child exits. Repeat separately during PSXtract and CHDman conversion. Inspect temporary .retro-part if the worker was force-terminated.
- [ ] V163-06 Reimport an identical single-disc PSN EBOOT under a different ZIP wrapper. Confirm exactly one CHD remains, with duplicate receipt outside scanned ROM folders.
- [ ] V163-07 Confirm batch summary lists per-game title/status/disc count/folder and My Games has an **Open game folder** button. At 125% Windows scale, no clipping.
- [ ] V163-08 Run Windows/Linux CI on exact PR SHA; then clean-extract the 1.6.3 source ZIP and test on Windows 11. CI is not proof of real CHDman, SMB stop, or physical RG Rotate behavior.

## Recovery of wrongly named v1.6.2 files
Only after independently verifying which source package produced each CHD can a user safely reimport it into a correctly named folder. v1.6.3 **does not migrate** generic PS1 folders because no trustworthy mapping of a CHD to its EBOOT is present in old receipts. Keep the old folder until the new named CHD is verified and gameplay checked, then remove duplicate *working copies only* through a separately reviewed manual cleanup. Do not use bulk "Remove verified working copies" to fix misidentified titles.
