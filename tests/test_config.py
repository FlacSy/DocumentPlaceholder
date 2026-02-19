"""Tests for the YAML config loader."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from document_placeholder.config import Config


class TestConfigFromFile:

    def _write_yaml(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_load_simple(self):
        path = self._write_yaml("KEY: value\n")
        cfg = Config(path)
        assert cfg.placeholders == {"KEY": "value"}

    def test_empty_file(self):
        path = self._write_yaml("")
        cfg = Config(path)
        assert cfg.placeholders == {}

    def test_on_start_single(self):
        path = self._write_yaml("ON_START: expr1\n")
        cfg = Config(path)
        assert cfg.on_start == ["expr1"]
        assert cfg.placeholders == {}

    def test_on_start_list(self):
        path = self._write_yaml("ON_START:\n  - a\n  - b\n")
        cfg = Config(path)
        assert cfg.on_start == ["a", "b"]

    def test_on_end(self):
        path = self._write_yaml("ON_END:\n  - cleanup\n")
        cfg = Config(path)
        assert cfg.on_end == ["cleanup"]


class TestConfigFromString:

    def test_basic(self):
        cfg = Config.from_string("A: 1\nB: 2\n")
        assert cfg.placeholders == {"A": 1, "B": 2}

    def test_empty(self):
        cfg = Config.from_string("")
        assert cfg.placeholders == {}

    def test_with_special_keys(self):
        cfg = Config.from_string("ON_START: init\n" "KEY: value\n" "ON_END: cleanup\n")
        assert cfg.on_start == ["init"]
        assert cfg.on_end == ["cleanup"]
        assert cfg.placeholders == {"KEY": "value"}


class TestOutputSettings:

    def test_output_name(self):
        cfg = Config.from_string('OUTPUT_NAME: "report-{NUM}"\n')
        assert cfg.output_name == "report-{NUM}"

    def test_output_name_missing(self):
        cfg = Config.from_string("KEY: val\n")
        assert cfg.output_name is None

    def test_output_format_list(self):
        cfg = Config.from_string("OUTPUT_FORMAT:\n  - docx\n  - pdf\n")
        assert cfg.output_format == ["docx", "pdf"]

    def test_output_format_single(self):
        cfg = Config.from_string("OUTPUT_FORMAT: pdf\n")
        assert cfg.output_format == ["pdf"]

    def test_output_format_empty(self):
        cfg = Config.from_string("KEY: val\n")
        assert cfg.output_format == []

    def test_output_format_strips_dot(self):
        cfg = Config.from_string("OUTPUT_FORMAT: .pdf\n")
        assert cfg.output_format == ["pdf"]

    def test_output_format_lowercased(self):
        cfg = Config.from_string("OUTPUT_FORMAT: PDF\n")
        assert cfg.output_format == ["pdf"]


class TestSpecialKeysExcluded:

    def test_all_special_keys_excluded(self):
        cfg = Config.from_string(
            "ON_START: a\n"
            "ON_END: b\n"
            "OUTPUT_NAME: c\n"
            "OUTPUT_FORMAT: d\n"
            "MY_KEY: value\n"
        )
        assert list(cfg.placeholders.keys()) == ["MY_KEY"]
