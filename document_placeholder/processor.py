"""Read a Word template, replace ``{PLACEHOLDER}`` markers, and save."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document


class DocumentProcessor:
    def __init__(self, template_path: str | Path) -> None:
        self.doc = Document(str(template_path))

    # -- public API -----------------------------------------------------------

    def replace_placeholders(self, values: dict[str, Any]) -> None:
        """Substitute every ``{KEY}`` found in paragraphs, tables, headers, and footers."""

        for paragraph in self.doc.paragraphs:
            self._replace_in_paragraph(paragraph, values)

        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_in_paragraph(paragraph, values)

        for section in self.doc.sections:
            for paragraph in section.header.paragraphs:
                self._replace_in_paragraph(paragraph, values)
            for paragraph in section.footer.paragraphs:
                self._replace_in_paragraph(paragraph, values)

    def save(self, output_path: str | Path) -> None:
        self.doc.save(str(output_path))

    # -- internals ------------------------------------------------------------

    @staticmethod
    def _replace_in_paragraph(paragraph, values: dict[str, Any]) -> None:
        runs = paragraph.runs
        if not runs:
            return

        full_text = "".join(run.text for run in runs)

        new_text = full_text
        for key, value in values.items():
            placeholder = "{" + key + "}"
            if placeholder in new_text:
                display = str(value) if value is not None else ""
                new_text = new_text.replace(placeholder, display)

        if new_text != full_text:
            runs[0].text = new_text
            for run in runs[1:]:
                run.text = ""
