from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QFrame
from PySide6.QtCore import Qt

from .. import jalali
from .. import recurrence
from .day_cell import DayCell


class MonthGrid(QWidget):
    day_clicked = Signal(int, int, int)      # y, m, d
    day_activated = Signal(int, int, int)    # y, m, d (double-click -> new event)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.year, self.month, self.day = jalali.today()
        self.selected_day = self.day
        self._cells: dict[int, DayCell] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        header = QFrame()
        header_layout = QGridLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)
        for i, name in enumerate(jalali.DAYS_ABBR):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            weight = "700" if i == jalali.WEEKEND_INDEX else "600"
            color = "#0f6f5c" if i == jalali.WEEKEND_INDEX else "#6b7280"
            lbl.setStyleSheet(f"font-weight:{weight}; color:{color}; padding:4px;")
            header_layout.addWidget(lbl, 0, i)
        outer.addWidget(header)

        self.grid = QGridLayout()
        self.grid.setSpacing(2)
        for c in range(7):
            self.grid.setColumnStretch(c, 1)
        outer.addLayout(self.grid, 1)
        # Note: caller is expected to invoke set_month() once wired up
        # (e.g. after set_events_provider), so the grid isn't populated twice.

    def set_month(self, year: int, month: int, keep_selection=False):
        self.year, self.month = year, month

        # clear old cells (detach immediately so nothing stale is left on screen;
        # deleteLater alone only schedules destruction for the next event loop turn)
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self._cells.clear()

        first_wd = jalali.weekday_of_first(year, month)
        length = jalali.month_length(year, month)
        n_rows = -(-(first_wd + length) // 7)
        for r in range(n_rows):
            self.grid.setRowStretch(r, 1)

        today_y, today_m, today_d = jalali.today()

        db_events = getattr(self, "_events_provider", None)
        events = db_events(year, month) if db_events else []
        by_day = recurrence.events_by_day_for_month(events, year, month)

        day = 1
        for r in range(n_rows):
            for wd in range(7):
                idx = r * 7 + wd
                if idx < first_wd or day > length:
                    cell = DayCell(None)
                else:
                    g = jalali.to_gregorian(year, month, day)
                    cell = DayCell(day, g.strftime("%b %-d"))
                    is_today = (year, month, day) == (today_y, today_m, today_d)
                    is_selected = keep_selection and day == self.selected_day
                    cell.set_state(
                        is_today=is_today,
                        is_weekend=(wd == jalali.WEEKEND_INDEX),
                        is_selected=is_selected,
                        events=by_day.get(day, []),
                    )
                    cell.clicked.connect(self._on_clicked)
                    cell.activated.connect(self._on_activated)
                    self._cells[day] = cell
                    day += 1
                self.grid.addWidget(cell, r, wd)

    def set_events_provider(self, fn):
        """fn(year, month) -> list[Event]"""
        self._events_provider = fn

    def refresh(self):
        self.set_month(self.year, self.month, keep_selection=True)

    def select_day(self, day: int):
        self.selected_day = day
        for d, cell in self._cells.items():
            cell.set_state(
                is_today=cell.is_today,
                is_weekend=cell.is_weekend,
                is_selected=(d == day),
                events=cell.events,
            )

    def _on_clicked(self, day: int):
        self.select_day(day)
        self.day_clicked.emit(self.year, self.month, day)

    def _on_activated(self, day: int):
        self.select_day(day)
        self.day_activated.emit(self.year, self.month, day)
