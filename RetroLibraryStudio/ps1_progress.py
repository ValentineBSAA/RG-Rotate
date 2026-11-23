"""Small, privacy-aware PSXtract console-to-UI milestone translator.

Recognizes only non-sensitive stage markers from PSXtract stdout. Never copies
the raw console log, source path, keys, decrypted bytes, serials or offsets to UI.
During extraction no honest percent or total-disc count is available yet, so
the existing activity bar stays indeterminate until the CHDman pipeline starts.
"""
from __future__ import annotations

import re

_DISC_NUMBER = re.compile(r'(?i)\bdisc\s*(\d{1,2})\b')
_SER = re.compile(r'(?i)^disc\s*(\d{1,2})\s*(?:serial|title)\s*:')
_BUILD = re.compile(r'(?i)building data track for disc\s*(\d{1,2})')
_PREBAKED = re.compile(r'(?i)(?:found prebaked cue file for disc|using prebaked cue file for disc)\s*(\d{1,2})')
_CONVERTED = re.compile(r'(?i)disc\s*(\d{1,2})\s+successfully converted')
_MD5_PASS = re.compile(r'(?i)\bmd5\b.{0,85}\b(?:pass|passed|match|matched|success|ok)\b')
_MD5_FAIL = re.compile(r'(?i)\bmd5\b.{0,85}\b(?:fail|mismatch|invalid|bad)\b')


class PSXtractMilestones:
    def __init__(self):
        self.disc = 0
        self.completed = set()
        self.last = ''
        self.discs_seen = set()
        self.md5_confirmed = False
        self.md5_failed = False

    def event(self, line: str) -> str | None:
        """Produce friendly per-disc status ONLY when a meaningful stage changes."""
        s = str(line).strip()[:500]
        if not s:
            return None
        text = s.casefold()
        msg = None
        if 'multi-disc game detected' in text:
            msg = 'Extracting PS1 Classic • multi-disc game recognized'
        elif _MD5_FAIL.search(s):
            self.md5_failed = True
            msg = 'Extracting PS1 Classic • MD5 check reported a problem'
        elif _MD5_PASS.search(s):
            self.md5_confirmed = True
            msg = 'Extracting PS1 Classic • MD5 integrity check passed'
        elif 'md5 verification' in text or 'md5 check' in text:
            msg = 'Extracting PS1 Classic • Checking disc data integrity (MD5)'
        elif m := _SER.search(s):
            self.disc = int(m.group(1))
            self.discs_seen.add(self.disc)
            msg = f'Extracting PS1 Classic • Disc {self.disc} identified'
        elif m := _PREBAKED.search(s):
            self.disc = int(m.group(1))
            self.discs_seen.add(self.disc)
            msg = f'Extracting PS1 Classic • Disc {self.disc} layout found'
        elif m := _BUILD.search(s):
            self.disc = int(m.group(1))
            self.discs_seen.add(self.disc)
            msg = f'Extracting PS1 Classic • Disc {self.disc}: rebuilding game data'
        elif m := _CONVERTED.search(s):
            self.disc = int(m.group(1))
            self.completed.add(self.disc)
            msg = f'Extracting PS1 Classic • Disc {self.disc} reconstructed ✓'
        elif 'attempting to extract audio tracks' in text and self.disc:
            msg = f'Extracting PS1 Classic • Disc {self.disc}: checking audio tracks'
        elif 'there are no cdda audio tracks' in text and self.disc:
            msg = f'Extracting PS1 Classic • Disc {self.disc}: no separate CD audio tracks'
        elif 'decrypting iso disc map' in text:
            msg = 'Extracting PS1 Classic • reading disc layout'
        elif 'decrypting iso header' in text and self.disc:
            msg = f'Extracting PS1 Classic • Disc {self.disc}: reading header'
        if msg == self.last:
            return None
        if msg:
            self.last = msg
        return msg

    def summary(self) -> str:
        """Only talk about observed completed discs; never invent a final count."""
        return f'{len(self.completed)} disc(s) reconstructed' if self.completed else 'PS1 disc extraction completed'
