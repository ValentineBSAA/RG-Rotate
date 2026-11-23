# Retro Library Studio v1.5.9 · Virtual exFAT + Multi-disc Details

**Date:** 2026-11-23. **Status:** Merged source beta; [main CI 45242023081](https://github.com/ValentineBSAA/RG-Rotate/actions/runs/45242023081) passed 301 Windows/300 Linux plus 1 skip; ZIP clean extract 273 passed/28 skipped. Real Windows 125%/actual microSD still pending.

## Actual prior Windows evidence

User screenshots of v1.5.8 show **Resident Evil 2 (USA) Disc 1.chd, Disc 2.chd and Resident Evil 2 (USA).m3u** inside one NAS virtual-card game folder. The M3U contains both CHDs in the correct order; CHDman reported verified conversions; artwork displayed and library scan completed. However, the badge stayed **M3U**, and format-details popup listed only the playlist. This was caused by the read-only scan protocol dropping the playlist members and prematurely hiding member CHDs.

## Fix

- `readonly_scan.py` now sends serialized `Entry.members` and leaves M3U CHDs in the scan list.
- `app.py` restores membership, allowing `logical_disc_groups()` to replace physical disc tiles with exactly one verified **2 DISCS** collection and list all members in file details. Supports legacy 5-field scan responses.
- Existing original CUE/BIN, CHD, M3U, artwork and titles are not modified.

## New virtual SDXC exFAT overlay

- `virtual_exfat.py` models a Windows 11 512 GB SDXC/exFAT target with an **assumed** 128 KiB allocation unit, exFAT FAT/bitmap/boot/upcase and partition alignment. Computes byte-precise mathematical *estimates*, not the real card's exact formatted capacity.
- Existing read-only inventory scan adds modeled allocation-unit slack; no new NAS traversal from Qt.
- Original **512 GB nominal** capacity strip and protected 8 GiB AI / 8 GiB free-space budgets remain; second virtual exFAT model strip, details button and expanded Exact sizes show estimates transparently.
- Windows physical card **Copy to card → Preview** remains the accurate measurement source when the actual microSD appears. **No actual formatting, partitioning, deletion, sparse image or large file allocation** occurs.

## Verification gate

- [x] GitHub Windows/Linux CI pass for exact merged source.
- [ ] Real Windows at 125%: original meter + exFAT overlay visible, 2 DISCS badge/format popup lists both discs.
- [ ] Actual 512 GB card: verify filesystem, formatted capacity, free bytes and transfer preflight; do not automatically reformat a card.
- [ ] Android RG Rotate: Cocoon single-game mapping, PS1 emulator M3U disc switching and save/playback.

[Detailed checklist](../docs/VIRTUAL_EXFAT_PLAN.md)
