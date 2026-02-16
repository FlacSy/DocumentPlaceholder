"""Tests for built-in math functions."""

from __future__ import annotations

import pytest

import document_placeholder.functions.math  # noqa: F401 — register functions

from document_placeholder.functions import FunctionRegistry

call = FunctionRegistry.call


class TestRound:
    def test_default_zero(self):
        assert call("ROUND", [3.7]) == 4.0

    def test_two_decimals(self):
        assert call("ROUND", [3.14159, 2]) == 3.14

    def test_round_down(self):
        assert call("ROUND", [3.14159, 3]) == 3.142

    def test_integer_input(self):
        assert call("ROUND", [5, 2]) == 5.0


class TestFloor:
    def test_positive(self):
        assert call("FLOOR", [3.9]) == 3

    def test_negative(self):
        assert call("FLOOR", [-1.1]) == -2

    def test_integer(self):
        assert call("FLOOR", [5.0]) == 5


class TestCeil:
    def test_positive(self):
        assert call("CEIL", [3.1]) == 4

    def test_negative(self):
        assert call("CEIL", [-1.9]) == -1

    def test_integer(self):
        assert call("CEIL", [5.0]) == 5


class TestAbs:
    def test_negative(self):
        assert call("ABS", [-5]) == 5

    def test_positive(self):
        assert call("ABS", [5]) == 5

    def test_zero(self):
        assert call("ABS", [0]) == 0

    def test_float(self):
        assert call("ABS", [-3.14]) == 3.14


class TestMin:
    def test_basic(self):
        assert call("MIN", [3, 1, 4, 1, 5]) == 1

    def test_single(self):
        assert call("MIN", [42]) == 42

    def test_negative(self):
        assert call("MIN", [-1, -5, 0]) == -5


class TestMax:
    def test_basic(self):
        assert call("MAX", [3, 1, 4, 1, 5]) == 5

    def test_single(self):
        assert call("MAX", [42]) == 42

    def test_negative(self):
        assert call("MAX", [-1, -5, 0]) == 0


class TestSum:
    def test_basic(self):
        assert call("SUM", [1, 2, 3]) == 6

    def test_single(self):
        assert call("SUM", [42]) == 42

    def test_with_negatives(self):
        assert call("SUM", [10, -3, 5]) == 12


class TestAvg:
    def test_basic(self):
        assert call("AVG", [10, 20, 30]) == 20.0

    def test_single(self):
        assert call("AVG", [7]) == 7.0

    def test_empty(self):
        assert call("AVG", []) == 0


class TestPow:
    def test_basic(self):
        assert call("POW", [2, 10]) == 1024.0

    def test_square(self):
        assert call("POW", [5, 2]) == 25.0

    def test_zero_exponent(self):
        assert call("POW", [99, 0]) == 1.0

    def test_fractional_exponent(self):
        assert call("POW", [9, 0.5]) == 3.0


class TestSqrt:
    def test_perfect_square(self):
        assert call("SQRT", [144]) == 12.0

    def test_non_perfect(self):
        assert abs(call("SQRT", [2]) - 1.41421356) < 1e-5

    def test_zero(self):
        assert call("SQRT", [0]) == 0.0


class TestInt:
    def test_from_float(self):
        assert call("INT", [9.87]) == 9

    def test_from_string(self):
        assert call("INT", ["42"]) == 42

    def test_negative(self):
        assert call("INT", [-3.9]) == -3


class TestFloat:
    def test_from_int(self):
        assert call("FLOAT", [42]) == 42.0

    def test_from_string(self):
        assert call("FLOAT", ["3.14"]) == 3.14


class TestFormatNum:
    def test_default_decimals(self):
        assert call("FORMAT_NUM", [1234567.891]) == "1,234,567.89"

    def test_zero_decimals(self):
        assert call("FORMAT_NUM", [5000, 0]) == "5,000"

    def test_small_number(self):
        assert call("FORMAT_NUM", [42, 2]) == "42.00"

    def test_three_decimals(self):
        assert call("FORMAT_NUM", [1.23456, 3]) == "1.235"


class TestRandomInt:
    def test_in_range(self):
        for _ in range(50):
            val = call("RANDOM_INT", [1, 10])
            assert 1 <= val <= 10

    def test_single_value(self):
        assert call("RANDOM_INT", [5, 5]) == 5
