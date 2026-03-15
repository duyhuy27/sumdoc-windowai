Param(
    [Parameter(Position = 0)]
    [string]$Mode,

    [Parameter(Position = 1)]
    [string]$InputValue,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Mode) -or [string]::IsNullOrWhiteSpace($InputValue)) {
    Write-Error "Usage: sumdoc.ps1 file <path> [--json] [--max-chars N] | text <raw_text> [--json] [--max-chars N]"
    exit 1
}

$RuntimeHome = $env:SUMDOC_DOCLING_HOME
if ([string]::IsNullOrWhiteSpace($RuntimeHome)) {
    $RuntimeHome = Join-Path $env:USERPROFILE "sumdoc_docling_runtime"
}

$ScriptPath = Join-Path $RuntimeHome "sumdoc_docling.py"
$VenvPython = Join-Path $RuntimeHome ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
} elseif ($env:SUMDOC_PYTHON) {
    $PythonExe = $env:SUMDOC_PYTHON
} else {
    $PythonExe = "python"
}

if (!(Test-Path $ScriptPath)) {
    Write-Error "Runtime script not found: $ScriptPath"
    Write-Host "Set SUMDOC_DOCLING_HOME to folder containing sumdoc_docling.py"
    exit 1
}

$Args = @()
switch ($Mode.ToLowerInvariant()) {
    "file" { $Args += @("--file", $InputValue) }
    "text" { $Args += @("--text", $InputValue) }
    default {
        Write-Error "Mode must be 'file' or 'text'."
        exit 1
    }
}

if ($ExtraArgs) {
    $Args += $ExtraArgs
}

& $PythonExe $ScriptPath @Args
exit $LASTEXITCODE
