from __future__ import annotations
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QFrame, QSizePolicy
)

from .. import jalali


class AgendaPanel(QWidget):
    new_event_requested = Signal()
    edit_event_requested = Signal(object)   # Event
    delete_event_requested = Signal(object)  # Event

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setMaximumWidth(380)
        self._events = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.date_label = QLabel("")
        self.date_label.setStyleSheet("font-size:13pt; font-weight:700; color:#1f2937;")
        self.date_label.setWordWrap(True)
        layout.addWidget(self.date_label)

        self.greg_label = QLabel("")
        self.greg_label.setStyleSheet("color:#8a8f98; font-size:9pt;")
        layout.addWidget(self.greg_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#e2e5e9;")
        layout.addWidget(line)

        self.list = QListWidget()
        self.list.setAlternatingRowColors(False)
        self.list.setWordWrap(True)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.list, 1)

        self.new_btn = QPushButton("New Event")
        self.new_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.new_btn.clicked.connect(self.new_event_requested.emit)
        layout.addWidget(self.new_btn)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._emit_edit)
        self.del_btn = QPushButton("Delete")
        self.del_btn.clicked.connect(self._emit_delete)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.del_btn)
        layout.addLayout(btn_row)

        self.new_btn.setStyleSheet(
            "QPushButton { background:#0f6f5c; color:white; border-radius:4px; padding:7px 10px; font-weight:600; }"
            "QPushButton:hover { background:#0c5c4c; }"
        )

    def show_day(self, year: int, month: int, day: int, events: list):
        self.date_label.setText(jalali.format_with_weekday(year, month, day))
        g = jalali.to_gregorian(year, month, day)
        self.greg_label.setText(f"Gregorian: {g.strftime('%B %-d, %Y')}")
        self._events = events
        self.list.clear()
        if not events:
            item = QListWidgetItem("No events \u2014 double-click \u201cNew Event\u201d to add one")
            item.setFlags(Qt.NoItemFlags)
            self.list.addItem(item)
            return
        for ev in sorted(events, key=lambda e: e.start_time or "00:00"):
            item = QListWidgetItem(f"{ev.time_label():>8}   {ev.title}")
            item.setData(Qt.UserRole, ev)
            self.list.addItem(item)

    def _current_event(self):
        item = self.list.currentItem()
        if not item:
            return None
        return item.data(Qt.UserRole)

    def _on_double_click(self, item):
        ev = item.data(Qt.UserRole)
        if ev:
            self.edit_event_requested.emit(ev)

    def _emit_edit(self):
        ev = self._current_event()
        if ev:
            self.edit_event_requested.emit(ev)

    def _emit_delete(self):
        ev = self._current_event()
        if ev:
            self.delete_event_requested.emit(ev)
