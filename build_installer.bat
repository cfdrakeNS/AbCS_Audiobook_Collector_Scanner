@echo off
setlocal EnableExtensions
REM ============================================================
REM  build_installer.bat
REM  Full Windows installer build for AbCS
REM
REM  What this does:
REM    Step 1 - Builds an onedir executable with PyInstaller
REM             (output: dist\AbCS\)
REM    Step 2 - Compiles dist\AbCS\ into a Windows installer
REM             using Inno Setup (output: releases\AbCS-Setup-x.x.x.exe)
REM
REM  Prerequisites:
REM    - Inno Setup 6 installed from https://jrsoftware.org/isdl.php
REM    - venv activated OR run from the project root with venv present
REM ============================================================

set "BUILD_LOG=build_installer.log"
if exist "%BUILD_LOG%" del "%BUILD_LOG%"
set "VENV_DIR="
if exist ".venv\Scripts\python.exe" set "VENV_DIR=.venv"
if not defined VENV_DIR if exist "venv\Scripts\python.exe" set "VENV_DIR=venv"
echo AbCS installer build started.
echo Detailed log: %BUILD_LOG%
echo.

REM ------------------------------------------------------------
REM  Resolve Python environment
REM ------------------------------------------------------------
if not defined VENV_DIR (
    echo ERROR: No virtual environment found.
    echo Create .venv or venv and install requirements.
    pause
    exit /b 1
)
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
echo Using environment: %VENV_DIR%

REM ------------------------------------------------------------
REM  Check / install PyInstaller
REM ------------------------------------------------------------
echo Step 1/4: Checking PyInstaller...
"%PYTHON_EXE%" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller. This may take a minute...
    "%PYTHON_EXE%" -m pip install pyinstaller >>"%BUILD_LOG%" 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller.
        echo See %BUILD_LOG% for details.
        pause
        exit /b 1
    )
)

"%PYTHON_EXE%" -c "import importlib.util, sys; mods=('pandas','openpyxl','odf','jinja2'); missing=[m for m in mods if importlib.util.find_spec(m) is None]; sys.exit(1 if missing else 0)" >nul 2>&1
if errorlevel 1 (
    echo Installing required build dependencies...
    "%PYTHON_EXE%" -m pip install -r requirements.txt jinja2 pyinstaller >>"%BUILD_LOG%" 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to install required build dependencies.
        echo See %BUILD_LOG% for details.
        pause
        exit /b 1
    )
)
echo PyInstaller ready.

REM ------------------------------------------------------------
REM  Step 1: Clean previous build artifacts
REM ------------------------------------------------------------
echo Step 2/4: Cleaning old build files...
taskkill /F /IM AbCS.exe >nul 2>&1
timeout /t 1 /nobreak >nul

if exist build    rmdir /s /q build
if exist dist     rmdir /s /q dist
if exist AbCS.spec del AbCS.spec

REM ------------------------------------------------------------
REM  Step 1 (cont): Build with PyInstaller in onedir mode
REM  onedir is used (not onefile) so Inno Setup can package
REM  individual files - faster app startup and better antivirus
REM  compatibility than onefile extraction to temp.
REM ------------------------------------------------------------
echo Step 3/4: Building app files...
echo Please wait...

"%PYTHON_EXE%" -m PyInstaller ^
    --name="AbCS" ^
    --onedir ^
    --windowed ^
    --log-level=WARN ^
    --clean ^
    --noconfirm ^
    --add-data="data/abcdDB_def.sql;data" ^
    --hidden-import="PySide6.QtCore" ^
    --hidden-import="PySide6.QtGui" ^
    --hidden-import="PySide6.QtWidgets" ^
    --hidden-import="mutagen" ^
    --hidden-import="mutagen.mp3" ^
    --hidden-import="mutagen.mp4" ^
    --hidden-import="mutagen.flac" ^
    --hidden-import="mutagen.oggvorbis" ^
    --hidden-import="mutagen.wave" ^
    --hidden-import="openpyxl" ^
    --hidden-import="odf" ^
    --hidden-import="odf.opendocument" ^
    --collect-submodules="odf" ^
    --exclude-module="PySide6.QtSql" ^
    --exclude-module="PySide6.QtQml" ^
    --exclude-module="PySide6.QtQuick" ^
    --exclude-module="PySide6.QtQuickShapes" ^
    --noconsole ^
    src/main.py >>"%BUILD_LOG%" 2>&1

if errorlevel 1 (
    echo ERROR: App build failed.
    echo See %BUILD_LOG% for details.
    pause
    exit /b 1
)

echo App build complete.

REM ------------------------------------------------------------
REM  Step 2: Locate Inno Setup Compiler (ISCC.exe)
REM ------------------------------------------------------------
echo Step 4/4: Building installer package...

set ISCC=

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    goto found_iscc
)
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    goto found_iscc
)

REM Not found
echo.
echo ERROR: Inno Setup 6 not found on this machine.
echo Install it from: https://jrsoftware.org/isdl.php
pause
exit /b 1

:found_iscc
echo Inno Setup found.

REM ------------------------------------------------------------
REM  Step 2 (cont): Ensure releases\ output folder exists
REM ------------------------------------------------------------
if not exist releases mkdir releases

REM ------------------------------------------------------------
REM  Step 2 (cont): Compile the installer
REM ------------------------------------------------------------
"%ISCC%" /Qp AbCS_installer.iss >>"%BUILD_LOG%" 2>&1

if errorlevel 1 (
    echo ERROR: Installer packaging failed.
    echo See %BUILD_LOG% for details.
    pause
    exit /b 1
)

REM Resolve version from installer preprocessor define
set "VER="
for /f "tokens=3" %%V in ('findstr /r /c:"^#define[ ][ ]*MyAppVersion" AbCS_installer.iss') do (
    set "VER=%%~V"
)
if not defined VER set "VER=unknown"
set "VER=%VER:\"=%"

echo Installer build complete.
echo Installer: releases\AbCS-Setup-%VER%.exe
echo Log file: %BUILD_LOG%
pause
