"""Retro Library Studio 1.5.0 | Cocoon APK Detection and NAS Safety / Windows PySide6 RG Rotate preparation.

Simple, non-destructive workflow: Welcome -> Add Games -> Apps & Tools -> Copy.
Core import, archive and verified transfer engines are reused from 1.0.0.
"""
from __future__ import annotations

import os
import sys
import json
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, QObject, QRunnable, QThreadPool, QSettings, QTimer, Signal, QUrl, QProcess, QPropertyAnimation
from PySide6.QtGui import QFont, QDesktopServices, QIcon, QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QFrame, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QStackedWidget, QComboBox, QProgressBar,
    QFileDialog, QCheckBox, QMessageBox, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QPlainTextEdit, QDialog, QDialogButtonBox,
    QSplitter, QInputDialog, QSizePolicy, QListView, QListWidget, QListWidgetItem,
    QStyledItemDelegate, QStyleOptionViewItem, QStyle, QGraphicsOpacityEffect, QMenu,
)

from core import (CAPACITY, COMPANION_BUDGET, FREE_RESERVE, SYSTEM_DIR, SUPPORTED,
                  Entry, prepare_layout, inventory, incoming_inventory, import_files,
                  pretty_bytes, safe_walk, within)
from sync_engine import SyncPlan, make_plan, transfer_verified
from transfer_feedback import preview_explanation, copy_explanation
from card_capacity import planned_card_budget, physical_card_preview, decimal_gb, binary_gib
from drives import list_windows_volumes, validate_physical_root
from destination_mode import is_volume_root, restore_destination_mode
from software import SOFTWARE, download_selected
from tool_setup import tool_status, tools_root, install_selected, ADB_DOCS, CHDMAN_DOCS, validate_installed_chdman
from health import inspect_library
from android_setup import connected_devices, install_local_apks
from library_import import infer_system, import_grouped
from apk_import import stage_local_apks, staged_apks
from batch_setup import prepare_batch, readiness, RECOMMENDED, DESCRIPTION
from storage_probe import (check_space_bounded, is_network_path, usable_stage_bytes,
                           has_workspace_payload_fast, describe_bytes)
from artwork import add_local_cover, fetch_cover_batch, unique_game_art_entries
from artwork_gallery import clean_title, cached_preview, local_index, game_key
from chd_convert import convert_cue, verify_tool
from library_presentation import group_games, preferred_title, gallery_columns, format_badge_info
from system_shelves import (PRIMARY_SYSTEMS, console_counts, console_order_key,
                            console_visual, grouped_shelves)
from workspace_setup import suggested_workspace, copy_existing_workspace, count_workspace_files

VERSION = '1.5.8 Beta – Smart Multi-disc Collections'
SCALE_CHOICES = [('100%', 100), ('110%', 110), ('125%', 125), ('140%', 140), ('150%', 150)]
MAX_VISIBLE_FILES = 1200


def theme(scale: int) -> str:
    k = scale / 100
    def px(n): return f'{round(n*k)}px'
    return f"""
    QWidget {{color:#eaf2ff; background:transparent; font-family:'Segoe UI'; font-size:{px(13)};}}
    QMainWindow, QWidget#Shell {{background:#0b1020;}}
    QFrame#Sidebar {{background:#101a2d; border-right:1px solid #24344f;}}
    QFrame#Card {{background:#141f34; border:1px solid #293d59; border-radius:{px(16)};}}
    QFrame#SubCard {{background:#1b2941; border:1px solid #2c4160; border-radius:{px(12)};}}
    QLabel#H1 {{font-size:{px(26)}; font-weight:800; color:#f8faff;}}
    QLabel#H2 {{font-size:{px(20)}; font-weight:750; color:#f7faff;}}
    QLabel#Brand {{font-size:{px(19)}; font-weight:800; color:#f7faff;}}
    QLabel#Subtitle {{font-size:{px(13)}; color:#a7bad5;}}
    QLabel#Small {{font-size:{px(12)}; color:#a6bbd6;}}
    QLabel#HeroNumber {{font-size:{px(27)}; font-weight:800; color:white;}}
    QLabel#StepNumber {{font-size:{px(15)}; font-weight:800; color:#8ab9ff;}}
    QPushButton {{background:#243854; border:1px solid #355071; border-radius:{px(10)};
                  padding:{px(11)} {px(16)}; color:#eaf2ff; font-weight:650;}}
    QPushButton:hover {{background:#315071; border-color:#55789c;}}
    QPushButton:focus {{border:2px solid #b3dcff;}}
    QTableWidget::item:selected {{background:#70b8ff; color:#061e37;}}
    QPushButton:disabled {{background:#18263b; color:#798ca7; border-color:#26354b;}}
    QPushButton#Primary {{background:#72a6ff; color:#09162b; border:1px solid #72a6ff;}}
    QPushButton#Primary:hover {{background:#94bdff;}}
    QPushButton#Accent {{background:#214e4d; border:1px solid #337f74; color:#baf7e6;}}
    QPushButton#Accent:hover {{background:#2b6963;}}
    QPushButton#Nav {{background:transparent; border:0; text-align:left; padding:{px(12)} {px(14)};
                     border-radius:{px(10)}; color:#bdcce4;}}
    QPushButton#Nav:hover {{background:#1f3450; color:white;}}
    QPushButton#Nav[active="true"] {{background:#294969; color:#ecf6ff;}}
    QLineEdit,QComboBox {{background:#1b2a43; border:1px solid #3a5273; border-radius:{px(9)};
                         padding:{px(10)}; color:#f3f7ff;}}
    QComboBox::drop-down {{border:0; min-width:{px(26)};}}
    QComboBox QAbstractItemView {{background:#172944; color:#f3f7ff; border:2px solid #6caeff;
             outline:0; selection-background-color:#66b3ff; selection-color:#081c32;
             padding:{px(4)};}}
    QListWidget#CoverSearchResults {{background:#14263e; border:1px solid #466a92; border-radius:8px; color:#f5faff;}}
    QListWidget#CoverSearchResults::item:selected {{background:#70b8ff; color:#061e37;}}
    QListView#SystemOptions {{background:#172944; border:2px solid #6caeff;
             color:#f3f7ff; outline:0;}}
    QLabel#Activity {{color:#a8ddff; font-weight:800; font-size:{px(13)};}}
    QFrame#ConsoleSection {{background:#16283f; border:1px solid #334d70; border-radius:{px(11)};}}
    QPushButton#SystemPill {{background:#1c2d47; border:1px solid #36516f;
                             border-radius:{px(14)}; padding:{px(9)} {px(13)};}}
    QPushButton#SystemPill:hover {{background:#2a476b; border-color:#72baff;}}
    QFrame#GameTile {{background:#1b2b46; border:1px solid #395574; border-radius:{px(14)};}}
    QPushButton#FormatBadge {{background:#29415d; color:#cfe3ff; border:1px solid #698cad;
               border-radius:{px(8)}; padding:{px(5)} {px(10)}; font-weight:800;}}
    QPushButton#FormatBadge:hover {{background:#3b628c; color:#ffffff;}}
    QMenu#GameContext {{background:#172944; color:#f2f8ff; border:1px solid #6b95bb;
                     padding:{px(9)}; border-radius:{px(12)};}}
    QMenu#GameContext::item {{padding:{px(11)} {px(22)}; border-radius:{px(7)};}}
    QMenu#GameContext::item:selected {{background:#3c658c; color:#ffffff;}}
    QMenu#GameContext::separator {{height:1px; background:#354f70; margin:{px(7)} {px(11)};}}
    QPushButton#FormatBadge[formatKind="CHD"] {{background:#194d48; color:#aaffdf; border-color:#399e86;}}
    QPushButton#FormatBadge[formatKind="BIN+CUE"] {{background:#51432b; color:#ffe5ac; border-color:#b9944c;}}
    QPushButton#FormatBadge[formatKind="M3U"] {{background:#3f3462; color:#e5d2ff; border-color:#9069bd;}}
    QFrame#GameTile:hover {{border:1px solid #6eacff; background:#223756;}}
    QLabel#CoverPreview {{background:#102039; border:1px solid #355276; border-radius:{px(9)};
                          color:#94aed1; font-size:{px(16)}; font-weight:700;}}
    QPushButton#ViewOption {{background:#203653; border:1px solid #385777;}}
    QPushButton#ViewOption[active="true"] {{background:#71a7fd; color:#08152b; border-color:#96c7ff;}}
    QFrame#LocationStrip {{background:#162b44; border:1px solid #49719b; border-radius:{px(12)};}}
    QLabel#LocationPath {{font-weight:750; color:#e9f6ff; font-size:{px(13)};}}
    QLabel#InstallerState[mode="ready"] {{color:#8ff1c4; font-weight:700;}}
    QLabel#InstallerState[mode="working"] {{color:#a6d4ff; font-weight:700;}}
    QLabel#InstallerState[mode="error"] {{color:#ffc18c; font-weight:700;}}
    QLabel#InstallerState[mode="pending"] {{color:#a7bad5;}}
    QFrame#DropZone {{background:#132b43; border:2px dashed #5a91c4;
                      border-radius:{px(14)};}}
    QFrame#DropZone[dragActive="true"] {{background:#254a6b; border:2px solid #9bd3ff;}}
    QLabel#DropHint {{color:#b5d8f3; font-weight:650;}}
    QProgressBar {{background:#263751; border:0; border-radius:{px(7)}; text-align:center;
                   min-height:{px(15)}; color:white; font-weight:700;}}
    QProgressBar::chunk {{background:#6cabff; border-radius:{px(7)};}}
    QTableWidget {{background:#111d31; border:1px solid #304560; border-radius:{px(10)};
                   gridline-color:#20344e; selection-background-color:#325678; alternate-background-color:#182840;}}
    QHeaderView::section {{background:#243850; padding:{px(10)}; font-weight:700; border:none;}}
    QPlainTextEdit {{background:#101b2e; border:1px solid #293f5b; border-radius:{px(10)}; padding:{px(10)};}}
    QScrollArea {{border:0; background:transparent;}}
    QScrollBar:vertical {{background:#101a2c; width:{px(12)};}}
    QScrollBar::handle:vertical {{background:#395778; min-height:{px(28)}; border-radius:{px(5)};}}
    QCheckBox {{spacing:{px(9)};}}
    """


class HighlightDelegate(QStyledItemDelegate):
    """Strong selected/hover rows even when Windows would show a weak Qt popup."""
    def paint(self, painter, option, index):
        if option.state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver):
            painter.save()
            painter.fillRect(option.rect, QColor('#79c1ff'))
            painter.setPen(QColor('#071b31'))
            painter.drawText(option.rect.adjusted(12, 0, -6, 0),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             str(index.data(Qt.ItemDataRole.DisplayRole) or ''))
            painter.restore()
            return
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        hint = super().sizeHint(option, index)
        hint.setHeight(max(hint.height(), 37))
        return hint


class FileDropZone(QFrame):
    """One file/folder drop surface; Windows Explorer drops are local paths only."""
    dropped = Signal(list)

    def __init__(self, heading: str, detail: str):
        super().__init__()
        self.setObjectName('DropZone')
        self.setAcceptDrops(True)
        self.setProperty('dragActive', False)
        self.setMinimumHeight(98)
        l = QVBoxLayout(self); l.setContentsMargins(20, 13, 20, 13); l.setSpacing(6)
        top = label(heading, 'DropHint'); top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip = label(detail, 'Small', True); tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for w in (top, tip):
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            l.addWidget(w)

    def _highlight(self, value: bool):
        self.setProperty('dragActive', value)
        self.style().unpolish(self); self.style().polish(self)
        self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(url.isLocalFile() for url in event.mimeData().urls()):
            event.acceptProposedAction()
            self._highlight(True)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._highlight(False)
        event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: event.ignore()

    def dropEvent(self, event):
        self._highlight(False)
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.dropped.emit(paths)
            event.acceptProposedAction()
        else:
            event.ignore()


class Signals(QObject):
    done = Signal(object)
    failed = Signal(str)
    progress = Signal(str, int, int)
    copy_progress = Signal(str, int, int, str, float, float)
    app_state = Signal(str, str)


class Job(QRunnable):
    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func, self.args, self.kwargs = func, args, kwargs
        self.signals = Signals()

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as exc:
            self.signals.failed.emit(f'{type(exc).__name__}: {exc}')
        else:
            self.signals.done.emit(result)


def label(text: str, style: str = '', wrap: bool = False) -> QLabel:
    w = QLabel(text)
    if style: w.setObjectName(style)
    w.setWordWrap(wrap or style in ('H1', 'H2', 'Brand'))
    return w


def button(text: str, slot: Callable, kind: str = '') -> QPushButton:
    b = QPushButton(text)
    if kind: b.setObjectName(kind)
    b.clicked.connect(slot)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


def card_layout(parent: QVBoxLayout, title: str | None = None, detail: str | None = None) -> QVBoxLayout:
    frame = QFrame(); frame.setObjectName('Card')
    col = QVBoxLayout(frame)
    col.setContentsMargins(21, 18, 21, 19); col.setSpacing(11)
    if title: col.addWidget(label(title, 'H2'))
    if detail: col.addWidget(label(detail, 'Subtitle', True))
    parent.addWidget(frame)
    return col


def expandable(parent, title, detail=None):
    frame = QFrame(); frame.setObjectName('Card'); outer = QVBoxLayout(frame)
    toggle = QPushButton(title + '  +'); toggle.setCheckable(True)
    outer.addWidget(toggle)
    content = QWidget(); layout = QVBoxLayout(content)
    if detail: layout.addWidget(label(detail, 'Small', True))
    content.setVisible(False); outer.addWidget(content); parent.addWidget(frame)
    def expand(checked):
        content.setVisible(checked); toggle.setText(title + ('  −' if checked else '  +'))
        if checked and QApplication.style().styleHint(QStyle.StyleHint.SH_Widget_Animate):
            effect = QGraphicsOpacityEffect(content); content.setGraphicsEffect(effect)
            animation = QPropertyAnimation(effect, b'opacity', content)
            animation.setDuration(140); animation.setStartValue(0.25); animation.setEndValue(1.0)
            content.reveal_animation = animation; animation.start()
    toggle.toggled.connect(expand)
    return layout


def page(title: str, subtitle: str) -> tuple[QWidget, QVBoxLayout]:
    outer = QWidget()
    layout = QVBoxLayout(outer)
    layout.setContentsMargins(0, 0, 5, 3); layout.setSpacing(17)
    layout.addWidget(label(title, 'H1'))
    layout.addWidget(label(subtitle, 'Subtitle', True))
    return outer, layout


def scroll_page(widget: QWidget) -> QScrollArea:
    view = QScrollArea(); view.setWidgetResizable(True)
    view.setWidget(widget); view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return view




class FittedCoverPreview(QLabel):
    """Scale cached cover image to the *actual* preview space, without clipping.

    Only an in-memory pixmap is used during resize: no network/SMB operations.
    """
    def __init__(self, text=''):
        super().__init__(text)
        self._original = QPixmap()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

    def set_cover(self, image):
        self._original = QPixmap(image)
        self._fit()

    def clear_cover(self, text=''):
        self._original = QPixmap()
        self.setPixmap(QPixmap())
        self.setText(text)

    def _fit(self):
        if self._original.isNull():
            return
        available = self.contentsRect().size()
        if available.width() < 10 or available.height() < 10:
            return
        self.setPixmap(self._original.scaled(available, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()


class CardFillMeter(QWidget):
    """Read-only segmented storage meter. Rendering never performs file I/O."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.capacity = CAPACITY
        self.used = 0
        self.queued = 0
        self.ai_remaining = COMPANION_BUDGET
        self.reserve = FREE_RESERVE
        self.setMinimumHeight(21)
        self.setMaximumHeight(26)
        self.setToolTip('Blue: files already staged; teal: pending copy; purple: AI budget; gold: free-space reserve.')

    def set_bytes(self, capacity, used, queued=0, ai_remaining=0, reserve=FREE_RESERVE):
        self.capacity = max(1, int(capacity))
        self.used = max(0, int(used))
        self.queued = max(0, int(queued))
        self.ai_remaining = max(0, int(ai_remaining))
        self.reserve = max(0, int(reserve))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 1, -1, -2)
        if rect.width() <= 0 or rect.height() <= 0:
            p.end(); return
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#263950'))
        p.drawRoundedRect(rect, 7, 7)
        p.setClipRect(rect)
        w, y, h = rect.width(), rect.y(), rect.height()
        denominator = max(1, self.capacity)
        used_width = min(w, round(w * self.used / denominator))
        queued_width = min(max(0, w - used_width), round(w * self.queued / denominator))
        ai_width = min(w, round(w * self.ai_remaining / denominator))
        reserved_width = min(w, round(w * self.reserve / denominator))
        if self.used and used_width == 0: used_width = 1
        if self.queued and queued_width == 0 and used_width < w: queued_width = 1
        if used_width: p.fillRect(0, y, used_width, h, QColor('#4DA8FF'))
        if queued_width: p.fillRect(used_width, y, queued_width, h, QColor('#3ED1B6'))
        ai_left = min(w, max(used_width + queued_width, w - reserved_width - ai_width))
        if ai_width and ai_left < w - reserved_width:
            p.fillRect(ai_left, y, min(ai_width, w - reserved_width - ai_left), h, QColor('#AA83DE'))
        if reserved_width:
            p.fillRect(w - reserved_width, y, reserved_width, h, QColor('#D5AB64'))
        p.end()


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('RetroLibraryStudio', 'RetroLibraryStudio')
        self.scale_percent = int(self.settings.value('ui_scale', 100))
        if self.scale_percent not in [n for _, n in SCALE_CHOICES]: self.scale_percent = 100
        default = Path.home() / 'Documents' / 'Retro Library Studio' / 'VirtualCard'
        saved_workspace = self.settings.value('workspace', '')
        self.needs_workspace_setup = not bool(saved_workspace)
        self.workspace = Path(str(saved_workspace or default))
        # A disconnected NAS must never stall the UI before the window appears.
        network_workspace = is_network_path(self.workspace)
        self.previous_location_missing = (bool(saved_workspace) and not network_workspace
                                          and not self.workspace.is_dir())
        if self.previous_location_missing:
            self.needs_workspace_setup = True
        self.incoming = Path(str(self.settings.value('incoming', str(Path.home() / 'Downloads'))))
        saved_target = str(self.settings.value('target', '') or '')
        self.target: Path | None = Path(saved_target) if saved_target else None
        self.default_practice_folder = Path.home() / 'Documents' / 'Retro Library Studio' / 'PracticeTransfer'
        self.saved_destination_mode = restore_destination_mode(
            self.target, str(self.settings.value('target_mode', '') or ''), self.default_practice_folder)
        if self.saved_destination_mode in ('practice', 'physical'):
            # Migrate known v1.4.3 destinations into explicit persisted mode settings.
            self.settings.setValue('target_mode', self.saved_destination_mode)
        if not network_workspace and self.workspace.is_dir():
            try:
                prepare_layout(self.workspace)
            except OSError:
                self.needs_workspace_setup = True
        self.card_entries: list[Entry] = []
        self.incoming_entries: list[Entry] = []
        self.staged_bytes = 0
        self.staged_files = 0
        self.staged_companion = 0
        self.last_physical_plan = None
        self.current_task = False
        self.current_task_name = ''
        self.scan_process = None  # Disposable child; safe to terminate for READ-ONLY scans.
        self.import_process = None  # Writes run in their own process, never a stuck GUI thread.
        self.import_output = ''
        self.import_error = ''
        self.import_result = None
        self.import_stopped = False
        self.import_finished_callback = None
        self.import_kind = "games"
        self.artwork_process = None
        self.transfer_process = None  # Isolated preview and copy helper, including NAS SMB reads.
        self.transfer_output = ''
        self.transfer_error = ''
        self.transfer_result = None
        self.transfer_stopped = False
        self.transfer_mode = ''
        self.transfer_simulation = False
        self.transfer_on_plan = None
        self.manual_cover_dialog = None
        self.manual_cover_entry = None
        self.artwork_result = None
        self.artwork_error = ''
        self.artwork_output = ''
        self.artwork_stopped = False
        self.artwork_mode = ''
        self.cover_index = local_index(self.workspace)
        self.pending_auto_artwork = False
        self.gallery_visible_cap = 48
        self.gallery_mode = str(self.settings.value('gallery_mode', 'Gallery'))
        self.scan_output = ''
        self.scan_result = None
        self.scan_error = ''
        self.scan_cancelled = False
        self.scan_finished_callback = None
        self.scan_mode = None
        self.close_when_idle = False
        self.cancel_requested = False
        self.cancel_signal = threading.Event()
        self.pool = QThreadPool(self); self.pool.setMaxThreadCount(1)
        self.space_pool = QThreadPool(self); self.space_pool.setMaxThreadCount(1)
        self.space_generation = 0
        self.latest_space = None
        self.task_buttons: list[QPushButton] = []
        self.pending_workspace_picker = False
        self.pending_workspace_destination: Path | None = None
        self.nav_buttons: list[QPushButton] = []
        self.setWindowTitle(f'Retro Library Studio  •  RG Rotate  •  {VERSION}')
        self.setMinimumSize(900, 620)
        self.resize(1240, 805)
        self.create_ui()
        self.apply_scale()
        geometry = self.settings.value('window_geometry')
        if geometry: self.restoreGeometry(geometry)
        state = self.settings.value('window_state')
        if state: self.restoreState(state)
        # The location is presented before any expensive inventory. Do not scan
        # Downloads or perform a hidden recursive scan on a new installation.
        self.update_workspace_location()
        if self.needs_workspace_setup:
            self.home_room.setText('Choose a PC folder to begin')
            self.home_hint.setText('Start by selecting where your virtual microSD should live on this PC.')
            self.task_title.setText('Ready • Choose your virtual card folder')
            self.status.setText('Nothing is being downloaded or scanned yet.')
        if self.needs_workspace_setup:
            QTimer.singleShot(0, self.offer_first_location)
        else:
            QTimer.singleShot(100, self.refresh)

    def closeEvent(self, event):
        if self.current_task:
            reply = QMessageBox.question(self, 'Finish safely before closing',
                f'Currently working on: {self.current_task_name or "Current task"}\n\n'
                'Stop the operation, then close automatically when it is safe?\n'
                'Your original files will be kept.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore(); return
            self.close_when_idle = True
            self.pending_workspace_picker = False
            self.cancel()
            event.ignore(); return
        self.settings.setValue('window_geometry', self.saveGeometry())
        self.settings.setValue('window_state', self.saveState())
        self.settings.setValue('ui_scale', self.scale_percent)
        super().closeEvent(event)

    def apply_scale(self):
        self.setStyleSheet(theme(self.scale_percent))
        font = QFont('Segoe UI'); font.setPointSizeF(9.8 * self.scale_percent / 100)
        self.setFont(font)
        if hasattr(self, 'sidebar'): self.sidebar.setFixedWidth(round(205 * min(1.15, self.scale_percent/100)))
        if hasattr(self, 'scale_combo'):
            self.scale_combo.blockSignals(True)
            self.scale_combo.setCurrentIndex([n for _,n in SCALE_CHOICES].index(self.scale_percent))
            self.scale_combo.blockSignals(False)
        self.settings.setValue('ui_scale', self.scale_percent)
        if getattr(self, 'card_entries', None) and hasattr(self, 'gallery_grid'):
            self.fill_card()

    def change_scale(self, index: int):
        self.scale_percent = SCALE_CHOICES[index][1]
        self.apply_scale()
        self.set_status(f'Interface scaled to {self.scale_percent}%. Size and position are remembered.')

    def create_ui(self):
        shell = QWidget(); shell.setObjectName('Shell'); self.setCentralWidget(shell)
        base = QHBoxLayout(shell); base.setContentsMargins(0,0,0,0); base.setSpacing(0)
        self.sidebar = QFrame(); self.sidebar.setObjectName('Sidebar')
        sl = QVBoxLayout(self.sidebar); sl.setContentsMargins(16,22,16,16); sl.setSpacing(9)
        sl.addWidget(label('Retro Library', 'Brand', True))
        sl.addWidget(label('RG Rotate setup', 'Small'))
        sl.addSpacing(22)
        navs = [
            ('⌂   Start', 0), ('▣   Add games', 1), ('✦   Prepare apps', 2),
            ('⇄   Copy to card', 3), ('✓   Library check', 4), ('⚙   Preferences', 5)]
        for text, index in navs:
            nav = button(text, lambda _=False, i=index: self.navigate(i), 'Nav')
            nav.setProperty('active', index==0)
            sl.addWidget(nav); self.nav_buttons.append(nav)
        sl.addStretch()
        sl.addWidget(label('Made for your 512 GB card', 'Small', True))
        sl.addWidget(label('Cocoon Shell • Default', 'Small'))
        base.addWidget(self.sidebar)
        right = QWidget()
        r = QVBoxLayout(right); r.setContentsMargins(24,15,23,17); r.setSpacing(11)
        toolbar = QHBoxLayout()
        toolbar.addWidget(label('Retro Library Studio', 'Subtitle'))
        toolbar.addStretch()
        toolbar.addWidget(label('VIEW SIZE', 'Small'))
        self.scale_combo = QComboBox()
        for text, pct in SCALE_CHOICES: self.scale_combo.addItem(text, pct)
        self.scale_combo.currentIndexChanged.connect(self.change_scale)
        toolbar.addWidget(self.scale_combo)
        r.addLayout(toolbar)
        location = QFrame(); location.setObjectName('LocationStrip')
        loc_layout = QHBoxLayout(location); loc_layout.setContentsMargins(14, 10, 14, 10)
        loc_text = QVBoxLayout(); loc_text.setSpacing(2)
        loc_text.addWidget(label('Your library folder on PC or NAS', 'Small'))
        self.active_workspace_label = label('Choose a folder for your virtual card', 'LocationPath', True)
        self.active_workspace_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        loc_text.addWidget(self.active_workspace_label)
        self.active_disk_free = label('', 'Small', True); loc_text.addWidget(self.active_disk_free)
        loc_layout.addLayout(loc_text, 1)
        self.location_button = button('Choose location…', self.choose_workspace, 'Primary')
        loc_layout.addWidget(self.location_button)
        # Open folder remains on Home and Library; keep this strip compact.
        self.capacity_button = button('Check storage', self.check_workspace_space)
        loc_layout.addWidget(self.capacity_button)
        r.addWidget(location)
        # The plan is VIRTUAL and visible on every page. No NAS disk scan to paint.
        plan_strip = QFrame(); plan_strip.setObjectName('Card')
        plan_box = QVBoxLayout(plan_strip); plan_box.setContentsMargins(13, 8, 13, 9); plan_box.setSpacing(4)
        plan_heading = QHBoxLayout()
        self.card_plan_name = label('512 GB virtual microSD • capacity preview', 'Small', True)
        self.card_plan_amount = label('0 B staged', 'Small')
        plan_heading.addWidget(self.card_plan_name)
        plan_heading.addStretch()
        plan_heading.addWidget(self.card_plan_amount)
        plan_heading.addWidget(button('Exact sizes…', self.show_card_plan_details))
        plan_box.addLayout(plan_heading)
        self.card_plan_bar = CardFillMeter()
        plan_box.addWidget(self.card_plan_bar)
        self.card_plan_note = label('Blue: staged files • Purple: AI space • Gold: protected free space', 'Small', True)
        plan_box.addWidget(self.card_plan_note)
        r.addWidget(plan_strip)
        self.stack = QStackedWidget(); r.addWidget(self.stack, 1)
        self.make_home(); self.make_library(); self.make_apps(); self.make_copy(); self.make_health(); self.make_prefs()
        self.update_card_plan()
        # Primary actions stay outside page scroll areas at every scale.
        self.command_host = QWidget()
        commands = QGridLayout(self.command_host); commands.setContentsMargins(0, 0, 0, 0)
        self.commands = commands
        self.page_action = self.register(button('Add My Games', self.run_page_action, 'Primary'))
        self.page_secondary = self.register(button('Add folder…', self.pick_folder))
        commands.addWidget(self.page_action, 0, 0)
        commands.addWidget(self.page_secondary, 0, 1)
        commands.addWidget(self.transfer_btn, 1, 0, 1, 2)
        commands.setColumnStretch(2, 1)
        r.addWidget(self.command_host)
        bottom = QFrame(); bottom.setObjectName('Card')
        b = QHBoxLayout(bottom); b.setContentsMargins(12,9,12,9)
        activity = QVBoxLayout(); activity.setSpacing(3)
        self.task_title = label('Ready • No tasks running', 'Activity', True)
        activity.addWidget(self.task_title)
        self.status = label('Choose what you want to do next.', 'Small', True)
        activity.addWidget(self.status)
        b.addLayout(activity, 2)
        self.bar = QProgressBar(); self.bar.setRange(0,100); self.bar.setValue(0)
        self.bar.setTextVisible(False); b.addWidget(self.bar, 1)
        self.cancel_btn = button('Stop task', self.cancel); self.cancel_btn.setEnabled(False)
        b.addWidget(self.cancel_btn)
        r.addWidget(bottom)
        base.addWidget(right, 1)
        self.navigate(0)

    def navigate(self, i: int, refresh_apps: bool = True):
        previous = self.stack.currentIndex()
        self.stack.setCurrentIndex(i)
        for j, b in enumerate(self.nav_buttons):
            b.setProperty('active', j==i)
            b.style().unpolish(b); b.style().polish(b)
        # Merely showing the current page should not launch a second NAS scan.
        # Importing APKs explicitly skips the status scan until copying finishes.
        if hasattr(self, 'page_action'):
            self.page_action.setText(['Add My Games', 'Add game files…', 'Prepare selected apps',
                                      'Preview changes', 'Check my library', 'Open library folder'][i])
            self.page_secondary.setVisible(i in (0, 1, 2, 3))
            self.page_secondary.setText('Convert PS1 discs…' if i == 2 else
                                        'Choose destination…' if i == 3 else 'Add folder…')
            try: self.page_secondary.clicked.disconnect()
            except RuntimeError: pass
            self.page_secondary.clicked.connect(self.choose_chd_conversion if i == 2 else
                                                self.choose_destination if i == 3 else self.pick_folder)
            self.transfer_btn.setVisible(i == 3)
            QTimer.singleShot(0, self.reflow_commands)
        if i == 2 and refresh_apps and i != previous and not self.current_task:
            self.update_tools_status()
        if i==3: self.update_destination_hint()
        if i==5: self.update_pref_paths()

    def register(self, b: QPushButton):
        self.task_buttons.append(b)
        return b

    def run_page_action(self):
        [self.pick_files, self.pick_files, self.install_recommended,
         self.start_preflight, self.health_check, self.open_workspace][self.stack.currentIndex()]()

    def make_home(self):
        page_widget, col = page('Your games. Your handheld. Ready.',
            'Keep your library on your PC or NAS, prepare the apps, then copy to your card. Your originals stay safe.')
        for title, detail, action in [
            ('Add My Games', 'Choose game files, ZIP / 7Z archives or whole folders.', lambda: self.navigate(1)),
            ('Prepare My RG Rotate', 'Prepare Cocoon, emulators and Windows tools in one batch.', lambda: self.navigate(2)),
            ('Copy to My microSD', 'Choose a destination, preview, then copy and verify. Try a practice folder first.', lambda: self.navigate(3)),
        ]:
            card = card_layout(col)
            row = QHBoxLayout()
            words = QVBoxLayout(); words.addWidget(label(title, 'H2'))
            words.addWidget(label(detail, 'Small', True)); row.addLayout(words, 1)
            row.addWidget(button('Open', action, 'Accent')); card.addLayout(row)
        home_drop = FileDropZone('Drop your games or Android APKs here',
            'Files are copied into your library folder. Original files are kept.')
        home_drop.dropped.connect(self.handle_home_drop); col.addWidget(home_drop)
        hero = card_layout(col, 'Your virtual card')
        line = QHBoxLayout(); self.home_used = label('0 GB', 'HeroNumber')
        line.addWidget(self.home_used); line.addStretch()
        self.home_room = label('Choose a PC folder to begin', 'Subtitle'); line.addWidget(self.home_room)
        hero.addLayout(line)
        self.home_meter = QProgressBar(); self.home_meter.setRange(0,10000); self.home_meter.setTextVisible(False)
        hero.addWidget(self.home_meter)
        hero.addWidget(label('512 GB profile • 8 GiB companion budget • 8 GiB protected card reserve', 'Small', True))
        self.host_storage_hint = label('Only the files you add take up space.', 'Small', True)
        hero.addWidget(self.host_storage_hint)
        self.home_workspace_tip = label('Choose your library folder in the strip above.', 'Small', True)
        hero.addWidget(self.home_workspace_tip)
        hero.addWidget(button('What is ready for my RG Rotate?', self.show_day_one_readiness))
        self.home_hint = label('Start by adding a game or folder.', 'Subtitle', True); col.addWidget(self.home_hint)
        col.addStretch(); self.stack.addWidget(scroll_page(page_widget))

    def show_day_one_readiness(self):
        """A truthful instant snapshot; never block on slow NAS I/O in the UI."""
        games = len(self.card_entries)
        used = pretty_bytes(self.staged_bytes)
        known_apps = getattr(self, 'last_app_states', None)
        if not known_apps:
            app_line = 'Not checked yet. Open Install Apps to inspect the software queue.'
        else:
            prepared = sum('ready' in str(known_apps.get(n, '')).lower()
                           for n in ('Cocoon Shell', 'PPSSPP', 'RetroArch'))
            app_line = f'{prepared}/3 core Android installers prepared or imported (not installed).'
        lines = [
            'VIRTUAL CARD',
            ('✓ Workspace selected' if not self.needs_workspace_setup else '! Choose a workspace folder'),
            f'{games} recognized game file(s), {used} staged as of the last completed scan.',
            '', 'SOFTWARE', app_line,
            '', 'BEFORE COPYING TO THE CARD',
            'Run Library Check for duplicates and broken CUE/M3U references.',
            'Run Copy to Card → Try a safe practice copy.',
            '', 'AFTER YOUR RG ROTATE ARRIVES',
            'Detect the real microSD, preview its actual capacity and confirm the destination.',
            'Run a verified copy and safely eject the card.',
            'Install/authorize Android apps, choose Cocoon as Home, assign emulators.',
            'Verify games, input, sound, saves, and Cocoon artwork on the actual handheld.',
            '', 'IMPORTANT: This is a planning snapshot, NOT an Android or hardware pass.'
        ]
        dialog = QMessageBox(self)
        dialog.setWindowTitle('RG Rotate: Day-One Checklist')
        dialog.setText('\n'.join(lines))
        install = dialog.addButton('Open Install Apps', QMessageBox.ButtonRole.ActionRole)
        transfer = dialog.addButton('Open Copy to Card', QMessageBox.ButtonRole.ActionRole)
        dialog.addButton('Close', QMessageBox.ButtonRole.RejectRole)
        dialog.exec()
        if dialog.clickedButton() is install: self.navigate(2)
        elif dialog.clickedButton() is transfer: self.navigate(3)

    def file_table(self, headings: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headings)); table.setHorizontalHeaderLabels(headings)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True); table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(len(headings)-1, QHeaderView.ResizeMode.ResizeToContents)
        table.setMinimumHeight(245)
        return table

    def make_library(self):
        p, c = page('My Games',
            'This is your virtual microSD card. Add games directly here. You do not need to put anything into a special incoming folder first.')
        location_row = QHBoxLayout()
        location_row.addWidget(label('All imported games are stored in the PC folder shown above.', 'Small', True), 1)
        location_row.addWidget(button('Change card location', self.choose_workspace))
        c.addLayout(location_row)
        actions = expandable(c, 'More import options',
            'Select individual files, a whole folder, or scan Downloads. ZIP and 7Z archives are unpacked automatically.')
        row = QGridLayout()
        row.addWidget(self.register(button('＋ Add Game Files', self.pick_files, 'Primary')), 0, 0)
        row.addWidget(self.register(button('＋ Add Folder', self.pick_folder, 'Accent')), 0, 1)
        row.addWidget(self.register(button('Find Games in Downloads', self.find_downloads)), 1, 0, 1, 2)
        actions.addLayout(row)
        game_drop = FileDropZone('Or drop your game files here', 'Game files, ZIP/7Z archives, or one game folder from Windows Explorer')
        game_drop.dropped.connect(self.handle_game_drop)
        actions.addWidget(game_drop)
        chooser = QHBoxLayout(); chooser.addWidget(label('For files we cannot identify, use:'))
        self.system = QComboBox()
        view = QListView(self.system)
        view.setObjectName('SystemOptions')
        view.setMouseTracking(True)
        view.viewport().setMouseTracking(True)
        view.setItemDelegate(HighlightDelegate(view))
        self.system.setView(view)
        self.system.addItems(SYSTEM_DIR.keys())
        self.system.setCurrentText('PS1')
        self.system.setToolTip('Only used when a game format could belong to more than one console.')
        chooser.addWidget(self.system); chooser.addStretch()
        actions.addLayout(chooser)
        actions.addWidget(label('Recognizable GBA, PSP, SNES and other files sort themselves. ISO, CHD and archives use your selected system unless their folder name gives a better clue.', 'Small', True))
        content = card_layout(c, 'Inside your virtual microSD')
        self.library_count = label('No games added yet', 'Subtitle'); content.addWidget(self.library_count)
        self.library_notice = label('Add games from anywhere on your computer. Your originals are never moved.', 'Small', True)
        content.addWidget(self.library_notice)
        content.addWidget(label('PS1 game collections: choose a complete game folder or all CUE/BIN discs together. '
            'Each disc becomes a verified CHD inside ROMs/psx/Game Title. One M3U playlist and one cover tile '
            'represent the collection. Missing tracks are never guessed or deleted.', 'Small', True))
        self.card_search = QLineEdit(); self.card_search.setPlaceholderText('Search the games you have added…')
        self.card_search.textChanged.connect(self._gallery_search_changed)
        content.addWidget(self.card_search)
        options = QHBoxLayout()
        options.addWidget(label('View:', 'Small'))
        self.grid_button = button('▦  Cover gallery', lambda: self.set_gallery_mode('Gallery'), 'ViewOption')
        self.list_button = button('☷  File list', lambda: self.set_gallery_mode('List'), 'ViewOption')
        options.addWidget(self.grid_button)
        options.addWidget(self.list_button)
        options.addSpacing(8)
        options.addWidget(label('System:', 'Small'))
        self.game_filter = QComboBox()
        self.game_filter.addItem('All systems')
        self.game_filter.addItems(SYSTEM_DIR.keys())
        self.game_filter.addItem('Other')
        self.game_filter.currentIndexChanged.connect(lambda _index: self.fill_card())
        options.addWidget(self.game_filter, 1)
        content.addLayout(options)
        self.console_nav = QScrollArea()
        self.console_nav.setWidgetResizable(True)
        self.console_nav.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.console_nav.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.console_nav.setMinimumHeight(76)
        self.console_nav.setMaximumHeight(95)
        self.console_nav_page = QWidget()
        self.console_nav_layout = QHBoxLayout(self.console_nav_page)
        self.console_nav_layout.setContentsMargins(2, 5, 2, 5)
        self.console_nav_layout.setSpacing(8)
        self.console_nav.setWidget(self.console_nav_page)
        content.addWidget(self.console_nav)
        self.cover_info = label('Your cover gallery will appear here after importing games.', 'Small', True)
        content.addWidget(self.cover_info)
        art_actions = QHBoxLayout()
        self.auto_cover = QCheckBox('Look for covers automatically after imports')
        self.auto_cover.setChecked(str(self.settings.value('auto_covers', 'true')).lower() not in ('false', '0'))
        self.auto_cover.toggled.connect(lambda enabled: self.settings.setValue('auto_covers', bool(enabled)))
        art_actions.addWidget(self.auto_cover, 1)
        art_actions.addWidget(self.register(button('Search for a game cover…', self.search_cover_for_game)))
        art_actions.addWidget(self.register(button('Find missing covers', self.fetch_covers)))
        content.addLayout(art_actions)
        disc_actions = QHBoxLayout()
        self.auto_ps1_chd = QCheckBox('Automatically convert PS1 CUE/BIN to CHD before adding to My Games')
        self.auto_ps1_chd.setChecked(str(self.settings.value('auto_ps1_chd', 'true')).lower() not in ('false', '0'))
        self.auto_ps1_chd.toggled.connect(lambda enabled: self.settings.setValue('auto_ps1_chd', bool(enabled)))
        disc_actions.addWidget(self.auto_ps1_chd, 1)
        disc_actions.addWidget(self.register(button('Convert earlier PS1 imports…', self.optimize_existing_ps1)))
        content.addLayout(disc_actions)
        collection_row = QHBoxLayout()
        collection_row.addWidget(self.register(button('＋ Import complete PS1 game folder…', self.pick_ps1_collection, 'Accent')))
        collection_row.addWidget(label('Choose the folder holding all discs; CHDs and M3U are prepared automatically.', 'Small', True), 1)
        content.addLayout(collection_row)
        batch_actions = QHBoxLayout()
        batch_actions.addWidget(self.register(button('◆ Batch convert remaining PS1 discs…', self.batch_convert_ps1, 'Accent')))
        batch_actions.addWidget(self.register(button('Open conversion backups', self.open_conversion_backups)))
        content.addLayout(batch_actions)
        content.addWidget(label('Batch conversion uses CHDman lossless CD codecs, verifies each CHD and lets you choose '
            'whether to keep or remove only the virtual-card CUE/BIN/IMG working copies. '
            'Your separate source library on the NAS is never touched.', 'Small', True))
        self.game_views = QStackedWidget()
        self.card_table = self.file_table(['Game / file', 'System', 'Size', 'Location'])
        self.card_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.card_table.customContextMenuRequested.connect(self.show_file_row_context_menu)
        self.game_views.addWidget(self.card_table)
        self.gallery_page = QWidget()
        self.gallery_grid = QGridLayout(self.gallery_page)
        self.gallery_grid.setContentsMargins(4, 7, 4, 9)
        self.gallery_grid.setHorizontalSpacing(12)
        self.gallery_grid.setVerticalSpacing(12)
        self.gallery_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.gallery_scroll = QScrollArea()
        self.gallery_scroll.setWidgetResizable(True)
        self.gallery_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.gallery_scroll.setMinimumHeight(430)
        self.gallery_scroll.setWidget(self.gallery_page)
        self.game_views.addWidget(self.gallery_scroll)
        content.addWidget(self.game_views)
        self.gallery_more = button('Show more games', self.show_more_gallery)
        content.addWidget(self.gallery_more)
        self.set_gallery_mode(self.gallery_mode)
        self.library_empty = QFrame(); self.library_empty.setObjectName('SubCard')
        empty_layout = QVBoxLayout(self.library_empty)
        empty_layout.setContentsMargins(22, 27, 22, 26); empty_layout.setSpacing(12)
        empty_layout.addWidget(label('Your first games go here', 'H2'))
        empty_layout.addWidget(label(
            'There is nothing on this virtual card yet. That is normal! Just select a game or folder from anywhere on your PC. We will handle organizing it.',
            'Subtitle', True))
        empty_buttons = QHBoxLayout()
        empty_buttons.addWidget(self.register(button('＋ Choose Game Files', self.pick_files, 'Primary')))
        empty_buttons.addWidget(self.register(button('＋ Choose a Folder', self.pick_folder)))
        empty_layout.addLayout(empty_buttons)
        content.addWidget(self.library_empty)
        footer = QHBoxLayout()
        footer.addWidget(button('Open virtual card in Explorer', self.open_workspace))
        footer.addWidget(self.register(button('↻ Refresh game list', self.refresh)))
        footer.addStretch(); footer.addWidget(button('Ready to copy?  →', lambda: self.navigate(3), 'Accent'))
        content.addLayout(footer)
        c.addStretch()
        self.stack.addWidget(scroll_page(p))

    def make_apps(self):
        p, c = page('Prepare My RG Rotate',
            'Just like Ninite: pick the apps once and press one button. We download the official software, skip prepared files, and show you what still needs installing on Android.')
        initial = card_layout(c, 'One-click recommended setup',
            'Leave the recommended boxes selected. Downloading happens in the background, with each app tracked separately. No firmware changes or surprise installs.')
        self.software_checks: dict[str,QCheckBox] = {}
        opts = [
            ('Cocoon Shell', 'Your default RG Rotate home screen', True),
            ('PPSSPP', 'PSP games', True),
            ('RetroArch', 'Other classic systems', True),
            ('Android Platform Tools', 'USB-assisted device setup on Windows', True),
            ('CHDman', 'Optional PS1 disc conversion on Windows', True),
            ('DuckStation', 'Optional PS1 app, Cocoon compatibility needs testing', False),
        ]
        self.install_state_labels: dict[str, QLabel] = {}
        for name, desc, checked in opts:
            row = QHBoxLayout(); row.setSpacing(13)
            cb = QCheckBox(name); cb.setChecked(checked); self.software_checks[name] = cb
            row.addWidget(cb, 2); row.addWidget(label(desc, 'Small', True), 3)
            state = label('Checking…', 'InstallerState', True)
            state.setProperty('mode', 'pending')
            state.setMinimumWidth(175)
            self.install_state_labels[name] = state
            row.addWidget(state, 2)
            initial.addLayout(row)
        action = QHBoxLayout()
        action.addWidget(self.register(button('↓  Install Recommended Setup', self.install_recommended, 'Primary')))
        # The primary button honors the visible checkboxes; no confusing second installer action.
        action.addWidget(button('Official download pages', self.show_official_pages))
        initial.addLayout(action)
        self.prep_status = label('Ready to download. Android installers will be prepared now, then installed when your RG Rotate is connected.', 'Subtitle', True)
        initial.addWidget(self.prep_status)
        local = card_layout(c, 'Already downloaded an Android app?',
            'For example, your Cocoon 3.1.1 APK. Add it here. We will copy it to the virtual card without moving or installing your original file.')
        drop = FileDropZone('Drop Android APK files here',
                            'Or choose them from Downloads or any folder on your PC. Only .apk files are accepted.')
        drop.dropped.connect(self.import_apks)
        local.addWidget(drop)
        apk_row = QHBoxLayout()
        apk_row.addWidget(self.register(button('＋ Add APK Files', self.pick_apks, 'Primary')))
        apk_row.addWidget(button('Open Android installers folder', self.open_apks_folder))
        local.addLayout(apk_row)
        self.apk_status = label('No Android installers added yet.', 'Subtitle', True)
        local.addWidget(self.apk_status)
        self.apk_table = self.file_table(['Android installer', 'File size', 'Status'])
        self.apk_table.setMinimumHeight(120)
        self.apk_table.setMaximumHeight(230)
        local.addWidget(self.apk_table)
        local.addWidget(label('Important: Staged ≠ installed. APKs require installation on Android later. A local APK filename is not proof of its publisher; use trusted sources.', 'Small', True))
        details = card_layout(c, 'What has been prepared?')
        self.tool_status_label = label('Checking local tools…', 'Subtitle', True)
        details.addWidget(self.tool_status_label)
        details.addWidget(label('CHDman and ADB are local Windows utilities. Cocoon, PPSSPP and RetroArch are Android APK installers. Copying an APK to the card does not install it.', 'Small', True))
        converter = expandable(c, 'PlayStation Disc Converter',
            'Uses your Windows CHDman tool. Choose a CUE file and an output folder. Your original BIN/CUE files are never deleted.')
        convrow = QHBoxLayout()
        convrow.addWidget(self.register(button('Choose a PS1 CUE and convert…', self.choose_chd_conversion, 'Accent')))
        convrow.addWidget(self.register(button('Test CHDman executable', self.test_chdman)))
        converter.addLayout(convrow)
        self.chd_status = label('Convert only after CHDman is ready. Output is verified before completion.', 'Small', True)
        converter.addWidget(self.chd_status)
        art = expandable(c, 'More artwork options',
            'Your covers are now managed directly in My Games. Online matches, review choices, and manual replacement are available there. Cocoon still manages its own Android artwork database.')
        ar = QHBoxLayout()
        ar.addWidget(self.register(button('Choose a local cover for a game…', self.choose_cover, 'Primary')))
        ar.addWidget(self.register(button('Find missing game covers…', self.fetch_covers)))
        ar.addWidget(button('Open artwork folder', lambda: self.open_path(self.workspace / 'Media' / 'BoxArt')))
        art.addLayout(ar)
        self.art_status = label('No artwork task has been run yet.', 'Small', True); art.addWidget(self.art_status)

        c.addStretch(); self.stack.addWidget(scroll_page(p))

    def make_copy(self):
        p, c = page('Copy to My microSD',
            'Insert the real card into your Windows reader. We will show you exactly what will be copied before any files are written.')
        from_area = card_layout(c, 'Copying FROM: your virtual card on this PC',
            'Your source may be a local PC folder or your mapped Synology NAS drive. All transfer data is read from that folder and verified on the destination.')
        from_area.addWidget(button('Change source virtual-card folder', self.choose_workspace))
        first = card_layout(c, '1. Choose where to copy',
            'Select the real card drive. If your RG Rotate has not arrived, use “Try a practice copy” to safely test with an ordinary folder.')
        self.dest_name = label('No card selected yet', 'Subtitle', True); first.addWidget(self.dest_name)
        self.card_measured = label('Real microSD capacity not measured yet. Select the card and run Preview.', 'Small', True)
        first.addWidget(self.card_measured)
        self.real_card_bar = CardFillMeter(); self.real_card_bar.setVisible(False)
        first.addWidget(self.real_card_bar)
        self.card_measured_details = label('', 'Small', True); first.addWidget(self.card_measured_details)
        r = QHBoxLayout()
        r.addWidget(self.register(button('Find inserted card', self.detect_card, 'Primary')))
        r.addWidget(self.register(button('Choose drive or folder…', self.choose_destination)))
        first.addLayout(r)
        first.addWidget(self.register(button('Try a safe practice copy first', self.prepare_practice, 'Accent')))
        self.simulation = QCheckBox('Practice folder (not a real microSD)')
        self.simulation.setChecked(self.saved_destination_mode == 'practice')
        self.simulation.toggled.connect(self.on_destination_mode_changed)
        first.addWidget(self.simulation)
        note = card_layout(c, '2. Preview before copying',
            'The app checks your drive, available space, existing files and any naming conflicts first.')
        note.addWidget(self.register(button('Check what would be copied', self.start_preflight, 'Accent')))
        self.preflight_text = label('No preview yet. Choose your destination, then click the check button.', 'Subtitle', True)
        note.addWidget(self.preflight_text)
        transfer = card_layout(c, '3. Transfer with verification',
            'Your original files remain untouched. Existing different files are never overwritten. Interrupted transfers can resume.')
        self.transfer_btn = self.register(button('⇄  Copy and Verify Files', self.start_transfer, 'Primary'))
        transfer.addWidget(self.transfer_btn)
        self.copy_meter = QProgressBar(); self.copy_meter.setRange(0,1000); self.copy_meter.setValue(0)
        transfer.addWidget(self.copy_meter)
        self.copy_detail = label('No transfer has run in this session. Preview first, then copy or verify.', 'Subtitle', True)
        transfer.addWidget(self.copy_detail)
        self.last_transfer_note = label('Current run: not started. No files have been verified in this run.', 'Small', True)
        transfer.addWidget(self.last_transfer_note)
        c.addStretch()
        self.copy_scroll = scroll_page(p)
        self.stack.addWidget(self.copy_scroll)

    def make_health(self):
        p, c = page('Check your game library',
            'Find duplicate file content and broken PlayStation disc references before transferring. This scan never deletes your files.')
        audit = card_layout(c, 'Run a safe library check')
        audit.addWidget(self.register(button('✓  Scan my virtual card', self.health_check, 'Primary')))
        self.health_result = QPlainTextEdit(); self.health_result.setReadOnly(True)
        self.health_result.setMinimumHeight(250)
        self.health_result.setPlainText('Your report will appear here. No changes will be made to your game files.')
        audit.addWidget(self.health_result)
        c.addStretch(); self.stack.addWidget(scroll_page(p))

    def make_prefs(self):
        p, c = page('Preferences & first-boot help',
            'The program remembers your window size, screen position, scale and folder choices automatically.')
        paths = card_layout(c, 'Folder locations',
            'Your virtual card is a normal folder on a PC drive or mapped Synology NAS share, not the real microSD. No empty 512 GB file is created.')
        self.workspace_path = label('', 'Small', True)
        paths.addWidget(label('Virtual card folder')); paths.addWidget(self.workspace_path)
        paths.addWidget(button('Choose or move my virtual card folder…', self.choose_workspace, 'Primary'))
        self.incoming_path = label('', 'Small', True)
        paths.addWidget(label('Downloads search folder')); paths.addWidget(self.incoming_path)
        paths.addWidget(self.register(button('Change downloads search folder…', self.choose_incoming)))
        row = QHBoxLayout()
        row.addWidget(button('Open my virtual card', self.open_workspace))
        row.addWidget(button('Open Windows tools folder', lambda: self.open_path(tools_root())))
        paths.addLayout(row)
        guide = card_layout(c, 'First boot on the RG Rotate',
            'Windows prepares the card and APK installers. Android will still ask you to grant storage permissions and select Cocoon as Home.')
        self.guide_text = label(
            '1. Insert your copied microSD into the RG Rotate.\n'
            '2. Install Cocoon and the emulator APKs from an approved Android method.\n'
            '3. Set Cocoon as the Home app and select the card’s ROMs folder.\n'
            '4. Add your own compatible PS1 BIOS if your chosen emulator requires one. PSP emulation with PPSSPP does not need a PSP BIOS.\n'
            '5. Grant Android file access, choose your emulator players, then scan games and fetch cover art in Cocoon.\n'
            '6. Test controls, audio, saves, and game launches on the real device.', 'Subtitle', True)
        guide.addWidget(self.guide_text)
        row2 = QHBoxLayout()
        row2.addWidget(self.register(button('Detect Android over USB', self.detect_android)))
        row2.addWidget(self.register(button('Install prepared APKs over USB…', self.install_apks)))
        guide.addLayout(row2)
        guide.addWidget(self.register(button('Add my own PS1 BIOS file…', self.add_bios_file)))
        guide.addWidget(self.register(button('Save setup guide and readiness report', self.save_readiness)))
        c.addStretch(); self.stack.addWidget(scroll_page(p))

    def set_status(self, text: str):
        self.status.setText(text[:180])

    def start_readonly_scan(self, mode: str, workspace: Path, finished):
        """Read-only NAS operations run in a disposable child, not a stuck Qt thread.

        Stop may terminate/kill this child after a grace period, because the child
        only reads filesystem metadata. Never use hard-stop for importing/copying.
        """
        if self.current_task:
            self.set_status(f'Already working on: {self.current_task_name}.')
            return
        self.current_task = True
        self.current_task_name = {'inventory': 'Checking Virtual Card',
                                  'count': 'Checking Existing Card Before Location Change',
                                  'apps': 'Checking Android Apps and Windows Tools'}[mode]
        self.cancel_requested = False
        self.cancel_signal.clear()
        self.scan_cancelled = False
        self.scan_result = None
        self.scan_error = ''
        self.scan_output = ''
        self.scan_mode = mode
        self.scan_finished_callback = finished
        self.cancel_btn.setEnabled(True)
        for b in self.task_buttons: b.setEnabled(False)
        self.bar.setRange(0, 0)
        self.task_title.setText(f'Working on: {self.current_task_name}')
        child = QProcess(self)
        self.scan_process = child
        child.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        child.readyReadStandardOutput.connect(self._scan_output_ready)
        child.readyReadStandardError.connect(self._scan_error_ready)
        child.finished.connect(self._scan_process_finished)
        child.errorOccurred.connect(self._scan_start_error)
        if getattr(sys, 'frozen', False):
            helper = Path(sys.executable).with_name('RetroLibraryScan.exe')
            if helper.is_file():
                # PyInstaller --windowed applications have no reliable stdout;
                # the companion console helper supplies a redirected pipe.
                child.start(str(helper), ['--mode', mode, '--path', str(workspace)])
            else:
                self.scan_error = ('Windows EXE build is missing RetroLibraryScan.exe. '
                                   'Keep both EXEs together, or use the source launcher.')
                QTimer.singleShot(0, lambda: self._scan_process_finished(-1, QProcess.ExitStatus.CrashExit))
        else:
            script = str(Path(__file__).with_name('readonly_scan.py'))
            child.start(sys.executable, ['-u', script, '--mode', mode, '--path', str(workspace)])
        # A slow SMB directory listing is not a GUI lock. User can navigate or Stop.

    def _scan_output_ready(self):
        child = self.scan_process
        if child is None:
            return
        self.scan_output += bytes(child.readAllStandardOutput()).decode('utf-8', errors='replace')
        while '\n' in self.scan_output:
            line, self.scan_output = self.scan_output.split('\n', 1)
            try:
                data = json.loads(line)
            except (ValueError, TypeError):
                continue
            if data.get('type') == 'progress' and not self.scan_cancelled:
                self.on_progress(data.get('message', 'Inspecting your virtual card'),
                                 int(data.get('current', 0)), int(data.get('total', 0)))
            elif data.get('type') == 'result':
                self.scan_result = data
            elif data.get('type') == 'error':
                self.scan_error = str(data.get('message', 'Unknown scan error'))

    def _scan_error_ready(self):
        if self.scan_process is not None:
            self.scan_error += bytes(self.scan_process.readAllStandardError()).decode('utf-8', errors='replace')[-1500:]

    def _scan_start_error(self, _error):
        if self.scan_process is not None and self.scan_process.error() == QProcess.ProcessError.FailedToStart:
            self.scan_error = 'The read-only scanning helper could not start. Check the application folder.'
            QTimer.singleShot(0, lambda: self._scan_process_finished(-1, QProcess.ExitStatus.CrashExit)
                              if self.scan_process is not None else None)

    def _finish_scan_cancelled(self):
        self._unlock()
        self.set_status('Read-only scan stopped. No files were changed.')
        if self.close_when_idle:
            self.close_when_idle = False
            QTimer.singleShot(0, self.close)

    def _scan_process_finished(self, code, status):
        child = self.scan_process
        if child is None:
            return
        # Drain remaining output before deciding success; large libraries can emit
        # the result in multiple chunks and quit before all readyRead signals fire.
        self._scan_output_ready()
        self._scan_error_ready()
        child.deleteLater()
        self.scan_process = None
        if self.scan_cancelled:
            self._finish_scan_cancelled()
            return
        mode = self.scan_mode
        callback = self.scan_finished_callback
        result = self.scan_result
        if code != 0 or result is None or status != QProcess.ExitStatus.NormalExit:
            self.job_failed(self.scan_error or f'Read-only scan stopped unexpectedly (exit {code})')
            return
        try:
            if mode == 'apps':
                payload = result
            elif mode == 'inventory':
                self.cue_tracks = {os.path.normcase(os.path.abspath(p)) for p in result.get('disc_tracks', [])}
                entries = [Entry(Path(row[0]), row[1], row[2], int(row[3]), row[4])
                           for row in result['entries']]
                payload = (Path(result['path']), entries, int(result['used']),
                           int(result['count']), int(result['companion']))
            else:
                payload = (int(result['count']), int(result['used']))
        except (KeyError, ValueError, IndexError, TypeError) as exc:
            self.job_failed(f'Unreadable scan result: {exc}')
            return
        self.job_done(callback, payload)

    def _stop_readonly_scan(self):
        child = self.scan_process
        if child is None:
            return
        self.scan_cancelled = True
        self.cancel_signal.set()
        self.cancel_btn.setEnabled(False)
        self.task_title.setText('Stopping read-only scan…')
        self.set_status('Stopping the NAS scan. No game files are being changed.')
        if child.state() != QProcess.ProcessState.NotRunning:
            child.terminate()
            # Termination is asynchronous. A stuck Windows file call can ignore it.
            # Kill ONLY the read-only child, never a writer, after a short grace.
            QTimer.singleShot(800, lambda proc=child: proc.kill()
                              if self.scan_process is proc and proc.state() != QProcess.ProcessState.NotRunning
                              else None)

    def job(self, fn, finished, *args, progress=False, transfer=False, app_states=False,
            task_name=None, **kwargs):
        if (self.needs_workspace_setup or
            (not is_network_path(self.workspace) and not self.workspace.is_dir())) and task_name not in (
                'Checking Existing Card Before Location Change',
                'Copying Virtual Card to New PC Folder'):
            self.ensure_workspace()
            return
        if self.current_task:
            self.set_status(f'Already working on: {self.current_task_name}. Use Stop task or let it finish.')
            return
        self.current_task = True
        self.current_task_name = task_name or fn.__name__.replace('_', ' ').title()
        self.cancel_requested = False
        self.cancel_signal.clear()
        self.cancel_btn.setEnabled(True)
        for b in self.task_buttons: b.setEnabled(False)
        # Unknown-length work is explicitly animated instead of falsely showing 0%.
        self.bar.setRange(0, 0)
        self.task_title.setText(f'Working on: {self.current_task_name}')
        work = Job(fn, *args, **kwargs)
        if progress: work.kwargs['progress'] = work.signals.progress.emit
        if transfer: work.kwargs['progress'] = work.signals.copy_progress.emit
        if app_states: work.kwargs['on_state'] = work.signals.app_state.emit
        work.signals.progress.connect(self.on_progress)
        work.signals.app_state.connect(self.on_app_state)
        work.signals.copy_progress.connect(self.on_copy_progress)
        work.signals.done.connect(lambda result: self.job_done(finished, result))
        work.signals.failed.connect(self.job_failed)
        self.pool.start(work)

    def start_import_process(self, request: dict, task_name: str, finished=None):
        """Isolate potentially hung SMB reads/writes in a disposable process.

        Graceful STOP is tried first. If it cannot return from network I/O,
        terminate the child. This may leave a *.retro-part, NEVER a finished
        partial game. Do not run another import until the child has exited.
        """
        if self.current_task:
            self.set_status(f'Already working on: {self.current_task_name}.')
            return
        self.current_task = True
        self.current_task_name = task_name
        self.import_finished_callback = finished or self.import_completed
        self.import_kind = request.get('mode', 'games')
        self.cancel_requested = False
        self.import_stopped = False
        self.import_output = ''
        self.import_error = ''
        self.import_result = None
        self.cancel_btn.setEnabled(True)
        for b in self.task_buttons: b.setEnabled(False)
        self.bar.setRange(0, 0)
        self.task_title.setText(f'Working on: {task_name}')
        proc = QProcess(self)
        self.import_process = proc
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        proc.readyReadStandardOutput.connect(self._import_output_ready)
        proc.readyReadStandardError.connect(self._import_error_ready)
        proc.finished.connect(self._import_process_finished)
        proc.errorOccurred.connect(self._import_start_error)
        payload = (json.dumps(request, ensure_ascii=True, separators=(',', ':')) + '\n').encode('ascii')
        proc.started.connect(lambda p=proc, data=payload: p.write(data))
        if getattr(sys, 'frozen', False):
            exe = Path(sys.executable).with_name('RetroLibraryImport.exe')
            if not exe.is_file():
                self.import_error = ('Missing RetroLibraryImport.exe. Keep all built EXEs '
                                     'together or launch from the Windows source folder.')
                QTimer.singleShot(0, lambda: self._import_process_finished(-1, QProcess.ExitStatus.CrashExit))
                return
            proc.start(str(exe), [])
        else:
            script = str(Path(__file__).with_name('import_worker.py'))
            proc.start(sys.executable, ['-u', script])

    def _import_output_ready(self):
        proc = self.import_process
        if proc is None:
            return
        self.import_output += bytes(proc.readAllStandardOutput()).decode('ascii', errors='replace')
        while '\n' in self.import_output:
            line, self.import_output = self.import_output.split('\n', 1)
            try:
                data = json.loads(line)
            except ValueError:
                self.import_error = 'The import helper returned an unreadable result.'
                continue
            typ = data.get('type')
            if typ == 'progress' and not self.import_stopped:
                self.on_progress(data.get('message', ''), int(data.get('current', 0)),
                                 int(data.get('total', 0)))
            elif typ == 'app_state':
                self.on_app_state(data['name'], data['state'])
            elif typ == 'result':
                self.import_result = data.get('data')
            elif typ == 'error':
                self.import_error = str(data.get('message', 'Import helper failed'))

    def _import_error_ready(self):
        if self.import_process is not None:
            self.import_error += bytes(self.import_process.readAllStandardError()).decode('utf-8', errors='replace')[-1400:]

    def _import_start_error(self, _error):
        proc = self.import_process
        if proc is not None and proc.error() == QProcess.ProcessError.FailedToStart:
            self.import_error = 'Cannot start the import helper. Please check the application folder.'
            QTimer.singleShot(0, lambda p=proc: self._import_process_finished(-1, QProcess.ExitStatus.CrashExit)
                              if self.import_process is p else None)

    def _import_process_finished(self, code, status):
        proc = self.import_process
        if proc is None:
            return
        self._import_output_ready()
        self._import_error_ready()
        proc.deleteLater()
        self.import_process = None
        stopped = self.import_stopped or self.cancel_requested
        result = self.import_result
        if stopped:
            self._unlock()
            if self.import_kind in ('inspect_discs', 'convert_discs', 'playlist', 'setup'):
                if self.import_kind == 'convert_discs' and isinstance(result, dict):
                    if not self.close_when_idle: self.chd_conversion_done(result)
                self.set_status('Task stopped. Original files were preserved. Review completed files before retrying.')
                if self.import_kind == 'setup': self.prep_status.setText('Setup stopped. Retry to check prepared packages.')
                else: self.chd_status.setText('Stopped. Verified discs already completed are kept; unfinished temporary output may need review.')
                if self.close_when_idle:
                    self.close_when_idle = False
                    QTimer.singleShot(0, self.close)
                return
            if self.import_kind == 'apks':
                self.apk_status.setText('APK import stopped. No incomplete APK will appear as ready. '                                         'You can retry the same file safely.')
                self.set_status('APK import stopped. Your original download was preserved.')
                if self.close_when_idle:
                    self.close_when_idle = False
                    QTimer.singleShot(0, self.close)
                return
            self.library_notice.setText('Import stopped. Originals remain untouched. '
                'Any incomplete .retro-part file must be reviewed before retrying that game.')
            self.set_status('Import stopped. You can navigate again. Completed games were preserved.')
            if self.close_when_idle:
                self.close_when_idle = False
                QTimer.singleShot(0, self.close)
            return
        if code != 0 or status != QProcess.ExitStatus.NormalExit or not isinstance(result, dict):
            self.job_failed(self.import_error or f'Import helper exited unexpectedly ({code})')
            return
        self.job_done(self.import_finished_callback or self.import_completed, result)

    def _stop_import_process(self):
        proc = self.import_process
        if proc is None:
            return
        self.import_stopped = True
        self.cancel_requested = True
        self.cancel_btn.setEnabled(False)
        self.task_title.setText('Stopping APK import…' if self.import_kind == 'apks' else 'Stopping game import…')
        self.set_status('Stopping isolated import worker. Original files remain protected.')
        if proc.state() == QProcess.ProcessState.NotRunning:
            return
        proc.write(b'STOP\n')  # Cooperative cancellation for current copy/archive operation.
        QTimer.singleShot(1400, lambda p=proc: self._terminate_stuck_import(p))

    def _terminate_stuck_import(self, proc):
        if self.import_process is not proc or proc.state() == QProcess.ProcessState.NotRunning:
            return
        self.task_title.setText('Stopping unresponsive NAS import…')
        self.set_status('NAS file operation did not respond. Ending isolated import process safely.')
        proc.kill()  # No published partial files: core writes to .retro-part first.
        QTimer.singleShot(3500, lambda p=proc: self._warn_import_shutdown(p))

    def _warn_import_shutdown(self, proc):
        if self.import_process is proc and proc.state() != QProcess.ProcessState.NotRunning:
            self.set_status('Windows is still closing the NAS worker. Browsing is safe; '
                            'new writes remain locked until it exits.')

    def _unlock(self):
        self.current_task = False
        self.cancel_requested = False
        self.current_task_name = ''
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText('Stop task')
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.task_title.setText('Ready • No tasks running')
        for b in self.task_buttons: b.setEnabled(True)
        if self.pending_workspace_picker:
            self.pending_workspace_picker = False
            QTimer.singleShot(0, self.choose_workspace)

    def job_done(self, finished, result):
        self._unlock()
        if self.close_when_idle:
            self.close_when_idle = False
            QTimer.singleShot(0, self.close)
            return
        finished(result)

    def job_failed(self, error):
        task = self.current_task_name
        if task in ('Checking Existing Card Before Location Change', 'Copying Virtual Card to New PC Folder'):
            self.pending_workspace_destination = None
        was_cancelled = self.cancel_requested
        self._unlock()
        if self.close_when_idle:
            self.close_when_idle = False
            QTimer.singleShot(0, self.close)
            return
        if was_cancelled:
            self.set_status('Operation stopped. Original files remain unchanged; incomplete writes may require review.')
            return
        self.set_status(f'{task} could not finish. See the message for details.')
        QMessageBox.warning(self, 'Something needs attention',
            f'We could not finish: {task}\n\n{error}')

    def _set_installer_state(self, name: str, state: str):
        if name not in getattr(self, 'install_state_labels', {}): return
        widget = self.install_state_labels[name]
        widget.setText(state)
        mode = ('error' if 'Needs attention' in state or 'review' in state else
                'ready' if ('ready' in state.lower() or 'downloaded' in state.lower()) and 'Downloading' not in state else
                'working' if 'Downloading' in state or 'Checking' in state or 'preparing' in state else 'pending')
        widget.setProperty('mode', mode)
        widget.style().unpolish(widget); widget.style().polish(widget)

    def on_app_state(self, name: str, state: str):
        self._set_installer_state(name, state)
        self.set_status(f'{name}: {state}')

    def on_progress(self, name, current, total):
        if name == '@capacity':
            self.staged_bytes = max(0, int(current))
            self.update_card_plan()
            self.home_used.setText(pretty_bytes(current))
            self.home_meter.setValue(min(10000, int(10000 * current/max(1, CAPACITY))))
        else:
            self.set_status(name)
            if total == 0 and name.lower().startswith(('converting', 'extracting')):
                # CHDman does not expose a trustworthy percentage here. Keep
                # ONE progress bar, animated rather than falsely frozen at 20%.
                self.bar.setRange(0, 0)
            elif total > 0:
                self.bar.setRange(0, 100)
                self.bar.setValue(min(100, int(100 * current/max(1, total))))

    def on_copy_progress(self, stage, copied, total, filename, speed, eta):
        ratio = min(1., copied/max(1,total))
        self.bar.setRange(0, 100)
        self.bar.setValue(int(ratio*100)); self.copy_meter.setValue(int(ratio*1000))
        minutes, seconds = divmod(round(eta), 60)
        if stage.startswith('Verifying'):
            detail = f'Verifying SHA-256 against source • {filename}\nHash verification in progress; copy ETA does not apply.'
        else:
            detail = (f'{pretty_bytes(copied)} of {pretty_bytes(total)}  •  '
                      f'{pretty_bytes(int(max(0, speed)))}/s  •  About {minutes}m {seconds:02d}s remaining\n{filename}')
        if stage.startswith('Files verified'): detail = stage + '\n' + detail
        self.copy_detail.setText(detail)
        self.set_status(f'{stage}: {filename[:75]}')

    def cancel(self):
        if not self.current_task:
            return
        if self.transfer_process is not None:
            self._stop_transfer_process()
            return
        if self.cancel_requested:
            return
        self.cancel_requested = True
        if self.scan_process is not None:
            self._stop_readonly_scan()
            return
        if self.import_process is not None:
            self._stop_import_process()
            return
        if self.artwork_process is not None:
            self._stop_artwork_process()
            return
        if self.transfer_process is not None:
            self._stop_transfer_process()
            return
        # Copying/writing workers are not killed: forced termination can leave
        # unverified partial files, particularly during NAS writes.
        self.cancel_signal.set()
        self.cancel_btn.setEnabled(False)
        self.task_title.setText(f'Stopping: {self.current_task_name}')
        self.set_status('Stop requested. Finishing the current safe I/O step…')
        QTimer.singleShot(5000, self._warn_if_stop_is_waiting)

    def _warn_if_stop_is_waiting(self):
        if self.current_task and self.cancel_requested and self.scan_process is None:
            self.set_status('Still waiting on file I/O, possibly the NAS. Copy cancellation is cooperative; original files remain protected.')

    def refresh(self):
        if self.needs_workspace_setup or (not is_network_path(self.workspace) and not self.workspace.is_dir()):
            self.set_status("Choose a valid PC or NAS folder before checking your virtual card.")
            return
        """Only check staged virtual-card contents. Downloads require a user action."""
        active_workspace = self.workspace
        self.set_status('Checking files inside your virtual card only. Downloads are not being scanned.')
        self.start_readonly_scan('inventory', active_workspace, self.render_scan)

    def show_card_plan_details(self):
        """Details from cached inventory/preview only; no GUI-thread NAS I/O."""
        model = planned_card_budget(self.staged_bytes, self.staged_companion)
        message = (
            'VIRTUAL 512 GB CARD (advertised planning size, not real capacity)\n\n'
            f'Nominal capacity: {model.capacity:,} bytes ({binary_gib(model.capacity)})\n'
            f'Currently staged: {model.staged:,} bytes ({decimal_gb(model.staged)})\n'
            f'AI companion already included: {model.companion_used:,} bytes\n'
            f'Additional AI allowance: {model.companion_remaining:,} bytes\n'
            f'Protected free space: {model.protected_free:,} bytes (8 GiB)\n'
            f'Remaining room for new games: {model.game_room:,} bytes ({decimal_gb(model.game_room)})\n\n'
            'Only actual files use NAS space. Nothing reserves or creates 512 GB. '
            'The formatted capacity of the real card may be smaller.\n'
        )
        if self.last_physical_plan is not None:
            real = self.last_physical_plan
            message += (
                '\nPHYSICAL CARD (preview only, no copying yet)\n'
                f'Measured capacity: {real.capacity:,} bytes ({binary_gib(real.capacity)})\n'
                f'Already occupied: {real.occupied_before:,} bytes\n'
                f'New bytes to copy: {real.queued_new_bytes:,} bytes\n'
                f'Estimated free after copy: {real.free_after:,} bytes\n'
                'Same-size files must be SHA-256 verified before counting as identical.\n'
            )
        else:
            message += '\nReal microSD capacity not measured yet. Choose the card and run Preview on Copy to card.'
        QMessageBox.information(self, 'Card capacity & exact byte counts', message)

    def update_card_plan(self):
        if not hasattr(self, 'card_plan_bar'):
            return
        model = planned_card_budget(self.staged_bytes, self.staged_companion)
        self.card_plan_bar.set_bytes(model.capacity, model.staged,
                                     ai_remaining=model.companion_remaining,
                                     reserve=model.protected_free)
        self.card_plan_amount.setText(
            f'{decimal_gb(model.staged)} staged / 512.00 GB  •  {model.staged_percent:.2f}%')
        self.card_plan_amount.setToolTip(
            f'Exact staged data: {model.staged:,} bytes = {binary_gib(model.staged)}. '
            f'Nominal 512 GB = {binary_gib(CAPACITY)}; real formatted card may differ.')
        self.card_plan_note.setText(
            f'Room for new game files: {decimal_gb(model.game_room)}  •  '
            f'AI budget remaining: {binary_gib(model.companion_remaining)}  •  '
            f'Keep {binary_gib(FREE_RESERVE)} free')
        if model.over_budget or model.companion_over_budget:
            self.card_plan_note.setText('⚠ Planned card exceeds its safe budget. ' + self.card_plan_note.text())
        self.card_plan_bar.setToolTip('512 GB advertised-size preview, NOT an allocated file or actual card reading. '
            f'{model.staged:,} staged bytes; {model.companion_remaining:,} future AI bytes budgeted; '
            f'{model.protected_free:,} protected free bytes. Storage is measured from virtual-card files.')

    def reset_physical_plan(self, note=None):
        self.last_physical_plan = None
        if hasattr(self, 'card_measured'):
            self.card_measured.setText(note or 'Real microSD not measured yet. Select the card and click Preview.')
            self.real_card_bar.setVisible(False)
            self.card_measured_details.setText('')

    def show_physical_preview(self, plan):
        # Target probe happens in isolated transfer helper, not the GUI.
        if plan.is_simulation:
            self.reset_physical_plan('Practice folder only. This is NOT the real microSD capacity.')
            return
        try:
            physical = physical_card_preview(plan.target_capacity, plan.current_target_free,
                                             plan.bytes_new)
        except ValueError:
            self.reset_physical_plan('Could not measure the selected card. Do not copy until a valid preview succeeds.')
            return
        self.last_physical_plan = physical
        self.card_measured.setText(
            f'REAL CARD • {decimal_gb(physical.capacity)} formatted ({binary_gib(physical.capacity)})  •  '
            'Preview only, not yet transferred')
        self.real_card_bar.set_bytes(physical.capacity, physical.occupied_before,
                                     queued=physical.queued_new_bytes, reserve=physical.protected_free)
        self.real_card_bar.setVisible(True)
        self.card_measured_details.setText(
            f'Currently used on card: {decimal_gb(physical.occupied_before)}  •  '
            f'New transfer: {decimal_gb(physical.queued_new_bytes)}  •  '
            f'Free afterward: {decimal_gb(physical.free_after)}  •  '
            + ('8 GiB safety reserve maintained' if physical.fits else '⚠ Free-space reserve NOT met'))
        self.real_card_bar.setToolTip('Blue: already occupied on card (including files not managed by app). '
             'Teal: estimated new data. Gold: protected free space. Preview is size-based; '
             'already-present files still require SHA-256 checking during copying.')

    def render_scan(self, result):
        if result is None or result[4] is None:
            self.set_status('Virtual-card check stopped. Your files were not changed.')
            return
        scan_path, entries, size, count, companion = result
        if scan_path != self.workspace:
            self.refresh()
            return
        self.card_entries, self.staged_bytes, self.staged_files = entries, size, count
        self.staged_companion = companion
        self.update_card_plan()
        if self.last_physical_plan is not None:
            self.reset_physical_plan('Staged files changed or were rescanned. Preview the card again for current numbers.')
        available = max(0, CAPACITY - size - FREE_RESERVE - max(0, COMPANION_BUDGET - companion))
        self.home_used.setText(pretty_bytes(size))
        self.home_room.setText(f'{pretty_bytes(available)} virtual-card budget remaining')
        self.home_meter.setValue(min(10000, int(10000*size/max(1,CAPACITY))))
        games = len(entries)
        self.home_hint.setText(f'{games:,} recognized game files on your virtual card. '
                               'Your Downloads folder is only searched when you choose Find Games in Downloads.')
        self.library_count.setText(f'{games:,} recognized game files • {count:,} total files • {pretty_bytes(size)} used')
        self.library_empty.setVisible(games == 0)
        self.game_views.setVisible(games != 0)
        self.card_search.setVisible(games != 0)
        self.cover_index = local_index(self.workspace)
        self.fill_card()
        initial_scan = (games > 0 and self.auto_cover.isChecked() and
                        str(self.settings.value('artwork_initialized_at', '')) != str(self.workspace))
        if initial_scan:
            # Run once for an upgraded/existing library, not on every startup.
            self.settings.setValue('artwork_initialized_at', str(self.workspace))
        if self.pending_auto_artwork or initial_scan:
            self.pending_auto_artwork = False
            if self.auto_cover.isChecked() and games:
                QTimer.singleShot(0, lambda: self.start_cover_scan(automatic=True))
        self.update_destination_hint()
        if self.stack.currentIndex() == 2:
            self.update_tools_status()
        self.update_workspace_location()
        self.set_status(f'Card check finished: {games:,} game files and {pretty_bytes(size)} used. No Downloads scan.')

    def _gallery_search_changed(self):
        self.gallery_visible_cap = 48
        self.fill_card()

    def set_gallery_mode(self, mode: str):
        mode = mode if mode in ('Gallery', 'List') else 'Gallery'
        self.gallery_mode = mode
        self.settings.setValue('gallery_mode', mode)
        if not hasattr(self, 'game_views'): return
        self.game_views.setCurrentIndex(1 if mode == 'Gallery' else 0)
        for widget, active in ((self.grid_button, mode == 'Gallery'),
                               (self.list_button, mode == 'List')):
            widget.setProperty('active', active)
            widget.style().unpolish(widget); widget.style().polish(widget)
        self.gallery_more.setVisible(mode == 'Gallery')
        if self.card_entries: self.fill_card()

    def show_more_gallery(self):
        self.gallery_visible_cap += 48
        self.fill_card()

    def _visible_games(self, ignore_system=False):
        term = self.card_search.text().casefold().strip()
        system = self.game_filter.currentText()
        tracks = getattr(self, 'cue_tracks', set())
        games = unique_game_art_entries([e for e in self.card_entries
            if os.path.normcase(os.path.abspath(str(e.path))) not in tracks])
        chd_siblings = {(e.system, str(e.path.parent).casefold(), e.path.stem.casefold())
                        for e in games if e.extension.lower() == '.chd'}
        # When an old CUE/BIN set was later converted, present the playable CHD
        # as the game. Originals remain protected but not duplicated in gallery.
        games = [e for e in games if not (e.extension.lower() == '.cue' and
                 (e.system, str(e.path.parent).casefold(), e.path.stem.casefold()) in chd_siblings)]
        self.disc_groups = {}
        visible = []
        for group in group_games(games):
            entry = group[0]
            self.disc_groups[game_key(entry.system, entry.label)] = group
            if (ignore_system or system == 'All systems' or entry.system == system) and any(
                term in (preferred_title(self.settings, e) + ' ' + e.label + ' ' + str(e.path)).casefold() for e in group):
                visible.append(entry)
        return visible

    def _render_console_nav(self, all_games):
        """Scrollable, synchronized console filters; count logical games only."""
        while self.console_nav_layout.count():
            item = self.console_nav_layout.takeAt(0)
            widget = item.widget()
            if widget is not None: widget.deleteLater()
        counts = console_counts(all_games)
        selected = self.game_filter.currentText()
        systems = sorted(set(PRIMARY_SYSTEMS) | set(counts), key=console_order_key)
        for system in ['All systems'] + systems:
            visual = console_visual(system)
            active = system == selected
            count = len(all_games) if system == 'All systems' else counts.get(system, 0)
            short = 'ALL' if system == 'All systems' else visual['short']
            pill = QPushButton(f'{short}   {count}')
            pill.setObjectName('SystemPill')
            pill.setProperty('active', active)
            accent = '#80BCFF' if system == 'All systems' else visual['accent']
            pill.setStyleSheet(
                f"QPushButton#SystemPill {{border:1px solid {accent};"
                f"background:{'#274464' if active else '#1c2d47'};"
                f"color:{'#ffffff' if active else accent};font-weight:750;}}"
            )
            desc = 'All available systems' if system == 'All systems' else visual['name']
            if visual['experimental']: desc += ' • Experimental on RG Rotate; performance not guaranteed'
            pill.setToolTip(f'{desc} • {count} games')
            pill.clicked.connect(lambda _checked=False, choice=system: self.game_filter.setCurrentText(choice))
            self.console_nav_layout.addWidget(pill)
        self.console_nav_layout.addStretch(1)

    def _clear_gallery(self):
        while self.gallery_grid.count():
            item = self.gallery_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def fill_card(self):
        if not hasattr(self, 'game_views'): return
        term = self.card_search.text().casefold()
        system = self.game_filter.currentText()
        entries = sorted((e for e in self.card_entries if term in (e.label + str(e.path)).casefold()
                   and (system == 'All systems' or e.system == system)),
                   key=lambda e: (console_order_key(e.system), e.label.casefold()))
        shown = entries[:MAX_VISIBLE_FILES]
        self.card_table_entries = shown
        self.card_table.setUpdatesEnabled(False)
        self.card_table.setRowCount(len(shown))
        for r,e in enumerate(shown):
            try: relative = str(e.path.relative_to(self.workspace))
            except ValueError: relative = str(e.path)
            for col, txt in enumerate((e.path.name, e.system, pretty_bytes(e.size), relative)):
                self.card_table.setItem(r, col, QTableWidgetItem(str(txt)))
        self.card_table.setUpdatesEnabled(True)
        all_games = self._visible_games(ignore_system=True)
        self._render_console_nav(all_games)
        games = [g for g in all_games if system == 'All systems' or g.system == system]
        self.library_count.setText(f'{len(games):,} games shown  •  {pretty_bytes(self.staged_bytes)} used on virtual card')
        if self.gallery_mode == 'Gallery':
            self._render_gallery(games)

    def _render_gallery(self, games):
        self._clear_gallery()
        ordered = [g for _, shelf in grouped_shelves(games) for g in shelf]
        shown = ordered[:self.gallery_visible_cap]
        cols = gallery_columns(self.gallery_scroll.viewport().width(), self.scale_percent)
        previews = 0
        row = 0
        for system, shelf in grouped_shelves(shown):
            visual = console_visual(system)
            header = QFrame(); header.setObjectName('ConsoleSection')
            header.setStyleSheet(
                f"QFrame#ConsoleSection {{border-left:4px solid {visual['accent']};}}"
            )
            h = QHBoxLayout(header); h.setContentsMargins(16, 11, 15, 11)
            name = QLabel(f"{visual['short']}   {visual['name']}")
            name.setStyleSheet(f"font-weight:850;color:{visual['accent']};")
            h.addWidget(name)
            h.addStretch(1)
            note = f"{len(shelf)} games"
            if visual['experimental']:
                note += '  •  Experimental device support'
            h.addWidget(label(note, 'Small'))
            self.gallery_grid.addWidget(header, row, 0, 1, cols)
            row += 1
            for i, game in enumerate(shelf):
                tile = QFrame(); tile.setObjectName('GameTile')
                tile.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                tile.customContextMenuRequested.connect(
                    lambda pos, g=game, frame=tile: self.show_game_context_menu(g, frame.mapToGlobal(pos)))
                tile.setMinimumWidth(round(158*self.scale_percent/100))
                t = QVBoxLayout(tile); t.setContentsMargins(10, 10, 10, 10); t.setSpacing(7)
                image = QLabel(); image.setObjectName('CoverPreview')
                image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image.setMinimumHeight(round(185*self.scale_percent/100))
                image.setMaximumHeight(round(208*self.scale_percent/100))
                group = self.disc_groups.get(game_key(game.system, game.label), [game])
                preview = cached_preview(self.workspace, game.system, game.label)
                # Reuse an earlier Disc 1 cover as a preview if a freshly-made
                # collection M3U lacks cover art. Local cache only; no NAS I/O.
                if game.extension.lower() == '.m3u' and not preview.is_file():
                    from ps1_collections import disc_identity
                    older_art = sorted((e for e in group if e.extension.lower() == '.chd'),
                                       key=lambda e: disc_identity(e.label)[1] or 999)
                    for disc in older_art:
                        candidate = cached_preview(self.workspace, disc.system, disc.label)
                        if candidate.is_file():
                            preview = candidate
                            break
                # Load local PC image only, never request SMB data in the GUI.
                if preview.is_file():
                    pixmap = QPixmap(str(preview))
                    if not pixmap.isNull():
                        image.setPixmap(pixmap.scaled(round(152*self.scale_percent/100),
                                 round(198*self.scale_percent/100),
                                 Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        previews += 1
                    else:
                        image.setText('Cover unavailable')
                else:
                    image.setText(f'{game.system}\n\nNo cover yet')
                t.addWidget(image)
                game_name = label(preferred_title(self.settings, game), '', True)
                game_name.setMinimumHeight(round(37*self.scale_percent/100))
                game_name.setToolTip(game.label)
                t.addWidget(game_name)
                # The badge comes from the actual scanned file extension, not the
                # expected converter output or a stale task status.
                fmt = format_badge_info(game, group)
                details = QHBoxLayout(); details.setSpacing(6)
                details.addWidget(label(f'{game.system}  •  {pretty_bytes(game.size)}', 'Small', True), 1)
                badge = QPushButton(fmt['badge']); badge.setObjectName('FormatBadge')
                badge.setProperty('formatKind', fmt['kind'])
                badge.setCursor(Qt.CursorShape.PointingHandCursor)
                badge.setToolTip('Click to see the actual stored format, files and verification limits')
                badge.clicked.connect(lambda _=False, g=game, grp=list(group): self.show_game_format(g, grp))
                details.addWidget(badge)
                t.addLayout(details)
                if len(group) > 1:
                    count = sum(e.extension.lower() == '.chd' for e in group)
                    detail = (f'{count} discs • one game collection • M3U playlist'
                              if game.extension.lower() == '.m3u' and count >= 2 else
                              f'{len(group)} disc / file variants • files kept separate')
                    discs = label(detail, 'Small', True)
                    discs.setToolTip('\n'.join(str(e.path) for e in group)); t.addWidget(discs)
                t.addWidget(button('Edit display title…', lambda _=False, g=game: self.edit_game_title(g)))
                info = self.cover_index.get(game_key(game.system, game.label), {})
                st = info.get('status', '')
                if not preview.is_file() and st in ('review', 'not found'):
                    t.addWidget(label('Match needs review', 'Small'))
                t.addWidget(button('Change cover' if preview.is_file() else 'Search for cover',
                                   lambda _=False, g=game: self.open_manual_cover_search(g)))
                self.gallery_grid.addWidget(tile, row + i//cols, i%cols)
            row += (len(shelf) + cols - 1) // cols
        self.gallery_more.setVisible(len(games) > len(shown))
        missing = len(shown) - previews
        self.cover_info.setText(f'{previews} covers visible  •  {missing} without a local cover preview. '
                                 'Use Find missing covers or choose a game to correct its cover.')

    def show_file_row_context_menu(self, position):
        row = self.card_table.rowAt(position.y())
        entries = getattr(self, 'card_table_entries', [])
        if 0 <= row < len(entries):
            self.show_game_context_menu(entries[row], self.card_table.viewport().mapToGlobal(position))

    def show_game_context_menu(self, entry, global_pos):
        """Native right-click commands for a single logical game, without NAS operations in Qt."""
        menu = QMenu(self); menu.setObjectName('GameContext')
        title_action = menu.addAction('✎  Edit game title')
        cover_action = menu.addAction('▧  Preview / change cover')
        info_action = menu.addAction('ⓘ  File format & details')
        menu.addSeparator()
        candidate = self.ps1_legacy_source_for(entry)
        eligible = candidate is not None
        convert_action = menu.addAction(
            '◆  Verify CHD + archive original tracks' if entry.extension.lower() == '.chd'
            else '◆  Convert to verified CHD + tidy PSX folder') if eligible else None
        if convert_action is None:
            disabled_action = menu.addAction('✓  No unconverted PS1 disc sources here')
            disabled_action.setEnabled(False)
        menu.addSeparator()
        folder_action = menu.addAction('▣  Open game folder')
        originals_action = menu.addAction('▣  Open conversion backups (old tracks)') if entry.system == 'PS1' else None
        chosen = menu.exec(global_pos)
        if chosen is None: return
        if chosen is title_action: self.edit_game_title(entry)
        elif chosen is cover_action: self.open_manual_cover_search(entry)
        elif chosen is info_action:
            self.show_game_format(entry, self.disc_groups.get(game_key(entry.system, entry.label), [entry]))
        elif chosen is convert_action: self.convert_game_to_chd(candidate)
        elif chosen is folder_action: self.open_path(entry.path.parent)
        elif originals_action is not None and chosen is originals_action:
            self.open_conversion_backups()

    def ps1_legacy_source_for(self, entry):
        """Find a source inside our already scanned inventory, not with NAS stat calls."""
        if entry.system != 'PS1': return None
        if entry.extension.lower() in ('.cue', '.img'): return entry
        if entry.extension.lower() != '.chd': return None
        for item in self.card_entries:
            if (item.system == 'PS1' and item.extension.lower() in ('.cue', '.img')
                    and item.path.parent == entry.path.parent
                    and item.path.stem.casefold() == entry.path.stem.casefold()):
                return item
        return None

    def convert_game_to_chd(self, entry):
        if self.current_task or not self.ensure_workspace(): return
        if entry.system != 'PS1' or entry.extension.lower() not in ('.cue', '.img'):
            QMessageBox.information(self, 'Conversion not available',
                'Right-click a PlayStation 1 BIN/CUE game or IMG source to convert it.'); return
        if not within(entry.path, self.workspace / 'ROMs' / 'psx'):
            QMessageBox.warning(self, 'Not a PS1 library file',
                'This game must live in the selected virtual-card PSX folder.'); return
        recovery = self.workspace.parent / (self.workspace.name + ' - Conversion Backups')
        answer = QMessageBox.question(self, 'Convert and tidy this PS1 game?',
            f'Convert “{entry.label}” into one verified CHD in the SAME PSX folder?\n\n'
            'Only after CHDman verifies the destination, the old CUE/BIN or IMG files '
            'will be moved OUT of the virtual card into a recoverable backup.\n\n'
            f'Recovery location:\n{recovery}\n\n'
            'Nothing is permanently deleted. An ambiguous IMG or missing track will stop safely.\n\n'
            'Continue?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes: return
        self.start_import_process({'mode':'convert_selected_ps1', 'workspace':str(self.workspace),
            'source':str(entry.path), 'binary':str(tools_root()/'chdman'/'chdman.exe')},
            'Converting & Organizing PS1 Game', finished=self.single_chd_completed)

    def single_chd_completed(self, result):
        if result.get('cancelled'):
            self.set_status('Conversion stopped. Original game files were protected.')
        elif result.get('errors'):
            QMessageBox.warning(self, 'CHD needs attention', '\n'.join(result['errors'][:6]))
            self.set_status('Conversion could not finish safely; sources kept.')
        else:
            notice = QMessageBox(self)
            notice.setWindowTitle('PS1 game prepared')
            notice.setIcon(QMessageBox.Icon.Information)
            notice.setText('The CHD passed verification and is ready in the PSX folder.')
            notice.setInformativeText(
                f"CHD: {result.get('output','')}\n\n"
                f"Recovery originals: {result.get('backup','')}\n\n"
                'Only the verified CHD remains on your virtual card. Recovery copies '
                'still use NAS storage until you review and remove them.')
            open_chd = notice.addButton('Open CHD folder', QMessageBox.ButtonRole.ActionRole)
            open_old = notice.addButton('Open recovery originals', QMessageBox.ButtonRole.ActionRole)
            notice.addButton('Done', QMessageBox.ButtonRole.AcceptRole)
            notice.exec()
            if notice.clickedButton() is open_chd and result.get('output'):
                self.open_path(Path(result['output']).parent)
            elif notice.clickedButton() is open_old and result.get('backup'):
                self.open_path(Path(result['backup']))
            self.set_status('CHD verified; old tracks moved to recovery outside the virtual card.')
        self.refresh()

    def conversion_recovery_root(self):
        return self.workspace.parent / (self.workspace.name + ' - Conversion Backups')

    def open_conversion_backups(self):
        """Old converted tracks live next to, not inside, the virtual card."""
        if self.current_task:
            QMessageBox.information(self, 'Task running', 'Wait until the current operation finishes.')
            return
        recovery = self.conversion_recovery_root()
        # Opening an existing recovery folder is read-only. Do not create or
        # scan an SMB folder from the GUI just to check if it exists.
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(recovery)))

    def batch_convert_ps1(self):
        if self.current_task or not self.ensure_workspace():
            return
        dialog = QMessageBox(self)
        dialog.setWindowTitle('Batch convert PS1 discs · lossless CHD')
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setText('Convert all remaining CUE/BIN and supported IMG discs in your virtual PSX folder?')
        dialog.setInformativeText(
            'Every disc is converted with the normal lossless CD codecs and verified by CHDman. '
            'The source library you imported from elsewhere on your NAS will NEVER be changed.\n\n'
            'Choose what happens to the COPIES already inside your virtual-card ROMs/psx folder. '
            'Unknown/ambiguous IMG images and broken disc sets will be skipped, not deleted.')
        keep = dialog.addButton('Keep recovery backups', QMessageBox.ButtonRole.AcceptRole)
        delete = dialog.addButton('Remove verified working copies', QMessageBox.ButtonRole.DestructiveRole)
        dialog.addButton('Cancel', QMessageBox.ButtonRole.RejectRole)
        dialog.setDefaultButton(keep)
        dialog.exec()
        selected = dialog.clickedButton()
        if selected not in (keep, delete): return
        mode = 'delete' if selected is delete else 'backup'
        if mode == 'delete':
            confirm = QMessageBox.question(self, 'Confirm deleting only virtual-card working tracks',
                'After EACH CHD passes verification, the app will permanently remove its '
                'old CUE/BIN/IMG working files INSIDE this virtual card only.\n\n'
                f'Virtual-card PSX folder: {self.workspace / "ROMs" / "psx"}\n\n'
                'The source game collection elsewhere on your NAS is NOT accessed or deleted. '
                'This option does NOT delete existing recovery backups from older conversions.\n\n'
                'Only a verified CHD will remain for each successfully converted single disc. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if confirm != QMessageBox.StandardButton.Yes: return
        self.start_import_process({'mode':'batch_convert_ps1', 'workspace':str(self.workspace),
            'binary':str(tools_root()/'chdman'/'chdman.exe'), 'cleanup_mode':mode},
            'Batch Converting PS1 Discs', finished=self.batch_chd_completed)

    def batch_chd_completed(self, result):
        done, total = result.get('completed',0), result.get('total',0)
        removed = result.get('deleted_files',0)
        bytes_removed = result.get('nas_bytes_reclaimed',0)
        errors = result.get('errors',[])
        message = (f'Processed {done} of {total} disc(s).\n'
                   f'New verified CHDs: {result.get("converted",0)}\n'
                   f'Previously existing verified CHDs: {result.get("skipped",0)}\n')
        if result.get('cleanup_mode') == 'delete':
            message += (f'Working files removed from virtual card: {removed}\n'
                        f'Approximate source bytes deleted: {pretty_bytes(bytes_removed)}\n')
        else:
            message += f'Recovery folders created: {len(result.get("backups",[]))}\n'
        if result.get('cancelled'):
            message += '\nStopped. Already completed and verified CHDs remain. '
        if errors:
            message += '\nThese discs need review (their originals were not deleted):\n' + '\n'.join(errors[:8])
        if not total and not errors:
            message += '\nNo CUE/IMG sources remain to convert in the PSX folder.'
        if result.get('cleanup_mode') == 'backup':
            message += '\n\nExisting and new recovery backups are outside the virtual card.'
        QMessageBox.warning(self, 'Batch PS1 conversion finished with warnings', message) if errors else \
            QMessageBox.information(self, 'Batch PS1 conversion finished', message)
        self.set_status('Batch PS1 conversion finished; review results above.')
        self.refresh()

    def show_game_format(self, entry, group):
        info = format_badge_info(entry, group)
        files = '\n'.join(f'  • {g.path.name} ({pretty_bytes(g.size)})' for g in group[:16])
        if len(group) > 16:
            files += f'\n  • … and {len(group)-16} more'
        QMessageBox.information(self, 'Game file format',
            f'{preferred_title(self.settings, entry)}\n\n'
            f'Format: {info["description"]}\n'
            f'Displayed file: {entry.path.name}\n'
            f'Listed file size: {pretty_bytes(entry.size)}\n\n'
            f'{info["verification"]}\n\n'
            f'Visible disc / playlist entries:\n{files}\n\n'
            'The badge describes the files in your virtual card. It does not '
            'claim the RG Rotate has launched this game successfully.')

    def edit_game_title(self, entry):
        title, accepted = QInputDialog.getText(self, 'Edit game title',
            'Display title (original files and artwork names stay the same):',
            text=preferred_title(self.settings, entry))
        if accepted and title.strip():
            self.settings.setValue('titles/' + game_key(entry.system, entry.label), title.strip())
            self.fill_card(); self.set_status('Display title saved. Original files kept.')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'command_host'): QTimer.singleShot(0, self.reflow_commands)
        if hasattr(self, 'gallery_scroll') and self.card_entries:
            if not hasattr(self, 'gallery_resize_timer'):
                self.gallery_resize_timer = QTimer(self); self.gallery_resize_timer.setSingleShot(True)
                self.gallery_resize_timer.timeout.connect(self.fill_card)
            self.gallery_resize_timer.start(120)

    def reflow_commands(self):
        if not hasattr(self, 'commands'): return
        widgets = [self.page_action, self.page_secondary, self.transfer_btn]
        required = sum(w.sizeHint().width() for w in widgets if not w.isHidden()) + 24
        narrow = required > self.command_host.width()
        for widget in widgets: self.commands.removeWidget(widget)
        self.commands.addWidget(self.page_action, 0, 0)
        self.commands.addWidget(self.page_secondary, 0, 1)
        if narrow:
            self.commands.addWidget(self.transfer_btn, 1, 0, 1, 2)
        else:
            self.commands.addWidget(self.transfer_btn, 0, 2)
        self.commands.setColumnStretch(2, 0)
        self.commands.setColumnStretch(3, 1)

    def edit_cover(self, entry):
        # Keep older menu callers functional; manual title search is now the
        # default, including for special-edition and modified game filenames.
        self.open_manual_cover_search(entry)

    def search_cover_for_game(self):
        """Open manual search even when the user is browsing File list mode."""
        games = unique_game_art_entries(self.card_entries)
        if not games:
            QMessageBox.information(self, 'Add a game first',
                                    'Import a game into My Games, then search for its cover.')
            return
        options = [f'{g.system}  •  {g.label}' for g in games]
        selected, ok = QInputDialog.getItem(self, 'Choose which game needs artwork',
                                             'Select your imported game:', options, 0, False)
        if ok:
            self.open_manual_cover_search(games[options.index(selected)])

    def open_manual_cover_search(self, entry):
        if not self.ensure_workspace(): return
        if self.current_task:
            QMessageBox.information(self, 'Another task is running',
                                    'Finish or stop the current task, then search for artwork.')
            return
        if self.manual_cover_dialog is not None:
            self.manual_cover_dialog.close()
        self.manual_cover_entry = entry
        dialog = QDialog(self)
        dialog.setWindowTitle('Find artwork for ' + clean_title(entry.label))
        dialog.setMinimumSize(600, 570)
        dialog.resize(740, 690)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(label(f'Find a cover for {clean_title(entry.label)}', 'H2', True))
        layout.addWidget(label(f'{entry.system} • Type the title YOU want to search for. '
            'Only the cover is added; your game file is never changed.', 'Subtitle', True))
        row = QHBoxLayout()
        self.manual_cover_query = QLineEdit(clean_title(entry.label))
        self.manual_cover_query.setPlaceholderText('For example: Resident Evil')
        self.manual_cover_query.returnPressed.connect(self.run_manual_cover_search)
        row.addWidget(self.manual_cover_query, 1)
        row.addWidget(button('Search', self.run_manual_cover_search, 'Primary'))
        layout.addLayout(row)
        layout.addWidget(label('Matching artwork titles (choose the correct edition):', 'Small'))
        self.manual_cover_results = QListWidget()
        self.manual_cover_results.setObjectName('CoverSearchResults')
        self.manual_cover_results.setMinimumHeight(190)
        self.manual_cover_results.itemSelectionChanged.connect(self.manual_cover_selection_changed)
        # A double click should preview, never accidentally apply unseen artwork.
        self.manual_cover_results.itemDoubleClicked.connect(lambda _item: self.preview_manual_cover())
        layout.addWidget(self.manual_cover_results, 2)
        self.manual_cover_preview_timer = QTimer(dialog)
        self.manual_cover_preview_timer.setSingleShot(True)
        self.manual_cover_preview_timer.setInterval(260)
        self.manual_cover_preview_timer.timeout.connect(self.preview_manual_cover)
        self.manual_cover_preview = FittedCoverPreview('Select an edition to see the artwork. Nothing is applied automatically.')
        self.manual_cover_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.manual_cover_preview.setObjectName('CoverPreview')
        self.manual_cover_preview.setMinimumHeight(250)
        layout.addWidget(self.manual_cover_preview, 1)
        self.manual_cover_status = label('Edit the title and press Search to find artwork.', 'Small', True)
        layout.addWidget(self.manual_cover_status)
        actions = QHBoxLayout()
        self.manual_preview_button = button('Preview selected', self.preview_manual_cover)
        self.manual_apply_button = button('Use selected cover', self.apply_manual_cover, 'Accent')
        self.manual_preview_button.setEnabled(False)
        self.manual_apply_button.setEnabled(False)
        actions.addWidget(self.manual_preview_button)
        actions.addWidget(self.manual_apply_button)
        layout.addLayout(actions)
        extras = QHBoxLayout()
        extras.addWidget(button('Choose image from PC instead', lambda: self.manual_local_cover(entry)))
        extras.addWidget(button('Browse Libretro covers', lambda: QDesktopServices.openUrl(QUrl('https://github.com/libretro-thumbnails/' + ('Sony_-_PlayStation' if entry.system == 'PS1' else 'libretro-thumbnails')))))
        extras.addWidget(button('Close', dialog.close))
        layout.addLayout(extras)
        self.manual_cover_dialog = dialog
        dialog.finished.connect(lambda _code, d=dialog: self.manual_dialog_closed(d))
        dialog.show()
        self.run_manual_cover_search()

    def manual_dialog_closed(self, dialog):
        if self.manual_cover_dialog is dialog:
            if hasattr(self, 'manual_cover_preview_timer'):
                self.manual_cover_preview_timer.stop()
            self.manual_cover_dialog = None
            self.manual_cover_entry = None

    def manual_local_cover(self, entry):
        if self.manual_cover_dialog is not None:
            self.manual_cover_dialog.close()
        self.choose_cover_for(entry)

    def manual_cover_selection_changed(self):
        selected = bool(self.manual_cover_results.selectedItems())
        self.manual_preview_button.setEnabled(selected and not self.current_task)
        self.manual_apply_button.setEnabled(selected and not self.current_task)
        self.manual_cover_preview.clear_cover('Loading artwork preview for the selected edition…' if selected else
                                             'Select an edition to preview its cover.')
        self.manual_cover_preview_timer.stop()
        if selected and not self.current_task:
            self.manual_cover_preview_timer.start()

    def selected_manual_cover_title(self):
        items = self.manual_cover_results.selectedItems() if self.manual_cover_dialog else []
        return items[0].data(Qt.ItemDataRole.UserRole) if items else None

    def run_manual_cover_search(self):
        if self.current_task or self.manual_cover_dialog is None or self.manual_cover_entry is None:
            return
        query = self.manual_cover_query.text().strip()
        if not query:
            self.manual_cover_status.setText('Enter a game title before searching.')
            self.manual_cover_query.setFocus()
            return
        self.manual_cover_results.clear()
        self.manual_cover_status.setText(f'Searching for: {query}…')
        self.manual_cover_preview.clear_cover('Searching the artwork catalog…')
        self.manual_preview_button.setEnabled(False)
        self.manual_apply_button.setEnabled(False)
        entry = self.manual_cover_entry
        self.start_artwork_process({'mode':'search', 'workspace':str(self.workspace),
            'system':entry.system, 'label':entry.label, 'query':query},
            'Searching Artwork: ' + query[:45])

    def preview_manual_cover(self):
        title = self.selected_manual_cover_title()
        if not title or self.current_task or self.manual_cover_entry is None: return
        entry = self.manual_cover_entry
        self.manual_cover_status.setText(f'Loading cover preview for {title}…')
        self.manual_cover_preview.clear_cover('Loading cover preview…')
        self.start_artwork_process({'mode':'preview', 'workspace':str(self.workspace),
            'system':entry.system, 'label':entry.label, 'source_title':title},
            'Previewing Artwork')

    def apply_manual_cover(self):
        title = self.selected_manual_cover_title()
        if not title or self.current_task or self.manual_cover_entry is None: return
        entry = self.manual_cover_entry
        if QMessageBox.question(self, 'Use this artwork?',
            f'Apply the cover for “{title}” to your imported game “{entry.label}”?\n\n'
            'Only its artwork will change. Your original game file will stay untouched.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        if self.manual_cover_dialog is not None:
            self.manual_cover_dialog.close()
        self.start_artwork_process({'mode':'pick', 'workspace':str(self.workspace),
            'system':entry.system, 'label':entry.label, 'source_title':title,
            'replace':True}, 'Saving Chosen Game Cover')

    def choose_cover_for(self, entry):
        file, _ = QFileDialog.getOpenFileName(self, 'Choose cover artwork', str(self.incoming),
                                              'Image files (*.png *.jpg *.jpeg *.webp)')
        if not file: return
        if QMessageBox.question(self, 'Use this game cover?',
                   'Apply the selected image to this game? If an older cover exists, it will be replaced. '
                   'Your original image file and your ROMs are untouched.',
                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                   QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self.start_artwork_process({'mode':'local', 'workspace':str(self.workspace),
                                    'system':entry.system, 'label':entry.label,
                                    'source_path':str(file), 'replace':True}, 'Saving Game Cover')

    def open_apks_folder(self):
        if not self.ensure_workspace(): return
        self.open_path(self.workspace / 'SetupPackages')

    def pick_apks(self):
        if not self.ensure_workspace(): return
        names, _ = QFileDialog.getOpenFileNames(self, 'Choose Android APK installers',
                                                 str(self.incoming), 'Android installers (*.apk *.APK);;All files (*.*)')
        if names: self.import_apks([Path(p) for p in names])

    def import_apks(self, paths: list[Path]):
        if not self.ensure_workspace(): return
        paths = [Path(p) for p in paths]
        if not paths: return
        not_apk = [p.name for p in paths if p.suffix.lower() != '.apk' or not p.is_file()]
        if not_apk:
            QMessageBox.information(self, 'Only Android installers here',
                'Please add .apk files in Apps & APKs. Games belong in My Games.\n\n'
                + 'Unsupported: ' + ', '.join(not_apk[:8]))
            return
        if self.current_task:
            QMessageBox.information(self, 'Another task is still running',
                f'Current operation: {self.current_task_name}.\n\n'
                'Wait for it to finish, or use Stop task, before adding Android APKs.')
            return
        self.navigate(2, refresh_apps=False)
        self.apk_status.setText(f'Adding {len(paths)} APK file(s) to your virtual card…')
        self.set_status(f'Preparing {len(paths)} Android installer(s)…')
        self.start_import_process({'mode': 'apks', 'paths': [str(p) for p in paths],
                                   'workspace': str(self.workspace)},
                                  'Adding Android APKs', finished=self.apk_import_completed)

    def apk_import_completed(self, result):
        added = result.get('added', 0)
        already = result.get('already', 0)
        errors = result.get('errors', [])
        root = self.workspace / 'SetupPackages'
        paths = result.get('paths', [])
        if result.get('cancelled'):
            self.apk_status.setText('APK import stopped. Original downloads were left untouched.')
            self.set_status('APK import cancelled safely.')
        elif not (added or already):
            reason = '\n'.join(errors[:8]) if errors else 'No APK files were imported.'
            self.apk_status.setText('APK import did not finish. Check the error message and retry.')
            QMessageBox.warning(self, 'APK import failed',
                f'No Android installers were added.\n\n{reason}\n\n'
                'You can retry. Your original APK is unchanged.')
            self.set_status('APK import failed. Nothing was added.')
        else:
            heading = 'APK import completed' if not errors else 'APK import completed with warnings'
            lines = [f'{added} APK(s) added; {already} already present.',
                     '', 'Saved to:', str(root)]
            if paths:
                lines.extend(['', 'Prepared installer(s):',
                              *[Path(p).name for p in paths[:8]]])
            lines.extend(['', 'The APK is prepared, not installed on Android yet.',
                          'The original download was not moved or deleted.'])
            if errors:
                lines.extend(['', 'Items needing attention:', *errors[:8]])
            self.apk_status.setText(f'{added + already} APK(s) prepared in {root}. '
                                    'Android installation still required.')
            (QMessageBox.warning if errors else QMessageBox.information)(
                self, heading, '\n'.join(lines))
            self.set_status(f'APK import completed: {added} new, {already} already present.')
        # Unlike the previous release, update the INSTALLER page, not the game list.
        # On network shares this is a stoppable, read-only helper process.
        if added or already:
            QTimer.singleShot(0, self.update_tools_status)

    def handle_home_drop(self, paths: list[Path]):
        if not self.ensure_workspace(): return
        if all(p.suffix.lower() == '.apk' for p in paths):
            self.import_apks(paths)
        elif any(p.suffix.lower() == '.apk' for p in paths):
            QMessageBox.information(self, 'Separate your game and Android files',
                'Drop APK installers into Apps & APKs, and game files into My Games.')
        else:
            self.handle_game_drop(paths)

    def handle_game_drop(self, paths: list[Path]):
        if not self.ensure_workspace(): return
        folders = [p for p in paths if p.is_dir()]
        files = [p for p in paths if p.is_file()]
        if any(p.suffix.lower() == '.apk' for p in files):
            QMessageBox.information(self, 'Android installer detected',
                'APK files belong in Apps & APKs, not inside the game folders.')
            return
        if folders:
            if len(folders) != 1 or files:
                QMessageBox.information(self, 'Drop one folder at a time',
                    'For safety, drop one game folder at a time, or select individual game files.')
                return
            self.import_folder_path(folders[0])
        elif files:
            self.import_paths(files)

    def ps1_import_options(self):
        return {'auto_ps1_chd': self.auto_ps1_chd.isChecked(),
                'auto_artwork': self.auto_cover.isChecked(),
                'binary': str(tools_root() / 'chdman' / 'chdman.exe')}

    def optimize_existing_ps1(self):
        if not self.ensure_workspace(): return
        if QMessageBox.question(self, 'Convert PS1 discs already in your card?',
                'This converts any existing PS1 CUE/BIN games to verified CHDs. '
                'The originals remain untouched and will still take up space until you review them. '
                'It may take a while, especially on a NAS. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self.start_import_process({'mode': 'optimize_existing_ps1',
                                   'workspace': str(self.workspace),
                                   'binary': str(tools_root() / 'chdman' / 'chdman.exe'),
                                   'auto_artwork': self.auto_cover.isChecked()},
                                  'Converting Earlier PlayStation Games', finished=self.import_completed)

    def pick_files(self):
        if not self.ensure_workspace(): return
        names, _ = QFileDialog.getOpenFileNames(self, 'Choose your existing game files', str(self.incoming),
            'Games and archives (*.zip *.7z *.chd *.cue *.bin *.img *.iso *.cso *.pbp *.m3u *.ccd *.ecm *.gba *.gb *.gbc *.nes *.sfc *.smc *.md *.gen *.nds *.n64 *.z64 *.v64 *.gdi *.cdi);;All files (*.*)')
        if names: self.import_paths([Path(x) for x in names])

    def pick_ps1_collection(self):
        """One clear import action for complete multi-disc PlayStation game sets."""
        if not self.ensure_workspace(): return
        folder = QFileDialog.getExistingDirectory(
            self, 'Choose one PlayStation 1 game folder with all CUE/BIN discs', str(self.incoming))
        if not folder: return
        self.navigate(1)
        self.set_status('Checking every PS1 disc, converting to verified CHD and preparing one game collection…')
        self.start_import_process({'mode': 'folder', 'folder': str(folder),
                                   'workspace': str(self.workspace), 'fallback': 'PS1',
                                   'auto_ps1_chd': True, 'auto_artwork': self.auto_cover.isChecked(),
                                   'binary': str(tools_root() / 'chdman' / 'chdman.exe')},
                                  'Importing PS1 Game Collection')

    def pick_folder(self):
        if not self.ensure_workspace(): return
        folder = QFileDialog.getExistingDirectory(self, 'Choose a folder containing your existing games', str(self.incoming))
        if not folder: return
        self.import_folder_path(Path(folder))

    def import_folder_path(self, path: Path):
        if not self.ensure_workspace(): return
        chosen = self.ask_unknown_system()
        if chosen is None: return
        self.navigate(1)
        self.set_status('Adding games from your selected folder…')
        self.start_import_process({'mode': 'folder', 'folder': str(path),
                                   'workspace': str(self.workspace), 'fallback': chosen,
                                   **self.ps1_import_options()},
                                  'Importing Games From Folder')

    def ask_unknown_system(self):
        systems = list(SYSTEM_DIR.keys())
        chosen, ok = QInputDialog.getItem(self, 'Which console are these games for?',
            'Any game files we cannot recognize automatically should be treated as:',
            systems, systems.index(self.system.currentText()), False)
        return chosen if ok else None

    def import_paths(self, paths: list[Path]):
        if not self.ensure_workspace(): return
        if not paths: return
        unsupported = [p for p in paths if p.suffix.lower() not in SUPPORTED]
        supported = [p for p in paths if p.suffix.lower() in SUPPORTED]
        if not supported:
            QMessageBox.information(self, 'No recognized games', 'Select ROMs, ZIP/7Z archives, or supported disc image formats.'); return
        ambiguous = {'.iso', '.chd', '.bin', '.img', '.zip', '.7z', '.ecm'}
        has_ambiguous = any(p.suffix.lower() in ambiguous and
                            infer_system(p, '') == '' for p in supported)
        fallback = self.system.currentText()
        if has_ambiguous:
            fallback = self.ask_unknown_system()
            if fallback is None: return
        self.navigate(1)
        self.set_status(f'Adding {len(supported):,} file(s) to your virtual card…')
        self.start_import_process({'mode': 'files', 'paths': [str(p) for p in supported],
                                   'workspace': str(self.workspace), 'fallback': fallback,
                                   **self.ps1_import_options()},
                                  'Importing Selected Games')
        if unsupported:
            self.set_status(f'{len(unsupported)} unsupported item(s) skipped; importing recognized files…')

    def import_completed(self, result):
        if result.get('cancelled'):
            self.library_notice.setText('Import stopped. Any files successfully copied are still safely on the virtual card.')
        elif result.get('empty'):
            QMessageBox.information(self, 'No recognized games found',
                'That folder does not contain supported game files or ZIP/7Z archives. You can try another folder or choose individual files.')
        elif result['errors']:
            QMessageBox.information(self, 'Import finished with some issues',
                f"Added {result['copied']} file(s), found {result['skipped']} already present.\n\n"
                + '\n'.join(result['errors'][:12]))
        else:
            self.library_notice.setText(f"✓ Added {result['copied']:,} file(s). {result['skipped']:,} already present. Your originals were not moved or deleted.")
            self.set_status('Import finished. Your new games are in My Games.')
        if result.get('converted') or result.get('playlists') or result.get('playlists_updated'):
            summary = (f"{result.get('converted', 0)} PS1 disc(s) converted to verified CHD; "
                       f"{result.get('playlists', 0)} M3U playlist(s) created, "
                       f"{result.get('playlists_updated', 0)} extended with new discs.")
            warning = ' Review the reported import issues before playing.' if result.get('errors') else ''
            self.library_notice.setText(summary + ' Original disc files were preserved.' + warning)
            self.set_status(summary)
        art = result.get('artwork') or {}
        if art and isinstance(art, dict):
            self.library_notice.setText(self.library_notice.text() +
                f" Artwork: {art.get('downloaded', 0)} downloaded, {art.get('review', 0)} for review, "
                f"{art.get('error', 0)} unavailable.")
        if result.get('artwork_attempted'):
            # The integrated import already looked for art; do not start a
            # duplicate automatic scan with another progress bar on refresh.
            self.settings.setValue('artwork_initialized_at', str(self.workspace))
            self.pending_auto_artwork = False
        elif result.get('copied', 0) and not result.get('cancelled'):
            self.pending_auto_artwork = True
        self.refresh()

    def find_downloads(self):
        if not self.ensure_workspace(): return
        """Scan Downloads only after the user clicks this button."""
        def scan_downloads():
            items, total = incoming_inventory(self.incoming, cancel=self.cancel_signal)
            if self.cancel_signal.is_set():
                return None
            return items, total
        self.set_status(f'You requested a game search in: {self.incoming}')
        self.job(scan_downloads, self.downloads_scanned, task_name='Finding Games in Downloads')

    def downloads_scanned(self, result):
        if result is None:
            self.set_status('Downloads search stopped. Nothing was imported.')
            return
        self.incoming_entries, _total_bytes = result
        self.set_status(f'Found {len(self.incoming_entries):,} recognized file(s) in Downloads. Nothing imported yet.')
        if not self.incoming_entries:
            QMessageBox.information(self, 'No games in Downloads',
                'No recognized game files were found in that folder. Nothing was changed.\n\n'
                'Use “Add Game Files” or “Add Folder” to choose wherever you keep them.')
            return
        self.show_download_choices()

    def show_download_choices(self):
        dlg = QDialog(self); dlg.setWindowTitle('Choose from your existing Downloads')
        dlg.resize(770, 510)
        lay = QVBoxLayout(dlg)
        lay.addWidget(label('These files were found in Downloads. Check what you want to add.', 'Subtitle', True))
        table = self.file_table(['Add', 'Name', 'Type', 'Size'])
        entries = self.incoming_entries[:1200]
        table.setRowCount(len(entries))
        for i, e in enumerate(entries):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            table.setItem(i, 0, item)
            for j, val in enumerate([e.path.name, e.extension.upper(), pretty_bytes(e.size)], 1):
                table.setItem(i, j, QTableWidgetItem(val))
        lay.addWidget(table)
        footer = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        footer.button(QDialogButtonBox.StandardButton.Ok).setText('Add checked games')
        footer.accepted.connect(dlg.accept); footer.rejected.connect(dlg.reject); lay.addWidget(footer)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            selected = [e.path for i,e in enumerate(entries)
                        if table.item(i,0).checkState()==Qt.CheckState.Checked]
            if selected: self.import_paths(selected)

    def offer_first_location(self):
        """First-run choice: use suggested place or choose any safe PC folder."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle('Where should your virtual microSD live?')
        dialog.setIcon(QMessageBox.Icon.Information)
        if self.previous_location_missing:
            dialog.setText('Your previous virtual-card folder could not be found.')
        else:
            dialog.setText('Choose where your RG Rotate library will be stored on your Windows PC.')
        dialog.setInformativeText(
            ('Last used location:\n' if self.previous_location_missing else 'Suggested folder:\n')
            + f'{self.workspace}\n\n'
            + ('It may be on a disconnected drive. Your files have NOT been deleted. '
               'Reconnect that drive and reopen the app, or choose another existing location.'
               if self.previous_location_missing else
               'This is where games and Android installers will be prepared. '
               'It is not the physical microSD card, and nothing is pre-allocated.'))
        choose = dialog.addButton('Choose my own location…', QMessageBox.ButtonRole.AcceptRole)
        use = (dialog.addButton('Use suggested folder', QMessageBox.ButtonRole.AcceptRole)
               if not self.previous_location_missing else None)
        dialog.exec()
        if dialog.clickedButton() == choose:
            self.choose_workspace()
        elif use is not None and dialog.clickedButton() == use:
            self.activate_workspace(self.workspace)
        # Closing the dialog changes nothing. The home button remains visible.

    def update_workspace_location(self):
        """Never block first run on a remote NAS capacity query."""
        if not hasattr(self, 'active_workspace_label'):
            return
        current = str(self.workspace)
        self.active_workspace_label.setText(current)
        self.active_workspace_label.setToolTip(current)
        self.cover_index = local_index(self.workspace)
        if hasattr(self, 'workspace_path'):
            self.workspace_path.setText(current)
        self.latest_space = None
        self.space_generation += 1    # invalidate any previous result
        self.capacity_button.setEnabled(True)
        self.capacity_button.setText('Check storage')
        if hasattr(self, 'home_workspace_tip'):
            self.home_workspace_tip.setText(f'Saving games to: {current} • Originals stay where they are.')
        if is_network_path(self.workspace):
            self.active_disk_free.setText(
                'NAS workspace selected • Capacity check optional • No 512 GB file is allocated')
            if hasattr(self, 'host_storage_hint'):
                self.host_storage_hint.setText(
                    'NAS free space not checked. Your virtual card uses only the files you import. '
                    'Click Check storage when you want to see NAS capacity.')
            # No automatic SMB capacity lookup: a sleeping NAS can stall Windows.
        else:
            self.active_disk_free.setText('Checking local drive free space in the background…')
            self.check_workspace_space()

    def check_workspace_space(self):
        """Manual remote capacity check, strictly limited in wall-clock time."""
        self.space_generation += 1
        generation = self.space_generation
        self.active_disk_free.setText('Checking storage capacity… this does not scan your games')
        self.capacity_button.setEnabled(False)
        self.capacity_button.setText('Checking…')
        work = Job(check_space_bounded, self.workspace)
        work.signals.done.connect(lambda space, g=generation: self.storage_checked(space, g))
        work.signals.failed.connect(lambda error, g=generation: self.storage_failed(error, g))
        self.space_pool.start(work)

    def storage_checked(self, space, generation: int):
        if generation != self.space_generation or space.path != str(self.workspace):
            return
        self.capacity_button.setEnabled(True)
        self.capacity_button.setText('Refresh storage')
        self.latest_space = space
        kind = 'NAS / mapped network share' if space.network else 'Windows drive'
        self.active_disk_free.setText(
            f'{describe_bytes(space.free)} free on this {kind} • '
            'Virtual card occupies only its actual files (not 512 GB)')
        if hasattr(self, 'host_storage_hint'):
            room = usable_stage_bytes(self.staged_bytes, space.free, CAPACITY, COMPANION_BUDGET, FREE_RESERVE)
            self.host_storage_hint.setText(
                f'Available to add right now: {describe_bytes(room)} • '
                f'Backing storage free: {describe_bytes(space.free)} • '
                '512 GB is a planning limit, not an allocated file')
            self.home_room.setText(f'{room / 1024**3:,.1f} GiB can be added now')

    def storage_failed(self, error: str, generation: int):
        if generation != self.space_generation:
            return
        self.latest_space = None
        self.capacity_button.setEnabled(True)
        self.capacity_button.setText('Retry storage check')
        self.active_disk_free.setText(
            'NAS capacity unavailable or slow. This check is optional; you can keep organizing games.')
        if hasattr(self, 'host_storage_hint'):
            self.host_storage_hint.setText(
                'Windows could not read the backing drive capacity. The app does not reserve 512 GB. '
                'Writes still depend on actual NAS space and may fail if it becomes full.')
        self.set_status(f'Storage capacity not verified: {error[:180]}')

    def ensure_workspace(self) -> bool:
        """Never silently stage files in an unconfirmed or disconnected folder."""
        if not self.needs_workspace_setup and (is_network_path(self.workspace) or self.workspace.is_dir()):
            # For NAS paths, I/O errors are handled in the background worker.
            return True
        QMessageBox.information(self, 'First choose your virtual-card folder',
            'Choose the PC or NAS folder where you want to prepare your RG Rotate library. '
            'The app will remember the location, and nothing is copied to the real microSD yet.')
        self.choose_workspace()
        return False

    def choose_workspace(self):
        """Choose a PC folder up front; never silently switch or discard files."""
        if self.current_task:
            if self.current_task_name == 'Checking Virtual Card':
                self.pending_workspace_picker = True
                self.cancel()
                self.set_status('Stopping the card inventory, then opening the folder chooser…')
                return
            QMessageBox.information(self, 'Finish the current operation first',
                f'Currently running: {self.current_task_name}.\n\n'
                'Please finish or stop that operation before changing the card location. '
                'This prevents partially importing files into two folders.')
            return
        proposed = QFileDialog.getExistingDirectory(
            self, 'Choose where to store your virtual microSD on your PC',
            str(self.workspace.parent if self.workspace.parent.exists() else Path.home()))
        if not proposed:
            return
        try:
            # Windows sometimes reports SD readers as removable. Do not let a
            # physical card become the PC staging workspace by accident.
            if any(v.removable and within(Path(proposed), v.root)
                   for v in list_windows_volumes()):
                raise ValueError('This is a removable drive. Choose a folder on your PC for the virtual card. The real microSD is selected later under Copy to Card.')
            path, dedicated = suggested_workspace(Path(proposed), self.workspace, self.target)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, 'Choose another PC folder', str(exc))
            return
        if path.resolve(strict=False) == self.workspace.resolve(strict=False):
            self.update_workspace_location()
            self.set_status('This folder is already your active virtual card.')
            return
        if dedicated:
            answer = QMessageBox.question(self, 'Create a dedicated virtual-card folder?',
                'To protect other files in the selected folder, Retro Library Studio will use:\n\n'
                f'{path}\n\nNo existing files will be changed. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if answer != QMessageBox.StandardButton.Yes:
                return
        # Never synchronously os.walk a NAS share on the main GUI thread.
        # Read-only subprocess checks are always stoppable, even if SMB hangs.
        if not is_network_path(self.workspace):
            try:
                if not has_workspace_payload_fast(self.workspace):
                    self.activate_workspace(path)
                    return
            except (OSError, ValueError):
                pass
        self.pending_workspace_destination = path
        self.start_readonly_scan('count', self.workspace, self.confirm_workspace_location)

    def confirm_workspace_location(self, result):
        if result is None:
            self.pending_workspace_destination = None
            self.set_status('Location change cancelled. Your current virtual card is unchanged.')
            return
        path = self.pending_workspace_destination
        if path is None:
            return
        old_count, old_bytes = result
        if old_count:
            options = QMessageBox(self)
            options.setWindowTitle('Keep your current virtual-card files?')
            options.setIcon(QMessageBox.Icon.Question)
            options.setText(f'Your current card contains {old_count:,} files ({pretty_bytes(old_bytes)}).')
            options.setInformativeText(
                f'New PC folder:\n{path}\n\n'
                'Copy all current files into the new folder (recommended), '
                'or switch to the new folder without copying. '
                'Either choice leaves the old folder and original downloads untouched.')
            migrate = options.addButton('Copy my card to the new folder', QMessageBox.ButtonRole.AcceptRole)
            fresh = options.addButton('Use new folder without copying', QMessageBox.ButtonRole.ActionRole)
            options.addButton(QMessageBox.StandardButton.Cancel)
            options.exec()
            if options.clickedButton() == migrate:
                self.pending_workspace_destination = path
                self.job(copy_existing_workspace, self.workspace_copy_finished,
                         self.workspace, path, transfer=True, cancel=self.cancel_signal,
                         task_name='Copying Virtual Card to New PC Folder')
            elif options.clickedButton() == fresh:
                self.pending_workspace_destination = None
                self.activate_workspace(path)
            else:
                self.pending_workspace_destination = None
            return
        self.pending_workspace_destination = None
        self.activate_workspace(path)

    def activate_workspace(self, path: Path):
        """Persist selection only after a safe choice or complete verified copy."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            prepare_layout(path)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, 'Cannot use this folder', str(exc))
            return
        self.workspace = path
        self.previous_location_missing = False
        self.settings.setValue('workspace', str(path))
        self.needs_workspace_setup = False
        self.card_entries = []
        self.staged_bytes = 0
        self.staged_files = 0
        self.update_workspace_location()
        self.update_pref_paths()
        self.home_used.setText('0 GB')
        self.home_room.setText('Checking selected folder…')
        self.library_count.setText('Checking selected folder…')
        self.set_status(f'Virtual card location saved: {path}')
        self.refresh()

    def workspace_copy_finished(self, result):
        target = self.pending_workspace_destination
        self.pending_workspace_destination = None
        if result.get('cancelled'):
            QMessageBox.information(self, 'Copy paused safely',
                'The original virtual card is still active and intact. '
                'You can choose the new folder again to resume the copy.')
            return
        if result.get('errors') or result.get('verified', 0) != result.get('files', -1):
            QMessageBox.warning(self, 'Could not finish copying your virtual card',
                'The old location is still active and untouched. '
                'Files already copied can be verified and reused next time.\n\n' +
                '\n'.join(result.get('errors', [])[:8]))
            return
        if target is not None:
            self.activate_workspace(target)
            QMessageBox.information(self, 'Virtual card location updated',
                f'Your virtual card is now prepared at:\n{target}\n\n'
                'Files were verified, and the old workspace was NOT deleted.')

    def choose_incoming(self):
        dest = QFileDialog.getExistingDirectory(self, 'Choose the folder you usually download games into', str(self.incoming))
        if dest:
            self.incoming = Path(dest)
            self.settings.setValue('incoming', str(self.incoming))
            self.incoming_entries = []
            self.update_pref_paths(); self.set_status('Downloads search folder changed. It will only be searched when you click Find Games in Downloads.')

    def update_pref_paths(self):
        self.workspace_path.setText(str(self.workspace))
        self.incoming_path.setText(str(self.incoming))

    def open_path(self, target: Path):
        target.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def open_workspace(self):
        if self.needs_workspace_setup:
            self.ensure_workspace(); return
        if not self.workspace.is_dir():
            QMessageBox.information(self, 'Virtual card folder unavailable',
                'The selected PC folder is missing or its drive is disconnected. '
                'Reconnect the drive or use Choose location to select another folder. '
                'Nothing has been deleted.')
            return
        self.open_path(self.workspace)

    def update_tools_status(self, update_app_labels=True):
        """Never block the Qt UI by synchronously reading NAS APK receipts."""
        if not hasattr(self, 'tool_status_label'):
            return
        if is_network_path(self.workspace):
            if self.current_task:
                self.tool_status_label.setText('An operation is running. App status can be checked afterward.')
                return
            self.start_readonly_scan('apps', self.workspace, self._apply_remote_app_status)
            return
        status = tool_status()
        packages_list = staged_apks(self.workspace)
        states = readiness(self.workspace, tools_root()) if update_app_labels else None
        self._render_app_status(status, states, packages_list)

    def _apply_remote_app_status(self, result):
        self._render_app_status(result.get('tools', {}), result.get('states', {}), result.get('apks', []))
        self.set_status('Android installer and Windows tool status checked.')

    def _render_app_status(self, status, states, packages_list):
        if states is not None:
            self.last_app_states = dict(states)
        lines = [f'{"✓ Ready" if row.get("installed") else "○ Not downloaded"}  {name}'
                 for name, row in status.items()]
        lines.append(f'{len(packages_list)} Android APK installer(s) staged')
        self.tool_status_label.setText('\n'.join(lines))
        if states is not None and hasattr(self, 'install_state_labels'):
            for name in self.install_state_labels:
                self._set_installer_state(name, states.get(name, 'Not prepared'))
        if hasattr(self, 'apk_table'):
            self.apk_table.setRowCount(len(packages_list))
            for row, item in enumerate(packages_list):
                for col, value in enumerate((item['name'], pretty_bytes(item['size']), 'Ready to transfer')):
                    self.apk_table.setItem(row, col, QTableWidgetItem(str(value)))
            self.apk_table.setVisible(bool(packages_list))
            self.apk_status.setText(
                f'{len(packages_list)} APK installer(s) ready for the RG Rotate. Android installation still required.'
                if packages_list else 'No APKs added yet. Drag your Cocoon APK above or click Add APK Files.')

    def install_recommended(self):
        if not self.ensure_workspace(): return
        """Ninite-style default button; custom selection remains available nearby."""
        # Unlike v1.1.5, the main button honors unchecked packages.
        self.prepare_essentials([name for name, cb in self.software_checks.items() if cb.isChecked()])

    def prepare_essentials(self, forced_names=None):
        if not self.ensure_workspace(): return
        names = list(forced_names) if isinstance(forced_names, list) else [
            name for name, cb in self.software_checks.items() if cb.isChecked()]
        if not names:
            QMessageBox.information(self, 'Choose apps', 'Select at least one app above.'); return
        reply = QMessageBox.question(self, 'Prepare the RG Rotate software?',
            'The installer will automatically download software from its official sources.\n\n'
            '• Android installers go into the virtual card’s SetupPackages.\n'
            '• Windows helpers go into your WindowsTools folder.\n'
            '• Previously prepared apps are skipped where verified.\n'
            '• Your own imported APKs are used when present (publisher not verified).\n'
            '• Android installation still requires the handheld and your approval.\n\n'
            'No ROMs, paid apps, firmware flashing, or drive formatting.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes)
        if reply != QMessageBox.StandardButton.Yes: return
        self.prep_status.setText(f'Preparing {len(names)} item(s). You can follow each status above…')
        self.start_import_process({'mode': 'setup', 'names': names, 'workspace': str(self.workspace),
                                   'host_tools': str(tools_root())},
                                  'Preparing Recommended Apps & Tools', self.essentials_done)

    def essentials_done(self, report):
        results = report['results']
        ready = [r for r in results if r['ok']]
        failed = [r for r in results if not r['ok']]
        stopped = report.get('cancelled', False)
        state = 'Stopped; run the installer again to resume.' if stopped else (
            f'{len(ready)} ready. {len(failed)} need attention.' if failed else
            f'All {len(ready)} selected items are prepared!')
        self.prep_status.setText(state + ' APKs still require installation on the RG Rotate.')
        self.update_tools_status(update_app_labels=False)
        self.set_status(state)
        if failed:
            QMessageBox.information(self, 'A few items need attention',
                'The rest of your setup is safe and preserved. You can retry without downloading everything again.\n\n'
                + '\n'.join(f'{r["name"]}: {r["state"][:170]}' for r in failed[:8]))
        elif not stopped:
            QMessageBox.information(self, 'Setup packages ready',
                f'{len(ready)} item(s) prepared.\n\n'
                'Android APKs are not installed yet. When the RG Rotate arrives, connect it by USB '
                'and use the Device Setup assistant, or install the APKs on Android yourself.')

    def show_official_pages(self):
        dlg = QDialog(self); dlg.setWindowTitle('Official download pages')
        lay = QVBoxLayout(dlg)
        lay.addWidget(label('If an automatic download is unavailable, open the official source directly.', 'Subtitle', True))
        for name, url in [
            ('Cocoon Shell', SOFTWARE['Cocoon Shell']['homepage']),
            ('PPSSPP', SOFTWARE['PPSSPP']['homepage']),
            ('RetroArch', SOFTWARE['RetroArch']['homepage']),
            ('Android Platform Tools (Google)', ADB_DOCS),
            ('CHDman (MAME)', CHDMAN_DOCS),
            ('DuckStation (optional)', SOFTWARE['DuckStation']['homepage'])]:
            lay.addWidget(button(f'{name}   ↗', lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u))))
        lay.addWidget(button('Close', dlg.accept))
        dlg.exec()

    def test_chdman(self):
        self.job(validate_installed_chdman, self.chd_test_done, tools_root(), task_name='Testing CHDman Executable')

    def chd_test_done(self, answer):
        ok, detail = answer
        self.chd_status.setText(('Ready: ' if ok else 'Needs attention: ') + detail)
        self.update_tools_status()

    def choose_chd_conversion(self):
        if self.current_task:
            self.set_status('Let the current task finish, or stop it first.'); return
        sources, _ = QFileDialog.getOpenFileNames(self, 'Select complete PS1 discs (CUE sheets)',
                    str(self.workspace / 'ROMs' / 'psx'), 'CUE disc images (*.cue)')
        if not sources: return
        directory = QFileDialog.getExistingDirectory(self, 'Save verified CHDs in this folder', str(Path(sources[0]).parent))
        if not directory: return
        self.disc_request = {'mode': 'convert_discs', 'paths': sources, 'output_dir': directory,
                             'binary': str(tools_root() / 'chdman' / 'chdman.exe')}
        self.start_import_process({'mode': 'inspect_discs', 'paths': sources},
                                  'Checking PS1 disc files', self.disc_inspection_done)

    def disc_inspection_done(self, report):
        lines = []
        errors = False
        for disc in report['results']:
            lines.append(f"{Path(disc['source']).name}: {len(disc['files'])} files, {len(disc['tracks'])} tracks")
            lines.extend('Needs attention: ' + e for e in disc['errors'])
            lines.extend('Warning: ' + w for w in disc['warnings'])
            errors = errors or bool(disc['errors'])
        dialog = QDialog(self); dialog.setWindowTitle('Review PlayStation discs'); dialog.resize(750, 540)
        lay = QVBoxLayout(dialog)
        lay.addWidget(label('Check every disc before converting', 'H2'))
        text = QPlainTextEdit(); text.setReadOnly(True); text.setPlainText('\n\n'.join(lines)); lay.addWidget(text)
        lay.addWidget(label('Original files are kept. Warnings do not prove corruption. Each output must pass CHDman verification.', 'Small', True))
        controls = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        if not errors:
            proceed = controls.addButton('Convert and verify', QDialogButtonBox.ButtonRole.AcceptRole)
        controls.accepted.connect(dialog.accept); controls.rejected.connect(dialog.reject); lay.addWidget(controls)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.start_import_process(self.disc_request, 'Converting and verifying PS1 discs', self.chd_conversion_done)

    def chd_conversion_done(self, report):
        results = report['results']
        good = [r for r in results if r.get('verified')]
        self.chd_status.setText(f"{len(good)}/{len(self.disc_request['paths'])} discs verified. Original CUE/BIN files kept.")
        dialog = QDialog(self); dialog.setWindowTitle('PlayStation conversion results'); dialog.resize(840, 550)
        lay = QVBoxLayout(dialog); lay.addWidget(label(self.chd_status.text(), 'H2', True))
        text = QPlainTextEdit(); text.setReadOnly(True)
        text.setPlainText('\n\n'.join(
            f"Source: {r['source']}\nOutput: {r.get('output', 'None')}\n"
            f"Size: {pretty_bytes(r.get('bytes', 0))}\nCHDman verification: {'Passed' if r.get('verified') else 'Not passed'}\n"
            + r.get('error', '') + '\n'.join(r.get('warnings', [])) for r in results))
        lay.addWidget(text)
        if len(good) > 1:
            lay.addWidget(label('For discs of the SAME game: select order in the next dialog before saving an M3U.', 'Small', True))
            lay.addWidget(button('Create multi-disc playlist…', lambda: self.choose_disc_playlist(good)))
        controls = QDialogButtonBox(QDialogButtonBox.StandardButton.Close); controls.rejected.connect(dialog.reject)
        lay.addWidget(controls); dialog.exec()

    def choose_disc_playlist(self, results):
        dialog = QDialog(self); dialog.setWindowTitle('Playlist disc order'); dialog.resize(650, 400)
        lay = QVBoxLayout(dialog); lay.addWidget(label('Drag discs into Disc 1, Disc 2 order. Use only discs of one game.', '', True))
        discs = QListWidget(); discs.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        for result in results: discs.addItem(result['output'])
        lay.addWidget(discs)
        controls = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        controls.accepted.connect(dialog.accept); controls.rejected.connect(dialog.reject); lay.addWidget(controls)
        if dialog.exec() != QDialog.DialogCode.Accepted: return
        destination, _ = QFileDialog.getSaveFileName(self, 'Save game playlist',
            str(Path(results[0]['output']).parent / 'Game.m3u'), 'M3U playlist (*.m3u)')
        if not destination: return
        self.start_import_process({'mode': 'playlist', 'paths': [discs.item(i).text() for i in range(discs.count())],
                                   'destination': destination}, 'Saving disc playlist',
                                  lambda r: QMessageBox.information(self, 'Playlist saved', r['playlist']))

    def choose_cover(self):
        entries = unique_game_art_entries(self.card_entries)
        if not entries:
            QMessageBox.information(self, 'Add a game first', 'Import a game in My Games first.')
            return
        options = [f'{g.system}  •  {g.label}' for g in entries]
        selected, ok = QInputDialog.getItem(self, 'Choose a game', 'Add a cover to:', options, 0, False)
        if ok: self.choose_cover_for(entries[options.index(selected)])

    def fetch_covers(self):
        self.start_cover_scan(automatic=False)

    def start_cover_scan(self, automatic: bool = False):
        if not self.ensure_workspace() or self.current_task: return
        entries = unique_game_art_entries(self.card_entries)
        if not entries: return
        # Prioritize new/unchecked games so large libraries don't rescan the first 80 forever.
        index = local_index(self.workspace)
        entries.sort(key=lambda g: (game_key(g.system, g.label) in index,
                                   cached_preview(self.workspace, g.system, g.label).exists()))
        if not automatic:
            reply = QMessageBox.question(self, 'Look for missing artwork?',
                'Find covers in the Libretro thumbnail library?\n\n'
                'Confident matches are saved automatically; uncertain editions and variants '
                'will be left for your review. This may access the internet and your NAS.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if reply != QMessageBox.StandardButton.Yes: return
        request = {'mode':'batch', 'workspace':str(self.workspace),
                   'games':[{'system':g.system,'label':g.label} for g in entries[:80]]}
        self.start_artwork_process(request, 'Finding Game Covers')

    def start_artwork_process(self, request: dict, task_name: str):
        # Isolate NAS reads, writes and HTTP lookups in a cancellable child.
        if self.current_task:
            self.set_status(f'Already running: {self.current_task_name}')
            return
        self.current_task = True
        self.current_task_name = task_name
        self.cancel_requested = False
        self.artwork_stopped = False
        self.artwork_error = ''
        self.artwork_output = ''
        self.artwork_result = None
        self.artwork_mode = request['mode']
        self.cancel_btn.setEnabled(True)
        for b in self.task_buttons: b.setEnabled(False)
        self.bar.setRange(0,0)
        self.task_title.setText(f'Working on: {task_name}')
        proc = QProcess(self); self.artwork_process = proc
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        proc.readyReadStandardOutput.connect(self._artwork_output_ready)
        proc.readyReadStandardError.connect(self._artwork_error_ready)
        proc.finished.connect(self._artwork_finished)
        proc.errorOccurred.connect(self._artwork_start_error)
        payload = (json.dumps(request, ensure_ascii=True) + '\n').encode('ascii')
        proc.started.connect(lambda p=proc, data=payload: p.write(data))
        if getattr(sys, 'frozen', False):
            helper = Path(sys.executable).with_name('RetroLibraryArtwork.exe')
            if not helper.is_file():
                self.artwork_error = 'Missing RetroLibraryArtwork.exe. Keep all helper EXEs together.'
                QTimer.singleShot(0, lambda: self._artwork_finished(-1, QProcess.ExitStatus.CrashExit))
                return
            proc.start(str(helper), [])
        else:
            proc.start(sys.executable, ['-u', str(Path(__file__).with_name('artwork_worker.py'))])

    def _artwork_output_ready(self):
        proc = self.artwork_process
        if proc is None: return
        self.artwork_output += bytes(proc.readAllStandardOutput()).decode('utf-8', errors='replace')
        while '\n' in self.artwork_output:
            line, self.artwork_output = self.artwork_output.split('\n', 1)
            try: msg = json.loads(line)
            except ValueError: continue
            if msg.get('type') == 'progress' and not self.artwork_stopped:
                self.on_progress(msg.get('message','Finding artwork'),
                                 int(msg.get('current',0)), int(msg.get('total',0)))
            elif msg.get('type') == 'result': self.artwork_result = msg.get('data')
            elif msg.get('type') == 'error': self.artwork_error = str(msg.get('message','Unknown error'))

    def _artwork_error_ready(self):
        if self.artwork_process:
            self.artwork_error += bytes(self.artwork_process.readAllStandardError()).decode('utf-8', errors='replace')[-1000:]

    def _artwork_start_error(self, _error):
        proc = self.artwork_process
        if proc is not None and proc.error() == QProcess.ProcessError.FailedToStart:
            self.artwork_error = 'The cover-art helper could not start. Check the source folder.'
            QTimer.singleShot(0, lambda p=proc: self._artwork_finished(-1, QProcess.ExitStatus.CrashExit)
                              if self.artwork_process is p else None)

    def _artwork_finished(self, code, status):
        proc = self.artwork_process
        if proc is None: return
        self._artwork_output_ready()
        self._artwork_error_ready()
        proc.deleteLater()
        self.artwork_process = None
        was_stopped = self.artwork_stopped or self.cancel_requested
        result = self.artwork_result
        self._unlock()
        if self.close_when_idle:
            self.close_when_idle = False
            QTimer.singleShot(0, self.close)
            return
        if was_stopped:
            self.set_status('Artwork lookup stopped. Your game files were not changed.')
            if self.artwork_mode in ('search', 'preview') and self.manual_cover_dialog is not None:
                self.manual_cover_status.setText('Search or preview stopped. You can try again.')
                self.manual_cover_preview.setText('Press Search to try again.')
            return
        if code != 0 or not isinstance(result,dict) or status != QProcess.ExitStatus.NormalExit:
            self.set_status('Artwork lookup could not finish.')
            if self.artwork_mode in ('search', 'preview') and self.manual_cover_dialog is not None:
                self.manual_cover_status.setText('Artwork lookup failed. Retry the search or use an image from your PC.')
                self.manual_cover_preview.setText('The online preview or search could not be loaded.')
            QMessageBox.warning(self,'Artwork needs attention',self.artwork_error or 'Artwork helper stopped unexpectedly.')
            return
        self.cover_index = local_index(self.workspace)
        if self.gallery_mode == 'Gallery': self.fill_card()
        mode = self.artwork_mode
        if mode == 'search':
            if self.manual_cover_dialog is None: return
            results = result.get('results', [])
            self.manual_cover_results.clear()
            for found in results:
                item = QListWidgetItem(found['title'])
                item.setData(Qt.ItemDataRole.UserRole, found['title'])
                self.manual_cover_results.addItem(item)
            if results:
                self.manual_cover_results.setCurrentRow(0)
                self.manual_cover_status.setText(
                    f'{len(results)} possible covers for “{result.get("query", "")}”. '
                    'Choose one, preview it, then apply when you are sure.')
                # SelectionChanged schedules a preview via the isolated artwork worker.
                self.manual_cover_preview.setText('Loading first matching cover…')
            else:
                self.manual_cover_status.setText(
                    'No matches found.' if result.get('catalog_size', 0) else
                    'The artwork catalog could not be reached from this PC. Try Search again, or choose an image from your PC. No game files were changed.')
                self.manual_cover_preview.setText('Try a shorter search, such as “Resident Evil”.')
            return
        if mode == 'preview':
            if self.manual_cover_dialog is None: return
            if result.get('source_title') != self.selected_manual_cover_title():
                self.manual_cover_selection_changed()
                return
            self.manual_preview_button.setEnabled(True)
            self.manual_apply_button.setEnabled(True)
            image = QPixmap(str(result.get('preview_path', '')))
            if image.isNull():
                self.manual_cover_preview.setText('Preview could not be displayed.')
            else:
                self.manual_cover_preview.setText('')
                self.manual_cover_preview.set_cover(image)
                self.manual_cover_status.setText(f'Previewing “{result.get("source_title", "")}”. '
                    'Use selected cover when it is the correct game.')
            return
        if mode == 'suggest':
            suggestions = result.get('suggestions', [])
            if not suggestions:
                QMessageBox.information(self,'No confident artwork matches',
                   'No matches were returned. The online catalog might be unavailable, or this edition may not have cover art. You can select your own PNG, JPG or WEBP image instead.')
                return
            options = [f'{row["title"]}  ({round(100*row["score"])}% similarity)' for row in suggestions]
            picked, ok = QInputDialog.getItem(self,'Review cover match',
                f'Choose the correct edition for {result["label"]}.\nNo cover is assigned automatically here:',
                options,0,False)
            if ok:
                source = suggestions[options.index(picked)]['title']
                if QMessageBox.question(self, 'Use this cover?',
                    f'Assign the online artwork for {source} to {result["label"]}?\n'
                    'If a cover already exists, it will be replaced. Your ROM files stay untouched.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes: return
                self.start_artwork_process({'mode':'pick','workspace':str(self.workspace),
                    'system':result['system'],'label':result['label'],
                    'source_title':source,'replace':True}, 'Downloading Chosen Cover')
            return
        if mode == 'batch':
            stats = result.get('stats',{})
            text = (f'{stats.get("downloaded",0)} new covers  •  '
                    f'{stats.get("already present",0)} already present  •  '
                    f'{stats.get("review",0)} need review  •  '
                    f'{stats.get("error",0)} errors')
        else:
            text = f'Cover updated: {result.get("label", "game")} ({result.get("status", "done")})'
        self.cover_info.setText(text)
        if hasattr(self,'art_status'): self.art_status.setText(text)
        self.set_status(text)

    def _stop_artwork_process(self):
        proc = self.artwork_process
        if proc is None: return
        self.artwork_stopped = True
        self.cancel_btn.setEnabled(False)
        self.task_title.setText('Stopping artwork task…')
        self.set_status('Stopping cover-art download or NAS write safely…')
        if proc.state() != QProcess.ProcessState.NotRunning:
            proc.write(b'STOP\n')
            QTimer.singleShot(350, lambda p=proc: p.terminate()
                  if self.artwork_process is p and p.state() != QProcess.ProcessState.NotRunning else None)
            QTimer.singleShot(1200, lambda p=proc: p.kill()
                  if self.artwork_process is p and p.state() != QProcess.ProcessState.NotRunning else None)

    def start_transfer_process(self, mode: str, simulation: bool, on_plan=None):
        """Do not run a potentially stalled NAS/SD copy or preview in a GUI thread."""
        if self.current_task:
            self.set_status(f'Already working on: {self.current_task_name}')
            return
        if not self.target:
            return
        self.current_task = True
        self.current_task_name = 'Previewing microSD Transfer' if mode == 'preview' else 'Copying and Verifying microSD'
        self.cancel_requested = False
        self.transfer_stopped = False
        self.transfer_output = ''
        self.transfer_error = ''
        self.transfer_result = None
        self.transfer_mode = mode
        self.transfer_simulation = simulation
        self.transfer_on_plan = on_plan
        self.cancel_btn.setText('Stop task')
        self.cancel_btn.setEnabled(True)
        for b in self.task_buttons: b.setEnabled(False)
        self.bar.setRange(0, 0)
        self.task_title.setText('Working on: ' + self.current_task_name)
        proc = QProcess(self); self.transfer_process = proc
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        proc.readyReadStandardOutput.connect(self._transfer_output_ready)
        proc.readyReadStandardError.connect(self._transfer_error_ready)
        proc.finished.connect(self._transfer_process_finished)
        proc.errorOccurred.connect(self._transfer_start_error)
        request = {'mode':mode, 'workspace':str(self.workspace), 'target':str(self.target),
                   'simulation':bool(simulation)}
        payload = (json.dumps(request, ensure_ascii=True, separators=(',', ':')) + '\n').encode('ascii')
        proc.started.connect(lambda p=proc, data=payload: p.write(data))
        if getattr(sys, 'frozen', False):
            exe = Path(sys.executable).with_name('RetroLibraryTransfer.exe')
            if not exe.is_file():
                self.transfer_error = 'RetroLibraryTransfer.exe is missing. Keep all five EXEs together.'
                QTimer.singleShot(0, lambda: self._transfer_process_finished(-1, QProcess.ExitStatus.CrashExit))
                return
            proc.start(str(exe), [])
        else:
            proc.start(sys.executable, ['-u', str(Path(__file__).with_name('transfer_worker.py'))])

    def _transfer_output_ready(self):
        proc = self.transfer_process
        if proc is None: return
        self.transfer_output += bytes(proc.readAllStandardOutput()).decode('ascii', errors='replace')
        while '\n' in self.transfer_output:
            line, self.transfer_output = self.transfer_output.split('\n', 1)
            try: data = json.loads(line)
            except ValueError:
                self.transfer_error = 'Transfer helper returned an unreadable response.'
                continue
            typ = data.get('type')
            if typ == 'progress' and not self.transfer_stopped:
                self.on_copy_progress(data.get('stage','Transferring'), int(data.get('copied',0)),
                    int(data.get('total',0)), str(data.get('filename','')),
                    float(data.get('speed',0)), float(data.get('eta',0)))
            elif typ == 'result':
                self.transfer_result = data.get('data')
            elif typ == 'error':
                self.transfer_error = str(data.get('message', 'Transfer helper failed'))

    def _transfer_error_ready(self):
        if self.transfer_process is not None:
            self.transfer_error += bytes(self.transfer_process.readAllStandardError()).decode('utf8', errors='replace')[-1600:]

    def _transfer_start_error(self, _error):
        proc = self.transfer_process
        if proc is not None and proc.error() == QProcess.ProcessError.FailedToStart:
            self.transfer_error = 'Could not start RetroLibraryTransfer helper.'
            QTimer.singleShot(0, lambda p=proc: self._transfer_process_finished(-1, QProcess.ExitStatus.CrashExit)
                              if self.transfer_process is p else None)

    def _transfer_process_finished(self, code, status):
        proc = self.transfer_process
        if proc is None: return
        self._transfer_output_ready(); self._transfer_error_ready()
        proc.deleteLater(); self.transfer_process = None
        result = self.transfer_result
        cancelled = self.transfer_stopped or self.cancel_requested
        if cancelled:
            self._unlock()
            self.cancel_btn.setText('Stop task')
            self.copy_meter.setValue(0)
            self.copy_detail.setText('Transfer stopped. Completed verified files stay intact. '
                'Any .retro-part file is incomplete and will be checked before resume.')
            self.set_status('Copy helper stopped. Source files remain untouched.')
            if self.close_when_idle:
                self.close_when_idle = False
                QTimer.singleShot(0, self.close)
            return
        if code != 0 or status != QProcess.ExitStatus.NormalExit or not isinstance(result, dict):
            self.cancel_btn.setText('Stop task')
            self.job_failed(self.transfer_error or f'Transfer helper failed ({code})')
            return
        callback = self.transfer_on_plan
        mode = self.transfer_mode
        self._unlock()
        self.cancel_btn.setText('Stop task')
        if self.close_when_idle:
            self.close_when_idle = False
            QTimer.singleShot(0, self.close)
            return
        if mode == 'preview':
            try: plan = SyncPlan(**result['plan'])
            except (KeyError, TypeError) as exc:
                self.job_failed(f'Invalid transfer preview: {exc}')
                return
            if callback: callback(plan)
        else:
            self.transfer_done(result.get('copy', {}))

    def _stop_transfer_process(self):
        proc = self.transfer_process
        if proc is None: return
        if self.transfer_stopped:
            reply = QMessageBox.warning(self, 'Force-stop a stalled copy?',
                'The NAS or microSD may be stuck in a file operation. Killing the copy helper '
                'can leave an incomplete .retro-part file on the destination.\n\n'
                'The next attempt will verify the partial before resuming. The original files '
                'are not deleted. Use this only if the copy does not respond to normal Stop.\n\n'
                'Force stop the copy helper?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes and proc.state() != QProcess.ProcessState.NotRunning:
                self.cancel_btn.setEnabled(False)
                proc.kill()
            return
        self.transfer_stopped = True
        self.cancel_requested = True
        self.task_title.setText('Stopping verified transfer…')
        self.set_status('Stop requested; waiting for current safe copy/verification step. Browse remains responsive.')
        proc.write(b'STOP\n')
        self.cancel_btn.setEnabled(False)
        QTimer.singleShot(6000, lambda p=proc: self._offer_transfer_force_stop(p))

    def _offer_transfer_force_stop(self, proc):
        if self.transfer_process is proc and proc.state() != QProcess.ProcessState.NotRunning:
            self.cancel_btn.setText('Force stop stalled copy…')
            self.cancel_btn.setEnabled(True)
            self.set_status('Still waiting on Windows/NAS I/O. Use Force stop to end only the copy helper.')

    def _remember_destination(self, target: Path, mode: str):
        """Save BOTH the destination and its kind; never silently treat a folder as a card."""
        self.target = target
        self.settings.setValue('target', str(target))
        self.settings.setValue('target_mode', mode)
        self.saved_destination_mode = mode
        self.simulation.blockSignals(True)
        self.simulation.setChecked(mode == 'practice')
        self.simulation.blockSignals(False)
        self.update_destination_hint()
        self.reset_physical_plan('Destination selected. Run Preview to measure its formatted capacity.')
        self.preflight_text.setText('Destination selected. Preview again before copying or verifying.')
        self._reset_copy_display('Destination or destination type changed. Previous results no longer apply.')

    def on_destination_mode_changed(self, practice: bool):
        if not self.target:
            self.simulation.blockSignals(True)
            self.simulation.setChecked(False)
            self.simulation.blockSignals(False)
            return
        if practice and is_volume_root(self.target):
            QMessageBox.warning(self, 'Physical-drive safety',
                'A drive root cannot be treated as a disposable practice folder. '
                'Choose a normal Windows folder with “Choose drive or folder…”, or use '
                '“Try a safe practice copy first”.')
            self.simulation.blockSignals(True)
            self.simulation.setChecked(False)
            self.simulation.blockSignals(False)
            return
        self.settings.setValue('target_mode', 'practice' if practice else 'unconfirmed')
        self.saved_destination_mode = 'practice' if practice else 'unconfirmed'
        self.update_destination_hint()
        self.reset_physical_plan('Destination type changed. Run Preview again.')
        self.preflight_text.setText('Destination mode changed. Run a new preview before copying.')
        self._reset_copy_display('Destination mode changed. Previous progress does not apply.')

    def _selected_transfer_mode(self):
        """Return True for an explicitly identified practice folder, False for a card."""
        if not self.target:
            return None
        if is_volume_root(self.target):
            if self.simulation.isChecked():
                QMessageBox.warning(self, 'Practice destination required',
                    'Practice Mode cannot use a drive root. Select a disposable test folder.')
                return None
            return False
        if self.simulation.isChecked():
            return True
        reply = QMessageBox.question(self, 'Confirm practice folder',
            f'{self.target} is a folder, not a microSD drive root.\n\n'
            'Use it as a disposable PRACTICE destination? This does not format or delete files.\n\n'
            'To copy to a real microSD, first choose its drive root instead.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return None
        self._remember_destination(self.target, 'practice')
        return True

    def choose_destination(self):
        path = QFileDialog.getExistingDirectory(self,
            'Choose a microSD drive ROOT or a disposable practice folder', str(self.target or Path.home()))
        if not path: return
        target = Path(path)
        if within(target, self.workspace) or within(self.workspace, target):
            QMessageBox.warning(self, 'Separate locations required',
                                'The destination cannot overlap your virtual card.'); return
        if is_volume_root(target):
            self._remember_destination(target, 'physical')
        else:
            self._remember_destination(target, 'practice')

    def prepare_practice(self):
        directory = self.default_practice_folder
        if within(directory, self.workspace) or within(self.workspace, directory):
            QMessageBox.warning(self, 'Choose a different workspace',
                                'The practice copy cannot overlap your virtual card.'); return
        directory.mkdir(parents=True, exist_ok=True)
        self._remember_destination(directory, 'practice')
        self.preflight_text.setText('Practice folder ready. Click “Check what would be copied” to preview.')

    def detect_card(self):
        candidates = [v for v in list_windows_volumes() if v.removable]
        if not candidates:
            QMessageBox.information(self, 'No removable microSD found',
                'Insert your microSD into a card reader first.\n\n'
                'Some readers appear as fixed disks in Windows. If yours does, you can choose it manually; '
                'the app will ask for extra confirmation before a real transfer.'); return
        choices = [f'{v.root}   {v.label or "Untitled"}   {v.filesystem}   {pretty_bytes(v.free)} free' for v in candidates]
        selected, ok = QInputDialog.getItem(self, 'Which card is yours?',
                                           'Detected removable drives:', choices, 0, False)
        if ok and selected:
            self._remember_destination(candidates[choices.index(selected)].root, 'physical')

    def update_destination_hint(self):
        if not hasattr(self, 'dest_name'): return
        # Display selected paths instantly. Capacity and availability are checked
        # in the isolated preview worker, never via synchronous SMB calls here.
        if self.target:
            mode = ('PRACTICE MODE' if self.simulation.isChecked() else
                    'REAL CARD MODE' if is_volume_root(self.target) else 'MODE NEEDS CONFIRMATION')
            self.dest_name.setText(f'Selected: {self.target} • {mode}. Preview checks space and availability.')
        else:
            self.dest_name.setText('No destination selected. Insert your card or select a practice folder.')

    def _reset_copy_display(self, message: str):
        """A new preview MUST NOT inherit the previous run's 100% result."""
        self.copy_meter.setRange(0, 1000)
        self.copy_meter.setValue(0)
        self.copy_detail.setText(message)
        self.transfer_btn.setText('⇄  Copy and Verify Files')

    def start_preflight(self):
        if not self.ensure_workspace(): return
        if not self.target:
            QMessageBox.information(self, 'Choose a destination first',
                'Insert a microSD and select it above, or select a disposable folder and enable Practice mode.'); return
        simulation = self._selected_transfer_mode()
        if simulation is None: return
        if not simulation:
            try: validate_physical_root(self.target)
            except ValueError as exc:
                QMessageBox.warning(self, 'Destination not safe', str(exc)); return
        self._reset_copy_display('Checking what exists on the destination. No copying or SHA-256 verification yet.')
        self.preflight_text.setText('Checking staged files and available storage…')
        self.start_transfer_process('preview', simulation, self.preflight_done)

    def preflight_done(self, plan):
        details, action, status = preview_explanation(plan, pretty_bytes)
        self.preflight_text.setText(details)
        self.show_physical_preview(plan)
        self._reset_copy_display('PREVIEW ONLY: No files transferred or SHA-256 verified by this preview.')
        self.transfer_btn.setText(action)
        self.set_status(status)
        if not plan.conflicts and plan.files:
            # Move the user to the next step instead of leaving it below the fold.
            QTimer.singleShot(0, lambda: self.copy_scroll.ensureWidgetVisible(self.transfer_btn, 0, 65))

    def start_transfer(self):
        if not self.ensure_workspace(): return
        if not self.target:
            QMessageBox.information(self, 'Choose your microSD first', 'Select a destination above before copying.'); return
        sim = self._selected_transfer_mode()
        if sim is None: return
        if not sim:
            try:
                volume = validate_physical_root(self.target)
            except ValueError as exc:
                QMessageBox.warning(self, 'Destination not safe', str(exc)); return
            if not volume.removable:
                answer = QMessageBox.warning(self, 'Windows says this is a fixed drive',
                    f'Windows reports {volume.root} as a FIXED disk, not removable.\n\n'
                    'Only continue if you are absolutely sure this is your microSD card.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if answer != QMessageBox.StandardButton.Yes: return
        self._reset_copy_display('Reviewing destination again. No files have been transferred in this run.')
        self.start_transfer_process('preview', sim, lambda plan: self.confirm_transfer(plan, sim))

    def confirm_transfer(self, plan, sim: bool):
        if plan.conflicts:
            QMessageBox.warning(self, 'Copy cannot start yet', '\n'.join(plan.conflicts[:10])); return
        if not plan.files:
            QMessageBox.information(self, 'Virtual card is still empty',
                                    'Add some games or prepare Android software first.'); return
        if not sim and plan.current_target_free - plan.bytes_new < FREE_RESERVE:
            QMessageBox.warning(self, 'Not enough free space',
                                'This transfer would leave less than the protected 8 GiB free-space buffer.'); return
        # Reject a stale selected root if the card vanished between detection and confirmation.
        if not sim:
            try:
                volume = validate_physical_root(self.target)
            except ValueError as exc:
                QMessageBox.warning(self, 'Card not available', str(exc)); return
            if plan.target_capacity != volume.total:
                QMessageBox.warning(self, 'Selected drive changed',
                    'The destination capacity changed during preview. Reinsert the intended card and preview again.'); return
        # Never reuse a stale preflight after the user changes the target.
        response = QMessageBox.question(self, 'Confirm verification' if plan.bytes_new == 0 else 'Confirm the destination',
            f'{"PRACTICE COPY" if sim else "REAL microSD COPY"}\n\n'
            f'Destination: {self.target}\nStaged: {plan.files:,} files / {pretty_bytes(plan.bytes_total)}\n'
            f'Estimated new copy: {pretty_bytes(plan.bytes_new)}\n'
            f'Already present (name and size): {plan.existing_files:,} file(s)\n'
            'Existing files have NOT been hash-verified by this preview.\n\n'
            'Different existing files will NOT be overwritten. Nothing will be deleted or formatted.\n\n'
            + ('Verify the existing files with SHA-256?' if plan.bytes_new == 0 else 'Start copying and verifying?'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if response != QMessageBox.StandardButton.Yes: return
        self.copy_meter.setValue(0)
        self.copy_detail.setText('Starting verified copy…')
        self.start_transfer_process('copy', sim)

    def transfer_done(self, result):
        summary, title, message, success = copy_explanation(result, self.transfer_simulation)
        self.copy_detail.setText(summary)
        if self.last_physical_plan is not None:
            self.card_measured.setText('Transfer complete. Preview again to measure the card after copying.')
            self.card_measured_details.setText('The prior bar was an estimate before transfer; actual new contents must be rechecked.')
            self.last_physical_plan = None
            self.real_card_bar.setVisible(False)
        self.last_transfer_note.setText(('Last completed run: ' if success else 'Last transfer attempt: ') + summary.replace('\n', '  '))
        if success:
            self.copy_meter.setValue(1000)
            if int(result.get('copied', 0)) == 0:
                self.transfer_btn.setText('✓  Verify These Files Again')
            else:
                self.transfer_btn.setText('⇄  Copy and Verify Again')
            self.set_status('COMPLETE: ' + summary)
            QMessageBox.information(self, title, message)
        else:
            self.copy_meter.setValue(0)
            self.set_status('Transfer stopped or needs attention. ' + summary)
            QMessageBox.warning(self, title, message)

    def health_check(self):
        self.health_result.setPlainText('Checking files and disc references…')
        self.job(inspect_library, self.health_done, self.workspace,
                 progress=True, cancel=self.cancel_signal, task_name='Checking Game Library')

    def health_done(self, report):
        directory = self.workspace/'.retro-library'; directory.mkdir(parents=True,exist_ok=True)
        (directory/'health_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        rows = [f"Files checked: {report['inspected_game_files']:,}",
                f"Duplicate groups: {len(report['possible_duplicates']):,}",
                f"Broken CUE/M3U references: {len(report['broken_playlists_or_cues']):,}",
                'Nothing was deleted.']
        for group in report['possible_duplicates'][:15]:
            rows.extend(['', 'Possible duplicates:', *[str(v) for v in group[:10]]])
        for missing in report['broken_playlists_or_cues'][:25]:
            rows.extend(['', 'Missing or broken: ' + str(missing)])
        if report.get('cancelled'): rows.insert(0, 'Scan cancelled; report is partial.')
        self.health_result.setPlainText('\n'.join(rows))
        self.set_status('Library check completed.')

    def detect_android(self):
        self.job(connected_devices, self.android_detect_done, task_name='Finding RG Rotate over USB')

    def android_detect_done(self, items):
        self.adb_devices = [serial for serial, state in items if state == 'device']
        QMessageBox.information(self, 'Android USB connection',
            '\n'.join(f'{serial} : {state}' for serial,state in items)
            if items else 'No Android device connected. USB debugging and on-device authorization may be required.')

    def install_apks(self):
        packages = sorted((self.workspace/'SetupPackages').glob('*.apk'))
        if not packages:
            QMessageBox.information(self, 'No Android installers prepared',
                'Open Apps & APKs, then choose Add APK Files or download official Android apps first.'); return
        devices = getattr(self, 'adb_devices', [])
        if len(devices) != 1:
            QMessageBox.information(self, 'Connect your RG Rotate',
                'Select Detect Android over USB and authorize exactly one device.\n\n'
                'This should be done only after the RG Rotate arrives.'); return
        serial = devices[0]
        selected = [p.name for p in packages]
        reply = QMessageBox.question(self, 'Confirm installation on Android',
            f'Device: {serial}\n\nInstall these {len(selected)} APK files to Android internal storage?\n'
            + '\n'.join(selected[:12]) + '\n\nExisting installed apps will not be silently replaced.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes: return
        self.job(install_local_apks, self.install_done, self.workspace, serial, selected,
                 progress=True, cancel=self.cancel_signal, task_name='Installing Android APKs over USB')

    def install_done(self, results):
        QMessageBox.information(self, 'Android installation report',
            '\n'.join(f"{'✓' if r['ok'] else '!'} {r['name']}: {r['detail']}" for r in results)
            if results else 'No installations attempted.')

    def add_bios_file(self):
        if not self.ensure_workspace(): return
        paths, _ = QFileDialog.getOpenFileNames(self, 'Choose your own PS1 BIOS file(s)', str(Path.home()),
                                                'BIOS files (*.bin *.rom *.bios);;All files (*.*)')
        if not paths: return
        from core import copy_atomic
        import_errors = []
        imported = 0
        for path in paths:
            source = Path(path)
            if source.stat().st_size > 64 * 1024**2:
                import_errors.append(f'{source.name}: unusually large for a BIOS file')
                continue
            try:
                status = copy_atomic(source, self.workspace/'BIOS'/source.name)
                imported += status == 'copied'
            except Exception as exc:
                import_errors.append(f'{source.name}: {exc}')
        self.set_status(f'{imported} BIOS file(s) copied. You still need to select compatible BIOS settings on your emulator.')
        if import_errors:
            QMessageBox.information(self, 'BIOS import needs attention', '\n'.join(import_errors[:12]))
        self.refresh()

    def save_readiness(self):
        if not self.ensure_workspace(): return
        folder=self.workspace/'.retro-library'; folder.mkdir(parents=True,exist_ok=True)
        companion=sum(f.stat().st_size for f in safe_walk(self.workspace/'CompanionData'))
        report = {'generated_utc':datetime.now(timezone.utc).isoformat(),
                  'version':VERSION, 'default_frontend':'Cocoon Shell',
                  'workspace':str(self.workspace), 'capacity_bytes':CAPACITY,
                  'companion_budget_bytes':COMPANION_BUDGET,
                  'free_space_reserve_bytes':FREE_RESERVE,
                  'companion_used_bytes':companion,
                  'virtual_used_bytes':self.staged_bytes,
                  'staged_game_file_count':len(self.card_entries),
                  'host_utilities':tool_status(),
                  'device_tested':False}
        (folder/'readiness.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        package=self.workspace/'SetupPackages'; package.mkdir(exist_ok=True)
        (package/'README_FIRST_BOOT.txt').write_text(self.guide_text.text(),encoding='utf-8')
        QMessageBox.information(self, 'Setup checklist saved',
            'Readiness report saved in .retro-library/readiness.json.\n'
            'First-boot guide staged in SetupPackages/README_FIRST_BOOT.txt.')
        self.set_status('Saved first-boot guide and readiness report.')


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--retro-readonly-scan':
        from readonly_scan import scan
        raise SystemExit(scan(sys.argv[2], Path(sys.argv[3])))
    if len(sys.argv) == 3 and sys.argv[1] == '--retro-probe-storage':
        from storage_probe import probe_storage_cli
        raise SystemExit(probe_storage_cli(sys.argv[2]))
    main()
