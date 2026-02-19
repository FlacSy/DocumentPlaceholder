"""Tokenizer and recursive-descent parser for config expressions.

Grammar
-------
expression     = comparison
comparison     = additive (('>' | '<' | '>=' | '<=' | '==' | '!=') additive)?
additive       = multiplicative (('+' | '-') multiplicative)*
multiplicative = unary (('*' | '/' | '%') unary)*
unary          = '-' unary | primary
primary        = NUMBER | STRING | identifier_or_call | '(' expression ')'
identifier_or_call = IDENTIFIER ( '(' args? ')' )?
args           = expression (',' expression)*
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------


class TokenType:
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA = "COMMA"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    PERCENT = "PERCENT"
    GT = "GT"
    LT = "LT"
    GTE = "GTE"
    LTE = "LTE"
    EQ = "EQ"
    NEQ = "NEQ"
    EOF = "EOF"


@dataclass
class Token:
    type: str
    value: Any
    pos: int


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------


class Tokenizer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.tokens: list[Token] = []
        self._tokenize()

    # -- public helpers -------------------------------------------------------

    @property
    def consumed_all(self) -> bool:
        """True when every character was consumed (no trailing junk)."""
        return self.pos >= len(self.text) or self.text[self.pos :].strip() == ""

    # -- internals ------------------------------------------------------------

    def _tokenize(self) -> None:
        while self.pos < len(self.text):
            self._skip_whitespace()
            if self.pos >= len(self.text):
                break

            ch = self.text[self.pos]

            # Two-character operators (must be checked first)
            two = self.text[self.pos : self.pos + 2]
            two_char: dict[str, str] = {
                ">=": TokenType.GTE,
                "<=": TokenType.LTE,
                "==": TokenType.EQ,
                "!=": TokenType.NEQ,
            }
            if two in two_char:
                self.tokens.append(Token(two_char[two], two, self.pos))
                self.pos += 2
                continue

            simple: dict[str, str] = {
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                ",": TokenType.COMMA,
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "%": TokenType.PERCENT,
                ">": TokenType.GT,
                "<": TokenType.LT,
            }

            if ch in simple:
                self.tokens.append(Token(simple[ch], ch, self.pos))
                self.pos += 1
            elif ch in ('"', "'"):
                self._read_string(ch)
            elif ch.isdigit():
                self._read_number()
            elif ch.isalpha() or ch == "_":
                self._read_identifier()
            else:
                raise SyntaxError(f"Unexpected character '{ch}' at position {self.pos}")

        self.tokens.append(Token(TokenType.EOF, None, self.pos))

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def _read_string(self, quote: str) -> None:
        start = self.pos
        self.pos += 1
        chars: list[str] = []
        escape_map = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\"}
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch == "\\" and self.pos + 1 < len(self.text):
                self.pos += 1
                chars.append(escape_map.get(self.text[self.pos], self.text[self.pos]))
            elif ch == quote:
                self.pos += 1
                self.tokens.append(Token(TokenType.STRING, "".join(chars), start))
                return
            else:
                chars.append(ch)
            self.pos += 1
        raise SyntaxError(f"Unterminated string starting at position {start}")

    def _read_number(self) -> None:
        start = self.pos
        has_dot = False
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch.isdigit():
                self.pos += 1
            elif ch == "." and not has_dot:
                has_dot = True
                self.pos += 1
            else:
                break
        text = self.text[start : self.pos]
        value: int | float = float(text) if has_dot else int(text)
        self.tokens.append(Token(TokenType.NUMBER, value, start))

    def _read_identifier(self) -> None:
        start = self.pos
        while self.pos < len(self.text) and (
            self.text[self.pos].isalnum() or self.text[self.pos] == "_"
        ):
            self.pos += 1
        name = self.text[start : self.pos]
        self.tokens.append(Token(TokenType.IDENTIFIER, name, start))


# ---------------------------------------------------------------------------
# AST nodes
# ---------------------------------------------------------------------------


@dataclass
class NumberLiteral:
    value: int | float


@dataclass
class StringLiteral:
    value: str


@dataclass
class Identifier:
    name: str


@dataclass
class FunctionCall:
    name: str
    args: list[Any]


@dataclass
class BinaryOp:
    op: str
    left: Any
    right: Any


@dataclass
class UnaryOp:
    op: str
    operand: Any


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _eat(self, token_type: str) -> Token:
        tok = self._current()
        if tok.type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, got {tok.type} at position {tok.pos}"
            )
        self.pos += 1
        return tok

    # -- entry point ----------------------------------------------------------

    def parse(self) -> Any:
        node = self._expression()
        if self._current().type != TokenType.EOF:
            raise SyntaxError(
                f"Unexpected token '{self._current().value}' "
                f"at position {self._current().pos}"
            )
        return node

    # -- grammar rules --------------------------------------------------------

    def _expression(self) -> Any:
        return self._comparison()

    def _comparison(self) -> Any:
        left = self._additive()
        cmp_ops = (
            TokenType.GT,
            TokenType.LT,
            TokenType.GTE,
            TokenType.LTE,
            TokenType.EQ,
            TokenType.NEQ,
        )
        if self._current().type in cmp_ops:
            op = self._current().value
            self.pos += 1
            right = self._additive()
            left = BinaryOp(op, left, right)
        return left

    def _additive(self) -> Any:
        left = self._multiplicative()
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self._current().value
            self.pos += 1
            right = self._multiplicative()
            left = BinaryOp(op, left, right)
        return left

    def _multiplicative(self) -> Any:
        left = self._unary()
        while self._current().type in (
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT,
        ):
            op = self._current().value
            self.pos += 1
            right = self._unary()
            left = BinaryOp(op, left, right)
        return left

    def _unary(self) -> Any:
        if self._current().type == TokenType.MINUS:
            self.pos += 1
            operand = self._unary()
            return UnaryOp("-", operand)
        return self._primary()

    def _primary(self) -> Any:
        tok = self._current()

        if tok.type == TokenType.NUMBER:
            self.pos += 1
            return NumberLiteral(tok.value)

        if tok.type == TokenType.STRING:
            self.pos += 1
            return StringLiteral(tok.value)

        if tok.type == TokenType.IDENTIFIER:
            self.pos += 1
            if self._current().type == TokenType.LPAREN:
                self.pos += 1  # skip '('
                args: list[Any] = []
                if self._current().type != TokenType.RPAREN:
                    args.append(self._expression())
                    while self._current().type == TokenType.COMMA:
                        self.pos += 1  # skip ','
                        args.append(self._expression())
                self._eat(TokenType.RPAREN)
                return FunctionCall(tok.value, args)
            return Identifier(tok.value)

        if tok.type == TokenType.LPAREN:
            self.pos += 1
            expr = self._expression()
            self._eat(TokenType.RPAREN)
            return expr

        raise SyntaxError(
            f"Unexpected token '{tok.value}' ({tok.type}) at position {tok.pos}"
        )
