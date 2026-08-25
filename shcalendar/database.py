from __future__ import annotations
import os
import sqlite3
from typing import List, Optional
from .models import Event

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    all_day INTEGER NOT NULL DEFAULT 1,
    start_time TEXT,
    reminder_minutes INTEGER,
    repeat TEXT NOT NULL DEFAULT 'none',
    color TEXT NOT NULL DEFAULT '#0f6f5c'
);

CREATE TABLE IF NOT EXISTS notified (
    event_id INTEGER NOT NULL,
    occurrence TEXT NOT NULL,
    PRIMARY KEY (event_id, occurrence)
);
"""


def default_db_path() -> str:
    data_home = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    d = os.path.join(data_home, "solar-hijri-calendar")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "events.db")


class Database:
    def __init__(self, path: Optional[str] = None):
        self.path = path or default_db_path()
        first_run = not os.path.exists(self.path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()
        if first_run:
            self._seed_defaults()

    def _seed_defaults(self):
        seeds = [
            Event(None, "Nowruz", "Persian New Year", 1405, 1, 1, True, None, 0, "yearly", "#0f6f5c"),
            Event(None, "Sizdah Bedar", "Nature Day", 1405, 1, 13, True, None, 0, "yearly", "#0f6f5c"),
            Event(None, "Shab-e Yalda", "Winter solstice eve", 1405, 9, 30, True, None, 0, "yearly", "#0f6f5c"),
        ]
        for ev in seeds:
            self.add_event(ev)

    # -- CRUD --
    def add_event(self, ev: Event) -> int:
        cur = self.conn.execute(
            "INSERT INTO events (title, description, year, month, day, all_day, "
            "start_time, reminder_minutes, repeat, color) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (ev.title, ev.description, ev.year, ev.month, ev.day, int(ev.all_day),
             ev.start_time, ev.reminder_minutes, ev.repeat, ev.color),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_event(self, ev: Event) -> None:
        self.conn.execute(
            "UPDATE events SET title=?, description=?, year=?, month=?, day=?, all_day=?, "
            "start_time=?, reminder_minutes=?, repeat=?, color=? WHERE id=?",
            (ev.title, ev.description, ev.year, ev.month, ev.day, int(ev.all_day),
             ev.start_time, ev.reminder_minutes, ev.repeat, ev.color, ev.id),
        )
        self.conn.commit()

    def delete_event(self, event_id: int) -> None:
        self.conn.execute("DELETE FROM events WHERE id=?", (event_id,))
        self.conn.execute("DELETE FROM notified WHERE event_id=?", (event_id,))
        self.conn.commit()

    def all_events(self) -> List[Event]:
        rows = self.conn.execute("SELECT * FROM events ORDER BY year, month, day").fetchall()
        return [self._row_to_event(r) for r in rows]

    def events_touching_month(self, year: int, month: int) -> List[Event]:
        """All events that *could* produce an occurrence in this month:
        non-repeating events in this exact month, plus any repeating event
        that started on or before the end of this month."""
        rows = self.conn.execute(
            "SELECT * FROM events WHERE "
            "(repeat='none' AND year=? AND month=?) OR "
            "(repeat!='none' AND (year < ? OR (year = ? AND month <= ?)))",
            (year, month, year, year, month),
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    @staticmethod
    def _row_to_event(r: sqlite3.Row) -> Event:
        return Event(
            id=r["id"], title=r["title"], description=r["description"],
            year=r["year"], month=r["month"], day=r["day"],
            all_day=bool(r["all_day"]), start_time=r["start_time"],
            reminder_minutes=r["reminder_minutes"], repeat=r["repeat"], color=r["color"],
        )

    # -- reminder tracking --
    def was_notified(self, event_id: int, occurrence: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM notified WHERE event_id=? AND occurrence=?", (event_id, occurrence)
        ).fetchone()
        return row is not None

    def mark_notified(self, event_id: int, occurrence: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO notified (event_id, occurrence) VALUES (?,?)",
            (event_id, occurrence),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
