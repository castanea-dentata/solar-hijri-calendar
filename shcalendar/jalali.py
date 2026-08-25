"""
Solar Hijri (Jalali) calendar utilities.

Weekday convention throughout this app: 0=Saturday ... 6=Friday,
matching jdatetime's native .weekday() numbering.
"""
from __future__ import annotations
import datetime as _dt
from dataclasses import dataclass
import jdatetime

MONTHS_FA = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
             'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
MONTHS_EN = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar',
             'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand']

DAYS_FA = ['شنبه', 'یک‌شنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
DAYS_EN = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
DAYS_ABBR = ['Sh', 'Ye', 'Do', 'Se', 'Ch', 'Pa', 'Jo']

WEEKEND_INDEX = 6  # Friday


def is_leap(year: int) -> bool:
    return jdatetime.date(year, 1, 1).isleap()


def month_length(year: int, month: int) -> int:
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    return 30 if is_leap(year) else 29


def weekday_of_first(year: int, month: int) -> int:
    """0=Saturday .. 6=Friday for the 1st of the given Jalali month."""
    return jdatetime.date(year, month, 1).weekday()


def today() -> tuple[int, int, int]:
    d = jdatetime.date.fromgregorian(date=_dt.date.today())
    return d.year, d.month, d.day


def now_ymd_hm() -> tuple[int, int, int, int, int]:
    g = _dt.datetime.now()
    jd = jdatetime.date.fromgregorian(date=g.date())
    return jd.year, jd.month, jd.day, g.hour, g.minute


def to_gregorian(year: int, month: int, day: int) -> _dt.date:
    return jdatetime.date(year, month, day).togregorian()


def from_gregorian(date: _dt.date) -> tuple[int, int, int]:
    d = jdatetime.date.fromgregorian(date=date)
    return d.year, d.month, d.day


def add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    idx = (year * 12 + (month - 1)) + delta
    return idx // 12, idx % 12 + 1


def format_long(year: int, month: int, day: int) -> str:
    return f"{day} {MONTHS_EN[month - 1]} {year}"


def format_with_weekday(year: int, month: int, day: int) -> str:
    wd = jdatetime.date(year, month, day).weekday()
    return f"{DAYS_EN[wd]}, {day} {MONTHS_EN[month - 1]} {year}"


@dataclass(frozen=True)
class JalaliDate:
    year: int
    month: int
    day: int

    def weekday(self) -> int:
        return jdatetime.date(self.year, self.month, self.day).weekday()

    def togregorian(self) -> _dt.date:
        return to_gregorian(self.year, self.month, self.day)

    def add_days(self, n: int) -> "JalaliDate":
        d = jdatetime.date(self.year, self.month, self.day) + jdatetime.timedelta(days=n)
        return JalaliDate(d.year, d.month, d.day)

    def __le__(self, other: "JalaliDate") -> bool:
        return (self.year, self.month, self.day) <= (other.year, other.month, other.day)

    def __lt__(self, other: "JalaliDate") -> bool:
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
