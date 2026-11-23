# v1.5.9 · Virtual Windows SDXC / exFAT format projection

**Status:** Simulation only. No SD card, NAS directory, partition, filesystem, sparse image, format operation, or existing file is created/deleted/rewritten by this feature.

## What the user requested

Keep their proven Windows/Synology virtual card and all existing PSP/PS1 CHDs, artwork, M3U, CompanionData and setup data. Add a layer that models what a newly formatted marketed **512 GB SDXC** microSD may look like after using **Windows 11 exFAT**, including actual data bytes plus allocation-unit rounding, and make the real measurement authoritative when a physical microSD is connected.

## Model boundaries

- The original 512,000,000,000-byte nominal/advertised staging planner remains unchanged and visible.
- A second **SIMULATED Windows 11 exFAT** meter is always visible below it. Its pure function models an assumed 128 KiB allocation unit, 1 MiB partition starting alignment, boot sectors, FAT entries, allocation bitmap and upcase metadata. These are *transparent assumptions*, not claims about the actual card or exact output of the Windows formatter.
- The read-only existing inventory worker accumulates per-file estimated cluster slack in **one scan**, including non-ROM files. It also sends M3U CHD membership to the UI; no additional NAS requests in Qt's paint path.
- The second meter uses modeled formatted capacity minus estimated actual allocation, future unused AI allowance (8 GiB total), and the **original 8 GiB protected free reserve**. Keep the older nominal capacity planner and core import safety checks in place. Do not allocate artificial 8 GiB data files.
- `exFAT details…` and `Exact sizes…` label every model value as estimated and every physical-preview value as Windows-measured.
- When the user selects the **physical destination** and runs **Copy to card → Preview**, the app uses Windows volume capacity / free space for safety and shows those values alongside the simulation. If these differ, real Windows measurements win; the program must not auto-format or infer a card just from a drive letter.
- A 512 GB SDXC card normally uses exFAT; Windows **does not automatically format every inserted card**. The user should verify existing format and compatibility before intentionally choosing to reformat. FAT32 is not a useful default for larger ROM files because of its 4 GiB file limit.

## Acceptance tests

- [ ] E159-01 Windows 125%: primary 512 GB nominal bar remains, a separate simulated exFAT bar and details button appear, labels fit/scroll.
- [ ] E159-02 Old virtual-card NAS path, custom cover art, CHD/M3U, settings, CompanionData and prior backups unchanged after opening the model.
- [ ] E159-03 A read-only scan includes *all staged files* for slack estimates, with no duplicate source files or added 512 GB image.
- [ ] E159-04 A real two-disc M3U (Resident Evil 2) is **one gallery tile, 2 DISCS badge**, and format details list playlist and both CHDs, not only the M3U. User screenshot previously showed a correct 2-line M3U and two CHD files but a stale M3U-only popup.
- [ ] E159-05 Empty library, nonstandard/large game files, and repeated scans never give negative capacity or create/erase anything.
- [ ] E159-06 When card arrives, choose the **correct physical removable drive** and preview. Compare its exact reported formatted total, filesystem, free space and projected copy to the estimate. Don't format it from Retro Library Studio; Windows may already see exFAT.
- [ ] E159-07 FAT32 physical target with any file >=4 GiB must be refused; acceptable exFAT targets verified by checksum copy/reinsert; selected target cannot be Windows C: or NAS virtual workspace.
- [ ] E159-08 Real RG Rotate recognizes the transferred filesystem and game files. Emulator compatibility remains separate from storage readiness.

## Evidence

- 2026-11-23 real Windows v1.5.8 screenshots: Resident Evil 2 Disc 1 CHD, Disc 2 CHD and one `.m3u` in `ROMs/psx/Resident Evil 2 (USA)/`. M3U contents list the two CHDs in order; CHDman reported verification and one new playlist. UI details showed M3U alone, a scan serialization/filter defect fixed in v1.5.9 source. No real RG Rotate playback has been asserted.
- Source automated CI and clean extraction must pass before claiming new v1.5.9 Windows beta is technically ready; user Windows/sync acceptance remains pending.
