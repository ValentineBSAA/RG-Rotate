"""Display metadata and disc grouping without reading or renaming any ROM."""
import re
from artwork_gallery import clean_title, game_key


def group_games(entries):
    groups = {}
    # Only discs with explicit disc tags group together. Editions are retained.
    for entry in entries:
        identity = (entry.system, str(entry.path.parent), clean_title(entry.label).casefold())
        groups.setdefault(identity, []).append(entry)
    return list(groups.values())


def preferred_title(settings, entry):
    return str(settings.value('titles/' + game_key(entry.system, entry.label), '') or clean_title(entry.label))


def gallery_columns(width, scale):
    return max(1, min(6, (max(1, width) - 20) // max(1, round(190 * scale / 100))))


def format_badge_info(entry, group=None):
    """Describe the actual scanned file format; never claim verification from an extension."""
    ext = str(entry.extension or entry.path.suffix).lower()
    if ext == '.chd':
        return {'kind':'CHD', 'badge':'CHD', 'description':'CHD disc image',
            'verification':'CHD detected by filename. Integrity has NOT been independently rechecked by this gallery; run Library Check or CHDman verification for confirmation.'}
    if ext == '.cue':
        return {'kind':'BIN+CUE', 'badge':'BIN/CUE', 'description':'CUE disc descriptor with external BIN tracks',
            'verification':'This is a CUE/BIN source disc, NOT a CHD. Tracks are not combined into CHD until conversion succeeds.'}
    if ext == '.m3u':
        return {'kind':'M3U', 'badge':'M3U', 'description':'Multi-disc playlist (.m3u)',
            'verification':'An M3U references separate disc images; it is not a CHD itself. Referenced files and disc switching require testing.'}
    known = {'.bin':'BIN', '.img':'IMG', '.iso':'ISO', '.pbp':'PBP', '.cso':'CSO', '.gba':'GBA', '.nds':'NDS'}
    badge = known.get(ext, (ext.lstrip('.') or 'FILE').upper()[:8])
    return {'kind':badge, 'badge':badge, 'description':f'{badge} game file',
            'verification':'Format detected by file extension. Actual emulator playability and integrity are not verified by the gallery.'}
