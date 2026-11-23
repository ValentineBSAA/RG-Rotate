# v1.6.0 · Friendly details + microSD adapter identity checks

**Source status:** v1.6.0 merged into main, [GitHub CI](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45246376971) 311 Windows and 310 Linux passed (1 Linux skipped). Final GitHub-generated Windows source ZIP CRC validated, exact source clean-extract 279 local passed / 32 skipped (without PySide6). **No real USB adapter or physical RG Rotate acceptance yet.**

## Your proven starting point
The user's real Windows v1.5.9 screenshots at 125% confirm Resident Evil 2 now displays **one cover tile, 2 DISCS**, with an M3U and both CHDs in game details. The nominal planner shows **2.71 GB staged / 512 GB advertised**, about **492.11 GB** further nominal game capacity after the AI/free budgets. The virtual exFAT model shows **511.98 GB estimated formatted**, about **492.09 GB** modeled game space. User requested that the dense details popups become as approachable as the rest of the application.

## What v1.6.0 changes
1. Three read-only popup screens (Game File Format, Exact sizes, exFAT details) become theme-matched cards with bold title, short summary, clear metric rows and file rows. Optional **Show exact bytes and technical details** exposes the original precision when needed; **Copy details** supports debugging. Text is selectable and scrollable. **No ROM, artwork, playlist or capacity algorithms changed.**
2. Copy to Card listens for candidate volumes on a background Qt worker **only while that page is open**. USB microSD adapters normally expose drive letters; some expose a **fixed** drive, which is suggested only if approximately 512 GB, with conspicuous uncertainty. The app will not auto-select, format or copy to a drive simply because it has an appropriate size.
3. A user reviews possible drives and selects the intended volume, then runs **Preview**. The isolated transfer worker reads Windows volume GUID, volume serial, formatted capacity and filesystem. Preview refuses unreliable volume identities, non-exFAT and mismatched destinations.
4. Before a physical transfer, the app runs **another fresh Preview**, rejects different card GUID/serial/capacity/filesystem, asks the user to confirm the actual Windows drive letter by typing it, and passes the fresh identity into the transfer worker.
5. The transfer worker refuses a physical copy without that explicit preview identity. The transfer engine rechecks identity **before every source file**, preserving checksum verification, non-overwrite, safe resume, and the 8 GiB free-space reserve. A card removal/swap interrupts rather than risks copying to an unexpected drive.
6. Windows volume GUID and volume serial are a **filesystem identity safeguard**, not a cryptographic manufacturer-card authenticity proof. The user still must compare the card label/size/drive letter in Windows. An incorrectly labeled fixed SSD must not be treated as a card; uncertainty demands explicit user approval.

## Windows 11 first connection
- [ ] C160-01 Insert 512 GB microSD in USB reader. Open **Copy to card** and confirm detection suggestion appears without blocking UI or copying files.
- [ ] C160-02 Review candidate list: correct drive letter, approx 512 GB advertised (~476.8 GiB), exFAT filesystem and expected label. Fixed-looking USB readers must explicitly say *possible card, Windows says fixed*.
- [ ] C160-03 Choose candidate then run **Check what would be copied**; inspect measured capacity, current free space, 8 GiB reserve and any file conflicts.
- [ ] C160-04 Open *Exact sizes*, *exFAT details* and Resident Evil 2 *2 DISCS* format details; verify large text, cards, wrapped file names, detail expander, easy closure at 125%.
- [ ] C160-05 Before copy, identify the selected microSD with Windows Explorer or Disk Management. Re-run Preview and type the exact drive letter to authorize transfer. **Never approve a drive by size alone.**
- [ ] C160-06 Reject wrong letter, mismatched GUID/volume serial, changed filesystem, unplug/reinsert, missing/unknown identity, and FAT32 card with >4 GiB files.
- [ ] C160-07 Copy a small game set, SHA-256 verify, eject/reinsert and repeat verification. Verify NAS source/CompanionData/CHDs/cover art unchanged.
- [ ] C160-08 Confirm game launch, save/load and M3U disc switching on the actual RG Rotate.
- [ ] C160-09 Confirm there is no physical **format** button and no automatic filesystem writes outside explicitly approved verified transfer.

## Evidence
- GitHub mocked/unit/Qt tests may confirm code behavior but **cannot prove an actual Windows USB reader or connected microSD was detected**. Real hardware testing is still required.
- If Windows does not return an identifiable exFAT volume, copying is blocked; the user can check the card in Windows safely but the software does **not** format it.
