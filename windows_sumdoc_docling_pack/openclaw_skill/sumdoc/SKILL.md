---
name: sumdoc
description: "Extract text from file/text using Docling runtime on Windows."
metadata: { "openclaw": { "emoji": "📄", "requires": { "bins": ["powershell"] }, "primaryEnv": "SUMDOC_DOCLING_HOME" } }
---

# /sumdoc - Docling text extraction (Windows)

Extract text from a file (pdf/docx/pptx/html/md/txt) or from raw text input.
Current mode is extraction only (no AI summarize model call).

## Rules

- Do not install packages during command execution.
- Do not use system-specific hardcoded paths.
- Always run the provided script command below.

## Usage

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" file "<ABSOLUTE_FILE_PATH>"
```

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" text "<RAW_TEXT>"
```

Optional flags:
- `--json` : return structured JSON
- `--max-chars 50000` : truncate long output

## Examples

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" file "D:\docs\abc.pdf"
```

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" text "Noi dung can parse."
```

## Runtime location

Set environment variable `SUMDOC_DOCLING_HOME` to the runtime folder copied from this package.
Example:

```powershell
setx SUMDOC_DOCLING_HOME "D:\sumdoc_docling_runtime"
```
