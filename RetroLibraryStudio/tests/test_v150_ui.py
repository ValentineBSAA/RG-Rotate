"""Actual Qt widgets; isolated settings and local fixtures, no user NAS access."""
import os
from pathlib import Path
import pytest
from core import Entry
from library_presentation import group_games, gallery_columns, preferred_title


def test_disc_groups_preserve_editions_paths_and_original_entries():
    entries = [Entry(Path('ROMs/psx') / (name + '.cue'), name, 'PS1', 1, '.cue') for name in
               ('Resident Evil 2 (USA) (Disc 1)', 'Resident Evil 2 (USA) (Disc 2)', 'Resident Evil 2 Gore Edition (Disc 1)')]
    groups = group_games(entries)
    assert len(groups) == 2 and len(groups[0]) == 2
    assert groups[0][0] is entries[0] and groups[0][1] is entries[1]


def test_narrow_gallery_allows_one_column():
    assert gallery_columns(220, 150) == 1
    assert gallery_columns(1000, 100) == 5


@pytest.fixture(scope='module')
def qt():
    pytest.importorskip('PySide6')
    os.environ.setdefault('QT_QPA_PLATFORM', 'windows' if os.name == 'nt' else 'offscreen')
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(qt, tmp_path, monkeypatch):
    import app
    from PySide6.QtCore import QSettings, Qt
    settings = QSettings(str(tmp_path / 'isolated.ini'), QSettings.Format.IniFormat)
    settings.setValue('workspace', str(tmp_path / 'Card'))
    (tmp_path / 'Card').mkdir()
    monkeypatch.setattr(app, 'QSettings', lambda *a: settings)
    for name in ('offer_first_location', 'refresh', 'update_tools_status', 'update_workspace_location'):
        monkeypatch.setattr(app.Window, name, lambda *a, **k: None)
    widget = app.Window()
    widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    widget.show(); qt.processEvents()
    yield widget
    widget.close(); qt.processEvents()


@pytest.mark.parametrize('scale', [100, 110, 125, 140, 150])
@pytest.mark.parametrize('size', [(1240, 805), (900, 620)])
def test_primary_actions_visible_on_every_page(window, qt, scale, size):
    from PySide6.QtCore import QPoint
    window.scale_percent = scale; window.apply_scale(); window.resize(*size)
    for page in range(6):
        window.navigate(page, refresh_apps=False)
        for _ in range(4): qt.processEvents()
        for action in (window.page_action, window.page_secondary, window.transfer_btn):
            if action.isHidden(): continue
            point = action.mapTo(window, QPoint(0, 0))
            assert 0 <= point.x() and 0 <= point.y()
            assert point.x() + action.width() <= window.width()
            assert point.y() + action.height() <= window.height()
        assert window.settings.value('ui_scale', type=int) == scale
    assert window.width() <= max(size[0], 1060), 'Unexpected horizontal growth'


def test_settings_keep_preferred_title_and_window_geometry(window, qt):
    from artwork_gallery import game_key
    from PySide6.QtWidgets import QMainWindow
    entry = Entry(Path('Game.cue'), 'Game (USA)', 'PS1', 10, '.cue')
    key = 'titles/' + game_key(entry.system, entry.label)
    window.settings.setValue(key, 'My chosen edition title')
    assert preferred_title(window.settings, entry) == 'My chosen edition title'
    window.resize(1130, 730); window.move(35, 45); qt.processEvents()
    window.close()
    restored = QMainWindow()
    saved_geometry = window.settings.value('window_geometry')
    assert saved_geometry is not None
    assert restored.restoreGeometry(saved_geometry)
    assert restored.width() > 0 and restored.height() > 0
    # Headless CI's virtual screen can be narrower than the app's 900px
    # minimum width. Qt then clamps restored windows to visible bounds.
    # Enforce exact geometry on actual sufficiently large displays only.
    available = qt.primaryScreen().availableGeometry()
    if available.width() >= window.width() + 2 and available.height() >= window.height() + 2:
        assert restored.size() == window.size()
    assert window.settings.value(key) == 'My chosen edition title'
    restored.close()


def test_setup_and_disc_work_use_process_worker(window, monkeypatch):
    import app
    calls = []
    monkeypatch.setattr(window, 'ensure_workspace', lambda: True)
    monkeypatch.setattr(app.QMessageBox, 'question', lambda *a, **k: app.QMessageBox.StandardButton.Yes)
    monkeypatch.setattr(window, 'start_import_process', lambda *args: calls.append(args))
    window.prepare_essentials(['Cocoon Shell', 'CHDman'])
    assert calls[0][0]['mode'] == 'setup'
    assert calls[0][0]['names'] == ['Cocoon Shell', 'CHDman']


def test_transfer_preview_never_reuses_previous_completion(window):
    window.copy_meter.setValue(1000)
    window._reset_copy_display('New preview: not hash verified')
    assert window.copy_meter.value() == 0
    assert 'New preview' in window.copy_detail.text()


def test_destination_hint_never_stats_network_paths(window, monkeypatch):
    window.target = Path('//NAS/Unavailable/Practice')
    def forbid(*args, **kwargs): raise AssertionError('GUI thread touched the NAS')
    monkeypatch.setattr(Path, 'is_dir', forbid)
    monkeypatch.setattr(Path, 'stat', forbid)
    window.update_destination_hint()
    assert 'NAS' in window.dest_name.text()
