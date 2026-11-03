$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Python do ambiente virtual não encontrado em .venv\Scripts\python.exe"
}

if (-not (Test-Path (Join-Path $PSScriptRoot "web_app.py"))) {
    throw "web_app.py não foi encontrado na pasta do projeto."
}

Write-Host "Iniciando GeraArteIA em http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Para encerrar, pressione Ctrl+C." -ForegroundColor Yellow

& $python -m uvicorn web_app:app --host 127.0.0.1 --port 8000
