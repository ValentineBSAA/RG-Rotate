"""Non-destructive Windows 11 SDXC/exFAT card capacity *simulation*.

This module never formats, mounts, partitions, reserves or creates storage.
Filesystem parameters on a real microSD depend on the card and formatter.
The modeled exact arithmetic is NOT an exact measurement of actual capacity.
"""
from __future__ import annotations

from dataclasses import dataclass
from core import CAPACITY, COMPANION_BUDGET, FREE_RESERVE

# 128 KiB is a selectable Windows-style modeling assumption for this size.
# A different Windows/device formatter may choose a different allocation unit.
MODEL_CLUSTER_BYTES = 128 * 1024
PARTITION_START_BYTES = 1024 * 1024
EXFAT_BOOT_SECTORS = 24
SECTOR_BYTES = 512
UPCASE_TABLE_ESTIMATE = 6 * 1024


def round_up(size: int, block: int) -> int:
    if size < 0 or block <= 0:
        raise ValueError('Invalid allocation rounding input')
    return ((size + block - 1) // block) * block


def model_metadata_bytes(nominal: int = CAPACITY, cluster: int = MODEL_CLUSTER_BYTES) -> int:
    """Approximate partition offset, exFAT FAT, allocation bitmap and metadata.

    The model explicitly excludes unknown manufacturer spare capacity and the
    actual partition layout. It is suitable for planning, not exact labeling.
    """
    if nominal <= PARTITION_START_BYTES + cluster or cluster < 512 or cluster & (cluster - 1):
        raise ValueError('Unsupported virtual card capacity or allocation unit')
    clusters = (nominal - PARTITION_START_BYTES - EXFAT_BOOT_SECTORS * SECTOR_BYTES) // cluster
    # exFAT FAT contains one 4-byte entry per cluster; bitmap has 1 bit/cluster.
    fat = round_up(4 * (clusters + 2), cluster)
    bitmap = round_up((clusters + 7) // 8, cluster)
    upcase = round_up(UPCASE_TABLE_ESTIMATE, cluster)
    return PARTITION_START_BYTES + EXFAT_BOOT_SECTORS * SECTOR_BYTES + fat + bitmap + upcase


@dataclass(frozen=True)
class VirtualExfatPreview:
    nominal_bytes: int
    modeled_formatted_bytes: int
    estimated_format_bytes: int
    cluster_bytes: int
    staged_file_bytes: int
    estimated_cluster_padding_bytes: int
    estimated_allocated_bytes: int
    companion_remaining_bytes: int
    protected_free_bytes: int
    estimated_room_for_games: int
    estimated_unreserved_free: int
    over_budget: bool


def virtual_exfat_preview(staged: int, companion_used: int = 0, cluster_padding: int = 0,
                          nominal: int = CAPACITY, cluster: int = MODEL_CLUSTER_BYTES,
                          companion_budget: int = COMPANION_BUDGET,
                          reserve: int = FREE_RESERVE) -> VirtualExfatPreview:
    if min(staged, companion_used, cluster_padding, companion_budget, reserve) < 0:
        raise ValueError('Negative byte counts are invalid')
    if companion_used > staged:
        raise ValueError('Companion files cannot exceed all staged bytes')
    overhead = model_metadata_bytes(nominal, cluster)
    formatted = nominal - overhead
    allocated = staged + cluster_padding
    remaining_ai = max(0, companion_budget - companion_used)
    room = formatted - allocated - remaining_ai - reserve
    return VirtualExfatPreview(
        nominal, formatted, overhead, cluster, staged, cluster_padding,
        allocated, remaining_ai, reserve, max(0, room),
        max(0, formatted - allocated), room < 0 or companion_used > companion_budget
    )
