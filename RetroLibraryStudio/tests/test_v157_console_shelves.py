"""Console shelves: data-only grouping plus optional real Qt gallery smoke."""
import os
from pathlib import Path
import pytest
from core import Entry, ROM_EXT, SYSTEM_DIR, prepare_layout
from library_import import infer_system
from system_shelves import (console_counts, console_order_key,
                            console_visual, grouped_shelves)


def sample(name, system, extension='.iso'):
    path = Path('VirtualCard/ROMs') / SYSTEM_DIR[system] / (name + extension)
    return Entry(path, name, system, 1234, extension)


def test_shelves_sort_systems_without_rewriting_titles_or_paths():
    original = [
        sample('Wind Waker', 'GameCube', '.gcm'),
        sample('Clock Tower', 'PS1', '.chd'),
        sample('Socom Tactical Strike', 'PSP'),
        sample('Final Fantasy', 'PS1', '.chd'),
        sample('Spirit Caller', 'Nintendo DS', '.nds'),
        sample('Gran Turismo', 'PSP'),
        sample('Most Wanted', 'PS2'),
    ]
    before = list(original)
    sections = grouped_shelves(original)
    assert [system for system, _ in sections] == [
        'PSP', 'PS1', 'Nintendo DS', 'PS2', 'GameCube']
    assert [g.label for g in sections[0][1]] == ['Socom Tactical Strike', 'Gran Turismo']
    assert sum(map(len, (entries for _, entries in sections))) == len(original)
    assert original == before
    assert console_counts(original) == {
        'PSP': 2, 'PS1': 2, 'Nintendo DS': 1, 'PS2': 1, 'GameCube': 1}
    assert console_visual('PS2')['experimental']
    assert console_visual('GameCube')['experimental']
    assert not console_visual('PSP')['experimental']
    assert console_order_key('PSP') < console_order_key('PS1') < console_order_key('PS2')


def test_rom_classification_is_conservative_and_card_folders_are_distinct(tmp_path):
    root = tmp_path / 'Card'
    prepare_layout(root)
    assert (root / 'ROMs' / 'ps2').is_dir()
    assert (root / 'ROMs' / 'gc').is_dir()
    assert infer_system(Path('downloads/Mario.gcm'), 'PS1') == 'GameCube'
    assert infer_system(Path('downloads/Unknown.iso'), 'PS2') == 'PS2'
    assert infer_system(Path('downloads/Unknown.iso'), 'PS1') == 'PS1'
    assert infer_system(Path('downloads/Unknown.rvz'), 'GameCube') == 'GameCube'
    assert {'.gcm', '.gcz', '.rvz'} <= ROM_EXT


@pytest.mark.parametrize('scale', [100, 125, 150])
def test_qt_console_nav_filters_gallery_and_preserves_game_entries(tmp_path, monkeypatch, scale):
    pytest.importorskip('PySide6')
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtCore import QSettings, Qt
    from PySide6.QtWidgets import QApplication, QFrame, QPushButton
    import app

    qt = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / 'isolated.ini'), QSettings.Format.IniFormat)
    root = tmp_path / 'Card'; root.mkdir()
    settings.setValue('workspace', str(root))
    monkeypatch.setattr(app, 'QSettings', lambda *a: settings)
    for method in ('offer_first_location', 'refresh', 'update_tools_status', 'update_workspace_location'):
        monkeypatch.setattr(app.Window, method, lambda *a, **kw: None)
    monkeypatch.setattr(app, 'cached_preview', lambda *a: tmp_path / 'no-cover.png')
    window = app.Window()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    try:
        window.scale_percent = scale
        window.apply_scale()
        window.show()
        window.card_entries = [
            sample('Clock Tower', 'PS1', '.chd'),
            sample('Socom', 'PSP'),
            sample('Wind Waker', 'GameCube', '.gcm'),
            sample('Spirit Caller', 'Nintendo DS', '.nds'),
        ]
        window.navigate(1, refresh_apps=False)
        window.fill_card()
        qt.processEvents()
        # Qt deleteLater() keeps former child widgets alive briefly. Inspect
        # only the live grid-layout membership, not all parented descendants.
        def gallery_items(kind):
            layout = window.gallery_grid
            return [layout.itemAt(i).widget() for i in range(layout.count())
                    if layout.itemAt(i).widget().objectName() == kind]
        pills = window.console_nav_page.findChildren(QPushButton, 'SystemPill')
        assert len(gallery_items('ConsoleSection')) == 4
        assert len(pills) >= 7
        assert len(gallery_items('GameTile')) == 4
        assert '4 games shown' in window.library_count.text()
        # Both the legacy combo and the new tabs share the same selected system.
        window.game_filter.setCurrentText('GameCube')
        qt.processEvents()
        assert len(gallery_items('GameTile')) == 1
        assert len(gallery_items('ConsoleSection')) == 1
        assert '1 games shown' in window.library_count.text()
        window.set_gallery_mode('List')
        assert window.card_table.rowCount() == 1
        window.game_filter.setCurrentText('All systems')
        assert window.card_table.rowCount() == 4
    finally:
        window.close()
        qt.processEvents()
