"""Tests for built-in date / time functions."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pytest

import document_placeholder.functions.date as date_mod  # noqa: F401 — register functions
from document_placeholder.functions import FunctionRegistry
from document_placeholder.functions.date import DateValue

call = FunctionRegistry.call

FIXED_TODAY = date(2026, 6, 15)  # Sunday


# ── DateValue ───────────────────────────────────────────────────────────────


class TestDateValue:

    def test_str_default_components(self):
        dv = DateValue(date(2026, 3, 5))
        assert str(dv) == "05.03.2026"

    def test_str_custom_components(self):
        dv = DateValue(date(2026, 3, 5), ["year", "month", "day"])
        assert str(dv) == "2026.03.05"

    def test_repr(self):
        dv = DateValue(date(2026, 1, 1))
        assert "DateValue" in repr(dv)

    def test_sub_timedelta(self):
        dv = DateValue(date(2026, 3, 10))
        result = dv - timedelta(days=5)
        assert isinstance(result, DateValue)
        assert result.date == date(2026, 3, 5)

    def test_sub_datevalue(self):
        a = DateValue(date(2026, 3, 10))
        b = DateValue(date(2026, 3, 1))
        result = a - b
        assert isinstance(result, timedelta)
        assert result.days == 9

    def test_sub_unsupported(self):
        dv = DateValue(date(2026, 1, 1))
        assert dv.__sub__("bad") is NotImplemented

    def test_add_timedelta(self):
        dv = DateValue(date(2026, 1, 1))
        result = dv + timedelta(days=10)
        assert isinstance(result, DateValue)
        assert result.date == date(2026, 1, 11)

    def test_add_unsupported(self):
        dv = DateValue(date(2026, 1, 1))
        assert dv.__add__("bad") is NotImplemented

    def test_radd_timedelta(self):
        dv = DateValue(date(2026, 1, 1))
        result = timedelta(days=5) + dv
        assert isinstance(result, DateValue)
        assert result.date == date(2026, 1, 6)


# ── CURRENT_DATE_NUM ────────────────────────────────────────────────────────


class TestCurrentDateNum:

    @patch("document_placeholder.functions.date.date")
    def test_year(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        assert call("CURRENT_DATE_NUM", ["year"]) == 2026

    @patch("document_placeholder.functions.date.date")
    def test_month(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        assert call("CURRENT_DATE_NUM", ["month"]) == 6

    @patch("document_placeholder.functions.date.date")
    def test_day(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        assert call("CURRENT_DATE_NUM", ["day"]) == 15

    @patch("document_placeholder.functions.date.date")
    def test_multiple_components(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        result = call("CURRENT_DATE_NUM", ["day", "month", "year"])
        assert isinstance(result, DateValue)
        assert str(result) == "15.06.2026"

    def test_unknown_component(self):
        with pytest.raises(ValueError, match="Unknown date component"):
            call("CURRENT_DATE_NUM", ["hour"])


# ── CURRENT_DATE_STR ────────────────────────────────────────────────────────


class TestCurrentDateStr:

    @patch("document_placeholder.functions.date.date")
    def test_month(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        assert call("CURRENT_DATE_STR", ["month"]) == "June"

    @patch("document_placeholder.functions.date.date")
    def test_day(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        assert call("CURRENT_DATE_STR", ["day"]) == "Monday"

    @patch("document_placeholder.functions.date.date")
    def test_year(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        assert call("CURRENT_DATE_STR", ["year"]) == "2026"

    @patch("document_placeholder.functions.date.date")
    def test_no_args(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        result = call("CURRENT_DATE_STR", [])
        assert result == "June 15, 2026"

    def test_unknown_component(self):
        with pytest.raises(ValueError, match="Unknown date component"):
            call("CURRENT_DATE_STR", ["hour"])


# ── DAYS / WEEKS / MONTHS / YEARS ──────────────────────────────────────────


class TestIntervals:

    def test_days(self):
        assert call("DAYS", [7]) == timedelta(days=7)

    def test_days_zero(self):
        assert call("DAYS", [0]) == timedelta(0)

    def test_weeks(self):
        assert call("WEEKS", [2]) == timedelta(weeks=2)

    def test_months(self):
        assert call("MONTHS", [3]) == timedelta(days=90)

    def test_years(self):
        assert call("YEARS", [1]) == timedelta(days=365)


# ── TODAY ───────────────────────────────────────────────────────────────────


class TestToday:

    @patch("document_placeholder.functions.date.date")
    def test_returns_date_value(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *a, **k: date(*a, **k)
        result = call("TODAY", [])
        assert isinstance(result, DateValue)
        assert result.date == FIXED_TODAY


# ── DATE ────────────────────────────────────────────────────────────────────


class TestDate:

    def test_basic(self):
        result = call("DATE", [2026, 3, 15])
        assert isinstance(result, DateValue)
        assert result.date == date(2026, 3, 15)

    def test_str(self):
        result = call("DATE", [2026, 1, 5])
        assert str(result) == "05.01.2026"

    def test_string_args(self):
        result = call("DATE", ["2026", "12", "25"])
        assert result.date == date(2026, 12, 25)


# ── DATE_FORMAT ─────────────────────────────────────────────────────────────


class TestDateFormat:

    def test_iso(self):
        dv = DateValue(date(2026, 3, 15))
        assert call("DATE_FORMAT", [dv, "%Y-%m-%d"]) == "2026-03-15"

    def test_verbose(self):
        dv = DateValue(date(2026, 3, 8))
        result = call("DATE_FORMAT", [dv, "%d %B %Y"])
        assert result == "08 March 2026"

    def test_raw_date(self):
        d = date(2026, 1, 1)
        assert call("DATE_FORMAT", [d, "%Y"]) == "2026"

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="DATE_FORMAT expects a date"):
            call("DATE_FORMAT", ["not-a-date", "%Y"])


# ── DAY_OF_WEEK ─────────────────────────────────────────────────────────────


class TestDayOfWeek:

    def test_specific_date(self):
        dv = DateValue(date(2026, 6, 15))  # Monday
        assert call("DAY_OF_WEEK", [dv]) == 1

    def test_sunday(self):
        dv = DateValue(date(2026, 6, 14))  # Sunday
        assert call("DAY_OF_WEEK", [dv]) == 7

    def test_raw_date(self):
        d = date(2026, 6, 15)
        assert call("DAY_OF_WEEK", [d]) == 1

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="DAY_OF_WEEK expects a date"):
            call("DAY_OF_WEEK", ["bad"])


# ── DAYS_BETWEEN ────────────────────────────────────────────────────────────


class TestDaysBetween:

    def test_positive(self):
        a = DateValue(date(2026, 1, 1))
        b = DateValue(date(2026, 2, 1))
        assert call("DAYS_BETWEEN", [a, b]) == 31

    def test_negative(self):
        a = DateValue(date(2026, 2, 1))
        b = DateValue(date(2026, 1, 1))
        assert call("DAYS_BETWEEN", [a, b]) == -31

    def test_same_date(self):
        a = DateValue(date(2026, 5, 5))
        assert call("DAYS_BETWEEN", [a, a]) == 0

    def test_mixed_types(self):
        a = DateValue(date(2026, 1, 1))
        b = date(2026, 1, 11)
        assert call("DAYS_BETWEEN", [a, b]) == 10
