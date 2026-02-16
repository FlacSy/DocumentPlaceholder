"""Tests for built-in logic / control-flow functions."""

from __future__ import annotations

import os

import pytest

import document_placeholder.functions.logic  # noqa: F401 — register functions

from document_placeholder.functions import FunctionRegistry

call = FunctionRegistry.call


class TestIf:
    def test_true_branch(self):
        assert call("IF", [True, "yes", "no"]) == "yes"

    def test_false_branch(self):
        assert call("IF", [False, "yes", "no"]) == "no"

    def test_truthy_int(self):
        assert call("IF", [1, "yes", "no"]) == "yes"

    def test_falsy_zero(self):
        assert call("IF", [0, "yes", "no"]) == "no"

    def test_no_else(self):
        assert call("IF", [False, "yes"]) == ""

    def test_no_else_truthy(self):
        assert call("IF", [True, "yes"]) == "yes"


class TestCoalesce:
    def test_first_non_none(self):
        assert call("COALESCE", [None, None, "found"]) == "found"

    def test_first_value(self):
        assert call("COALESCE", ["first", "second"]) == "first"

    def test_all_none(self):
        assert call("COALESCE", [None, None]) is None

    def test_zero_is_not_none(self):
        assert call("COALESCE", [0, "fallback"]) == 0

    def test_empty_string_is_not_none(self):
        assert call("COALESCE", ["", "fallback"]) == ""


class TestDefault:
    def test_value_present(self):
        assert call("DEFAULT", [42, "fallback"]) == 42

    def test_none_returns_fallback(self):
        assert call("DEFAULT", [None, "fallback"]) == "fallback"

    def test_zero_is_kept(self):
        assert call("DEFAULT", [0, 99]) == 0


class TestDefined:
    def test_defined(self):
        assert call("DEFINED", [42]) is True

    def test_none(self):
        assert call("DEFINED", [None]) is False

    def test_empty_string(self):
        assert call("DEFINED", [""]) is True

    def test_zero(self):
        assert call("DEFINED", [0]) is True


class TestNot:
    def test_true(self):
        assert call("NOT", [True]) is False

    def test_false(self):
        assert call("NOT", [False]) is True

    def test_truthy(self):
        assert call("NOT", [1]) is False

    def test_falsy(self):
        assert call("NOT", [0]) is True

    def test_none(self):
        assert call("NOT", [None]) is True


class TestAnd:
    def test_all_true(self):
        assert call("AND", [True, True, True]) is True

    def test_one_false(self):
        assert call("AND", [True, False, True]) is False

    def test_single_true(self):
        assert call("AND", [True]) is True

    def test_single_false(self):
        assert call("AND", [False]) is False


class TestOr:
    def test_one_true(self):
        assert call("OR", [False, True, False]) is True

    def test_all_false(self):
        assert call("OR", [False, False]) is False

    def test_all_true(self):
        assert call("OR", [True, True]) is True

    def test_single_false(self):
        assert call("OR", [False]) is False


class TestChoose:
    def test_first(self):
        assert call("CHOOSE", [0, "a", "b", "c"]) == "a"

    def test_middle(self):
        assert call("CHOOSE", [1, "a", "b", "c"]) == "b"

    def test_last(self):
        assert call("CHOOSE", [2, "a", "b", "c"]) == "c"

    def test_out_of_range(self):
        with pytest.raises(ValueError, match="out of range"):
            call("CHOOSE", [5, "a", "b"])

    def test_negative_index(self):
        with pytest.raises(ValueError, match="out of range"):
            call("CHOOSE", [-1, "a", "b"])


class TestSwitch:
    def test_match_first(self):
        assert call("SWITCH", ["a", "a", "Alpha", "b", "Beta"]) == "Alpha"

    def test_match_second(self):
        assert call("SWITCH", ["b", "a", "Alpha", "b", "Beta"]) == "Beta"

    def test_no_match_no_default(self):
        assert call("SWITCH", ["c", "a", "Alpha", "b", "Beta"]) is None

    def test_default_value(self):
        result = call("SWITCH", ["c", "a", "Alpha", "b", "Beta", "Default"])
        assert result == "Default"


class TestEnv:
    def test_existing_var(self):
        os.environ["_DP_TEST_VAR"] = "hello"
        try:
            assert call("ENV", ["_DP_TEST_VAR"]) == "hello"
        finally:
            del os.environ["_DP_TEST_VAR"]

    def test_missing_var_default(self):
        assert call("ENV", ["_DP_NONEXISTENT_VAR_12345"]) == ""

    def test_custom_fallback(self):
        assert call("ENV", ["_DP_NONEXISTENT_VAR_12345", "fallback"]) == "fallback"
