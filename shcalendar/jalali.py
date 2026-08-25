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
MONTHS_EN = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

DAYS_FA = ['شنبه', 'یک‌شنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
DAYS_EN = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
DAYS_ABBR = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

WEEKEND_INDEX = {0, 6}  # Saturday amd Sunday

def is_leap(year: int) -> bool:
    return jdatetime.date(year, 1, 1).isleap()


def month_length(year: int, month: int) -> int:
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    return 30 if is_leap(year) else 29


def weekday_of_first(year: int, month: int) -> int:
    native = jdatetime.date(year, month, 1).weekday()  # 0=Sat..6=Fri
    return (native - 1) % 7  # 0=Sun..6=Sat


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

HOLOCENE_OFFSET = 10621

def format_long(year: int, month: int, day: int) -> str:
    return f"{day} {MONTHS_EN[month - 1]} {year + HOLOCENE_OFFSET}"

def format_with_weekday(year: int, month: int, day: int) -> str:
    native_wd = jdatetime.date(year, month, day).weekday()  # 0=Sat..6=Fri, jdatetime's fixed convention
    wd = (native_wd - 1) % 7  # 0=Sun..6=Sat, matches your reordered DAYS_EN
    return f"{DAYS_EN[wd]}, {day} {MONTHS_EN[month - 1]} {year + HOLOCENE_OFFSET}"

@dataclass(frozen=True)
class JalaliDate:
    year: int
    month: int
    day: int

    def weekday(self) -> int:
        native = jdatetime.date(year, month, 1).weekday()  # 0=Sat..6=Fri
        return (native - 1) % 7  # 0=Sun..6=Sat

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
