@echo off
REM Build Web-Enhanced AbCS executable using PyInstaller
REM This script creates a standalone .exe with web metadata features

echo ========================================
echo Building Web-Enhanced AbCS Executable
echo ========================================
echo.
echo ACCESSIBILITY: Web-enhanced build script has started.
echo ACCESSIBILITY: Python add-on checks and installs may begin next.
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Install PyInstaller if not already installed
echo Checking for PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ACCESSIBILITY: Installing required Python add-on PyInstaller.
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully
)

REM Install requests library for web functionality
echo Checking for requests library...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ACCESSIBILITY: Installing required Python add-on requests.
    echo Installing requests...
    python -m pip install requests
    if errorlevel 1 (
        echo ERROR: Failed to install requests
        pause
        exit /b 1
    )
    echo requests installed successfully
)

REM Install jinja2 (optional pandas dependency; prevents PyInstaller hidden-import warning)
echo Checking for jinja2 library...
python -c "import jinja2" >nul 2>&1
if errorlevel 1 (
    echo Installing jinja2 (required to suppress PyInstaller build warning)...
    python -m pip install jinja2
    if errorlevel 1 (
        echo WARNING: Failed to install jinja2 - build will proceed with a warning
    ) else (
        echo jinja2 installed successfully
    )
)
echo.

REM Clean previous builds
echo Cleaning previous builds...
echo Stopping running AbCS processes if any...
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

REM Build web-enhanced executable
echo.
echo Building web-enhanced executable...
echo This may take several minutes...
echo PyInstaller log level: WARN
echo.

python -m PyInstaller ^
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
    --hidden-import="requests" ^
    --hidden-import="json" ^
    --hidden-import="urllib.request" ^
    --hidden-import="urllib.parse" ^
    --hidden-import="urllib.error" ^
    --exclude-module="PySide6.QtSql" ^
    --exclude-module="PySide6.QtQml" ^
    --exclude-module="PySide6.QtQuick" ^
    --exclude-module="PySide6.QtQuickShapes" ^
    --noconsole ^
    src/main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Web-Enhanced Build Complete!
echo ========================================
echo.
echo Executable location: dist\AbCS.exe
echo Database schema bundled: data\abcdDB_def.sql
echo Web features included: Google Books API integration
echo.
echo You can now distribute dist\AbCS.exe with web metadata capabilities.
echo.
echo Note: No database file is bundled; first run creates a new database automatically.
echo.

pause
