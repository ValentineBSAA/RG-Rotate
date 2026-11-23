"""Readable, themed, accessible read-only information panels.

Replaces dense native text blocks only where the user requested it. Dialogs
never modify games, cards, NAS folders or settings.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget)


def _label(value: str, size: int = 13, color: str = '#ebf4ff', bold: bool = False):
    item = QLabel(str(value))
    item.setWordWrap(True)
    item.setStyleSheet(f'color:{color};font-size:{size}px;font-weight:{750 if bold else 450};')
    item.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return item


class DetailsDialog(QDialog):
    """One prominent conclusion, grouped facts, optional raw bytes/paths.

    sections = [(heading, [(label, value), ...]), ...].
    items = list of optional named files (not explanatory paragraphs).
    """
    def __init__(self, parent, *, title: str, subtitle: str, sections=(),
                 items=(), note: str = '', technical: str = '',
                 accent: str = '#7cb8ff'):
        super().__init__(parent)
        self.setObjectName('ReadableDetails')
        self.setWindowTitle(title)
        self.setMinimumSize(540, 350)
        self.resize(690, 565)
        self.setStyleSheet("""
            QDialog#ReadableDetails {background:#0e192c; color:#eef7ff;}
            QScrollArea {border:0; background:transparent;}
            QFrame#DetailSection {background:#172941; border:1px solid #395578;
                                  border-radius:13px;}
            QPushButton {background:#233e5b; color:#f1f8ff; border:1px solid #40688b;
                         padding:11px 16px; border-radius:9px; font-weight:650;}
            QPushButton:hover {background:#315579;}
            QPlainTextEdit {background:#0c1728; color:#d5e9ff;
                            border:1px solid #355276; border-radius:9px; padding:10px;}
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 18)
        root.setSpacing(13)
        heading = _label(title, 23, '#f8fbff', True)
        root.addWidget(heading)
        sub = _label(subtitle, 14, accent, True)
        root.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 5, 2)
        layout.setSpacing(11)

        for section_title, rows in sections:
            frame = QFrame(); frame.setObjectName('DetailSection')
            area = QVBoxLayout(frame)
            area.setContentsMargins(16, 12, 16, 13)
            area.setSpacing(8)
            area.addWidget(_label(section_title, 15, '#9fc9ff', True))
            for key, value in rows:
                line = QHBoxLayout()
                line.setSpacing(18)
                first = _label(key, 12, '#aebfda', True)
                first.setMinimumWidth(118)
                first.setMaximumWidth(200)
                second = _label(str(value), 14, '#f5faff')
                line.addWidget(first, 1)
                line.addWidget(second, 3)
                area.addLayout(line)
            layout.addWidget(frame)

        if items:
            frame = QFrame(); frame.setObjectName('DetailSection')
            box = QVBoxLayout(frame); box.setContentsMargins(16, 12, 16, 13)
            box.setSpacing(9)
            box.addWidget(_label('Files in this collection', 15, '#b9a0ff', True))
            for i, item in enumerate(items, 1):
                box.addWidget(_label(f'{i}.  {item}', 13))
            layout.addWidget(frame)
        if note:
            layout.addWidget(_label(note, 12, '#abc1dd'))
        layout.addStretch(1)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        self.technical = str(technical)
        if technical:
            self.expand = QPushButton('Show exact bytes and technical details')
            self.expand.setCheckable(True)
            root.addWidget(self.expand)
            self.raw = QPlainTextEdit()
            self.raw.setPlainText(technical)
            self.raw.setReadOnly(True)
            self.raw.setMinimumHeight(130)
            self.raw.setMaximumHeight(185)
            self.raw.setVisible(False)
            root.addWidget(self.raw)
            self.expand.toggled.connect(self._expanded)

        actions = QHBoxLayout()
        if technical:
            copy = QPushButton('Copy details')
            copy.clicked.connect(lambda: QApplication.clipboard().setText(self.technical))
            actions.addWidget(copy)
        actions.addStretch(1)
        done = QPushButton('Done')
        done.setObjectName('Primary')
        done.clicked.connect(self.accept)
        done.setDefault(True)
        actions.addWidget(done)
        root.addLayout(actions)

    def _expanded(self, opened: bool):
        self.raw.setVisible(opened)
        self.expand.setText('Hide technical details' if opened else
                            'Show exact bytes and technical details')
