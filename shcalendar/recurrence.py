"""
Expands a (possibly repeating) event into concrete occurrence dates
that fall within a given Jalali month.
"""
from __future__ import annotations
from typing import List
from . import jalali
from .jalali import JalaliDate
from .models import Event


def occurrences_in_month(event: Event, year: int, month: int) -> List[JalaliDate]:
    start = JalaliDate(event.year, event.month, event.day)
    month_start = JalaliDate(year, month, 1)
    month_len = jalali.month_length(year, month)
    month_end = JalaliDate(year, month, month_len)

    if start > month_end:
        return []  # event hasn't started yet by this month

    rule = event.repeat

    if rule == "none":
        return [start] if (year, month) == (event.year, event.month) else []

    if rule == "daily":
        first = start if start > month_start else month_start
        out = []
        d = first
        while d <= month_end:
            out.append(d)
            d = d.add_days(1)
        return out

    if rule == "weekly":
        target_wd = start.weekday()
        out = []
        d = month_start
        while d <= month_end:
            if d.weekday() == target_wd and d >= start:
                out.append(d)
            d = d.add_days(1)
        return out

    if rule == "monthly":
        if (year, month) < (event.year, event.month):
            return []
        day = min(event.day, jalali.month_length(year, month))
        occ = JalaliDate(year, month, day)
        return [occ] if occ >= start else []

    if rule == "yearly":
        if month != event.month:
            return []
        if year < event.year:
            return []
        day = event.day
        if month == 12 and day == 30 and not jalali.is_leap(year):
            day = 29  # Esfand 30 -> 29 in common years
        occ = JalaliDate(year, month, day)
        return [occ] if occ >= start else []

    return []


def events_by_day_for_month(events: list[Event], year: int, month: int) -> dict[int, list[Event]]:
    """Returns {day_of_month: [events...]} for quick lookup while painting the grid."""
    result: dict[int, list[Event]] = {}
    for ev in events:
        for occ in occurrences_in_month(ev, year, month):
            result.setdefault(occ.day, []).append(ev)
    return result
