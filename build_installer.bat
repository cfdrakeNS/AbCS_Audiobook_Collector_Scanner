@echo off
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

echo ========================================
echo  AbCS - Windows Installer Build
echo ========================================
echo.

REM ------------------------------------------------------------
REM  Activate virtual environment
REM ------------------------------------------------------------
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment.
    echo Make sure venv exists in the project root.
    echo Run: python -m venv venv
    echo Then: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM  Check / install PyInstaller
REM ------------------------------------------------------------
echo Checking for PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller.
        pause
        exit /b 1
    )
)
echo PyInstaller ready.
echo.

REM ------------------------------------------------------------
REM  Step 1: Clean previous build artifacts
REM ------------------------------------------------------------
echo Step 1: Cleaning previous build artifacts...
taskkill /F /IM AbCS.exe >nul 2>&1
timeout /t 1 /nobreak >nul

if exist build    rmdir /s /q build
if exist dist     rmdir /s /q dist
if exist AbCS.spec del AbCS.spec
echo Clean complete.
echo.

REM ------------------------------------------------------------
REM  Step 1 (cont): Build with PyInstaller in onedir mode
REM  onedir is used (not onefile) so Inno Setup can package
REM  individual files - faster app startup and better antivirus
REM  compatibility than onefile extraction to temp.
REM ------------------------------------------------------------
echo Step 1: Building with PyInstaller (onedir mode)...
echo This may take several minutes...
echo.

python -m PyInstaller ^
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
    --exclude-module="PySide6.QtSql" ^
    --exclude-module="PySide6.QtQml" ^
    --exclude-module="PySide6.QtQuick" ^
    --exclude-module="PySide6.QtQuickShapes" ^
    --noconsole ^
    src/main.py

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed. See output above.
    pause
    exit /b 1
)

echo.
echo Step 1 complete. Build output: dist\AbCS\
echo.

REM ------------------------------------------------------------
REM  Step 2: Locate Inno Setup Compiler (ISCC.exe)
REM ------------------------------------------------------------
echo Step 2: Locating Inno Setup 6 compiler...

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
echo.
echo Download and install from:
echo   https://jrsoftware.org/isdl.php
echo.
echo After installing, rerun this script.
pause
exit /b 1

:found_iscc
echo Found: %ISCC%
echo.

REM ------------------------------------------------------------
REM  Step 2 (cont): Ensure releases\ output folder exists
REM ------------------------------------------------------------
if not exist releases mkdir releases

REM ------------------------------------------------------------
REM  Step 2 (cont): Compile the installer
REM ------------------------------------------------------------
echo Step 2: Compiling installer with Inno Setup...
echo.

"%ISCC%" AbCS_installer.iss

if errorlevel 1 (
    echo.
    echo ERROR: Inno Setup compilation failed. See output above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installer build complete!
echo ========================================
echo.

REM Print the output filename by reading the version from the script
for /f "tokens=2 delims==" %%V in ('findstr /i "MyAppVersion" AbCS_installer.iss') do (
    set VER=%%V
    goto got_ver
)
:got_ver
set VER=%VER:"=%
set VER=%VER: =%
echo Installer: releases\AbCS-Setup-%VER%.exe
echo.
echo Distribute this file to users. It installs AbCS to:
echo   C:\Program Files\AbCS\
echo and registers it in Add / Remove Programs.
echo.
pause
