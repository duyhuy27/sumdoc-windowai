# Dong goi sumdoc + Docling + Local Summarize API cho Windows

Muc tieu hien tai:
- `/sumdoc file <path>` se parse file bang Docling.
- Text da parse duoc goi toi API local: `http://localhost:8000/summarize`.
- Ket qua tra ve la summary + metadata.
- Log day du de debug neu loi.

---

## 1) Noi dung bo dong goi

Folder nay gom 2 phan:

- `runtime/`
  - `sumdoc_docling.py`: script full flow parse + summarize
  - `requirements.txt`: dependency (`docling`, `requests`)
  - `setup_windows.ps1`: tao venv va cai dependency
- `openclaw_skill/sumdoc/`
  - `SKILL.md`, `config.json`, `_meta.json`
  - `scripts/sumdoc.ps1`, `scripts/sumdoc.cmd`

---

## 2) Cach copy sang may Windows

Tu may hien tai, copy **nguyen folder** `windows_sumdoc_docling_pack` sang may Windows.

Vi du dat tai:
- `D:\handover\windows_sumdoc_docling_pack`

---

## 3) Cai runtime tren Windows (Python 3.10)

Mo PowerShell tren may Windows:

```powershell
cd D:\handover\windows_sumdoc_docling_pack\runtime
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1 -PythonExe python
```

Sau lenh tren, ban se co:
- `D:\handover\windows_sumdoc_docling_pack\runtime\.venv\Scripts\python.exe`

---

## 4) Dat bien moi truong cho OpenClaw

Dat bien moi truong tro den runtime:

```powershell
setx SUMDOC_DOCLING_HOME "D:\handover\windows_sumdoc_docling_pack\runtime"
```

Dat API local + tham so summarize:

```powershell
setx SUMDOC_SUMMARIZE_API_URL "http://localhost:8000/summarize"
setx SUMDOC_MAX_NEW_TOKEN "50"
setx SUMDOC_API_TIMEOUT_S "600"
```

Dong mo lai terminal/OpenClaw de nhan bien moi.

---

## 5) Cai skill vao OpenClaw

Copy folder:
- Nguon: `D:\handover\windows_sumdoc_docling_pack\openclaw_skill\sumdoc`
- Dich: `%USERPROFILE%\.openclaw\workspace\skills\sumdoc`

Neu da co skill `sumdoc` cu, backup roi overwrite.

---

## 6) Test nhanh truoc khi chat

### 6.1 Test runtime truc tiep

```powershell
cd D:\handover\windows_sumdoc_docling_pack\runtime
.\.venv\Scripts\python.exe .\sumdoc_docling.py --text "Xin chao tu runtime"
```

### 6.2 Test parse + summarize file

```powershell
.\.venv\Scripts\python.exe .\sumdoc_docling.py --file "D:\docs\abc.pdf"
```

### 6.3 Test voi JSON output (de check metadata)

```powershell
.\.venv\Scripts\python.exe .\sumdoc_docling.py --file "D:\docs\abc.pdf" --json
```

### 6.4 Test script cua skill

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" file "D:\docs\abc.pdf"
```

Neu can JSON:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" file "D:\docs\abc.pdf" --json
```

Neu can test parse-only (bo qua summarize API):

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" file "D:\docs\abc.pdf" --extract-only
```

---

## 7) Cach su dung trong OpenClaw chat

Nhap lenh:

```text
sumdoc file D:\docs\abc.pdf
```

Hoac:

```text
sumdoc text Noi dung can xu ly
```

Ket qua hien tai la **summary** tra ve tu API local.

---

## 8) API contract da chot

Request:

```json
{
  "text": "text parse ra tu docling",
  "max_new_token": 50
}
```

Response (expected):

```json
{
  "summary": "la summary ma model tra ve",
  "input_chars": 50,
  "ouput_tokens": 37,
  "latency_ms": 188353.3,
  "num_chunks": null
}
```

Luu y:
- Runtime giu nguyen key `ouput_tokens` theo API phia model.
- Neu backend dung `output_tokens`, runtime van map duoc.

---

## 9) Log va debug (rat quan trong)

Runtime se log 2 noi:

- stdout: moi event dang JSON (`[LOG] {...}`)
- file jsonl: mac dinh `sumdoc_runtime_<run_id>.jsonl` (tai thu muc runtime hien tai)

Co the set duong dan log cu the:

```powershell
setx SUMDOC_LOG_FILE "D:\logs\sumdoc_runtime.jsonl"
```

Khi loi, runtime in them:
- `[ERROR] <message>`
- `[ERROR] See log file: <path>`

Event log quan trong:
- `run_start`
- `parse_start` / `parse_done`
- `normalize_done`
- `api_call_start` / `api_call_response`
- `run_done`
- `run_error`

---

## 10) Troubleshooting

- Loi `Runtime script not found`:
  - Kiem tra `SUMDOC_DOCLING_HOME` da dung chua.
- Loi `Docling is not installed`:
  - Chay lai `setup_windows.ps1`.
- Loi `Cannot connect summarize API`:
  - Kiem tra server API dang chay tai `localhost:8000`.
- Loi HTTP 500/4xx:
  - Xem `response_preview` trong file log jsonl.
- Loi Unicode voi file txt:
  - Doi file ve UTF-8.
- File qua lon:
  - Them `--max-chars 50000` (hoac so nho hon) de tranh output qua dai.

---

## 11) Lenh full flow de chay ngay

Sau khi setup xong, ban co the chay lien tiep:

```powershell
cd D:\handover\windows_sumdoc_docling_pack\runtime
.\.venv\Scripts\python.exe .\sumdoc_docling.py --file "D:\docs\abc.pdf" --json
```

Va tren OpenClaw chat:

```text
sumdoc file D:\docs\abc.pdf
```
