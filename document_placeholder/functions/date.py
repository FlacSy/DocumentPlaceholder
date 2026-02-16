from __future__ import annotations

from datetime import date, timedelta

from document_placeholder.functions import FunctionRegistry


class DateValue:
    """A date with a remembered component order for string formatting."""

    def __init__(self, d: date, components: list[str] | None = None):
        self.date = d
        self.components = components or ["day", "month", "year"]

    # -- arithmetic ----------------------------------------------------------

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return DateValue(self.date - other, self.components)
        if isinstance(other, DateValue):
            return self.date - other.date
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, timedelta):
            return DateValue(self.date + other, self.components)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, timedelta):
            return DateValue(self.date + other, self.components)
        return NotImplemented

    # -- display --------------------------------------------------------------

    def __str__(self) -> str:
        parts: list[str] = []
        for comp in self.components:
            if comp == "day":
                parts.append(f"{self.date.day:02d}")
            elif comp == "month":
                parts.append(f"{self.date.month:02d}")
            elif comp == "year":
                parts.append(str(self.date.year))
        return ".".join(parts)

    def __repr__(self) -> str:
        return f"DateValue({self.date!r}, {self.components!r})"


MONTH_NAMES: dict[int, str] = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

DAY_NAMES: dict[int, str] = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


@FunctionRegistry.register("CURRENT_DATE_NUM")
def current_date_num(*args: str):
    """Return numeric date component(s).

    Single arg  → ``int``  (e.g. ``CURRENT_DATE_NUM(year)`` → 2026)
    Multiple    → ``DateValue`` that formats as ``dd.mm.yyyy``
    """
    today = date.today()

    if len(args) == 1:
        comp = args[0]
        if comp == "year":
            return today.year
        if comp == "month":
            return today.month
        if comp == "day":
            return today.day
        raise ValueError(f"Unknown date component: {comp}")

    return DateValue(today, list(args))


@FunctionRegistry.register("CURRENT_DATE_STR")
def current_date_str(*args: str):
    """Return a human-readable string for a date component.

    ``CURRENT_DATE_STR(month)`` → ``"February"``
    """
    today = date.today()

    if not args:
        return today.strftime("%B %d, %Y")

    comp = args[0]
    if comp == "month":
        return MONTH_NAMES[today.month]
    if comp == "day":
        return DAY_NAMES[today.weekday()]
    if comp == "year":
        return str(today.year)
    raise ValueError(f"Unknown date component: {comp}")


@FunctionRegistry.register("DAYS")
def days(n) -> timedelta:
    """Return a ``timedelta`` of *n* days."""
    return timedelta(days=int(n))


@FunctionRegistry.register("WEEKS")
def weeks(n) -> timedelta:
    """Return a ``timedelta`` of *n* weeks."""
    return timedelta(weeks=int(n))


@FunctionRegistry.register("MONTHS")
def months(n) -> timedelta:
    """Approximate ``timedelta`` of *n* months (30 days each)."""
    return timedelta(days=int(n) * 30)


@FunctionRegistry.register("YEARS")
def years(n) -> timedelta:
    """Approximate ``timedelta`` of *n* years (365 days each)."""
    return timedelta(days=int(n) * 365)


@FunctionRegistry.register("TODAY")
def today():
    """Return today's date as a ``DateValue``."""
    return DateValue(date.today())


@FunctionRegistry.register("DATE")
def make_date(year, month, day):
    """Construct a ``DateValue`` from explicit components.

    ``DATE(2026, 3, 15)`` → ``15.03.2026``
    """
    return DateValue(date(int(year), int(month), int(day)))


@FunctionRegistry.register("DATE_FORMAT")
def date_format(d, fmt) -> str:
    """Format a date using a ``strftime``-style *fmt* string.

    ``DATE_FORMAT(TODAY(), '%Y-%m-%d')`` → ``"2026-02-16"``
    """
    if isinstance(d, DateValue):
        return d.date.strftime(str(fmt))
    if isinstance(d, date):
        return d.strftime(str(fmt))
    raise TypeError(f"DATE_FORMAT expects a date, got {type(d).__name__}")


@FunctionRegistry.register("DAY_OF_WEEK")
def day_of_week(d=None) -> int:
    """Return the ISO weekday number (Monday=1 … Sunday=7)."""
    if d is None:
        return date.today().isoweekday()
    if isinstance(d, DateValue):
        return d.date.isoweekday()
    if isinstance(d, date):
        return d.isoweekday()
    raise TypeError(f"DAY_OF_WEEK expects a date, got {type(d).__name__}")


@FunctionRegistry.register("DAYS_BETWEEN")
def days_between(a, b) -> int:
    """Return the number of days between two dates (``b - a``).

    Result is negative when *a* is after *b*.
    """
    da = a.date if isinstance(a, DateValue) else a
    db = b.date if isinstance(b, DateValue) else b
    return (db - da).days
