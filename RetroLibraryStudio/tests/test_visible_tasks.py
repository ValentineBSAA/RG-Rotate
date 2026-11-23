"""Downloads scans are opt-in; cancellation interrupts inventory."""
import ast
import threading
from pathlib import Path
from core import inventory, incoming_inventory


def test_cancelled_manual_download_scan_stops(tmp_path):
    for i in range(7):
        (tmp_path / f"game{i}.gba").write_bytes(b"1")
    stop = threading.Event(); stop.set()
    result, used = incoming_inventory(tmp_path, cancel=stop)
    assert result == [] and used == 0


def test_cancelled_virtual_inventory_stops(tmp_path):
    roms = tmp_path / "ROMs" / "gba"; roms.mkdir(parents=True)
    (roms / "game.gba").write_bytes(b"game")
    stop = threading.Event(); stop.set()
    assert inventory(tmp_path, cancel=stop) == ([],0,0)


def test_gui_does_not_automatically_scan_downloads_on_startup():
    path = Path(__file__).resolve().parents[1] / "app.py"
    root = ast.parse(path.read_text(encoding="utf-8"))
    cls = next(node for node in root.body if isinstance(node, ast.ClassDef) and node.name == 'Window')
    method = lambda name: next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name==name)
    def calls(method_name):
        return [n.func.attr for n in ast.walk(method(method_name)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    assert 'incoming_inventory' not in calls('__init__')
    assert 'incoming_inventory' not in calls('refresh')
    assert any(isinstance(n, ast.Name) and n.id=='incoming_inventory' for n in ast.walk(method('find_downloads')))
    assert 'refresh_timer' not in path.read_text(encoding='utf-8')


def test_theme_renders_without_qt_runtime():
    # Extract the pure theme function to catch f-string stylesheet mistakes
    # without requiring PySide6 to be installed on the test machine.
    source = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    definition = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name=="theme")
    scope = {}
    exec(compile(ast.Module(body=[definition], type_ignores=[]), "theme", "exec"), scope)
    css = scope["theme"](125)
    assert "QLabel#Activity {color:#a8ddff" in css
    assert "selection-background-color:#66b3ff" in css
