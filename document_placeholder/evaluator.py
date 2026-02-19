"""Evaluate parsed expressions and template strings with ``{expr}`` interpolation."""

from __future__ import annotations

from typing import Any

from document_placeholder.functions import FunctionRegistry
from document_placeholder.parser import (
    BinaryOp,
    FunctionCall,
    Identifier,
    NumberLiteral,
    Parser,
    StringLiteral,
    Tokenizer,
    UnaryOp,
)


class Evaluator:
    """Evaluate config values: literals, expressions, and template strings."""

    # -- AST evaluation -------------------------------------------------------

    def evaluate(self, node: Any) -> Any:
        if isinstance(node, NumberLiteral):
            return node.value

        if isinstance(node, StringLiteral):
            return node.value

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, FunctionCall):
            args = [self.evaluate(arg) for arg in node.args]
            return FunctionRegistry.call(node.name, args)

        if isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == "+":
                return left + right
            if node.op == "-":
                return left - right
            if node.op == "*":
                return left * right
            if node.op == "/":
                return left / right
            if node.op == "%":
                return left % right
            if node.op == ">":
                return left > right
            if node.op == "<":
                return left < right
            if node.op == ">=":
                return left >= right
            if node.op == "<=":
                return left <= right
            if node.op == "==":
                return left == right
            if node.op == "!=":
                return left != right

        if isinstance(node, UnaryOp):
            operand = self.evaluate(node.operand)
            if node.op == "-":
                return -operand

        raise ValueError(f"Unknown AST node: {type(node).__name__}")

    # -- high-level helpers ---------------------------------------------------

    def evaluate_expression(self, text: str) -> Any:
        """Parse *text* as a single expression and return its value."""
        tokenizer = Tokenizer(text)
        parser = Parser(tokenizer.tokens)
        return self.evaluate(parser.parse())

    def evaluate_template(self, text: str) -> str:
        """Replace every ``{expression}`` in *text* with its evaluated value."""
        result: list[str] = []
        i = 0
        while i < len(text):
            if text[i] == "{":
                end = self._find_closing_brace(text, i)
                expr_text = text[i + 1 : end]
                value = self.evaluate_expression(expr_text)
                result.append(str(value) if value is not None else "")
                i = end + 1
            else:
                result.append(text[i])
                i += 1
        return "".join(result)

    def evaluate_value(self, value: Any) -> Any:
        """Evaluate a raw config value (number, expression string, or template)."""
        if not isinstance(value, str):
            return value

        # 1) Try to interpret the whole string as an expression.
        try:
            return self.evaluate_expression(value)
        except SyntaxError:
            pass

        # 2) If it contains {…}, treat as template with interpolation.
        if "{" in value:
            return self.evaluate_template(value)

        # 3) Plain literal string.
        return value

    # -- output name resolution -----------------------------------------------

    def resolve_output_name(
        self,
        raw_name: str,
        values: dict[str, object],
    ) -> str:
        """Resolve ``OUTPUT_NAME``: substitute ``{KEY}`` placeholders, then
        evaluate any remaining ``{expression}`` patterns."""
        result = str(raw_name)
        for key, value in values.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(
                    placeholder, str(value) if value is not None else ""
                )
        # Only evaluate remaining {expr} patterns — never parse the whole
        # string as a single expression (it may contain literal dashes, etc.)
        if "{" in result:
            return self.evaluate_template(result)
        return result

    # -- internals ------------------------------------------------------------

    @staticmethod
    def _find_closing_brace(text: str, start: int) -> int:
        """Return the index of the ``}`` matching the ``{`` at *start*."""
        depth = 1
        i = start + 1
        in_string: str | None = None
        while i < len(text):
            ch = text[i]
            if in_string:
                if ch == "\\" and i + 1 < len(text):
                    i += 2
                    continue
                if ch == in_string:
                    in_string = None
            else:
                if ch in ('"', "'"):
                    in_string = ch
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return i
            i += 1
        raise SyntaxError(f"Unmatched '{{' at position {start}")
