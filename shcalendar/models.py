from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

REPEAT_CHOICES = ["none", "daily", "weekly", "monthly", "yearly"]

REMINDER_CHOICES = [
    ("None", None),
    ("At start time", 0),
    ("5 minutes before", 5),
    ("15 minutes before", 15),
    ("30 minutes before", 30),
    ("1 hour before", 60),
    ("1 day before", 1440),
]


@dataclass
class Event:
    id: Optional[int]
    title: str
    description: str
    year: int
    month: int
    day: int
    all_day: bool
    start_time: Optional[str]   # "HH:MM", None if all_day
    reminder_minutes: Optional[int]
    repeat: str = "none"
    color: str = "#0f6f5c"

    def time_label(self) -> str:
        if self.all_day:
            return "All day"
        return self.start_time or ""
