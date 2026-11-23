# Source publication and GitHub workflow
_Last checked 2026-11-23._

## Current limitation (important)

The GitHub repository currently has **project documentation and roadmap**, not the complete Python source. The latest complete source was assembled as:

`RetroLibraryStudio_v1.5.1_Automatic_CHD_M3U_Artwork_Windows_Source.zip`

- SHA-256: `abc1fb3496826357e27aebf463c26453d381b6fba3f275f6bffba70e7e464001`
- Size: **3,074,882 bytes**.
- ZIP structure: **65 files** under `RetroLibraryStudio_1.5.1/` (plus tests and optional custom cover).
- ZIP self-check: pass.
- `python -m pytest -q --disable-warnings --maxfail=1` on Linux: **225 passed, 15 skipped**.
- Windows CHDman conversion and live RG Rotate testing: **not performed on this v1.5.1 artifact**.

The connected GitHub write API supports UTF-8 files, but this session has not transferred the ZIP's binary bytes or the entire source tree. **Do not infer that a document about v1.5.1 means v1.5.1 code has been pushed.**

## Publish source with GitHub Desktop (recommended)

1. Download the ZIP artifact from the producing chat and extract it **into a NEW folder**, keeping the existing working installed v1.4.4 and virtual NAS workspace intact.
2. Open **GitHub Desktop**, choose **File → Clone repository**, choose `ValentineBSAA/RG-Rotate`.
3. In the clone create the subfolder `RetroLibraryStudio/`; copy the **contents** of extracted `RetroLibraryStudio_1.5.1/` into it. Include Python modules, Windows batch launchers, tests, docs, requirements, `.gitignore`. Optional cover is user-created but need not be included if privacy/licensing uncertain.
4. Never copy actual `ROMs/`, `BIOS/`, `SetupPackages/`, `WindowsTools/`, `CompanionData/`, saves, downloaded proprietary APKs, tokens, credentials, personal NAS paths, or local `.venv/` and Python caches.
5. Commit as `feat: import Retro Library Studio v1.5.1 source baseline` and push to `main`.
6. Confirm the repository displays `RetroLibraryStudio/app.py`, `ps1_pipeline.py`, `tests/`, and `requirements.txt`; run the tests on Windows using the included test runner.
7. Update the README statement that source publication is pending and check the [roadmap](ROADMAP.md) publication item once GitHub files are actually visible.

Alternative: use the Git CLI in the repository clone, then `git add RetroLibraryStudio`, `git commit`, and `git push`, but only after reviewing the staged file list.

## Ongoing maintenance contract

For **every** feature, bugfix, test, new build or real-device acceptance:
- Work against the latest actual published source branch and create an issue/PR or identifiable commit.
- Run tests and capture environment-dependent passes/failures.
- Update [ROADMAP.md](ROADMAP.md), [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md), [VERIFICATION_MATRIX.md](VERIFICATION_MATRIX.md), and app version/changelog *in the same PR/commit*.
- Keep a current release ZIP/checksum and state exactly which Windows/hardware tests remain.
- Never mark tasks done only because code was written or mocked tests passed.

This is **commit-by-commit maintenance**, not an unattended background service. A new ChatGPT session should read the repo at the beginning of work and finish by updating it.

## Security and compatibility

- Public repository: source, documentation, and appropriately licensed original assets only.
- Commercial games, copyrighted firmware, private device identifiers, saves, API keys, user chats, NAS credentials and network shares stay out.
- Do not confuse adding an APK file to a staging folder with installing it on Android.
- Avoid pushing incomplete CHDs or source game tracks; keep game conversion output on the user's card/NAS.
