"""Load and expose a YAML config with lifecycle hooks and placeholder mappings."""

from __future__ import annotations

from pathlib import Path

import yaml

SPECIAL_KEYS = {"ON_START", "ON_END", "OUTPUT_NAME", "OUTPUT_FORMAT"}


class Config:
    def __init__(self, path: str | Path) -> None:
        with open(path, "r", encoding="utf-8") as fh:
            self.data: dict = yaml.safe_load(fh) or {}

    @classmethod
    def from_string(cls, text: str) -> Config:
        """Create a Config directly from a YAML string (no file needed)."""
        obj = cls.__new__(cls)
        obj.data = yaml.safe_load(text) or {}
        return obj

    # -- lifecycle hooks ------------------------------------------------------

    @property
    def on_start(self) -> list:
        return self._as_list(self.data.get("ON_START"))

    @property
    def on_end(self) -> list:
        return self._as_list(self.data.get("ON_END"))

    # -- output settings ------------------------------------------------------

    @property
    def output_name(self) -> str | None:
        """Raw OUTPUT_NAME value (may contain ``{KEY}`` references)."""
        return self.data.get("OUTPUT_NAME")

    @property
    def output_format(self) -> list[str]:
        """List of requested output formats, e.g. ``["docx", "pdf"]``."""
        raw = self._as_list(self.data.get("OUTPUT_FORMAT"))
        return [str(f).lower().strip(".") for f in raw]

    # -- placeholder map ------------------------------------------------------

    @property
    def placeholders(self) -> dict:
        return {k: v for k, v in self.data.items() if k not in SPECIAL_KEYS}

    # -- helpers --------------------------------------------------------------

    @staticmethod
    def _as_list(value) -> list:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]
