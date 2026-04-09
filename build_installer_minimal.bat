@echo off
REM Minimal AbCS installer builder

REM Set up environment
set "VENV_DIR="
if exist ".venv\Scripts\python.exe" set "VENV_DIR=.venv"
if not defined VENV_DIR if exist "venv\Scripts\python.exe" set "VENV_DIR=venv"
if not defined VENV_DIR (
    echo ERROR: No virtual environment found.
    exit /b 1
)
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

REM Extract version from src\main.py
"%PYTHON_EXE%" -c "import pathlib, re; t=pathlib.Path('src/main.py').read_text(encoding='utf-8'); m=re.search(r'^\s*APP_VERSION\s*=\s*\"([^\"]+)\"', t, re.MULTILINE); open('abcs_version.txt', 'w', encoding='utf-8').write(m.group(1) if m else '')"
set /p VER=<abcs_version.txt
del abcs_version.txt
if "%VER%"=="" (
    echo ERROR: Could not extract APP_VERSION from src\main.py
    exit /b 1
)
echo Using APP_VERSION: %VER%

REM Find Inno Setup
set ISCC=
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
    echo ERROR: Inno Setup 6 not found.
    exit /b 1
)
echo Inno Setup found: %ISCC%

REM Ensure releases folder exists
if not exist releases mkdir releases

REM Build installer
"%ISCC%" /Qp /DMyAppVersion=%VER% AbCS_installer.iss
if errorlevel 1 (
    echo ERROR: Installer packaging failed.
    exit /b 1
)
echo Installer build complete: releases\AbCS-Setup-%VER%.exe
