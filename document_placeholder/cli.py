"""Command-line interface for DocumentPlaceholder."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import document_placeholder.functions.date  # noqa: F401 — register functions
import document_placeholder.functions.logic  # noqa: F401
import document_placeholder.functions.math  # noqa: F401
import document_placeholder.functions.string  # noqa: F401
import document_placeholder.functions.sql as sql_mod
from document_placeholder.config import Config
from document_placeholder.evaluator import Evaluator
from document_placeholder.exporter import export_document
from document_placeholder.processor import DocumentProcessor


def main() -> None:
    """Entry point for the ``docplaceholder`` console command."""
    parser = argparse.ArgumentParser(
        description="DocumentPlaceholder — fill Word templates using YAML configs",
    )
    parser.add_argument(
        "-c",
        "--config",
        default="template.yaml",
        help="YAML config path (default: template.yaml)",
    )
    parser.add_argument(
        "-t",
        "--template",
        default="template.docx",
        help="Word template path (default: template.docx)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output.docx",
        help="Output file path (default: output.docx)",
    )
    parser.add_argument(
        "--db",
        default="data.db",
        help="SQLite database path (default: data.db)",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__import__('document_placeholder').__version__}",
    )
    args = parser.parse_args()

    sql_mod.init(args.db)

    try:
        config = Config(args.config)
        evaluator = Evaluator()

        for expr in config.on_start:
            evaluator.evaluate_value(expr)

        values: dict[str, object] = {}
        for key, raw in config.placeholders.items():
            values[key] = evaluator.evaluate_value(raw)
            print(f"  {key} = {values[key]}")

        processor = DocumentProcessor(args.template)
        processor.replace_placeholders(values)

        output_arg = Path(args.output)
        output_dir = output_arg.parent or Path(".")

        if config.output_name:
            base_name = evaluator.resolve_output_name(config.output_name, values)
        else:
            base_name = output_arg.stem

        formats = config.output_format
        if not formats:
            ext = output_arg.suffix.lstrip(".").lower()
            formats = [ext if ext else "docx"]

        print(f"\n  Output: {base_name} [{', '.join(formats)}]")

        docx_path = output_dir / f"{base_name}.docx"
        processor.save(str(docx_path))

        generated: list[Path] = []
        for fmt in formats:
            if fmt == "docx":
                generated.append(docx_path)
            else:
                target = output_dir / f"{base_name}.{fmt}"
                export_document(str(docx_path), str(target))
                generated.append(target)

        if "docx" not in formats:
            docx_path.unlink(missing_ok=True)

        for expr in config.on_end:
            evaluator.evaluate_value(expr)

        for g in generated:
            print(f"  -> {g}")

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        sql_mod.close()


if __name__ == "__main__":
    main()
