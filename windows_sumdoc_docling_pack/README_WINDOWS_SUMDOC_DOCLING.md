# Dong goi sumdoc + Docling cho Windows (toi gian)

Muc tieu hien tai:
- Chi dung `Docling` de parse file ra text.
- Chua goi model summarize.
- Khi chat voi OpenClaw theo dang `sumdoc file <path>`, he thong se tra text trich xuat.

---

## 1) Noi dung bo dong goi

Folder nay gom 2 phan:

- `runtime/`
  - `sumdoc_docling.py`: script parse file/text
  - `requirements.txt`: dependency toi thieu (`docling`)
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
.\.venv\Scripts\python.exe .\sumdoc_docling.py --text "Xin chao tu Docling runtime"
```

### 6.2 Test parse file

```powershell
.\.venv\Scripts\python.exe .\sumdoc_docling.py --file "D:\docs\abc.pdf"
```

### 6.3 Test script cua skill

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" file "D:\docs\abc.pdf"
```

Neu can JSON:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\sumdoc\scripts\sumdoc.ps1" file "D:\docs\abc.pdf" --json
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

Ket qua hien tai la **text da parse** (khong summarize bang model).

---

## 8) Troubleshooting

- Loi `Runtime script not found`:
  - Kiem tra `SUMDOC_DOCLING_HOME` da dung chua.
- Loi `Docling is not installed`:
  - Chay lai `setup_windows.ps1`.
- Loi Unicode voi file txt:
  - Doi file ve UTF-8.
- File qua lon:
  - Them `--max-chars 50000` (hoac so nho hon) de tranh output qua dai.

---

## 9) Mo rong sau nay (khi model san sang)

Sau khi team AI xong model, co the mo rong theo huong:
- Giu nguyen skill `sumdoc`.
- Trong `sumdoc_docling.py`, sau buoc parse/normalize se goi them summarize endpoint/model.
- Khong can thay doi luong copy/cau hinh OpenClaw.
