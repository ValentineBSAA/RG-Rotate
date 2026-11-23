"""Pure storage math for virtual-card planning and measured physical cards.

The 512 GB size is a marketed nominal capacity, not an allocated image or a
promise of physical formatted space. Bytes are authoritative; UI may round.
"""
from dataclasses import dataclass
from core import CAPACITY, COMPANION_BUDGET, FREE_RESERVE


@dataclass(frozen=True)
class CardBudget:
    capacity: int
    staged: int
    companion_used: int
    companion_remaining: int
    protected_free: int
    game_room: int
    unallocated: int
    staged_percent: float
    over_budget: bool
    companion_over_budget: bool


def planned_card_budget(staged: int, companion_used: int = 0, capacity: int = CAPACITY,
                        companion_budget: int = COMPANION_BUDGET,
                        protected_free: int = FREE_RESERVE) -> CardBudget:
    """Account for companion *already in staged* exactly once.

    Reserved AI space is a budget for *future* content, not an empty file; the
    protected free minimum is distinct. An overfull card is never advertised
    as safe simply because the meter was clamped for drawing.
    """
    if min(staged, companion_used, capacity, companion_budget, protected_free) < 0:
        raise ValueError('Storage byte counts cannot be negative')
    if companion_used > staged:
        raise ValueError('CompanionData cannot exceed all staged bytes')
    companion_remaining = max(0, companion_budget - companion_used)
    game_room = max(0, capacity - staged - companion_remaining - protected_free)
    raw_free = capacity - staged - companion_remaining - protected_free
    return CardBudget(capacity, staged, companion_used, companion_remaining,
                      protected_free, game_room, max(0, capacity - staged),
                      100.0 * staged / max(1, capacity),
                      raw_free < 0, companion_used > companion_budget)


@dataclass(frozen=True)
class PhysicalCardPreview:
    capacity: int
    occupied_before: int
    queued_new_bytes: int
    occupied_after: int
    free_after: int
    protected_free: int
    fits: bool


def physical_card_preview(capacity: int, free_before: int, queued_new_bytes: int,
                          protected_free: int = FREE_RESERVE) -> PhysicalCardPreview:
    """Use measured filesystem values from transfer preview, not 512 GB guess.

    Files already present are counted only in occupied_before; name/size
    matches have *not* been SHA-256-verified until transfer actually runs.
    """
    if capacity <= 0 or min(free_before, queued_new_bytes, protected_free) < 0 or free_before > capacity:
        raise ValueError('Invalid physical card preview')
    occupied = capacity - free_before
    free_after = free_before - queued_new_bytes
    return PhysicalCardPreview(capacity, occupied, queued_new_bytes,
                               occupied + queued_new_bytes, free_after,
                               protected_free, free_after >= protected_free)


def decimal_gb(n: int) -> str:
    return f'{n / 1_000_000_000:,.2f} GB'


def binary_gib(n: int) -> str:
    return f'{n / (1024**3):,.2f} GiB'
