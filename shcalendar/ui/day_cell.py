from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from PySide6.QtWidgets import QFrame, QSizePolicy


class DayCell(QFrame):
    clicked = Signal(int)          # day
    activated = Signal(int)        # double-click -> new event on this day

    def __init__(self, day: int | None, greg_label: str = "", parent=None):
        super().__init__(parent)
        self.day = day
        self.greg_label = greg_label
        self.is_today = False
        self.is_weekend = False
        self.is_selected = False
        self.events = []  # list[Event]
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(70, 56)
        self.setCursor(Qt.PointingHandCursor if day else Qt.ArrowCursor)

    def set_state(self, is_today=False, is_weekend=False, is_selected=False, events=None):
        self.is_today = is_today
        self.is_weekend = is_weekend
        self.is_selected = is_selected
        self.events = events or []
        self.update()

    def mousePressEvent(self, event):
        if self.day:
            self.clicked.emit(self.day)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.day:
            self.activated.emit(self.day)
        super().mouseDoubleClickEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)

        if not self.day:
            p.fillRect(rect, QColor(0, 0, 0, 0))
            p.end()
            return

        # background
        if self.is_today:
            bg = QColor("#0f6f5c")
        elif self.is_selected:
            bg = QColor("#cfe6e1")
        elif self.is_weekend:
            bg = QColor("#fbeee9")
        else:
            bg = self.palette().base().color()
        p.fillRect(rect, bg)

        if self.is_selected and not self.is_today:
            pen = QPen(QColor("#0f6f5c"))
            pen.setWidth(2)
            p.setPen(pen)
            p.drawRect(rect.adjusted(1, 1, -1, -1))

        text_color = QColor("#ffffff") if self.is_today else QColor("#1f2937")
        muted = QColor("#e8f3f0") if self.is_today else QColor("#8a8f98")

        p.setPen(text_color)
        f = QFont()
        f.setPointSize(13)
        f.setBold(True)
        p.setFont(f)
        p.drawText(rect.adjusted(8, 4, -6, 0), Qt.AlignLeft | Qt.AlignTop, str(self.day))

        p.setPen(muted)
        f2 = QFont()
        f2.setPointSize(8)
        p.setFont(f2)
        p.drawText(rect.adjusted(0, 6, -6, 0), Qt.AlignRight | Qt.AlignTop, self.greg_label)

        # event dots / bars (up to 3 titles, then "+N more")
        max_lines = 3
        line_h = 13
        y = rect.top() + 26
        shown = self.events[:max_lines]
        for ev in shown:
            dot_color = QColor(ev.color)
            p.setBrush(QBrush(dot_color))
            p.setPen(Qt.NoPen)
            p.drawEllipse(rect.left() + 8, y + 4, 6, 6)
            p.setPen(text_color if self.is_today else QColor("#374151"))
            f3 = QFont()
            f3.setPointSize(7.5)
            p.setFont(f3)
            label = ev.title if len(ev.title) <= 14 else ev.title[:13] + "\u2026"
            p.drawText(rect.left() + 18, y, rect.width() - 22, line_h,
                       Qt.AlignLeft | Qt.AlignVCenter, label)
            y += line_h
        extra = len(self.events) - len(shown)
        if extra > 0:
            p.setPen(muted)
            f4 = QFont()
            f4.setPointSize(7.2)
            p.setFont(f4)
            p.drawText(rect.left() + 8, y, rect.width() - 12, line_h,
                       Qt.AlignLeft | Qt.AlignVCenter, f"+{extra} more")

        p.end()
