"""512 GB virtual planner and real measured destination safety checks."""
from pathlib import Path
from core import CAPACITY, GIB, COMPANION_BUDGET, FREE_RESERVE, prepare_layout
from card_capacity import planned_card_budget, physical_card_preview, decimal_gb, binary_gib
from sync_engine import make_plan
import pytest


def test_nominal_512gb_is_decimal_not_512_gib():
    empty = planned_card_budget(0)
    assert CAPACITY == 512_000_000_000
    assert decimal_gb(CAPACITY) == '512.00 GB'
    assert binary_gib(CAPACITY) == '476.84 GiB'
    assert empty.staged_percent == 0
    assert empty.game_room == CAPACITY - 2 * 8 * GIB
    assert empty.companion_remaining == COMPANION_BUDGET
    assert not empty.over_budget


def test_companion_reserved_only_once_and_grows_dynamically():
    staged = 9 * GIB
    companion = 3 * GIB
    usage = planned_card_budget(staged, companion)
    assert usage.companion_remaining == 5 * GIB
    assert usage.game_room == CAPACITY - staged - 5 * GIB - FREE_RESERVE
    assert usage.staged_percent == pytest.approx(staged / CAPACITY * 100)
    full_ai = planned_card_budget(staged, COMPANION_BUDGET)
    assert full_ai.companion_remaining == 0
    assert full_ai.game_room == CAPACITY - staged - FREE_RESERVE


def test_overfill_flags_and_no_negative_room():
    usage = planned_card_budget(CAPACITY - FREE_RESERVE // 2, 0)
    assert usage.game_room == 0 and usage.over_budget
    over = planned_card_budget(12 * GIB, 10 * GIB)
    assert over.companion_over_budget
    with pytest.raises(ValueError): planned_card_budget(5, 6)
    with pytest.raises(ValueError): planned_card_budget(-2)


def test_measured_physical_card_is_not_nominal_profile():
    p = physical_card_preview(499_000_000_000, 491_000_000_000, 2_000_000_000)
    assert p.capacity == 499_000_000_000
    assert p.occupied_before == 8_000_000_000
    assert p.occupied_after == 10_000_000_000
    assert p.free_after == 489_000_000_000
    assert p.fits


def test_physical_card_existing_files_not_counted_as_new():
    p = physical_card_preview(32 * GIB, 23 * GIB, 3 * GIB)
    assert p.occupied_before == 9 * GIB
    assert p.occupied_after == 12 * GIB
    assert p.free_after == 20 * GIB
    p = physical_card_preview(32 * GIB, 9 * GIB, 2 * GIB)
    assert not p.fits
    with pytest.raises(ValueError): physical_card_preview(32, 33, 0)


def test_real_transfer_preview_reports_card_capacity_too_small(tmp_path, monkeypatch):
    source = tmp_path / 'virtual'
    destination = tmp_path / 'card'
    prepare_layout(source)
    destination.mkdir()
    (source / 'ROMs' / 'psx' / 'sample.chd').write_bytes(b'GAME' * 10)
    import sync_engine
    class U: total = 12 * GIB; used = 0; free = 12 * GIB
    monkeypatch.setattr(sync_engine.shutil, 'disk_usage', lambda _: U())
    plan = make_plan(source, destination, simulation=False)
    assert plan.target_capacity == 12 * GIB
    assert any('capacity' in msg.lower() for msg in plan.conflicts)


def test_nominal_meter_uses_snapshot_no_fs_or_network_calls(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, 'disk_usage', lambda *_a: pytest.fail('unexpected NAS probe'))
    assert planned_card_budget(54400000).staged == 54400000
    assert physical_card_preview(100 * GIB, 80 * GIB, 4 * GIB).fits


@pytest.mark.parametrize('scale', [100, 125, 150])
def test_qt_capacity_strip_renders_without_filesystem_scan(tmp_path, monkeypatch, scale):
    """Installed Qt runs the real widget test in Windows/Linux GitHub CI."""
    pytest.importorskip('PySide6')
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings, Qt
    import app
    qt = QApplication.instance() or QApplication([])
    setting = QSettings(str(tmp_path/'settings.ini'), QSettings.Format.IniFormat)
    target = tmp_path/'VirtualCard'; target.mkdir()
    setting.setValue('workspace', str(target))
    monkeypatch.setattr(app, 'QSettings', lambda *args: setting)
    for method in ('offer_first_location','refresh','update_tools_status','update_workspace_location'):
        monkeypatch.setattr(app.Window, method, lambda *a, **kw: None)
    window = app.Window()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    window.scale_percent = scale
    window.apply_scale()
    window.show()
    qt.processEvents()
    try:
        window.staged_bytes = 2_450_000_000
        window.staged_companion = 1_000_000_000
        monkeypatch.setattr(Path, 'stat', lambda *_a, **_kw: pytest.fail('GUI tried a stat() call'))
        window.update_card_plan()
        assert '2.45 GB staged' in window.card_plan_amount.text()
        assert 'Room for new game files' in window.card_plan_note.text()
        assert window.card_plan_bar.capacity == CAPACITY
        assert window.card_plan_bar.used == 2_450_000_000
        window.navigate(1, refresh_apps=False)
        qt.processEvents()
        assert window.card_plan_bar.isVisible()
    finally:
        window.close()
