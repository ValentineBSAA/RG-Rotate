# Retro Library Studio v1.6.7 Beta · PSXtract PGD failure and PS1 picker clarity

## Actual user Windows observations (November 23, 2026)
- In v1.6.6, the **custom title-aware PS1 picker succeeded**: 30 PS1 EBOOT packages were recognized by public PBP metadata. The user selected only **Clock Tower II - The Struggle Within**, source Sony folder `SLUS00695`, approximately 139 MB.
- The importer returned **0 imported / 1 needs attention / 0 verified CHDs** almost immediately. The console shows PBP unpacking, `Single disc game detected!`, `Decrypting ISO header...`, then `PGD: Invalid 0x80 MAC hash!` and `ERROR: ISO header decryption failed!`.
- Therefore this is a **PSXtract authentication/extraction failure**, NOT a CHDman conversion failure, invalid cover, wrong title or failed PS1 chooser. No validated CUE/CHD was produced.
- User also reported long, cluttered title/picker header and excessive repetitive failure text at 125% display scaling.

## Code analysis and limits
- Retro Library Studio has an optional PSXtract helper (currently pinned to the open-source has207/psxtract-2 v3.0 bundle). Existing wrapper passes positional arguments `-c EBOOT.PBP [DOCUMENT.DAT] [KEYS.BIN]`. When a KEYS.BIN exists **without** a DOCUMENT.DAT, the wrapper does not pass the KEYS argument, because the legacy positional layout has DOCUMENT in that slot. This may force the helper's built-in key derivation and may contribute to PGD failures; without the user's actual folder contents we **cannot claim** it caused this particular failure.
- Never construct fake keys, invent a manual, substitute companions, silently retry with unknown cryptographic options or call the game corrupt from the screenshot. A matching genuine source package or independently supported helper version may be required. We cannot guarantee every copyrighted/commercial PSN EBOOT is convertible.
- New `PSXtractMilestones` recognizes PGD `0x80 MAC` and ISO-header decryption failures from output as discrete privacy-safe stage markers. `describe_extractor_failure` produces actionable wording: CHD never started, whether KEYS/DOCUMENT were present, and what remains untouched. Does not echo raw paths, serials, key bytes, hashes or unbounded helper logs.
- The picker now has a shorter heading, brief source-folder label with complete path only in a tooltip, a short search hint and concise selected-game summary. The details dialog says `Game import results`, separates successful CHDs from extractor failures and labels the short technical details.
- Existing v1.6.6 post-verification automatic artwork, Stop, CHD verification, duplicate receipts and NAS preservation must not regress.

## Automated gates
- [ ] Windows/Linux exact source tests including new `test_v167_psn_extract_diagnostics.py`.
- [ ] ZIP contains correct v1.6.7 source, all docs/tests; CRC checks pass.
- [ ] Old tests for v1.6.6 post-CHD artwork, v1.6.5 title picker, full workflows remain green.

## Real Windows acceptance still required
- [ ] Open 30-title chooser and confirm short heading, readable source label, search, multi-select, accurate game names at 125%.
- [ ] For `SLUS00695` EBOOT, app reports **PSXtract blocked at encrypted header / 0x80 MAC** rather than opaque negative exit and explicitly says **CHD not started**. No generic PS1 tile/CHD should be created. Check optional companion status via row tooltip.
- [ ] Do NOT share KEYS.BIN contents or PBP private metadata in diagnostic logs. If checking for completeness, use only the presence of original KEYS.BIN/DOCUMENT.DAT, not contents.
- [ ] Convert an already-proven working EBOOT and verify CHD then confident USA cover. Failed Clock Tower does not invalidate other games.
- [ ] Verify source originals remain unchanged, no partial CHD appears on card, all other games can be selected and imported independently.
- [ ] Investigate Clock Tower's actual helper compatibility/sidecars separately; do not mark this EBOOT fixed until physical conversion succeeds.
- [ ] Physical RG Rotate game launch and multi-package library test remain pending.

## Status
v1.6.7 improves diagnosis and UI. **It does not claim to bypass a genuine PGD authentication failure or repair a mismatched EBOOT/key package.** Those issues require genuine source/compatible extractor evidence.
