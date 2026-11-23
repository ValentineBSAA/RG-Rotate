"""Read-only Windows removable-card identity and copy safeguards.

A drive letter is NOT a physical identity. Copies require a confirmed,
freshly measured volume GUID / serial and an explicit destination approval.
This never formats, partitions or deletes any card.
"""
from __future__ import annotations

from pathlib import Path

MIN_CARD_BYTES = 350_000_000_000
MAX_CARD_BYTES = 650_000_000_000
EXFAT = {'EXFAT'}


def card_candidate(volume, system_root=None) -> bool:
    """Suggest removable readers; fixed-looking ~512 GB drives are uncertain.

    Size is ONLY discovery assistance, NEVER proof a disk is removable/safe.
    """
    if system_root is not None and str(volume.root).casefold() == str(system_root).casefold():
        return False
    return bool(volume.removable or MIN_CARD_BYTES <= volume.total <= MAX_CARD_BYTES)


def fingerprint(volume) -> dict:
    """Stable-ish Windows volume identity, not a hardware serial guarantee."""
    return {'root': str(volume.root).casefold(),
            'guid': str(getattr(volume, 'guid', '') or '').casefold(),
            'serial': int(getattr(volume, 'serial', 0) or 0),
            'capacity': int(volume.total),
            'filesystem': str(volume.filesystem or '').upper(),
            'label': str(volume.label or '')}


def matches(expected: dict, volume) -> bool:
    if not isinstance(expected, dict):
        return False
    now = fingerprint(volume)
    # GUID/serial distinguish swapped cards with the same letter/capacity.
    if not expected.get('guid') and not expected.get('serial'):
        return False
    return (expected.get('root') == now['root'] and
            expected.get('capacity') == now['capacity'] and
            expected.get('filesystem') == now['filesystem'] and
            expected.get('guid', '') == now['guid'] and
            int(expected.get('serial') or 0) == now['serial'])


def verify_card(target: Path, expected: dict, validator=None):
    """Re-read Windows volume properties before writing and per file.

    Never infer card identity from size or drive letter alone.
    """
    if validator is None:
        from drives import validate_physical_root
        validator = validate_physical_root
    volume = validator(Path(target))
    if not matches(expected, volume):
        raise ValueError('Card identity changed or could not be established. '
                         'No copying: remove/reinsert the intended microSD and run Preview again.')
    if str(volume.filesystem).upper() not in EXFAT:
        raise ValueError(f'Card filesystem is {volume.filesystem or "unknown"}, not exFAT. '
                         'Confirm Android compatibility and choose an exFAT card; no automatic formatting.')
    return volume
