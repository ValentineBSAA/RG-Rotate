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
