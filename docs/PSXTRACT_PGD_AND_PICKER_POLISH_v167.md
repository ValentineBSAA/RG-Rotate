# Retro Library Studio v1.6.7 Beta · PSXtract PGD failure and PS1 picker clarity

## Actual user Windows observations (November 23, 2026)
- In v1.6.6, the **custom title-aware PS1 picker succeeded**: 30 PS1 EBOOT packages were recognized by public PBP metadata. The user selected only **Clock Tower II - The Struggle Within**, source Sony folder `SLUS00695`, approximately 139 MB.
- The importer returned **0 imported / 1 needs attention / 0 verified CHDs** almost immediately. The console shows PBP unpacking, `Single disc game detected!`, `Decrypting ISO header...`, then `PGD: Invalid 0x80 MAC hash!` and `ERROR: ISO header decryption failed!`.
- Therefore this is a **PSXtract authentication/extraction failure**, NOT a CHDman conversion failure, invalid cover, wrong title or failed PS1 chooser. No validated CUE/CHD was produced.
- User also reported long, cluttered title/picker header and excessive repetitive failure text at 125% display scaling.

## Code analysis and limits
- Retro Library Studio has an optional PSXtract helper (currently pinned to the open-source has207/psxtract-2 v3.0 bundle). Existing wrapper passes positional arguments `-c EBOOT.PBP [DOCUMENT.DAT] [KEYS.BIN]`. When a KEYS.BIN exists **without** a DOCUMENT.DAT, the wrapper does not pass the KEYS argument, because the legacy positional layout has DOCUMENT in that slot. This may force the helper's built-in key derivation and may contribute to PGD failures; without the user's actual folder contents we **cannot claim** it caused this particular failure.
- **Actual key-only compatibility repair:** The pinned has207/psxtract-2 v3 source safely checks `fopen("")` for the missing optional manual, so a verified v3 helper can receive `-c EBOOT.PBP "" KEYS.BIN` without creating any file or altering keys. The app now uses that argument layout **only if the existing installer receipt verifies v3**; unknown or replaced PSXtract binaries use the prior conservative internal-derivation path, since older helpers may crash on an empty argument. The matching KEYS file is only read by the verified helper in temporary storage; no secrets enter logs.
- Never construct fake keys, invent a manual, substitute companions, retry blindly with unverified binaries or call the game corrupt from the screenshot. A matching genuine source package may still be required. We cannot guarantee every PSN EBOOT is convertible.
- New `PSXtractMilestones` recognizes PGD `0x80 MAC` and ISO-header decryption failures from output as discrete privacy-safe stage markers. `describe_extractor_failure` produces actionable wording: CHD never started, whether KEYS/DOCUMENT were present, and what remains untouched. Does not echo raw paths, serials, key bytes, hashes or unbounded helper logs.
- The picker now has a shorter heading, brief source-folder label with complete path only in a tooltip, a short search hint and concise selected-game summary. The details dialog says `Game import results`, separates successful CHDs from extractor failures and labels the short technical details.
- Existing v1.6.6 post-verification automatic artwork, Stop, CHD verification, duplicate receipts and NAS preservation must not regress.

## Automated gates
- [ ] Windows/Linux exact source tests including new `test_v167_psn_extract_diagnostics.py`.
- [ ] ZIP contains correct v1.6.7 source, all docs/tests; CRC checks pass.
- [ ] Old tests for v1.6.6 post-CHD artwork, v1.6.5 title picker, full workflows remain green.
- [ ] Regression verifies key-only CLI args on receipt-verified v3, conservative fallback for custom helpers, no source modification or key-byte exposure.

## Real Windows acceptance still required
- [ ] Open 30-title chooser and confirm short heading, readable source label, search, multi-select, accurate game names at 125%.
- [ ] For `SLUS00695` EBOOT with authentic adjacent KEYS.BIN and no manual, verify receipt-approved v3 actually receives the KEYS positional argument. The game may still fail for incompatible/mismatched source; if so app reports **PSXtract blocked / 0x80 MAC** and **CHD not started**. Do not create generic tiles/CHDs. Check optional companion presence in row tooltip.
- [ ] Do NOT share KEYS.BIN contents or PBP private metadata in diagnostic logs. If checking for completeness, use only the presence of original KEYS.BIN/DOCUMENT.DAT, not contents.
- [ ] Convert an already-proven working EBOOT and verify CHD then confident USA cover. Failed Clock Tower does not invalidate other games.
- [ ] Verify source originals remain unchanged, no partial CHD appears on card, all other games can be selected and imported independently.
- [ ] Investigate Clock Tower's actual helper compatibility/sidecars separately; do not mark this EBOOT fixed until physical conversion succeeds.
- [ ] Physical RG Rotate game launch and multi-package library test remain pending.

## Status
v1.6.7 improves diagnosis and UI **and fixes one genuine integration limitation** by providing the real adjacent KEYS.BIN when the authenticated v3 CLI accepts the empty optional manual slot. **It does not guarantee a mismatched/incompatible package will decrypt.** Real Clock Tower conversion requires a Windows retest.
