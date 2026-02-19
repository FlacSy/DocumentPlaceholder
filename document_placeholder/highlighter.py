"""Regex-based syntax highlighting for YAML configs and SQL."""

from __future__ import annotations

import re
import tkinter as tk

import customtkinter as ctk  # optional dependency (gui extra)

# ── colour palettes ────────────────────────────────────────────────────────

DARK = {
    "hl_key": "#7DCFFF",
    "hl_special_key": "#BB9AF7",
    "hl_string": "#9ECE6A",
    "hl_number": "#FF9E64",
    "hl_function": "#E0AF68",
    "hl_comment": "#565F89",
    "hl_brace": "#73DACA",
    "hl_list_marker": "#89DDFF",
    "hl_boolean": "#FF9E64",
    "hl_keyword": "#7AA2F7",
    "hl_operator": "#89DDFF",
}

LIGHT = {
    "hl_key": "#0550AE",
    "hl_special_key": "#8250DF",
    "hl_string": "#116329",
    "hl_number": "#CF222E",
    "hl_function": "#953800",
    "hl_comment": "#6E7781",
    "hl_brace": "#0550AE",
    "hl_list_marker": "#0550AE",
    "hl_boolean": "#CF222E",
    "hl_keyword": "#CF222E",
    "hl_operator": "#0550AE",
}


# ── base class ─────────────────────────────────────────────────────────────


class _Highlighter:
    """Apply regex-based syntax highlighting to a :class:`tkinter.Text` widget.

    Subclasses define ``PATTERNS``, ``TAGS`` and ``PRIORITY``.
    """

    # (tag_name, regex, group_to_highlight, re_flags)
    PATTERNS: list[tuple[str, str, int, int]] = []
    TAGS: list[str] = []
    PRIORITY: list[str] = []  # lowest → highest visual priority

    def __init__(self, text_widget: tk.Text) -> None:
        self._tw = text_widget
        self._mode: str | None = None

    def apply(self) -> None:
        mode = ctk.get_appearance_mode()
        if mode != self._mode:
            self._mode = mode
            self._configure_tags()

        text = self._tw.get("1.0", "end-1c")

        for tag in self.TAGS:
            self._tw.tag_remove(tag, "1.0", "end")

        for tag, pattern, group, flags in self.PATTERNS:
            for m in re.finditer(pattern, text, flags):
                s = f"1.0+{m.start(group)}c"
                e = f"1.0+{m.end(group)}c"
                self._tw.tag_add(tag, s, e)

        for tag in self.PRIORITY:
            self._tw.tag_raise(tag)

    def _configure_tags(self) -> None:
        colors = DARK if self._mode == "Dark" else LIGHT
        for tag in self.TAGS:
            if tag in colors:
                self._tw.tag_configure(tag, foreground=colors[tag])


# ── YAML / config highlighter ─────────────────────────────────────────────


class YamlHighlighter(_Highlighter):
    """Highlights standard YAML *and* custom constructs:
    ``SQL(...)``, ``CURRENT_DATE_NUM(...)``, ``{expression}``, etc.
    """

    TAGS = [
        "hl_number",
        "hl_boolean",
        "hl_list_marker",
        "hl_key",
        "hl_comment",
        "hl_special_key",
        "hl_string",
        "hl_function",
        "hl_brace",
    ]
    PRIORITY = TAGS

    _SPECIAL = "ON_START|ON_END|OUTPUT_NAME|OUTPUT_FORMAT"

    PATTERNS = [
        # low-priority first ─────────────────────────────────────────
        ("hl_number", r"\b\d+(?:\.\d+)?\b", 0, 0),
        ("hl_boolean", r"\b(?:true|false|null|yes|no)\b", 0, re.IGNORECASE),
        ("hl_list_marker", r"^([ ]*-)(?=\s)", 1, re.MULTILINE),
        ("hl_key", r"^[ ]*([A-Za-z_][\w]*)(?=\s*:)", 1, re.MULTILINE),
        ("hl_comment", r"(?:(?<=\s)|^)#.*$", 0, re.MULTILINE),
        ("hl_special_key", rf"^[ ]*({_SPECIAL})(?=\s*:)", 1, re.MULTILINE),
        # strings override comment colour inside quotes ──────────────
        ("hl_string", r'"(?:[^"\\]|\\.)*"', 0, 0),
        ("hl_string", r"'(?:[^'\\]|\\.)*'", 0, 0),
        # custom constructs on top ───────────────────────────────────
        ("hl_function", r"\b([A-Z][A-Z_0-9]{2,})(?=\s*\()", 1, 0),
        ("hl_brace", r"[{}]", 0, 0),
    ]


# ── SQL highlighter ───────────────────────────────────────────────────────


class SqlHighlighter(_Highlighter):

    TAGS = [
        "hl_operator",
        "hl_number",
        "hl_keyword",
        "hl_comment",
        "hl_string",
        "hl_function",
    ]
    PRIORITY = TAGS

    _KW = (
        "SELECT|FROM|WHERE|AND|OR|NOT|IN|IS|NULL|AS|ON|JOIN|LEFT|RIGHT|"
        "INNER|OUTER|GROUP|BY|ORDER|HAVING|LIMIT|OFFSET|UNION|ALL|"
        "DISTINCT|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|"
        "DROP|ALTER|ADD|COLUMN|INDEX|IF|EXISTS|PRIMARY|KEY|FOREIGN|"
        "REFERENCES|DEFAULT|CONSTRAINT|INTEGER|TEXT|REAL|BLOB|"
        "AUTOINCREMENT|PRAGMA|IGNORE|REPLACE|BEGIN|COMMIT|ROLLBACK|"
        "TRANSACTION|WITH|ASC|DESC|BETWEEN|LIKE|CASE|WHEN|THEN|ELSE|"
        "END|CHECK|UNIQUE|BOOLEAN|DATE|VARCHAR|CHAR|TIMESTAMP|ROWID|"
        "ABORT|CASCADE|EACH|EXCEPT|GLOB|INSTEAD|INTERSECT|ISNULL|"
        "NOTNULL|OF|PLAN|QUERY|RAISE|RECURSIVE|RELEASE|RENAME|"
        "SAVEPOINT|TEMP|TRIGGER|VACUUM|VIEW|VIRTUAL|WITHOUT"
    )

    _FN = (
        "COUNT|SUM|AVG|MIN|MAX|COALESCE|LENGTH|SUBSTR|SUBSTRING|"
        "UPPER|LOWER|TRIM|ABS|ROUND|TYPEOF|IFNULL|NULLIF|TOTAL|"
        "GROUP_CONCAT|PRINTF|INSTR|UNICODE|HEX|ZEROBLOB|RANDOM|"
        "CHANGES|LAST_INSERT_ROWID|TOTAL_CHANGES|QUOTE"
    )

    PATTERNS = [
        ("hl_operator", r"[<>=!]+|[+\-*/%|&~]", 0, 0),
        ("hl_number", r"\b\d+(?:\.\d+)?\b", 0, 0),
        ("hl_keyword", rf"\b({_KW})\b", 1, re.IGNORECASE),
        ("hl_comment", r"--.*$", 0, re.MULTILINE),
        ("hl_string", r"'(?:[^'\\]|\\.)*'", 0, 0),
        ("hl_string", r'"(?:[^"\\]|\\.)*"', 0, 0),
        ("hl_function", rf"\b({_FN})(?=\s*\()", 1, re.IGNORECASE),
    ]
