"""Built-in string manipulation functions."""

from __future__ import annotations

from document_placeholder.functions import FunctionRegistry

_reg = FunctionRegistry.register


@_reg("UPPER")
def upper(text) -> str:
    """Convert *text* to uppercase."""
    return str(text).upper()


@_reg("LOWER")
def lower(text) -> str:
    """Convert *text* to lowercase."""
    return str(text).lower()


@_reg("CAPITALIZE")
def capitalize(text) -> str:
    """Capitalize the first letter."""
    return str(text).capitalize()


@_reg("TITLE")
def title(text) -> str:
    """Title-case every word."""
    return str(text).title()


@_reg("TRIM")
def trim(text) -> str:
    """Strip leading/trailing whitespace."""
    return str(text).strip()


@_reg("TRIM_LEFT")
def trim_left(text) -> str:
    """Strip leading whitespace."""
    return str(text).lstrip()


@_reg("TRIM_RIGHT")
def trim_right(text) -> str:
    """Strip trailing whitespace."""
    return str(text).rstrip()


@_reg("LEN")
def len_fn(text) -> int:
    """Return the length of *text*."""
    return len(str(text))


@_reg("REPLACE")
def replace(text, old, new) -> str:
    """Replace every occurrence of *old* with *new* in *text*."""
    return str(text).replace(str(old), str(new))


@_reg("SUBSTR")
def substr(text, start, length=None) -> str:
    """Return a substring starting at *start* (0-based) with optional *length*."""
    s = str(text)
    start = int(start)
    if length is None:
        return s[start:]
    return s[start : start + int(length)]


@_reg("LEFT")
def left(text, n) -> str:
    """Return the first *n* characters."""
    return str(text)[: int(n)]


@_reg("RIGHT")
def right(text, n) -> str:
    """Return the last *n* characters."""
    return str(text)[-int(n) :]


@_reg("PAD_LEFT")
def pad_left(text, width, char=" ") -> str:
    """Right-justify *text* in a field of *width*, padding with *char*."""
    return str(text).rjust(int(width), str(char)[0])


@_reg("PAD_RIGHT")
def pad_right(text, width, char=" ") -> str:
    """Left-justify *text* in a field of *width*, padding with *char*."""
    return str(text).ljust(int(width), str(char)[0])


@_reg("REPEAT")
def repeat(text, n) -> str:
    """Repeat *text* *n* times."""
    return str(text) * int(n)


@_reg("CONCAT")
def concat(*args) -> str:
    """Concatenate all arguments into one string."""
    return "".join(str(a) for a in args)


@_reg("JOIN")
def join(sep, *args) -> str:
    """Join arguments with *sep* separator."""
    return str(sep).join(str(a) for a in args)


@_reg("CONTAINS")
def contains(text, sub) -> bool:
    """Return ``True`` if *text* contains *sub*."""
    return str(sub) in str(text)


@_reg("STARTS_WITH")
def starts_with(text, prefix) -> bool:
    """Return ``True`` if *text* starts with *prefix*."""
    return str(text).startswith(str(prefix))


@_reg("ENDS_WITH")
def ends_with(text, suffix) -> bool:
    """Return ``True`` if *text* ends with *suffix*."""
    return str(text).endswith(str(suffix))


@_reg("SPLIT")
def split(text, sep, index) -> str:
    """Split *text* by *sep* and return the part at *index*."""
    return str(text).split(str(sep))[int(index)]


@_reg("REVERSE")
def reverse(text) -> str:
    """Reverse *text*."""
    return str(text)[::-1]


@_reg("COUNT_SUBSTR")
def count_substr(text, sub) -> int:
    """Count non-overlapping occurrences of *sub* in *text*."""
    return str(text).count(str(sub))
