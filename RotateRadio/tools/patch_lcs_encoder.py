#!/usr/bin/env python3
"""Patch pinned upstream's ATRAC3+ bit allocation and container frame length together.
Do not truncate encoded frames or change headers alone."""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
changes = {
    "crates/atracdenc/src/lib.rs": (
        "const AT3P_FRAME_SZ: u32 = 2048;",
        "const AT3P_FRAME_SZ: u32 = 744;",
    ),
    "crates/atracdenc-core/src/at3p/encoder.rs": (
        "bitstream: At3PBitStream::new(2048),",
        "bitstream: At3PBitStream::new(744),",
    ),
}
for path, (before, after) in changes.items():
    p = root / path
    text = p.read_text()
    if text.count(before) != 1:
        raise SystemExit(f"Unexpected pinned source: {path}")
    p.write_text(text.replace(before, after))
    print(f"Patched {path}: 744-byte ATRAC3+ frames")
