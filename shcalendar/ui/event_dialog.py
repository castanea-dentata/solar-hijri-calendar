from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QTextEdit, QCheckBox, QTimeEdit,
    QComboBox, QDialogButtonBox, QVBoxLayout, QLabel
)

from .. import jalali
from ..models import Event, REMINDER_CHOICES, REPEAT_CHOICES

REPEAT_LABELS = {
    "none": "Does not repeat",
    "daily": "Daily",
    "weekly": "Weekly",
    "monthly": "Monthly (same day of month)",
    "yearly": "Yearly (same date)",
}


class EventDialog(QDialog):
    def __init__(self, year: int, month: int, day: int, event: Optional[Event] = None, parent=None):
        super().__init__(parent)
        self.year, self.month, self.day = year, month, day
        self.source_event = event
        self.setWindowTitle("Edit Event" if event else "New Event")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        date_lbl = QLabel(jalali.format_with_weekday(year, month, day))
        date_lbl.setStyleSheet("color:#0f6f5c; font-weight:600; font-size:11pt;")
        layout.addWidget(date_lbl)

        form = QFormLayout()
        form.setSpacing(8)

        self.title_edit = QLineEdit(event.title if event else "")
        self.title_edit.setPlaceholderText("Event title")
        form.addRow("Title", self.title_edit)

        self.desc_edit = QTextEdit(event.description if event else "")
        self.desc_edit.setFixedHeight(70)
        form.addRow("Notes", self.desc_edit)

        self.all_day_check = QCheckBox("All day")
        self.all_day_check.setChecked(event.all_day if event else True)
        form.addRow("", self.all_day_check)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        if event and event.start_time:
            h, m = map(int, event.start_time.split(":"))
            self.time_edit.setTime(QTime(h, m))
        else:
            self.time_edit.setTime(QTime(9, 0))
        self.time_edit.setEnabled(not self.all_day_check.isChecked())
        self.all_day_check.toggled.connect(lambda on: self.time_edit.setEnabled(not on))
        form.addRow("Time", self.time_edit)

        self.repeat_combo = QComboBox()
        for r in REPEAT_CHOICES:
            self.repeat_combo.addItem(REPEAT_LABELS[r], r)
        if event:
            self.repeat_combo.setCurrentIndex(REPEAT_CHOICES.index(event.repeat))
        form.addRow("Repeat", self.repeat_combo)

        self.reminder_combo = QComboBox()
        for label, _ in REMINDER_CHOICES:
            self.reminder_combo.addItem(label)
        if event:
            for i, (_, val) in enumerate(REMINDER_CHOICES):
                if val == event.reminder_minutes:
                    self.reminder_combo.setCurrentIndex(i)
                    break
        else:
            self.reminder_combo.setCurrentIndex(3)  # default: 15 minutes before
        form.addRow("Reminder", self.reminder_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._result_event: Optional[Event] = None

    def _on_accept(self):
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.setFocus()
            return
        all_day = self.all_day_check.isChecked()
        start_time = None if all_day else self.time_edit.time().toString("HH:mm")
        reminder_minutes = REMINDER_CHOICES[self.reminder_combo.currentIndex()][1]
        repeat = self.repeat_combo.currentData()

        self._result_event = Event(
            id=self.source_event.id if self.source_event else None,
            title=title,
            description=self.desc_edit.toPlainText().strip(),
            year=self.year, month=self.month, day=self.day,
            all_day=all_day,
            start_time=start_time,
            reminder_minutes=reminder_minutes,
            repeat=repeat,
            color=self.source_event.color if self.source_event else "#0f6f5c",
        )
        self.accept()

    def result_event(self) -> Optional[Event]:
        return self._result_event
