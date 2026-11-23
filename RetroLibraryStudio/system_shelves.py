"""Read-only console presentation for the Windows game library.

Never infer an emulator from a color, icon or header. These helpers only arrange
already-scanned Entry objects; they perform no NAS I/O or ROM modification.
"""
from collections import Counter

# Visual order is deliberately independent of the on-disk layout.
PRIMARY_SYSTEMS = ('PSP', 'PS1', 'Nintendo DS', 'GBA', 'PS2', 'GameCube')
SYSTEM_ORDER = PRIMARY_SYSTEMS + (
    'GB', 'GBC', 'Nintendo 64', 'SNES', 'NES', 'Genesis', 'Dreamcast', 'Other'
)
# Accent colors are UI-only. System names match core.SYSTEM_DIR exactly.
VISUALS = {
    'PSP': ('PSP', 'PlayStation Portable', '#74B7FF', False),
    'PS1': ('PS1', 'Original PlayStation', '#B9A0FF', False),
    'PS2': ('PS2', 'PlayStation 2', '#F5A96D', True),
    'GameCube': ('GC', 'Nintendo GameCube', '#B98BFF', True),
    'Nintendo DS': ('DS', 'Nintendo DS', '#71DBC9', False),
    'GBA': ('GBA', 'Game Boy Advance', '#E8C678', False),
    'GB': ('GB', 'Game Boy', '#AAC4B0', False),
    'GBC': ('GBC', 'Game Boy Color', '#C1B4FF', False),
    'Nintendo 64': ('N64', 'Nintendo 64', '#8BCB98', False),
    'SNES': ('SNES', 'Super Nintendo', '#B8ACD6', False),
    'NES': ('NES', 'Nintendo Entertainment System', '#ED9A9A', False),
    'Genesis': ('MD', 'Sega Genesis', '#A3BBD5', False),
    'Dreamcast': ('DC', 'Sega Dreamcast', '#F6BA8B', False),
    'Other': ('?', 'Unclassified game files', '#9CABBC', False),
}


def console_visual(system: str) -> dict:
    short, full, accent, experimental = VISUALS.get(
        system, (system[:8], system, '#9CABBC', False))
    return {'short': short, 'name': full, 'accent': accent,
            'experimental': experimental}


def console_order_key(system: str) -> tuple:
    try:
        return (SYSTEM_ORDER.index(system), '')
    except ValueError:
        return (len(SYSTEM_ORDER), system.casefold())


def console_counts(entries) -> dict[str, int]:
    """Counts *logical gallery entries*, not BIN tracks or physical files."""
    return dict(Counter(e.system for e in entries))


def grouped_shelves(entries) -> list[tuple[str, list]]:
    """Stable within-system ordering, predictable system order, no mutations."""
    result = {}
    for entry in entries:
        result.setdefault(entry.system, []).append(entry)
    return [(system, result[system]) for system in sorted(result, key=console_order_key)]
