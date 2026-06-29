#!/usr/bin/env powershell
# PowerShell helper script to run the basis scraper

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

Set-Location $ProjectRoot
if (Test-Path $VenvPython) {
    & $VenvPython main.py
} else {
    py -3 main.py
}

Read-Host "Press Enter to exit"
