#!/usr/bin/env python3
"""
sumdoc_docling.py

Flow:
  1) Parse input file/text with Docling (or direct txt/md read)
  2) Normalize text
  3) Call local summarize API: http://localhost:8000/summarize
  4) Print summary (or full JSON with --json)

Detailed forensic logs:
  - stdout stage logs
  - jsonl diagnostic log file
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import requests

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".pptx", ".html", ".htm", ".md"}
DEFAULT_MAX_CHARS = 50_000
DEFAULT_SOFT_LIMIT = 15_000
DEFAULT_API_URL = "http://localhost:8000/summarize"
DEFAULT_MAX_NEW_TOKEN = 50
DEFAULT_TIMEOUT_S = 600


RUN_ID = os.environ.get("SUMDOC_RUN_ID", uuid4().hex[:12])
RUN_START = time.monotonic()
DEFAULT_LOG_FILE = Path(os.environ.get("SUMDOC_LOG_FILE", f"sumdoc_runtime_{RUN_ID}.jsonl"))


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _diag_log(event: str, log_file: Path, **fields) -> None:
    payload = {
        "ts": _now_iso(),
        "run_id": RUN_ID,
        "elapsed_s": round(time.monotonic() - RUN_START, 3),
        "event": event,
    }
    payload.update(fields)
    line = json.dumps(payload, ensure_ascii=False)
    print(f"[LOG] {line}")
    try:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        print("[WARN] Could not write diagnostic log file.", file=sys.stderr)


def parse_document(path: str, log_file: Path) -> str:
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

    _diag_log("parse_start", log_file, file_path=str(file_path), extension=ext)
    t0 = time.monotonic()

    if ext in {".txt", ".md"}:
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"File is not valid UTF-8 text: {file_path.name}") from exc
        if not text.strip():
            raise ValueError(f"File is empty: {file_path.name}")
        _diag_log(
            "parse_done",
            log_file,
            parser="direct_read",
            raw_chars=len(text),
            elapsed_s=round(time.monotonic() - t0, 3),
        )
        return text

    try:
        from docling.document_converter import DocumentConverter  # pyright: ignore[reportMissingImports]
    except ImportError as exc:
        raise RuntimeError("Docling is not installed. Run: pip install docling") from exc

    converter = DocumentConverter()
    result = converter.convert(str(file_path))
    text = result.document.export_to_markdown()
    if not text.strip():
        raise RuntimeError("Docling returned empty content")
    _diag_log(
        "parse_done",
        log_file,
        parser="docling",
        raw_chars=len(text),
        elapsed_s=round(time.monotonic() - t0, 3),
    )
    return text


def normalize_text(
    text: str,
    log_file: Path,
    max_chars: int = DEFAULT_MAX_CHARS,
    soft_limit: int = DEFAULT_SOFT_LIMIT,
) -> str:
    t0 = time.monotonic()
    normalized = text.strip()
    if not normalized:
        raise ValueError("Document is empty after parsing.")

    normalized = re.sub(r"\r\n", "\n", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    truncated = False
    if len(normalized) > max_chars:
        normalized = normalized[:max_chars] + "\n\n[... truncated ...]"
        truncated = True
    elif len(normalized) > soft_limit:
        print(f"[WARN] Text is fairly long ({len(normalized):,} chars).", file=sys.stderr)

    _diag_log(
        "normalize_done",
        log_file,
        normalized_chars=len(normalized),
        truncated=truncated,
        max_chars=max_chars,
        elapsed_s=round(time.monotonic() - t0, 3),
    )
    return normalized


def call_summarize_api(
    text: str,
    api_url: str,
    max_new_token: int,
    timeout_s: int,
    log_file: Path,
) -> dict:
    payload = {
        "text": text,
        "max_new_token": max_new_token,
    }

    _diag_log(
        "api_call_start",
        log_file,
        api_url=api_url,
        timeout_s=timeout_s,
        max_new_token=max_new_token,
        input_chars=len(text),
    )
    t0 = time.monotonic()
    try:
        resp = requests.post(api_url, json=payload, timeout=timeout_s)
        elapsed = round((time.monotonic() - t0) * 1000, 1)
        _diag_log(
            "api_call_response",
            log_file,
            status_code=resp.status_code,
            elapsed_ms=elapsed,
            response_preview=resp.text[:300],
        )
    except requests.exceptions.Timeout as exc:
        raise TimeoutError(f"Summarize API timeout after {timeout_s}s: {api_url}") from exc
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError(f"Cannot connect summarize API: {api_url}") from exc

    if resp.status_code != 200:
        raise RuntimeError(f"Summarize API HTTP {resp.status_code}: {resp.text[:300]}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError(f"Summarize API returned invalid JSON: {resp.text[:300]}") from exc

    if "summary" not in data:
        raise RuntimeError(f"Summarize response missing 'summary'. Keys: {list(data.keys())}")
    return data


def _build_output(source: str, normalized: str, summary_response: dict) -> dict:
    output_tokens = summary_response.get("ouput_tokens")
    if output_tokens is None:
        output_tokens = summary_response.get("output_tokens")
    return {
        "ok": True,
        "source": source,
        "input_chars_local": len(normalized),
        "summary": str(summary_response.get("summary", "")),
        "input_chars": summary_response.get("input_chars"),
        "ouput_tokens": output_tokens,
        "latency_ms": summary_response.get("latency_ms"),
        "num_chunks": summary_response.get("num_chunks"),
        "raw_api_response": summary_response,
    }


def run(
    file_path: str | None,
    raw_text: str | None,
    max_chars: int,
    as_json: bool,
    api_url: str,
    max_new_token: int,
    timeout_s: int,
    extract_only: bool,
    log_file: Path,
) -> int:
    _diag_log(
        "run_start",
        log_file,
        mode="file" if file_path else "text",
        api_url=api_url,
        max_new_token=max_new_token,
        timeout_s=timeout_s,
        extract_only=extract_only,
        log_file_path=str(log_file),
    )

    if file_path:
        raw = parse_document(file_path, log_file=log_file)
        source = file_path
    elif raw_text:
        raw = raw_text
        source = "raw_text"
        _diag_log("parse_done", log_file, parser="raw_text", raw_chars=len(raw))
    else:
        raise ValueError("Provide --file or --text.")

    normalized = normalize_text(raw, max_chars=max_chars, log_file=log_file)

    if extract_only:
        _diag_log("extract_only_done", log_file, output_chars=len(normalized))
        if as_json:
            print(
                json.dumps(
                    {
                        "ok": True,
                        "mode": "extract_only",
                        "source": source,
                        "chars": len(normalized),
                        "text": normalized,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(normalized)
        return 0

    summary_response = call_summarize_api(
        text=normalized,
        api_url=api_url,
        max_new_token=max_new_token,
        timeout_s=timeout_s,
        log_file=log_file,
    )
    output = _build_output(source=source, normalized=normalized, summary_response=summary_response)
    _diag_log(
        "run_done",
        log_file,
        summary_chars=len(output["summary"]),
        latency_ms=output.get("latency_ms"),
    )

    if as_json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # Keep stdout concise for OpenClaw chat.
        print(output["summary"])
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Docling + local summarize API runtime for OpenClaw.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", help="Path to input file")
    group.add_argument("--text", "-t", help="Raw text input")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Hard input text limit before summarize (default: {DEFAULT_MAX_CHARS})",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("SUMDOC_SUMMARIZE_API_URL", DEFAULT_API_URL),
        help=f"Summarize API URL (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--max-new-token",
        type=int,
        default=int(os.environ.get("SUMDOC_MAX_NEW_TOKEN", str(DEFAULT_MAX_NEW_TOKEN))),
        help=f"max_new_token sent to summarize API (default: {DEFAULT_MAX_NEW_TOKEN})",
    )
    parser.add_argument(
        "--timeout-s",
        type=int,
        default=int(os.environ.get("SUMDOC_API_TIMEOUT_S", str(DEFAULT_TIMEOUT_S))),
        help=f"HTTP timeout in seconds (default: {DEFAULT_TIMEOUT_S})",
    )
    parser.add_argument(
        "--log-file",
        default=str(DEFAULT_LOG_FILE),
        help="Path to diagnostic JSONL log file",
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Skip summarize API and output normalized text only (debug mode)",
    )
    parser.add_argument("--json", action="store_true", help="Print structured JSON output")
    args = parser.parse_args()

    log_file = Path(args.log_file)

    try:
        code = run(
            file_path=args.file,
            raw_text=args.text,
            max_chars=args.max_chars,
            as_json=args.json,
            api_url=args.api_url,
            max_new_token=args.max_new_token,
            timeout_s=args.timeout_s,
            extract_only=args.extract_only,
            log_file=log_file,
        )
        sys.exit(code)
    except Exception as exc:
        _diag_log(
            "run_error",
            log_file,
            error=str(exc),
            error_type=type(exc).__name__,
            traceback=traceback.format_exc(),
        )
        print(f"[ERROR] {exc}", file=sys.stderr)
        print(f"[ERROR] See log file: {log_file}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
