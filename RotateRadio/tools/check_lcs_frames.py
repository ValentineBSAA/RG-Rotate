#!/usr/bin/env python3
"""Validate the actual encoded RIFF against LCS initial streaming constraints."""
import pathlib
import struct
import sys

b = pathlib.Path(sys.argv[1]).read_bytes()
assert b[:4] == b"RIFF" and b[8:12] == b"WAVE"
assert struct.unpack_from("<I", b, 4)[0] + 8 == len(b)
p = 12
fmt = None
while p + 8 <= len(b):
    tag, size = struct.unpack_from("<4sI", b, p)
    p += 8
    assert p + size <= len(b)
    if tag == b"fmt ":
        fmt = struct.unpack_from("<HHIIHH", b, p)
    if tag == b"data":
        assert fmt is not None
        codec, channels, rate, avg, block, bits = fmt
        assert (codec, channels, rate, block) == (0xfffe, 2, 44100, 744), fmt
        assert avg == 744 * 44100 // 2048
        assert size > 0 and size % block == 0
        assert p + 2 * block <= 2048, (p, block)
        print(f"ATRAC3+ {avg*8} bps, {block} bytes/frame, data offset {p}, two frames fit 2048-byte initial buffer")
        break
    p += size + (size & 1)
else:
    raise SystemExit("Missing data chunk")
