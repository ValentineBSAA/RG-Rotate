# Verification matrix · Retro Library Studio
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
