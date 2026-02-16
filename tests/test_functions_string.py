"""Tests for built-in string functions."""

from __future__ import annotations

import pytest

import document_placeholder.functions.string  # noqa: F401 — register functions

from document_placeholder.functions import FunctionRegistry

call = FunctionRegistry.call


class TestUpper:
    def test_basic(self):
        assert call("UPPER", ["hello"]) == "HELLO"

    def test_mixed(self):
        assert call("UPPER", ["Hello World"]) == "HELLO WORLD"

    def test_numeric_input(self):
        assert call("UPPER", [42]) == "42"


class TestLower:
    def test_basic(self):
        assert call("LOWER", ["HELLO"]) == "hello"

    def test_mixed(self):
        assert call("LOWER", ["Hello World"]) == "hello world"


class TestCapitalize:
    def test_basic(self):
        assert call("CAPITALIZE", ["hello world"]) == "Hello world"

    def test_already_capitalized(self):
        assert call("CAPITALIZE", ["Hello"]) == "Hello"

    def test_all_upper(self):
        assert call("CAPITALIZE", ["HELLO"]) == "Hello"


class TestTitle:
    def test_basic(self):
        assert call("TITLE", ["hello world"]) == "Hello World"

    def test_single_word(self):
        assert call("TITLE", ["hello"]) == "Hello"


class TestTrim:
    def test_both_sides(self):
        assert call("TRIM", ["  hello  "]) == "hello"

    def test_no_whitespace(self):
        assert call("TRIM", ["hello"]) == "hello"

    def test_tabs_and_newlines(self):
        assert call("TRIM", ["\n\thello\t\n"]) == "hello"


class TestTrimLeft:
    def test_basic(self):
        assert call("TRIM_LEFT", ["  hello  "]) == "hello  "


class TestTrimRight:
    def test_basic(self):
        assert call("TRIM_RIGHT", ["  hello  "]) == "  hello"


class TestLen:
    def test_basic(self):
        assert call("LEN", ["hello"]) == 5

    def test_empty(self):
        assert call("LEN", [""]) == 0

    def test_numeric(self):
        assert call("LEN", [12345]) == 5


class TestReplace:
    def test_basic(self):
        assert call("REPLACE", ["foo bar foo", "foo", "baz"]) == "baz bar baz"

    def test_no_match(self):
        assert call("REPLACE", ["hello", "xyz", "abc"]) == "hello"

    def test_empty_replacement(self):
        assert call("REPLACE", ["hello", "l", ""]) == "heo"


class TestSubstr:
    def test_from_start(self):
        assert call("SUBSTR", ["hello world", 6]) == "world"

    def test_with_length(self):
        assert call("SUBSTR", ["hello world", 0, 5]) == "hello"

    def test_middle(self):
        assert call("SUBSTR", ["abcdef", 2, 2]) == "cd"


class TestLeft:
    def test_basic(self):
        assert call("LEFT", ["abcdef", 3]) == "abc"

    def test_full(self):
        assert call("LEFT", ["abc", 10]) == "abc"


class TestRight:
    def test_basic(self):
        assert call("RIGHT", ["abcdef", 3]) == "def"

    def test_full(self):
        assert call("RIGHT", ["abc", 10]) == "abc"


class TestPadLeft:
    def test_basic(self):
        assert call("PAD_LEFT", ["42", 6, "0"]) == "000042"

    def test_default_char(self):
        assert call("PAD_LEFT", ["hi", 5]) == "   hi"

    def test_no_padding_needed(self):
        assert call("PAD_LEFT", ["hello", 3, "0"]) == "hello"


class TestPadRight:
    def test_basic(self):
        assert call("PAD_RIGHT", ["hi", 5, "."]) == "hi..."

    def test_default_char(self):
        assert call("PAD_RIGHT", ["hi", 5]) == "hi   "


class TestRepeat:
    def test_basic(self):
        assert call("REPEAT", ["ab", 3]) == "ababab"

    def test_zero(self):
        assert call("REPEAT", ["x", 0]) == ""


class TestConcat:
    def test_basic(self):
        assert call("CONCAT", ["a", "b", "c"]) == "abc"

    def test_mixed_types(self):
        assert call("CONCAT", ["item", 1]) == "item1"

    def test_empty(self):
        assert call("CONCAT", []) == ""


class TestJoin:
    def test_basic(self):
        assert call("JOIN", [", ", "a", "b", "c"]) == "a, b, c"

    def test_single_item(self):
        assert call("JOIN", ["-", "only"]) == "only"

    def test_numbers(self):
        assert call("JOIN", ["-", 1, 2, 3]) == "1-2-3"


class TestContains:
    def test_true(self):
        assert call("CONTAINS", ["hello world", "world"]) is True

    def test_false(self):
        assert call("CONTAINS", ["hello world", "xyz"]) is False

    def test_empty_sub(self):
        assert call("CONTAINS", ["hello", ""]) is True


class TestStartsWith:
    def test_true(self):
        assert call("STARTS_WITH", ["hello world", "hello"]) is True

    def test_false(self):
        assert call("STARTS_WITH", ["hello world", "world"]) is False


class TestEndsWith:
    def test_true(self):
        assert call("ENDS_WITH", ["hello world", "world"]) is True

    def test_false(self):
        assert call("ENDS_WITH", ["hello world", "hello"]) is False


class TestSplit:
    def test_basic(self):
        assert call("SPLIT", ["a-b-c", "-", 1]) == "b"

    def test_first(self):
        assert call("SPLIT", ["user@example.com", "@", 0]) == "user"

    def test_last(self):
        assert call("SPLIT", ["user@example.com", "@", 1]) == "example.com"


class TestReverse:
    def test_basic(self):
        assert call("REVERSE", ["abc"]) == "cba"

    def test_palindrome(self):
        assert call("REVERSE", ["racecar"]) == "racecar"

    def test_empty(self):
        assert call("REVERSE", [""]) == ""


class TestCountSubstr:
    def test_basic(self):
        assert call("COUNT_SUBSTR", ["banana", "an"]) == 2

    def test_no_match(self):
        assert call("COUNT_SUBSTR", ["hello", "xyz"]) == 0

    def test_single_char(self):
        assert call("COUNT_SUBSTR", ["aaa", "a"]) == 3
