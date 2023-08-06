# rdate: Alternative to standard datetime library.
# Copyright: (c) 2018, t5w5h5@gmail.com. All rights reserved.
# License: MIT, see LICENSE for details.

import calendar as _calendar
import datetime as _datetime
import enum as _enum
import re as _re


__all__ = ['Period', 'Weekday', 'set_first_day_of_week', 'Time', 'Date', 'DateTime', 'timestamp']


class Period(_enum.Enum):
    """Enumeration of time periods."""

    Day = 'd'
    Week = 'w'
    Month = 'm'
    Year = 'y'

    def __lt__(self, other):
        """Return True if *other* is shorter than self."""
        order = {'d': 0, 'w': 1, 'm': 2, 'y': 3}
        return isinstance(other, Period) and order[self.value] < order[other.value]


class Weekday(_enum.Enum):
    """Enumeration of week days."""

    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

    def __add__(self, n):
        """Return Weekday *n* days after self."""
        return Weekday(self.value+(n % 7))

    def __sub__(self, n):
        """Return Weekday *n* days before self.
        Return difference in days between two week days if *n* is a Weekday.
        """
        if isinstance(n, Weekday):
            return self.value - n.value
        else:
            return Weekday(self.value+((7-n) % 7))

    def __lt__(self, other):
        """Return True if *other* is before self."""
        return isinstance(other, Weekday) and Weekday._order[self] < Weekday._order[other]

    @classmethod
    def first_day_of_week(cls):
        """Return Weekday with which the week begins."""
        return cls.range()[0]

    @classmethod
    def last_day_of_week(cls):
        """Return Weekday with which the week ends."""
        return cls.range()[-1]

    @classmethod
    def range(cls):
        """Return [Weekday] for one week."""
        return list(cls._order.keys())


def set_first_day_of_week(weekday):
    """Set the Weekday wich which the week begins (defaults to Monday.)"""
    Weekday._order = {Weekday(n % 7): p for p, n in enumerate(range(weekday.value, weekday.value+7))}

set_first_day_of_week(Weekday.Monday)


class Time:
    """Time representation with second precision."""

    @classmethod
    def now(cls):
        """Return Time object that represents 'now'."""
        now = _datetime.datetime.now()
        return cls(now.hour, now.minute, now.second)

    @classmethod
    def start_of_day(cls):
        """Return Time object that represents the start of the day (mid-night.)"""
        return cls(0)

    @classmethod
    def end_of_day(cls):
        """Return Time object that represents the end of the day (one second to mid-night.)"""
        return cls(23, 59, 59)

    def _init(self, hour, minute, second):
        """Set and verify valid time.
        Raise ValueError if *hour*, *minute*, or *second* is out of the valid range."""
        self._hour = int(hour)
        if self.hour < 0 or self.hour > 23:
            raise ValueError(f'Invalid hour: {self.hour}')
        self._minute = int(minute)
        if self.minute < 0 or self.minute > 59:
            raise ValueError(f'Invalid minute: {self.minute}')
        self._second = int(second)
        if self.second < 0 or self.second > 59:
            raise ValueError(f'Invalid second: {self.second}')

    def __init__(self, value, minute=0, second=0):
        """Create new Time object from integer arguments or a string of format 'hh:mm[:ss]'.
        Raise ValueError if arguments are invalid or string cannot be parsed."""
        if isinstance(value, int):
            self._init(value, minute, second)
        elif isinstance(value, str):
            found = _re.match('^(\d{1,2}):(\d{1,2}):(\d{1,2})', value + ':00')
            if not found:
                raise ValueError(f'Invalid time: {value}')
            self._init(found.group(1), found.group(2), found.group(3))
        elif isinstance(value, Time):
            self._init(value.hour, value.minute, value.second)
        else:
            raise ValueError(f'Invalid time: {value}')

    @property
    def hour(self):
        return self._hour

    @property
    def minute(self):
        return self._minute

    @property
    def second(self):
        return self._second

    def diff(self, other):
        """Return difference to *other* in seconds (positive if other is later.)"""
        return (other.hour - self.hour) * 3600 + (other.minute - self.minute) * 60 + (other.second - self.second)

    def __eq__(self, other):
        return isinstance(other, Time) and self.hour == other.hour and self.minute == other.minute and self.second == other.second

    def __lt__(self, other):
        return self.diff(other) > 0

    def __le__(self, other):
        return self == other or self < other

    def __str__(self):
        return f'{self.hour:02}:{self.minute:02}:{self.second:02}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__repr__())


class Date:
    """Date representation with utility methods."""

    @classmethod
    def today(cls):
        """Return Date object that represents 'today'."""
        today = _datetime.date.today()
        return cls(today.year, today.month, today.day)

    @classmethod
    def find_day(cls, year, month, weekday, n=1):
        """Return Date object which represents the *n*th *weekday* within a *month*, e.g. 3rd Monday.
        Raise ValueError if *n* is not realistic e.g. 5th Monday."""
        if n > 5:
            raise ValueError('Cannot find day')
        d = cls(year, month, 1)
        while n > 0:
            while d.weekday != weekday:
                d = d.next()
            n -= 1
            if n > 0:
                d = d.next()
        if d.month != month:
            raise ValueError('Cannot find day')
        return d

    _min_year = 1500
    _max_year = 2500

    def _init(self, year, month, day):
        """Set and verify valid date.
        Raise ValueError if *year*, *month*, or *day* is out of the valid range."""
        self._year = int(year)
        if self.year < Date._min_year or self.year > Date._max_year:
            raise ValueError(f'Invalid year ({Date._min_year}-{Date._max_year}): {self.year}')
        self._month = int(month)
        if self.month < 1 or self.month > 12:
            raise ValueError(f'Invalid month: {self.month}')
        self._day = int(day)
        _, last_day_of_month = _calendar.monthrange(self.year, self.month)
        if self.day < 1 or self.day > last_day_of_month:
            raise ValueError(f'Invalid day (1-{last_day_of_month}): {self.day}')

    def __init__(self, value, month=1, day=1):
        """Create new Date object from integer arguments or a string of format 'YYYY-MM-DD'.
        Raise ValueError if arguments are invalid or string cannot be parsed."""
        if isinstance(value, int):
            self._init(value, month, day)
        elif isinstance(value, str):
            found = _re.match('^(\d{4})-(\d{1,2})-(\d{1,2})', value)
            if not found:
                raise ValueError(f'Invalid date: {value}')
            self._init(found.group(1), found.group(2), found.group(3))
        elif isinstance(value, Date):
            self._init(value.year, value.month, value.day)
        else:
            raise ValueError(f'Invalid date: {value}')

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    @property
    def weekday(self):
        return Weekday(_calendar.weekday(self.year, self.month, self.day))

    @property
    def istoday(self):
        """True if self is today"""
        return self == Date.today()

    _weekend_days = {Weekday.Saturday, Weekday.Sunday}

    @property
    def isweekend(self):
        """True if self is Saturday or Sunday"""
        return self.weekday in Date._weekend_days

    @property
    def isleap(self):
        """True if self is a Date within a leap year"""
        return self.length(period=Period.Year) == 366

    def move(self, n=0, period=Period.Day):
        """Return new Date *n* periods away from self. *n* can be negative or positive."""
        if period is Period.Day:
            moved_date = _datetime.date(self.year, self.month, self.day) + _datetime.timedelta(days=n)
            return Date(moved_date.year, moved_date.month, moved_date.day)
        if period is Period.Week:
            return self.move(n*7, Period.Day)
        if period is Period.Month:
            if (self.month + n) < 1:
                year = self.year + int((self.month + n - 12) / 12)
            else:
                year = self.year + int((self.month + n - 1) / 12)
            month = (self.month + n) % 12
            if month < 1:
                month += 12
            _, last_day_of_month = _calendar.monthrange(year, month)
            return Date(year, month, min(self.day, last_day_of_month))
        if period is Period.Year:
            return Date(self.year + n, self.month, self.day)

    def next(self, n=1, period=Period.Day):
        """Return new Date *n* periods after self."""
        return self.move(+n, period)

    def prev(self, n=1, period=Period.Day):
        """Return new Date *n* periods prior to self."""
        return self.move(-n, period)

    def envelope(self, period=Period.Week, to_date=None):
        """Return tuple of *period* that envelopes self. If *to_date* is not None, the envelope will
        include both self and *to_date*."""
        to_date = to_date or self
        if period is Period.Day:
            if to_date < self:
                raise ValueError('to_date must be after this date')
            return self, to_date
        if period is Period.Week:
            return self.move(-self.weekday.value), to_date.move(6-to_date.weekday.value)
        if period is Period.Month:
            _, last_day_of_month = _calendar.monthrange(to_date.year, to_date.month)
            return Date(self.year, self.month, 1), Date(to_date.year, to_date.month, last_day_of_month)
        if period is Period.Year:
            return Date(self.year, 1, 1), Date(to_date.year, 12, 31)

    def diff(self, other, period=Period.Day):
        """Return difference to *other* date in *period* (positive if other is later.)"""
        if period is Period.Day:
            return _datetime.date(other.year, other.month, other.day).toordinal() - _datetime.date(self.year, self.month, self.day).toordinal()
        if period is Period.Week:
            if self <= other:
                first, last = self.envelope(period, other)
                return int(first.diff(last) / 7)
            first, last = other.envelope(period, self)
            return -int(first.diff(last) / 7)
        if period is Period.Month:
            return (other.year - self.year) * 12 + (other.month - self.month)
        if period is Period.Year:
            return other.year - self.year

    def length(self, period=Period.Month):
        """Return length in days of *period* that contains self (e.g. length of month or year.)"""
        first, last = self.envelope(period)
        return first.diff(last) + 1

    def range(self, to_date=None, n=None):
        """Return list of dates between self and *to_date* or for *n* days starting with
        self (backwards if *n* is negative or *to_date* is before self.)"""
        if to_date is not None:
            n = self.diff(to_date)
        n = n + 1 if n >= 0 else n - 1
        return [self.move(n=_) for _ in range(0, n, 1 if n >= 1 else -1)]

    def __eq__(self, other):
        return isinstance(other, Date) and self.year == other.year and self.month == other.month and self.day == other.day

    def __lt__(self, other):
        return self.year < other.year or \
               (self.year == other.year and self.month < other.month) or \
               (self.year == other.year and self.month == other.month and self.day < other.day)

    def __le__(self, other):
        return self == other or self < other

    def __str__(self):
        return 'f{self.year:04}-{self.month:02}-{self.day:02}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__repr__())


# TODO Support other timezones.

class Timezone(_enum.Enum):
    """Supported time zones."""

    EST5EDT = 'EST'

    @classmethod
    def default(cls):
        """Return module timezone."""
        return cls.EST5EDT

    @classmethod
    def offset(cls, dt):
        """Return time offset for the date/time based on timezone and DST rules."""
        assert dt.timezone == Timezone.EST5EDT
        dst_start = Date.find_day(dt.date.year, 3, Weekday.Sunday, 2)
        dst_end = Date.find_day(dt.date.year, 11, Weekday.Sunday, 1)
        return 4 if dst_start <= dt.date <= dst_end else 5


class DateTime:
    """DateTime representation based on a tuple of Date and Time."""

    @classmethod
    def now(cls):
        """Return DateTime that represents 'now'."""
        return cls((Date.today(), Time.now()))

    def __init__(self, value):
        """Create new DateTime from a Date, a Date and Time tuple, an integer timestamp, or a string of format 'YYYY-MM-DD hh:mm[:ss]'.
        Raise ValueError if arguments are invalid or string cannot be parsed."""
        self._timezone = Timezone.default()
        if isinstance(value, Date):
            self._date = value
            self._time = Time.start_of_day()
        elif isinstance(value, tuple):
            self._date, self._time = value
        elif isinstance(value, str):
            try:
                found = _re.match('^([\d-]*)[ .,@:T]([\d:]*)', value)
                self._date = Date(found.group(1))
                self._time = Time(found.group(2))
            except:
                raise ValueError(f'Invalid date/time: {value}')
        elif isinstance(value, int):
            dt = _datetime.datetime.fromtimestamp(value)
            self._date = Date(dt.year, dt.month, dt.day)
            self._time = Time(dt.hour, dt.minute, dt.second)
        elif isinstance(value, DateTime):
            self._date = Date(value.date)
            self._time = Time(value.time)
        else:
            raise ValueError(f'Invalid date/time: {value}')

    @property
    def date(self):
        return self._date

    @property
    def time(self):
        return self._time

    @property
    def timezone(self):
        return self._timezone

    @property
    def offset(self):
        """Current time offset for the date based on timezone and DST rules"""
        return Timezone.offset(self)

    def diff(self, other):
        """Return difference to *other* in seconds (positive if other is later.)"""
        assert other is None or self.timezone == other.timezone
        delta = _datetime.datetime(other.date.year, other.date.month, other.date.day, other.time.hour, other.time.minute, other.time.second) - \
                _datetime.datetime(self.date.year, self.date.month, self.date.day, self.time.hour, self.time.minute, self.time.second)
        return int(delta.total_seconds())

    def since(self):
        """Return seconds passed from self to now."""
        return self.diff(DateTime.now())

    def to(self, seconds):
        """Return new DateTime after *seconds* from self."""
        dt = _datetime.datetime(self.date.year, self.date.month, self.date.day, self.time.hour, self.time.minute, self.time.second)
        dt += _datetime.timedelta(seconds=seconds)
        return DateTime((Date(dt.year, dt.month, dt.day), Time(dt.hour, dt.minute, dt.second)))

    def __eq__(self, other):
        assert other is None or self.timezone == other.timezone
        return isinstance(other, DateTime) and self.date == other.date and self.time == other.time

    def __lt__(self, other):
        assert other is None or self.timezone == other.timezone
        return self.date < other.date or (self.date == other.date and self.time < other.time)

    def __le__(self, other):
        return self == other or self < other

    def isostr(self):
        """Return an ISO formatted string."""
        return f'{self.date.year:04}-{self.date.month:02}-{self.date.day:02}T{self.time.hour:02}:{self.time.minute:02}:{self.time.second:02}.000000-{self.offset:02}:00'

    def __str__(self):
        return f'{self.date.year:04}-{self.date.month:02}-{self.date.day:02} {self.time.hour:02}:{self.time.minute:02}:{self.time.second:02} {self.timezone.value}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__repr__())


def timestamp(value=None, prec=0.001):
    """Return POSIX timestamp as int for DateTime, Date, or Date and Time tuple in seconds.
    Return current POSIX timestamp as int if value is None with given precision (defaults to 0.001 for milliseconds.)"""
    if value is None:
        return int(_datetime.datetime.now().timestamp()/prec)
    if isinstance(value, DateTime):
        date = value.date
        time = value.time
    elif isinstance(value, Date):
        date = value
        time = Time.start_of_day()
    elif isinstance(value, tuple):
        date, time = value
    else:
        raise ValueError(f'Invalid date/time: {value}')
    return int(_datetime.datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute, second=time.second).timestamp())
