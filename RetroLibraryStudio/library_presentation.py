"""Display metadata and disc grouping without reading or renaming any ROM."""
import os
import re
from artwork_gallery import clean_title, game_key
from ps1_collections import disc_identity, logical_disc_groups


def group_games(entries):
    groups = {}
    collections, claimed = logical_disc_groups(entries)
    # A scan-validated M3U is the only tile representing its CHD disc set.
    # Keep referenced entries in the group for searching and file details.
    for entry in entries:
        path_key = os.path.normcase(os.path.abspath(str(entry.path)))
        if path_key in claimed:
            continue
        if path_key in collections:
            groups[('multi-disc', path_key)] = collections[path_key]
            continue
        if entry.system == 'PS1' and entry.extension.lower() == '.chd' and disc_identity(entry.label)[1] is not None:
            # Invalid/incomplete M3Us never conceal individual disc CHDs.
            identity = ('unpaired-disc', path_key)
        elif entry.system == 'PS1' and entry.extension.lower() == '.m3u':
            identity = ('unverified-playlist', path_key)
        else:
            identity = (entry.system, str(entry.path.parent), clean_title(entry.label).casefold())
        groups.setdefault(identity, []).append(entry)
    return list(groups.values())


def preferred_title(settings, entry):
    chosen = settings.value('titles/' + game_key(entry.system, entry.label), '')
    if chosen:
        return str(chosen)
    if entry.system == 'PS1' and entry.extension.lower() == '.chd':
        base, number = disc_identity(entry.label)
        if number is not None and entry.path.parent.name.casefold() == base.casefold():
            return clean_title(base)
    return clean_title(entry.label)


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
        discs = [e for e in (group or []) if str(e.extension).lower() == '.chd']
        count = len(discs)
        return {'kind':'M3U', 'badge':f'{count} DISCS' if count >= 2 else 'M3U',
            'description':f'{count} disc playlist (.m3u), with separate CHDs' if count >= 2 else 'Multi-disc playlist (.m3u)',
            'verification':'The playlist groups separate CHDs into one game entry. File scanning checks references; actual CHD integrity and emulator disc switching still require independent verification.'}
    known = {'.bin':'BIN', '.img':'IMG', '.iso':'ISO', '.pbp':'PBP', '.cso':'CSO', '.gba':'GBA', '.nds':'NDS'}
    badge = known.get(ext, (ext.lstrip('.') or 'FILE').upper()[:8])
    return {'kind':badge, 'badge':badge, 'description':f'{badge} game file',
            'verification':'Format detected by file extension. Actual emulator playability and integrity are not verified by the gallery.'}
