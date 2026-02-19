"""Built-in math / numeric functions."""

from __future__ import annotations

import math as _math

from document_placeholder.functions import FunctionRegistry

_reg = FunctionRegistry.register


@_reg("ROUND")
def round_fn(n, decimals=0):
    """Round *n* to *decimals* decimal places."""
    return round(float(n), int(decimals))


@_reg("FLOOR")
def floor(n) -> int:
    """Return the largest integer ≤ *n*."""
    return _math.floor(float(n))


@_reg("CEIL")
def ceil(n) -> int:
    """Return the smallest integer ≥ *n*."""
    return _math.ceil(float(n))


@_reg("ABS")
def abs_fn(n):
    """Return the absolute value of *n*."""
    return abs(n)


@_reg("MIN")
def min_fn(*args):
    """Return the smallest argument."""
    return min(args)


@_reg("MAX")
def max_fn(*args):
    """Return the largest argument."""
    return max(args)


@_reg("SUM")
def sum_fn(*args):
    """Return the sum of all arguments."""
    return sum(args)


@_reg("AVG")
def avg(*args):
    """Return the arithmetic mean of all arguments."""
    if not args:
        return 0
    return sum(args) / len(args)


@_reg("POW")
def pow_fn(base, exp):
    """Return *base* raised to the power *exp*."""
    return float(base) ** float(exp)


@_reg("SQRT")
def sqrt(n):
    """Return the square root of *n*."""
    return _math.sqrt(float(n))


@_reg("INT")
def int_fn(n) -> int:
    """Convert *n* to integer (truncates toward zero)."""
    return int(float(n))


@_reg("FLOAT")
def float_fn(n) -> float:
    """Convert *n* to float."""
    return float(n)


@_reg("FORMAT_NUM")
def format_num(n, decimals=2) -> str:
    """Format *n* with thousands separators and *decimals* decimal places.

    ``FORMAT_NUM(1234567.891, 2)`` → ``"1,234,567.89"``
    """
    return f"{float(n):,.{int(decimals)}f}"


@_reg("RANDOM_INT")
def random_int(low, high) -> int:
    """Return a random integer in [*low*, *high*]."""
    import random

    return random.randint(int(low), int(high))
