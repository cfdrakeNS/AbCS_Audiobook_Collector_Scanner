@echo off
setlocal EnableExtensions
REM Build AbCS executable using PyInstaller
REM This script creates a standalone .exe for distribution

set "BUILD_LOG=build.log"
if exist "%BUILD_LOG%" del "%BUILD_LOG%"
set "VENV_DIR="
if exist ".venv\Scripts\python.exe" set "VENV_DIR=.venv"
if not defined VENV_DIR if exist "venv\Scripts\python.exe" set "VENV_DIR=venv"
echo AbCS build started.
echo Detailed log: %BUILD_LOG%
echo.

REM Resolve Python environment
if not defined VENV_DIR (
    echo ERROR: No virtual environment found.
    echo Create .venv or venv and install requirements.
    pause
    exit /b 1
)
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
echo Using environment: %VENV_DIR%

REM Install PyInstaller if not already installed
echo Step 1/3: Checking PyInstaller...
"%PYTHON_EXE%" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller. This may take a minute...
    "%PYTHON_EXE%" -m pip install pyinstaller >>"%BUILD_LOG%" 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
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

REM Clean previous builds
echo Step 2/3: Cleaning old build files...
taskkill /F /IM AbCS.exe >nul 2>&1
timeout /t 1 /nobreak >nul

if exist dist\AbCS.exe (
    echo Removing existing dist\AbCS.exe...
    attrib -r dist\AbCS.exe >nul 2>&1
    del /f /q dist\AbCS.exe >nul 2>&1
    if exist dist\AbCS.exe (
        echo ERROR: dist\AbCS.exe is locked and cannot be replaced.
        echo Close any running AbCS window, File Explorer preview, or antivirus lock, then retry.
        pause
        exit /b 1
    )
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AbCS.spec del AbCS.spec

REM Build executable
echo Step 3/3: Building executable...
echo Please wait...

"%PYTHON_EXE%" -m PyInstaller ^
    --name="AbCS" ^
    --onefile ^
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
    echo ERROR: Build failed.
    echo See %BUILD_LOG% for details.
    pause
    exit /b 1
)

echo Build complete.
echo Executable location: dist\AbCS.exe
echo Log file: %BUILD_LOG%

pause
