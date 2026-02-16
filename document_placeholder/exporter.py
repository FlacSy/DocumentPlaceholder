"""Export a .docx file to other formats (currently PDF via LibreOffice)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def export_document(input_path: str | Path, output_path: str | Path) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)
    ext = output_path.suffix.lower()

    if ext == ".docx":
        shutil.copy2(input_path, output_path)
    elif ext == ".pdf":
        _convert_with_libreoffice(input_path, output_path)
    else:
        raise ValueError(f"Unsupported output format: {ext}")


def _convert_with_libreoffice(input_path: Path, output_path: Path) -> None:
    output_dir = output_path.parent or Path(".")
    result = subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(input_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed:\n{result.stderr}")

    converted = output_dir / input_path.with_suffix(".pdf").name
    if converted.resolve() != output_path.resolve():
        shutil.move(str(converted), str(output_path))
