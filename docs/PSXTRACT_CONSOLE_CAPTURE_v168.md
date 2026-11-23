# v1.6.8 Beta · Clock Tower II PSXtract output capture and honest retry

## Windows evidence from user
On November 23, 2026, the actual v1.6.7 Windows retest of **Clock Tower II - The Struggle Within** selected the correct package in the 30-title chooser, but returned **1 checked, 0 imported, 0 already present, 1 could not finish, 0 verified CHDs**. The UI again displayed a generic **helper status 4294967295** instead of the specific PGD/ISO-header diagnosis observed earlier in the visible startup terminal. This is an **extractor failure, not CHDman conversion or artwork**. There is no successful Clock Tower CHD.

## Source-based root cause: error output bypasses GUI
Upstream has207/psxtract-2 v3 `src/psxtract.cpp` enters `main`, calls `AttachConsole(ATTACH_PARENT_PROCESS)`, then `freopen("CONOUT$", "w", stdout)` and `freopen("CONOUT$", "w", stderr)` when it successfully attaches. Retro Library Studio was launched via a Windows batch file from a console, so PSXtract can attach to its parent's terminal and redirect **away from the Python Popen(stdout=PIPE)**. Therefore the app doesn't observe lines such as `PGD: Invalid 0x80 MAC hash!` even though the user can see them in the startup console. This is a plausible, source-grounded explanation for the 1.6.7 regression; exact real-machine reproduction remains pending.

## Implementation
- `psxtract_launch_options()`: On Windows create a **separate hidden console** (`CREATE_NEW_CONSOLE`, `SW_HIDE` via STARTUPINFO) for the exact PSXtract helper. Upstream `AttachConsole(ATTACH_PARENT_PROCESS)` now fails because the child already has a console; the inherited stdout/stderr pipes stay intact. Thus the existing bounded, allowlisted milestone parser can see errors *without* key bytes or raw decrypted data entering the UI. Other OSes preserve normal launch behavior. Stop still terminates the exact PSXtract child.
- Add **Windows-only genuine smoke tests** of both console and GUI-subsystem helper analogues (python.exe/pythonw.exe), calling `AttachConsole(ATTACH_PARENT_PROCESS)` and emitting a synthetic PGD error. This goes beyond mocked Popen tests while needing no commercial PBP, key material or downloaded binary.
- If a KEYS.BIN exists, check only its **length** against the v3 helper's first-16-byte read; reject an obviously incomplete key early without reading or printing bytes.
- Normalize Windows wrapped exit status `4294967295` to `-1`. If helper output still does not contain a recognized stage, say so rather than blaming CHDman or pretending a known PGD cause.
- Report whether an existing key was **passed as a positional argument**, merely present but unverified helper couldn't use it, or absent; do not claim that key belongs to the EBOOT without proof.
- Preserve v1.6.7 verified-v3-only empty optional DOCUMENT slot for a valid adjacent KEYS.BIN, plus safe fallback to internal derivation for other helpers. Do not fabricate DOCUMENT or keys.
- Preserve single/multiple PS1 custom title chooser, auto-art *after verified CHD*, existing duplicate receipts, cancel/Stop and all older generic PS1 entries. No auto-deletion or renaming.

## Real Windows acceptance (NOT yet passed)
- [ ] Exact source SHA Windows/Linux regression CI passes including both real Windows AttachConsole smoke tests.
- [ ] Windows beta source ZIP CRC, included files, readme and version all verified.
- [ ] Run v1.6.8 with the original **Clock Tower II SLUS00695 EBOOT**; see whether the GUI captures `0x80 MAC` / `ISO header failed` and no longer shows the opaque 4294967295.
- [ ] If genuine adjacent KEYS.BIN is present and the pinned v3 helper receipt is valid, verify it is offered to PSXtract. If receipt isn't verified, report the conservative fallback and allow official setup repair rather than silent key-only guesses.
- [ ] If Clock Tower now decrypts, require reconstructed disc, CHDman createcd, CHD verify, correct game tile, **then** exact cover. No cover until CHD verified. If still invalid MAC, mark this source **unsupported/unverified** and do not repeat indefinitely.
- [ ] Repeat proven Crash Bandicoot EBOOT conversion/duplicate case to ensure unchanged successful paths.
- [ ] Do not move/copied unverified PS1 files to the physical RG Rotate microSD; start by using independently verified formats and games.

## Scope
This is an actual **error-output routing fix** and incomplete-key detection, not a decryption bypass. It may expose a useful cause without making an incompatible EBOOT playable. No test uses or distributes commercial game data or keys.
