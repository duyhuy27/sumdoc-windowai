#!/usr/bin/env python3
"""
Minimal sumdoc runtime:
- Parse file/text input
- Use Docling for non-txt formats
- Normalize and print text output
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".pptx", ".html", ".htm", ".md"}
DEFAULT_MAX_CHARS = 50_000
DEFAULT_SOFT_LIMIT = 15_000


def parse_document(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if ext in {".txt", ".md"}:
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"File is not valid UTF-8 text: {file_path.name}") from exc
        if not text.strip():
            raise ValueError(f"File is empty: {file_path.name}")
        return text

    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise RuntimeError("Docling is not installed. Run: pip install docling") from exc

    converter = DocumentConverter()
    result = converter.convert(str(file_path))
    text = result.document.export_to_markdown()
    if not text.strip():
        raise RuntimeError("Docling returned empty content")
    return text


def normalize_text(
    text: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    soft_limit: int = DEFAULT_SOFT_LIMIT,
) -> str:
    normalized = text.strip()
    if not normalized:
        raise ValueError("Document is empty after parsing.")

    normalized = re.sub(r"\r\n", "\n", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    if len(normalized) > max_chars:
        normalized = normalized[:max_chars] + "\n\n[... truncated ...]"
    elif len(normalized) > soft_limit:
        print(
            f"[WARN] Text is fairly long ({len(normalized):,} chars).",
            file=sys.stderr,
        )
    return normalized


def run(file_path: str | None, raw_text: str | None, max_chars: int, as_json: bool) -> int:
    if file_path:
        raw = parse_document(file_path)
        source = file_path
    elif raw_text:
        raw = raw_text
        source = "raw_text"
    else:
        raise ValueError("Provide --file or --text.")

    normalized = normalize_text(raw, max_chars=max_chars)
    if as_json:
        payload = {
            "ok": True,
            "source": source,
            "chars": len(normalized),
            "text": normalized,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(normalized)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text with Docling for OpenClaw sumdoc.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", help="Path to input file")
    group.add_argument("--text", "-t", help="Raw text input")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Hard output limit (default: {DEFAULT_MAX_CHARS})",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    try:
        code = run(args.file, args.text, args.max_chars, args.json)
        sys.exit(code)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
