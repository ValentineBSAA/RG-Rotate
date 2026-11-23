# Verification matrix · Retro Library Studio

## v1.6.1 candidate | PS1 Classics PSN EBOOT and 7Z

| Feature | Source/mock test | Real Windows PSN FFVII | Physical RG Rotate |
| --- | --- | --- | --- |
| Actual py7zr .7z with 3 synthetic CUE/BIN discs | Added, CI pending | Real user archive pending | N/A |
| PSN PBP + KEYS/DOCUMENT distinguished from PSP native | Synthetic header/source tests, CI pending | Original package classification pending | N/A |
| PSXtract pinned release downloaded only by consent | Installer ZIP/integrity mock tests, CI pending | Real install pending | N/A |
| PSXtract decrypts real FFVII disc images | MOCKED helper only | **NOT VERIFIED** | N/A |
| CHDman verifies discs, ordered M3U, one artwork tile | Fake three-disc regression, CI pending | **NOT VERIFIED for PBP source**; RE2 path previously passed | Disc switching pending |
| Original key/manual and NAS archive preserved | Code/test fixtures | User check pending | N/A |

[Required real-file testing](PS1_CLASSICS_7Z_ACCEPTANCE.md). A helper's checksum is release integrity, NOT independent security certification.


## v1.6.0 candidate · readable dialogs / safe card discovery

| Test | Source/CI | User Windows USB card | Physical RG Rotate |
| --- | --- | --- | --- |
| Three readable themed information dialogs and exact technical expander | New Qt tests passed GitHub CI | Pending 125% screenshots | N/A |
| Background candidate drive detection (removable/uncertain fixed) | Pure tests passed GitHub CI | Pending actual USB reader | N/A |
| Identity capture on Preview, exFAT + typed drive-letter approval | Mocked volume tests passed GitHub CI | Pending actual Windows formatted card | N/A |
| Volume identity verified at worker start and per-file before writing | Worker/per-file unit tests passed GitHub CI | Pending card/disconnection test | N/A |
| Existing ZIP import, CHDman, M3U, artwork and virtual NAS remain unchanged | Older regression suite to rerun | Previous v1.5.9 observed | Not yet launched |
| Small game launch, savestates and swap in Cocoon/emulators | Not testable in CI | Pending | Pending |

[Acceptance steps](CARD_DETECTION_AND_READABLE_DIALOGS.md).


## v1.5.9 candidate · Virtual exFAT layer + M3U member details

| Verification | Source | Actual Windows / NAS | Physical card / RG Rotate |
| --- | --- | --- | --- |
| CHD + M3U membership survives JSON worker handoff | Regression added, CI pending | User confirmed ordered files, **2 DISCS display pending** | Emulator disc switching pending |
| Nominal advertised 512 GB planner stays intact | Code unchanged + new layer tests, CI pending | User v1.5.8 nominal UI passed; v1.5.9 screenshot pending | Not a real card size |
| Non-destructive 128 KiB exFAT model and cluster slack | Pure math/scan tests, CI pending | v1.5.9 screenshot pending | Actual Windows formatted size pending |
| Real card source of truth | Existing measured physical preview retained | Pending physical card connection | Pending real drive/filesystem test |

See [non-destructive exFAT acceptance](VIRTUAL_EXFAT_PLAN.md). **No virtual formatting of real disk or virtual NAS directory takes place.**


## v1.5.8 · Multi-disc PS1 collections (merged source beta)

| Acceptance | Automated source / mock | User Windows + Synology | Actual RG Rotate |
| --- | --- | --- | --- |
| RE2 (USA) Disc 1+2 complete CUE/BIN → two verified CHDs, one parent folder and M3U | New synthetic tests; Windows/Linux CI passed | **Pending** M02–M03 | Pending |
| One My Games tile, cover, N DISCS badge; broken M3U does not hide discs | New pure/Qt tests passed GitHub CI | **Pending** M04/M08 | Cocoon art and playlist pending |
| FFVII 3 discs, FFVIII 4 discs; distinct editions/regions | New synthetic regression passed GitHub CI | **Pending** M06 | Pending |
| Disc 3 imported later extends validated M3U without clobbering custom playlist | New synthetic regression passed GitHub CI | **Pending** M05/M08 | Pending |
| Already-compressed CHD verified and organized (no recompression) | New synthetic regression passed GitHub CI | **Pending** M07 | Pending |
| NAS originals/backup/CompanionData never modified | Code safety rules/test doubles | **Pending** M02/M07–M09 | Pending |
| In-emulator disc swapping/saves | Not simulated by tests | Not applicable | **Pending** M10 |

Do not conflate generated/verified CHD output under a mocked converter with actual Windows CHDman or game runtime acceptance. See [test plan](MULTIDISC_ACCEPTANCE.md).


**v1.5.8 CI:** [run 45162967417](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45162967417): Windows 289 tests passed, Linux 288 passed/1 skipped. GitHub ZIP extracted and passed 264 local tests, with 25 skipped (no local Qt). No real user multi-disc CHDman/Synology test or emulator disc swap has passed yet.

## v1.5.7 console shelves (source merged, 2026-11-23)

**Main CI confirmed:** [run 45155602315](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45155602315), Windows 279 passed; Linux 278 passed, 1 skipped. No user Windows/NAS or physical-card acceptance follows from CI.

| Feature | Code change/test | Real Windows/Synology | RG Rotate |
| --- | --- | --- | --- |
| PSP/PS1/DS/GBA/PS2/GameCube visual sections, count pills, search/filter/file list | Source and optional Qt regression tests passed [PR run 45155293003](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45155293003): Windows 279 passed; Linux 278 passed, 1 skipped | **Pending** A01-A09 | Not applicable |
| Explicit PS2 and GameCube import organization | Source folder map + GCM classification tests passed in PR CI (not tested against real NAS files) | **Pending** A10 | Experimental gameplay F12 |
| Library titles, CHDs, covers, cancellation, backup safety | Existing behavior preserved by design; regression rerun **pending** | v1.5.4 single-disc CHDs observed; newer v1.5.5 batch safety **pending** | **Pending** |
| v1.5.6 512 GB virtual + real capacity meter | CI passed on prior v1.5.6 commit | **Pending** 125% Windows UX and physical-card comparison | **Pending** |

See [full testing checklist](FULL_TEST_CHECKLIST.md) for reproducible steps and exact prior observed passes. This candidate is **source-only**, not a new downloadable Windows ZIP/EXE.

_Last reviewed 2026-11-23. Only exact observed outcomes are marked **Passed**._

## Acceptance tiers
- **Code / mocked**: Unit/integration tests with fake CHDman, local temp directories, simulated network or isolated workers.
- **Windows real**: Screenshots or explicit user report of the program running on their Windows PC with the actual Synology NAS.
- **Hardware real**: User test on physical RG Rotate and microSD card.

| Feature | Code / mocked | Windows real | RG Rotate / card real | Notes |
| --- | --- | --- | --- | --- |
| Startup / PySide6 UI | Passed earlier | **Passed** through v1.4.x | N/A | User screenshot; v1.5.1 revised GUI still untested |
| Remember virtual NAS location | Passed | **Passed** | N/A | Real mapped Synology location |
| No forced 512 GB allocation | Passed | **Passed** | Pending | Virtual budget, actual files only |
| NAS free-space probe optional | Passed | **Passed** | N/A | Prevents long startup wait |
| Import ordinary PS1 file to NAS | Passed | **Passed** | Pending | Resident Evil Gore Edition imported |
| Cancel NAS import | Passed | **Passed** | N/A | User confirmed Stop returned control |
| Artwork tile/manual selection | Passed | **Passed** | Pending in Cocoon | User's Resident Evil custom cover displayed |
| Automatic online artwork matching | Basic code tests | **Needs retest** | Pending | Edition-safe fallback, live results unverified |
| Manual Cocoon APK import | Passed | **Passed** | Not installed | `cocon-311.apk` staged |
| PPSSPP/RetroArch APK batch download | Passed | **Reported ready** | Not installed | Files visible in SetupPackages |
| CHDman/ADB installation | Mocked/code checks | **Reported ready; functionality not confirmed** | N/A | Verify executable --version/help |
| CHD CUE picker | Passed | **Opens** | N/A | Does not prove CHD conversion |
| CHD real conversion/verification | Mocked | **Pending** | Pending emulator launch | RE2 disc discrepancy unresolved |
| Library health checker | Passed | **Passed** | N/A | 1 file, 0 duplicates, 0 broken refs in sample |
| Fresh practice copy + SHA-256 | Passed | **Passed** | Pending | NAS→Windows practice: 6/6, 1.21 GB |
| Repeated copy / hash check | Passed | **Passed** | Pending | 0 new files, 6 identical, 6/6 verified |
| Physical microSD selection/copy | Passed mock/preflight | **Pending** | **Pending** | Test on actual reader/card |
| Clock Tower CUE+BIN grouping | Passed with synthetic files | **Files imported together** | Pending | v1.5.0 My Games shows tiny CUE size |
| v1.5.1 CHD before My Games | **Passed with mocked CHDman** | **Pending** | Pending | Must test genuine CUE/2 BINs |
| v1.5.1 M3U for multi-disc | **Passed with mocks** | **Pending** | **Pending** | Correct ordering, disc swap |
| v1.5.1 combined game-size display | Code passed | **Pending** | Pending | 226/228-byte reported size bug |
| v1.5.1 unified progress | Code path implemented | **Pending UI acceptance** | N/A | Clear stages, cancellation |
| 125% UI scaling/window persistence | Earlier versions observed | **Passed for v1.4.x** | N/A | v1.5.1 redesign not retested |
| RG Rotate DS screen switching | Planned | N/A | **Pending** | One screen at a time, button toggle |
| Cocoon Home/ROM configuration | Planned | Staging only | **Pending** | Requires Android permissions |
| AI companion vs built-in Anbernic AI | Planned | N/A | **Pending assessment** | Do not overbuild before testing |

## Source publication

- **Passed:** Source files and tests from v1.5.1 were pushed as browsable UTF-8 files to `RetroLibraryStudio/` on 2026-11-23 (commit `b458028`). Published `app.py` and `ps1_pipeline.py` were fetched back through the GitHub connector and verified as present. Optional generated cover artwork excluded.
- **Pending:** GitHub-hosted Windows CI and external release packaging.

## GitHub Actions CI (2026-11-23)

- **Passed:** [CI run 45138220982](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45138220982), source commit `e51d25a`: **Windows 241 passed**, **Linux 240 passed / 1 skipped**.
- CI initially exposed a **real Windows ZIP/CUE companion-track alias bug**: BIN files were treated as standalone even after the CUE had been selected. Canonical path match fixed in `89b1b6c`, regression added in `e51d25a`.
- CI is a **mocked/source test**, not proof of live CHDman, NAS SMB, user monitor DPI, physical card, or RG Rotate emulation.

## Test runs
- **v1.4.4**: historical source package reported **180 automated tests** plus the real user NAS transfer outcomes above.
- **v1.5.0**: uploaded source file was reviewed; in the current environment its Linux run was reported **205 passed, 15 skipped**. Its own release report claims 220 Windows passes; this report is not independent evidence here.
- **v1.5.1**: **2026-11-23** rerun from source directory: `python -m pytest -q --disable-warnings --maxfail=1` → **225 passed, 15 skipped** (Linux). ZIP has **65 members**, passed `ZipFile.testzip()`; **size 3,074,882 bytes**. Test harness does not prove actual CHDman, live art-provider downloads, Windows DPI, NAS stall or hardware behavior.

## Automated GitHub CI results, 2026-11-23

- **Run [45138220982](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45138220982): PASSED.** Windows: **241 passed**. Linux: **240 passed, 1 skipped**. These are automated source tests, not genuine CHDman execution or RG Rotate hardware acceptance.
- First run caught an actual Windows ZIP/CUE companion path normalization issue. Fixed in commits `89b1b6c` and `e51d25a`; subsequent cross-platform CI passed.

## Exact next real-world checklist
1. On Windows run v1.5.1 in a new program directory while pointing at **existing** NAS library; do not delete or reset old workspace.
2. Confirm CHDman actually runs, not just that chdman.exe exists.
3. Import a **test copy** of Clock Tower CUE + both BIN tracks. Confirm: one playable `.chd`, verified, appropriate non-tiny size, one gallery tile, originals unaffected.
4. Import Disc 1 and Disc 2 of a known complete multi-disc title. Confirm two CHDs + one M3U and actual emulator disc change. Never combine multi-disc media into one CHD.
5. Exercise online artwork fallback/manual picker; record provider and error if it fails.
6. Run NAS→Windows practice preflight, copy, repeat verify, stop and resume in disposable destination.
7. Only then test physical microSD and Android first boot.

## Evidence update template

Date, app version/commit, OS/drive/device, input fixture and hashes if applicable, procedure, actual result, evidence (screenshot/log), and status: **Passed / Failed / Pending / Blocked**.

Never infer a PASS from a progress bar screenshot alone when the underlying verification has not completed.

## v1.5.2 package build · 2026-11-23

- **Passed:** source ZIP created, SHA-256 and ZIP member integrity confirmed, clean extracted Linux pytest **226 passed / 15 skipped**.
- Matching core GitHub Windows CI on v1.5.1 revision: **241 passed**; it does not validate v1.5.2 user GUI execution or CHDman binary.
- **Pending:** actual Windows 11 v1.5.2 startup, CHDman Clock Tower conversion, artwork, user NAS, physical card and Cocoon.

## v1.5.3 game format / artwork review (2026-11-23)

- **Passed local source tests:** 230 passed, 15 skipped; included offline Libretro-server outage and GitHub artwork-catalog/image fallback tests, true file-extension badge classification, and unsafe redirect rejection.
- **Observed on v1.5.2 Windows:** Clock Tower reported 118.0 MB with no cover; on-screen search said the artwork catalog was unavailable.
- **Pending:** The user must test v1.5.3 on Windows 11 and confirm actual CHD vs BIN/CUE badge, clickable metadata dialog, live cover results and NAS behavior; external internet services can be unavailable even with fallback.
- **Pending:** Actual CHDman verification and game launch on physical RG Rotate. Filename extension is not integrity evidence.

### GitHub v1.5.3 CI (run 45141431778)

- **Passed**: [GitHub Windows job 245 passed](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45141431778), Linux 244 passed + 1 skipped. Mocked artwork catalog outage fallback and truthful format badges tested. Windows UI and real artwork provider connectivity are **not** acceptance verified.

## v1.5.4 code vs real Windows verification · 2026-11-23

- **Observed v1.5.3 GUI pass:** Clock Tower format is `BIN/CUE`, size **118.0 MB**, cover search returned multiple titles, selected cover appeared in gallery. Automatic visual preview on selecting candidate was missing in this build.
- **v1.5.4 local source test:** **240 passed, 15 skipped** including 10 new organizer tests: CUE/BIN conversion/tidy, existing CHD, verify failure safety, cancel safety, external path refusal, shared BIN refusal, raw IMG, ambiguous IMG, CloneCD metadata blocking, and no single-disc M3U.
- **Windows CI:** Pending at time of source publication. This is not evidence of actual user Windows interaction.
- **User acceptance still pending:** 125% context menu, async artwork previews, real CHDman conversion, NAS file moves/recovery, real physical microSD and Cocoon playback. See [#8](https://github.com/ValentineBSAA/RG-Rotate/issues/8).

### v1.5.4 GitHub Actions confirmation

- [run 45144304702](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45144304702) passed: **255 Windows**, **254 Linux + 1 skipped**. Qt UI and PS1 organizer unit tests executed on CI. CHDman subprocess is mocked in conversion tests; physical Windows NAS hardware and emulator playback still pending.

## v1.5.4 actual Windows acceptance and v1.5.5 source tests

- **Actual Windows 11 v1.5.4 passed (user screenshots):** Clock Tower: The First Fear CHD created and CHDman verified (55.4 MB), Resident Evil Gore Edition CHD created and CHDman verified (311.9 MB). Both cover images retained and CHD badges present. Prior old tracks moved into sibling recovery on Synology NAS.
- **v1.5.5 local Linux code-only tests:** 248 passed, 16 skipped; new fixtures verify preserving external originals, delete-within-card only after verification, recovered backup mode, failed CHD preservation, cancel, multiple discs, duplicate IMG/CUE, and resized cover preview (Qt skipped on Linux). Clean-extracted ZIP integrity passed.
- **Pending Windows v1.5.5:** Actual batch conversion including destructive cleanup confirmation, verifying external original and previous recovery backups untouched, genuine lossless CHDman verification, responsive GUI, fitted artwork preview.
- **Pending RG Rotate:** Physical-device game launch and M3U disc switching.

### GitHub v1.5.5 CI (2026-11-23)

- **Passed:** [run 45148569884](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45148569884), **Windows 264 passed**, **Linux 263 passed / 1 skipped**, including Qt aspect-fit preview test. All conversion tools mocked in automated tests.
- Package ZIP clean extraction on Linux: **248 passed / 16 skipped**. **Pending:** Real v1.5.5 Windows batch deletion and Synology NAS user acceptance.


## v1.5.5 batch conversion / cleanup (2026-11-23)

| Test | Evidence | Status |
| --- | --- | --- |
| Existing v1.5.4 Clock Tower conversion and cover | User screenshots show CHD badge, 55.4 MB, cover | **Windows observed pass (previous version)** |
| Existing v1.5.4 Resident Evil Gore Edition | User screenshots show verified CHD dialogue, 311.9 MB, cover | **Windows observed pass (previous version)** |
| New v1.5.5 batch CUE/IMG conversion orchestration | Local simulated CHDman tests, failed/missing-track/cancel cases | **Source tests passed** |
| New v1.5.5 cleanup of virtual PSX working tracks | Local tests prevent deleting external originals, check verification before cleanup | **Source tests passed** |
| New v1.5.5 preview resizing and Windows context-menu behavior | PySide6 GUI not exercised here | **Pending real Windows** |
| New v1.5.5 batch with actual CHDman + Synology SMB | No physical test yet | **Pending** |
| v1.5.5 archive | 73 members; ZIP integrity passed; SHA-256 `e1a00b4f0147353ffdc37f47bb49e69a87afd5bfc23a9839968232834d441350` | **Package verified** |
| v1.5.5 automated test run | **248 passed, 16 skipped on Linux** | **Code passed, GUI unverified** |
| v1.5.5 GitHub CI | [Run 45149019365](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45149019365): Windows **264 passed**, Linux **263 passed, 1 skipped** | **Automated tests passed** |

Do not mistake CHD compression for lossy audio/video reduction: conventional CHD CD codecs preserve disc data. CHD extension by itself is not a verification receipt.

## v1.5.6 capacity-meter verification (2026-11-23)

- **Code test passed:** nominal 512 GB is 476.84 GiB, actual staged byte count vs reserved companion headroom, over-budget cases, measured physical card capacity, free-after-transfer math, preflight capacity conflicts, and no NAS capacity probe on model calculation.
- **Local source test:** 255 passed / 19 skipped (including the new PySide6 display checks because Qt isn't installed locally).
- **Pending:** Windows GitHub Actions UI smoke tests, actual formatted microSD capacity, real card filesystem and verified transfer, 125% display screenshot and user acceptance.
- **Important:** Nominal virtual budget != actual card formatted capacity != backing NAS free space. Display all three separately and never claim bytes copied from preview alone.

### v1.5.6 packaging evidence

- [GitHub Actions 45152416169](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45152416169): **Windows 274 passed; Linux 273 passed / 1 skipped**.
- Build ZIP: `RetroLibraryStudio_v1.5.6_Windows_Test_Beta.zip`, SHA-256 `1bf62b798111f9d621ee5fffb07ba37ecfbcc854b1f3c186dc8495cac1efe36f`, 3,107,017 bytes, 76 members, ZIP CRC clean, extracted local source **255 passed / 19 skipped**.
- **Pending Windows real UI and physical card acceptance**: 125% meter layout, staged file total, actual capacity/preview, bytes remaining, transfer safety.
