"""Built-in logic / control-flow functions."""

from __future__ import annotations

import os

from document_placeholder.functions import FunctionRegistry

_reg = FunctionRegistry.register


@_reg("IF")
def if_fn(condition, then_val, else_val=None):
    """Return *then_val* when *condition* is truthy, otherwise *else_val*.

    ``IF(PRICE > 1000, 'expensive', 'cheap')``
    """
    return then_val if condition else (else_val if else_val is not None else "")


@_reg("COALESCE")
def coalesce(*args):
    """Return the first non-``None`` argument (or ``None``)."""
    for a in args:
        if a is not None:
            return a
    return None


@_reg("DEFAULT")
def default(val, fallback):
    """Return *val* if it is not ``None``, otherwise *fallback*."""
    return val if val is not None else fallback


@_reg("DEFINED")
def defined(val) -> bool:
    """Return ``True`` if *val* is not ``None``."""
    return val is not None


@_reg("NOT")
def not_fn(val) -> bool:
    """Logical NOT."""
    return not val


@_reg("AND")
def and_fn(*args) -> bool:
    """Logical AND — ``True`` when every argument is truthy."""
    return all(args)


@_reg("OR")
def or_fn(*args) -> bool:
    """Logical OR — ``True`` when at least one argument is truthy."""
    return any(args)


@_reg("CHOOSE")
def choose(index, *args):
    """Pick a value by 0-based *index*.

    ``CHOOSE(1, 'a', 'b', 'c')`` → ``'b'``
    """
    i = int(index)
    if 0 <= i < len(args):
        return args[i]
    raise ValueError(f"CHOOSE index {i} out of range (0..{len(args) - 1})")


@_reg("SWITCH")
def switch(value, *pairs):
    """Match *value* against ``(case, result)`` pairs with optional default.

    ``SWITCH(STATUS, 'draft', 'Draft', 'sent', 'Sent', 'Unknown')``

    Odd number of remaining args means the last one is the default.
    """
    it = iter(pairs)
    for case in it:
        result = next(it, None)
        if result is None:
            return case  # last unpaired value = default
        if value == case:
            return result
    return None


@_reg("ENV")
def env(name, fallback="") -> str:
    """Read an environment variable (with optional *fallback*).

    ``ENV('HOME')`` → ``/home/user``
    """
    return os.environ.get(str(name), str(fallback))
