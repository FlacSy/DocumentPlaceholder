"""Tests for the tokenizer and parser."""

from __future__ import annotations

import pytest

from document_placeholder.parser import (
    BinaryOp,
    FunctionCall,
    Identifier,
    NumberLiteral,
    Parser,
    StringLiteral,
    Token,
    TokenType,
    Tokenizer,
    UnaryOp,
)

# ── Tokenizer ───────────────────────────────────────────────────────────────


class TestTokenizer:
    """Tokenizer unit tests."""

    def _types(self, text: str) -> list[str]:
        return [t.type for t in Tokenizer(text).tokens]

    def _values(self, text: str) -> list:
        return [t.value for t in Tokenizer(text).tokens]

    # -- literals -------------------------------------------------------------

    def test_integer(self):
        assert self._values("42") == [42, None]

    def test_float(self):
        assert self._values("3.14") == [3.14, None]

    def test_string_double(self):
        assert self._values('"hello"') == ["hello", None]

    def test_string_single(self):
        assert self._values("'world'") == ["world", None]

    def test_string_escape(self):
        assert self._values(r'"a\nb"') == ["a\nb", None]

    def test_string_escape_tab(self):
        assert self._values(r'"a\tb"') == ["a\tb", None]

    def test_unterminated_string(self):
        with pytest.raises(SyntaxError, match="Unterminated string"):
            Tokenizer('"oops')

    # -- identifiers ----------------------------------------------------------

    def test_identifier(self):
        assert self._values("foo_bar") == ["foo_bar", None]

    def test_identifier_with_digits(self):
        assert self._values("x2") == ["x2", None]

    # -- operators ------------------------------------------------------------

    def test_arithmetic_operators(self):
        types = self._types("+ - * / %")
        assert types == [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT,
            TokenType.EOF,
        ]

    def test_comparison_single_char(self):
        types = self._types("> <")
        assert types == [TokenType.GT, TokenType.LT, TokenType.EOF]

    def test_comparison_two_char(self):
        types = self._types(">= <= == !=")
        assert types == [
            TokenType.GTE,
            TokenType.LTE,
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.EOF,
        ]

    def test_two_char_priority_over_single(self):
        types = self._types(">=")
        assert types == [TokenType.GTE, TokenType.EOF]

    # -- parentheses and comma ------------------------------------------------

    def test_parens_comma(self):
        types = self._types("(a, b)")
        assert types == [
            TokenType.LPAREN,
            TokenType.IDENTIFIER,
            TokenType.COMMA,
            TokenType.IDENTIFIER,
            TokenType.RPAREN,
            TokenType.EOF,
        ]

    # -- whitespace -----------------------------------------------------------

    def test_whitespace_ignored(self):
        assert self._values("  42  ") == [42, None]

    # -- unexpected character -------------------------------------------------

    def test_unexpected_char(self):
        with pytest.raises(SyntaxError, match="Unexpected character"):
            Tokenizer("@")

    # -- consumed_all ---------------------------------------------------------

    def test_consumed_all_true(self):
        t = Tokenizer("42")
        assert t.consumed_all is True

    # -- complex expression ---------------------------------------------------

    def test_complex(self):
        types = self._types("FOO(1, 'a') + 3 >= 10")
        assert types == [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.STRING,
            TokenType.RPAREN,
            TokenType.PLUS,
            TokenType.NUMBER,
            TokenType.GTE,
            TokenType.NUMBER,
            TokenType.EOF,
        ]


# ── Parser ──────────────────────────────────────────────────────────────────


class TestParser:
    """Parser unit tests — verify AST structure."""

    def _parse(self, text: str):
        tokens = Tokenizer(text).tokens
        return Parser(tokens).parse()

    # -- literals -------------------------------------------------------------

    def test_number_literal(self):
        node = self._parse("42")
        assert isinstance(node, NumberLiteral)
        assert node.value == 42

    def test_float_literal(self):
        node = self._parse("3.14")
        assert isinstance(node, NumberLiteral)
        assert node.value == 3.14

    def test_string_literal(self):
        node = self._parse("'hello'")
        assert isinstance(node, StringLiteral)
        assert node.value == "hello"

    def test_identifier(self):
        node = self._parse("foo")
        assert isinstance(node, Identifier)
        assert node.name == "foo"

    # -- unary ----------------------------------------------------------------

    def test_unary_minus(self):
        node = self._parse("-5")
        assert isinstance(node, UnaryOp)
        assert node.op == "-"
        assert isinstance(node.operand, NumberLiteral)

    def test_double_unary_minus(self):
        node = self._parse("--5")
        assert isinstance(node, UnaryOp)
        assert isinstance(node.operand, UnaryOp)

    # -- binary arithmetic ----------------------------------------------------

    def test_addition(self):
        node = self._parse("1 + 2")
        assert isinstance(node, BinaryOp) and node.op == "+"

    def test_subtraction(self):
        node = self._parse("5 - 3")
        assert isinstance(node, BinaryOp) and node.op == "-"

    def test_multiplication(self):
        node = self._parse("2 * 3")
        assert isinstance(node, BinaryOp) and node.op == "*"

    def test_division(self):
        node = self._parse("10 / 2")
        assert isinstance(node, BinaryOp) and node.op == "/"

    def test_modulo(self):
        node = self._parse("10 % 3")
        assert isinstance(node, BinaryOp) and node.op == "%"

    # -- precedence -----------------------------------------------------------

    def test_mul_before_add(self):
        node = self._parse("1 + 2 * 3")
        assert isinstance(node, BinaryOp)
        assert node.op == "+"
        assert isinstance(node.right, BinaryOp)
        assert node.right.op == "*"

    def test_parentheses_override_precedence(self):
        node = self._parse("(1 + 2) * 3")
        assert isinstance(node, BinaryOp)
        assert node.op == "*"
        assert isinstance(node.left, BinaryOp)
        assert node.left.op == "+"

    # -- comparison -----------------------------------------------------------

    def test_gt(self):
        node = self._parse("5 > 3")
        assert isinstance(node, BinaryOp) and node.op == ">"

    def test_lt(self):
        node = self._parse("2 < 8")
        assert isinstance(node, BinaryOp) and node.op == "<"

    def test_gte(self):
        node = self._parse("5 >= 5")
        assert isinstance(node, BinaryOp) and node.op == ">="

    def test_lte(self):
        node = self._parse("3 <= 4")
        assert isinstance(node, BinaryOp) and node.op == "<="

    def test_eq(self):
        node = self._parse("1 == 1")
        assert isinstance(node, BinaryOp) and node.op == "=="

    def test_neq(self):
        node = self._parse("1 != 2")
        assert isinstance(node, BinaryOp) and node.op == "!="

    def test_comparison_lower_precedence_than_add(self):
        node = self._parse("1 + 2 > 3")
        assert isinstance(node, BinaryOp)
        assert node.op == ">"
        assert isinstance(node.left, BinaryOp)
        assert node.left.op == "+"

    # -- function calls -------------------------------------------------------

    def test_function_no_args(self):
        node = self._parse("FOO()")
        assert isinstance(node, FunctionCall)
        assert node.name == "FOO"
        assert node.args == []

    def test_function_single_arg(self):
        node = self._parse("FOO(42)")
        assert isinstance(node, FunctionCall)
        assert len(node.args) == 1

    def test_function_multiple_args(self):
        node = self._parse("FOO(1, 'a', bar)")
        assert isinstance(node, FunctionCall)
        assert len(node.args) == 3

    def test_nested_function_call(self):
        node = self._parse("FOO(BAR(1))")
        assert isinstance(node, FunctionCall)
        assert isinstance(node.args[0], FunctionCall)

    # -- error cases ----------------------------------------------------------

    def test_trailing_junk(self):
        with pytest.raises(SyntaxError, match="Unexpected token"):
            self._parse("42 42")

    def test_missing_rparen(self):
        with pytest.raises(SyntaxError, match="Expected RPAREN"):
            self._parse("FOO(1")

    def test_unexpected_token_primary(self):
        with pytest.raises(SyntaxError):
            self._parse(")")
