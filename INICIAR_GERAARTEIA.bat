@echo off
chcp 65001 > nul
title GeraArteIA

echo ==========================================
echo            GERAARTEIA
echo ==========================================
echo.
echo Iniciando o sistema...
echo.
echo Aguarde alguns segundos.
echo O navegador sera aberto automaticamente.
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado.
    echo Execute primeiro INSTALAR_GERAARTEIA.bat
    echo.
    pause
    exit /b 1
)

start "" http://127.0.0.1:8000

.venv\Scripts\python.exe -m uvicorn web_app:app --host 127.0.0.1 --port 8000

pause