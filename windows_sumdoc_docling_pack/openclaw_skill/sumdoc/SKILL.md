---
name: sumdoc
description: "Summarize file/text via Docling + local API on Windows."
metadata: { "openclaw": { "emoji": "📄", "requires": { "bins": ["powershell"] }, "primaryEnv": "SUMDOC_DOCLING_HOME" } }
---

# /sumdoc - Docling + Local Summarize API (Windows)

Summarize from:
- file input (pdf/docx/pptx/html/md/txt), parsed by Docling
- raw text input

Default summarize API:
- `http://localhost:8000/summarize`
- payload: `{ "text": "<normalized_text>", "max_new_token": 50 }`

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
- `--max-chars 50000` : truncate long parsed text before summarize
- `--max-new-token 50` : pass to summarize API
- `--timeout-s 600` : HTTP timeout
- `--extract-only` : debug mode (skip summarize API, output parsed text)

## Examples

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" file "D:\docs\abc.pdf"
```

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" text "Noi dung can parse."
```

Use custom API URL:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" text "abc" --api-url "http://localhost:8000/summarize"
```

## Runtime location

Set environment variable `SUMDOC_DOCLING_HOME` to the runtime folder copied from this package.
Example:

```powershell
setx SUMDOC_DOCLING_HOME "D:\sumdoc_docling_runtime"
```

Optional env:

```powershell
setx SUMDOC_SUMMARIZE_API_URL "http://localhost:8000/summarize"
setx SUMDOC_MAX_NEW_TOKEN "50"
setx SUMDOC_API_TIMEOUT_S "600"
```
