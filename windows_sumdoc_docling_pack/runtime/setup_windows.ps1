Param(
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$RuntimeDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $RuntimeDir ".venv"

Write-Host "[1/4] Runtime dir: $RuntimeDir"
Write-Host "[2/4] Creating venv with: $PythonExe"
& $PythonExe -m venv $VenvDir

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (!(Test-Path $VenvPython)) {
    throw "Cannot find venv python: $VenvPython"
}

Write-Host "[3/4] Upgrading pip"
& $VenvPython -m pip install --upgrade pip

Write-Host "[4/4] Installing requirements"
& $VenvPython -m pip install -r (Join-Path $RuntimeDir "requirements.txt")

Write-Host ""
Write-Host "DONE."
Write-Host "Use this python path in OpenClaw skill if needed:"
Write-Host $VenvPython
