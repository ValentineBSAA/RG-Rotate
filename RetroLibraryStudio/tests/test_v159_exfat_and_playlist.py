"""v1.5.9: Real read-only worker protocol and non-destructive exFAT model.

The projection is NEVER a measurement of an uninserted microSD.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from core import Entry, CAPACITY, COMPANION_BUDGET, FREE_RESERVE, inventory, prepare_layout
from library_presentation import group_games, format_badge_info
from virtual_exfat import (MODEL_CLUSTER_BYTES, model_metadata_bytes, round_up,
                           virtual_exfat_preview)

ROOT = Path(__file__).resolve().parents[1]


def read_scan(card):
    completed = subprocess.run(
        [sys.executable, '-u', str(ROOT / 'readonly_scan.py'),
         '--mode', 'inventory', '--path', str(card)],
        capture_output=True, text=True, timeout=20)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    return json.loads(completed.stdout.splitlines()[-1])


def rehydrate(snapshot):
    """Match the Qt reconstruction, including the optional legacy row shape."""
    return [Entry(Path(row[0]), row[1], row[2], int(row[3]), row[4],
                  tuple(str(x) for x in row[5]) if len(row) > 5 else ())
            for row in snapshot['entries']]


def prepared_multidisc(card):
    folder = card / 'ROMs' / 'psx' / 'Resident Evil 2 (USA)'
    folder.mkdir(parents=True)
    disc1 = folder / 'Resident Evil 2 (USA) (Disc 1).chd'
    disc2 = folder / 'Resident Evil 2 (USA) (Disc 2).chd'
    disc1.write_bytes(b'CHD1' * 211)
    disc2.write_bytes(b'CHD2' * 258)
    m3u = folder / 'Resident Evil 2 (USA).m3u'
    m3u.write_text(disc1.name + '\n' + disc2.name + '\n')
    return folder, (disc1, disc2), m3u


def test_scan_round_trip_preserves_chd_playlist_members_and_badge(tmp_path):
    prepare_layout(tmp_path)
    folder, discs, playlist = prepared_multidisc(tmp_path)
    snapshot = read_scan(tmp_path)
    assert snapshot['type'] == 'result'
    assert snapshot['exfat_cluster_padding'] >= 0
    assert all(str(d) not in snapshot['disc_tracks'] for d in discs)
    assert len(snapshot['entries']) == 3
    entries = rehydrate(snapshot)
    m3u_entry = next(e for e in entries if e.extension == '.m3u')
    assert tuple(m3u_entry.members) == tuple(str(d.resolve()) for d in discs)
    collection = group_games(entries)
    assert len(collection) == 1
    assert collection[0][0].path == playlist
    assert len(collection[0]) == 3
    fmt = format_badge_info(collection[0][0], collection[0])
    assert fmt['badge'] == '2 DISCS'
    assert fmt['kind'] == 'M3U'
    assert 'separate CHDs' in fmt['description']
    assert snapshot['used'] == sum(p.stat().st_size for p in [*discs, playlist])


def test_broken_playlist_never_hides_chds_during_worker_scan(tmp_path):
    prepare_layout(tmp_path)
    _, discs, playlist = prepared_multidisc(tmp_path)
    playlist.write_text(discs[0].name + '\nmissing-disc2.chd\n')
    snapshot = read_scan(tmp_path)
    groups = group_games(rehydrate(snapshot))
    assert len(groups) == 3
    assert all(d.exists() for d in discs)


def test_empty_library_scan_has_zero_slack_and_no_format_side_effect(tmp_path):
    prepare_layout(tmp_path)
    snapshot = read_scan(tmp_path)
    assert snapshot['used'] == 0
    assert snapshot['exfat_cluster_padding'] == 0
    assert snapshot['entries'] == []
    assert not list(tmp_path.glob('**/*.img'))


def test_exfat_virtual_model_accounts_for_metadata_cluster_padding_and_budgets():
    nominal = CAPACITY
    model = virtual_exfat_preview(2_710_000_000, 0, 1024 * 1024)
    assert 0 < model.estimated_format_bytes < 50_000_000
    assert model.modeled_formatted_bytes == nominal - model.estimated_format_bytes
    assert model.estimated_allocated_bytes == 2_710_000_000 + 1024 * 1024
    assert model.companion_remaining_bytes == COMPANION_BUDGET
    assert model.protected_free_bytes == FREE_RESERVE
    assert model.estimated_room_for_games == (
        model.modeled_formatted_bytes - model.estimated_allocated_bytes
        - COMPANION_BUDGET - FREE_RESERVE)
    assert model.modeled_formatted_bytes < nominal
    assert virtual_exfat_preview(0).estimated_room_for_games > 490_000_000_000


def test_allocated_cluster_padding_one_pass_without_changing_files(tmp_path):
    prepare_layout(tmp_path)
    source = tmp_path / 'ROMs' / 'psx' / 'Tiny.chd'
    source.write_bytes(b'x' * 27)
    metrics = {'allocation_unit': MODEL_CLUSTER_BYTES}
    before = source.read_bytes()
    entries, used, count = inventory(tmp_path, metrics=metrics)
    assert used == 27 and count == 1 and len(entries) == 1
    assert metrics['cluster_padding'] == MODEL_CLUSTER_BYTES - 27
    assert source.read_bytes() == before
    assert not (tmp_path / 'VirtualExfat.img').exists()


@pytest.mark.parametrize('bad', [(-1, 0, 0), (10, 11, 0), (0, 0, -1)])
def test_exfat_rejects_invalid_counts(bad):
    with pytest.raises(ValueError):
        virtual_exfat_preview(*bad)


def test_exfat_budgets_report_overflow_not_false_free_space():
    model = virtual_exfat_preview(CAPACITY, 0, 0)
    assert model.over_budget
    assert model.estimated_room_for_games == 0
    assert round_up(129, 128) == 256
    assert model_metadata_bytes() == virtual_exfat_preview(0).estimated_format_bytes


@pytest.mark.parametrize('scale',[100,125,150])
def test_qt_shows_two_discs_and_virtual_exfat_model(tmp_path, monkeypatch, scale):
    pytest.importorskip('PySide6')
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtCore import Qt, QSettings
    from PySide6.QtWidgets import QApplication,QPushButton
    import app

    root = tmp_path/'Card'
    prepare_layout(root)
    _, discs, playlist = prepared_multidisc(root)
    snapshot = read_scan(root)
    qt = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / 'isolated.ini'), QSettings.Format.IniFormat)
    settings.setValue('workspace', str(root))
    monkeypatch.setattr(app, 'QSettings', lambda *args: settings)
    for method in ('offer_first_location','refresh','update_tools_status','update_workspace_location'):
        monkeypatch.setattr(app.Window, method, lambda *a,**kw: None)
    window = app.Window()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen,True)
    try:
        window.scale_percent=scale
        window.apply_scale()
        window.show()
        window.card_entries=rehydrate(snapshot)
        window.staged_bytes=snapshot['used']
        window.staged_cluster_padding=snapshot['exfat_cluster_padding']
        window.cue_tracks=set()
        window.update_card_plan()
        window.navigate(1, refresh_apps=False)
        window.fill_card()
        qt.processEvents()
        live=[window.gallery_grid.itemAt(i).widget() for i in range(window.gallery_grid.count())]
        tiles=[w for w in live if w.objectName()=='GameTile']
        assert len(tiles)==1
        assert any(b.text()=='2 DISCS' for b in tiles[0].findChildren(QPushButton))
        assert '1 games shown' in window.library_count.text()
        assert 'exFAT' in window.exfat_title.text()
        assert window.exfat_bar.capacity < CAPACITY
        assert window.card_plan_bar.capacity == CAPACITY
    finally:
        window.close()
        qt.processEvents()
