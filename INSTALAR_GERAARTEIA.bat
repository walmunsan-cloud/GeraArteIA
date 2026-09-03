@echo off
chcp 65001 > nul
title Instalador - GeraArteIA

echo ==========================================
echo        INSTALADOR DO GERAARTEIA
echo ==========================================
echo.

echo Verificando Python...
python --version

if errorlevel 1 (
    echo.
    echo Python nao foi encontrado.
    echo Instale o Python 3.11 ou 3.12 e tente novamente.
    pause
    exit /b 1
)

echo.
echo Criando ambiente virtual...
python -m venv .venv

echo.
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo.
echo Atualizando pip...
python -m pip install --upgrade pip

echo.
echo Instalando dependencias do projeto...
pip install -r requirements.txt

echo.
echo ==========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ==========================================
echo.
echo Agora execute:
echo INICIAR_GERAARTEIA.bat
echo.
pause
