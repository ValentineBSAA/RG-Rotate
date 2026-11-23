# v1.6.1 | 7-Zip and PSN PS1 Classics into verified CHDs

**User screenshot:** Final Fantasy VII (English)(PSN) / NPEF00069 contains EBOOT.PBP, KEYS.BIN and DOCUMENT.DAT. This is a PS1 Classics PSN package, not an ordinary PSP ISO or a CUE/BIN disc. **KEYS.BIN is companion key material, not a game disc and not something to convert into CHD.** DOCUMENT.DAT is the digital manual. Original Final Fantasy VII on PS1 contains three discs. "7-Zip" refers to the .7z archive.

## Workflow
1. Add games > Add game files > select a .7z/.zip archive with fallback PS1. Or import the game folder.
2. The existing archive importer safely extracts to disposable local Windows storage, not the NAS. Enforce safe paths, no symlinks, 32 GB per-archive uncompressed limit, enough temporary free space, and py7zr >=1.1.3. Nested archives are not automatically unpacked.
3. Detect a PS1 Classics PBP by its PSAR signature and companion KEYS.BIN (if supplied). Ordinary native PSP EBOOTs are never silently converted into false PS1 CHDs.
4. Optional PSXtract v3.0 is installed only after explicit selection under Prepare apps plus download confirmation. Pin to the upstream GitHub asset at https://github.com/has207/psxtract-2/releases/tag/v3.0 with SHA-256 7bca7a8d982f7503a0d9348a3cc043385ee22264eb59ef7edf7fac9388b72013. A matching asset checksum proves identity of downloaded package, not its independent safety or compatibility.
5. PSXtract extracts disc CUE/BIN into disposable local storage. The importer verifies all referenced tracks and disc order before proceeding. Ambiguous numbering or missing discs aborts without publishing incomplete CHDs.
6. Feed complete CUE/BIN discs into existing CHDman createcd + verify, publish one CHD per disc, one ordered M3U, and one gallery tile with the correct game title and 3 DISCS badge.
7. Keep the source archive, EBOOT.PBP, KEYS.BIN, DOCUMENT.DAT and existing NAS ROMs/backup/CompanionData untouched. KEY data is not copied into ROMs or shown in detailed logs. Temporary extracted files disappear after import.

## Verification boundaries
- The automated test creates a REAL .7z archive with three synthetic CUE/BIN pairs and verifies extraction, CHD handoff and M3U grouping.
- The PSN package test uses synthetic PBP headers and a MOCK extraction tool. It does not verify PSXtract can decrypt the user's actual PSN EBOOT or correctly reconstruct CD audio.
- Some PSN Classics use ATRAC-compressed audio. Reconstructed audio may not be losslessly identical to an original CD. CHD compression cannot recover information already removed by the source encoding.
- The external binary is not bundled with the Retro Library Studio ZIP and is not installed without user approval. It runs only when the user initiates an import.
- Only process titles users are authorized to possess and convert.

## Real Windows/handheld acceptance
- [x] A01: [Main GitHub Windows/Linux CI](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45251934269) green: 326 Windows passed; 325 Linux passed/1 skipped. Real 7z synthetic archive extraction and safe ZIP path tests passed. User real FFVII PSN extraction still pending.
- [ ] A02: Optional PSXtract checkbox/consent installs pinned release and checks SHA-256; no automatic binary execution on install.
- [ ] A03: Choose the actual Final Fantasy VII (English)(PSN) .7z and PS1 fallback; recognizes EBOOT.PBP, KEYS.BIN and DOCUMENT.DAT as one PS1 Classic.
- [ ] A04: Real PSXtract yields complete, correctly ordered three CUE/BIN disc sets. Failure leaves the NAS unchanged.
- [ ] A05: CHDman verifies Disc 1/2/3 CHDs, builds ordered Final Fantasy VII.m3u, displays one cover with 3 DISCS and all members in details.
- [ ] A06: Preserve original EBOOT, keys and manual; never put KEYS.BIN in ROMs; old Resident Evil 2 remains unchanged.
- [ ] A07: Repeat import, cancellation and missing-key cases do not overwrite existing files or falsely claim success.
- [ ] A08: Real RG Rotate/emulator gameplay, disc swapping, saves and artwork are tested separately.
