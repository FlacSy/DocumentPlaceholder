"""Tests for the expression evaluator."""

from __future__ import annotations

import pytest

# Ensure all function modules are imported so that the registry is populated.
import document_placeholder.functions.date     # noqa: F401
import document_placeholder.functions.logic    # noqa: F401
import document_placeholder.functions.math     # noqa: F401
import document_placeholder.functions.string   # noqa: F401

from document_placeholder.evaluator import Evaluator


@pytest.fixture()
def ev() -> Evaluator:
    return Evaluator()


# ── Arithmetic operators ────────────────────────────────────────────────────


class TestArithmeticOps:

    def test_add(self, ev: Evaluator):
        assert ev.evaluate_expression("2 + 3") == 5

    def test_subtract(self, ev: Evaluator):
        assert ev.evaluate_expression("10 - 4") == 6

    def test_multiply(self, ev: Evaluator):
        assert ev.evaluate_expression("3 * 7") == 21

    def test_divide(self, ev: Evaluator):
        assert ev.evaluate_expression("10 / 4") == 2.5

    def test_modulo(self, ev: Evaluator):
        assert ev.evaluate_expression("10 % 3") == 1

    def test_unary_minus(self, ev: Evaluator):
        assert ev.evaluate_expression("-5") == -5

    def test_complex_arithmetic(self, ev: Evaluator):
        assert ev.evaluate_expression("2 + 3 * 4 - 1") == 13

    def test_parentheses(self, ev: Evaluator):
        assert ev.evaluate_expression("(2 + 3) * 4") == 20


# ── Comparison operators ────────────────────────────────────────────────────


class TestComparisonOps:

    def test_gt_true(self, ev: Evaluator):
        assert ev.evaluate_expression("5 > 3") is True

    def test_gt_false(self, ev: Evaluator):
        assert ev.evaluate_expression("2 > 3") is False

    def test_lt_true(self, ev: Evaluator):
        assert ev.evaluate_expression("2 < 5") is True

    def test_lt_false(self, ev: Evaluator):
        assert ev.evaluate_expression("5 < 3") is False

    def test_gte_equal(self, ev: Evaluator):
        assert ev.evaluate_expression("5 >= 5") is True

    def test_gte_greater(self, ev: Evaluator):
        assert ev.evaluate_expression("6 >= 5") is True

    def test_gte_less(self, ev: Evaluator):
        assert ev.evaluate_expression("4 >= 5") is False

    def test_lte_equal(self, ev: Evaluator):
        assert ev.evaluate_expression("5 <= 5") is True

    def test_lte_less(self, ev: Evaluator):
        assert ev.evaluate_expression("3 <= 5") is True

    def test_lte_greater(self, ev: Evaluator):
        assert ev.evaluate_expression("6 <= 5") is False

    def test_eq_true(self, ev: Evaluator):
        assert ev.evaluate_expression("7 == 7") is True

    def test_eq_false(self, ev: Evaluator):
        assert ev.evaluate_expression("7 == 8") is False

    def test_neq_true(self, ev: Evaluator):
        assert ev.evaluate_expression("7 != 8") is True

    def test_neq_false(self, ev: Evaluator):
        assert ev.evaluate_expression("7 != 7") is False

    def test_comparison_with_arithmetic(self, ev: Evaluator):
        assert ev.evaluate_expression("2 + 3 > 4") is True


# ── Template evaluation ────────────────────────────────────────────────────


class TestTemplateEvaluation:

    def test_plain_text(self, ev: Evaluator):
        assert ev.evaluate_template("hello world") == "hello world"

    def test_single_expression(self, ev: Evaluator):
        assert ev.evaluate_template("{2 + 2}") == "4"

    def test_mixed_template(self, ev: Evaluator):
        result = ev.evaluate_template("sum is {10 + 5}!")
        assert result == "sum is 15!"

    def test_multiple_expressions(self, ev: Evaluator):
        result = ev.evaluate_template("{1 + 1} and {2 * 3}")
        assert result == "2 and 6"

    def test_nested_braces_with_function(self, ev: Evaluator):
        result = ev.evaluate_template("{UPPER('hello')}")
        assert result == "HELLO"

    def test_unmatched_brace(self, ev: Evaluator):
        with pytest.raises(SyntaxError, match="Unmatched"):
            ev.evaluate_template("{oops")


# ── evaluate_value ──────────────────────────────────────────────────────────


class TestEvaluateValue:

    def test_passthrough_number(self, ev: Evaluator):
        assert ev.evaluate_value(42) == 42

    def test_passthrough_list(self, ev: Evaluator):
        assert ev.evaluate_value([1, 2]) == [1, 2]

    def test_expression_string(self, ev: Evaluator):
        assert ev.evaluate_value("2 + 2") == 4

    def test_function_string(self, ev: Evaluator):
        assert ev.evaluate_value("UPPER('hello')") == "HELLO"

    def test_template_string(self, ev: Evaluator):
        result = ev.evaluate_value("result is {3 * 3}")
        assert result == "result is 9"

    def test_plain_string(self, ev: Evaluator):
        assert ev.evaluate_value("just plain text") == "just plain text"


# ── resolve_output_name ────────────────────────────────────────────────────


class TestResolveOutputName:

    def test_plain_name(self, ev: Evaluator):
        assert ev.resolve_output_name("report", {}) == "report"

    def test_placeholder_substitution(self, ev: Evaluator):
        result = ev.resolve_output_name("Invoice-{NUM}", {"NUM": 42})
        assert result == "Invoice-42"

    def test_multiple_placeholders(self, ev: Evaluator):
        result = ev.resolve_output_name("{A}-{B}", {"A": "x", "B": "y"})
        assert result == "x-y"

    def test_none_placeholder_becomes_empty(self, ev: Evaluator):
        result = ev.resolve_output_name("doc-{X}", {"X": None})
        assert result == "doc-"

    def test_expression_after_substitution(self, ev: Evaluator):
        result = ev.resolve_output_name(
            "report-{UPPER('draft')}",
            {},
        )
        assert result == "report-DRAFT"
