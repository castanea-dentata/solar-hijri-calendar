from __future__ import annotations
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QToolBar, QMessageBox, QSystemTrayIcon, QSizePolicy
)

from .. import jalali
from ..database import Database
from ..models import Event
from .month_grid import MonthGrid
from .agenda_panel import AgendaPanel
from .event_dialog import EventDialog
from ..notifier import ReminderService, build_tray_icon

RESOURCES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources")


class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("Solar Hijri Calendar")
        self.resize(980, 640)

        icon_path = os.path.join(RESOURCES, "icon.svg")
        self.app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self.setWindowIcon(self.app_icon)

        self._build_toolbar()
        self._build_central_widget()
        self._build_menu()

        self.tray = build_tray_icon(
            self.windowHandle().screen().parent() if False else self._app(),
            self.app_icon, self.show_and_raise, self.quit_app,
        )
        self.reminders = ReminderService(self.db, self.tray)

        self.refresh_month()
        self.month_grid.select_day(self.month_grid.day)
        self._show_agenda_for_selected()

    # -- setup helpers --
    def _app(self):
        from PySide6.QtWidgets import QApplication
        return QApplication.instance()

    def _build_toolbar(self):
        tb = QToolBar()
        tb.setMovable(False)
        self.addToolBar(tb)

        prev_btn = QPushButton("\u25c0")
        prev_btn.setFixedWidth(34)
        prev_btn.clicked.connect(self.go_prev_month)
        tb.addWidget(prev_btn)

        self.month_label = QLabel()
        self.month_label.setStyleSheet("font-size:14pt; font-weight:700; padding:0 10px;")
        tb.addWidget(self.month_label)

        next_btn = QPushButton("\u25b6")
        next_btn.setFixedWidth(34)
        next_btn.clicked.connect(self.go_next_month)
        tb.addWidget(next_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tb.addWidget(spacer)

        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.go_today)
        tb.addWidget(today_btn)

    def _build_central_widget(self):
        splitter = QSplitter()

        self.month_grid = MonthGrid()
        self.month_grid.set_events_provider(self.db.events_touching_month)
        self.month_grid.set_month(self.month_grid.year, self.month_grid.month)
        self.month_grid.day_clicked.connect(self.on_day_clicked)
        self.month_grid.day_activated.connect(self.on_day_activated)
        splitter.addWidget(self.month_grid)

        self.agenda = AgendaPanel()
        self.agenda.new_event_requested.connect(self.new_event_for_selected_day)
        self.agenda.edit_event_requested.connect(self.edit_event)
        self.agenda.delete_event_requested.connect(self.delete_event)
        splitter.addWidget(self.agenda)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

    def _build_menu(self):
        m_file = self.menuBar().addMenu("&File")
        new_act = QAction("New Event\u2026", self)
        new_act.setShortcut(QKeySequence("Ctrl+N"))
        new_act.triggered.connect(self.new_event_for_selected_day)
        m_file.addAction(new_act)
        m_file.addSeparator()
        quit_act = QAction("Quit", self)
        quit_act.setShortcut(QKeySequence("Ctrl+Q"))
        quit_act.triggered.connect(self.quit_app)
        m_file.addAction(quit_act)

        m_view = self.menuBar().addMenu("&View")
        today_act = QAction("Go to Today", self)
        today_act.setShortcut(QKeySequence("Ctrl+T"))
        today_act.triggered.connect(self.go_today)
        m_view.addAction(today_act)

        m_help = self.menuBar().addMenu("&Help")
        about_act = QAction("About", self)
        about_act.triggered.connect(self.show_about)
        m_help.addAction(about_act)

    # -- navigation --
    def refresh_month(self):
        self.month_grid.refresh()
        self.month_label.setText(
            f"{jalali.MONTHS_EN[self.month_grid.month - 1]} {self.month_grid.year}"
        )

    def go_prev_month(self):
        y, m = jalali.add_months(self.month_grid.year, self.month_grid.month, -1)
        self.month_grid.set_month(y, m)
        self.refresh_month()

    def go_next_month(self):
        y, m = jalali.add_months(self.month_grid.year, self.month_grid.month, 1)
        self.month_grid.set_month(y, m)
        self.refresh_month()

    def go_today(self):
        y, m, d = jalali.today()
        self.month_grid.set_month(y, m)
        self.month_grid.selected_day = d
        self.refresh_month()
        self.month_grid.select_day(d)
        self._show_agenda_for_selected()

    # -- day / event interactions --
    def on_day_clicked(self, y, m, d):
        self._show_agenda_for_selected()

    def on_day_activated(self, y, m, d):
        self.new_event_for_selected_day()

    def _show_agenda_for_selected(self):
        y, m = self.month_grid.year, self.month_grid.month
        d = self.month_grid.selected_day
        events = self.db.events_touching_month(y, m)
        from .. import recurrence
        by_day = recurrence.events_by_day_for_month(events, y, m)
        self.agenda.show_day(y, m, d, by_day.get(d, []))

    def new_event_for_selected_day(self):
        y, m = self.month_grid.year, self.month_grid.month
        d = self.month_grid.selected_day
        dlg = EventDialog(y, m, d, parent=self)
        if dlg.exec():
            ev = dlg.result_event()
            self.db.add_event(ev)
            self.refresh_month()
            self.month_grid.select_day(d)
            self._show_agenda_for_selected()

    def edit_event(self, ev: Event):
        dlg = EventDialog(ev.year, ev.month, ev.day, event=ev, parent=self)
        if dlg.exec():
            updated = dlg.result_event()
            self.db.update_event(updated)
            self.refresh_month()
            self.month_grid.select_day(self.month_grid.selected_day)
            self._show_agenda_for_selected()

    def delete_event(self, ev: Event):
        resp = QMessageBox.question(
            self, "Delete Event", f"Delete \u201c{ev.title}\u201d?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.db.delete_event(ev.id)
            self.refresh_month()
            self.month_grid.select_day(self.month_grid.selected_day)
            self._show_agenda_for_selected()

    def show_about(self):
        QMessageBox.about(
            self, "About Solar Hijri Calendar",
            "<b>Solar Hijri Calendar</b><br>"
            "A native Qt PIM calendar built on the Jalali (Solar Hijri) calendar system.<br><br>"
            "Week runs Saturday \u2192 Friday. Events, reminders, and recurrence "
            "are stored locally in a SQLite database.",
        )

    # -- lifecycle --
    def show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def quit_app(self):
        self._app().quit()

    def closeEvent(self, event):
        if QSystemTrayIcon.isSystemTrayAvailable():
            event.ignore()
            self.hide()
            self.tray.showMessage(
                "Solar Hijri Calendar",
                "Still running in the tray \u2014 reminders stay active.",
                QSystemTrayIcon.Information, 4000,
            )
        else:
            event.accept()
