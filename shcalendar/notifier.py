from __future__ import annotations
import datetime as _dt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from . import jalali
from .database import Database


class ReminderService:
    """Polls the database once a minute for due reminders and shows tray notifications."""

    def __init__(self, db: Database, tray: QSystemTrayIcon, poll_seconds: int = 30):
        self.db = db
        self.tray = tray
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_due_reminders)
        self.timer.start(poll_seconds * 1000)

    def check_due_reminders(self):
        from . import recurrence  # local import avoids a cycle at module load time

        y, m, d, hh, mm = jalali.now_ymd_hm()
        now_minutes = hh * 60 + mm

        events = self.db.events_touching_month(y, m)
        for ev in events:
            if ev.reminder_minutes is None:
                continue
            for occ in recurrence.occurrences_in_month(ev, y, m):
                if occ.day != d:
                    continue
                occurrence_key = str(occ)
                if self.db.was_notified(ev.id, occurrence_key):
                    continue

                if ev.all_day:
                    due_minutes = 0  # all-day reminders fire at start of day
                else:
                    eh, em = map(int, ev.start_time.split(":"))
                    due_minutes = eh * 60 + em - ev.reminder_minutes

                if now_minutes >= due_minutes:
                    self._notify(ev)
                    self.db.mark_notified(ev.id, occurrence_key)

    def _notify(self, ev):
        when = "today" if ev.all_day else f"at {ev.start_time}"
        self.tray.showMessage(
            ev.title,
            f"{when}" + (f"\n{ev.description}" if ev.description else ""),
            QSystemTrayIcon.Information,
            8000,
        )


def build_tray_icon(app: QApplication, icon: QIcon, on_show, on_quit) -> QSystemTrayIcon:
    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip("Solar Hijri Calendar")
    menu = QMenu()
    show_action = menu.addAction("Show Calendar")
    show_action.triggered.connect(on_show)
    menu.addSeparator()
    quit_action = menu.addAction("Quit")
    quit_action.triggered.connect(on_quit)
    tray.setContextMenu(menu)
    tray.activated.connect(lambda reason: on_show() if reason == QSystemTrayIcon.Trigger else None)
    tray.show()
    return tray
