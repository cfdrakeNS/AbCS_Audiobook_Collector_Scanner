@echo off
REM Build AbCS executable using PyInstaller
REM This script creates a standalone .exe for distribution

echo ========================================
echo Building AbCS Executable
echo ========================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat
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
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully
)
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AbCS.spec del AbCS.spec

REM Build executable
echo.
echo Building executable...
echo This may take several minutes...
echo.

python -m PyInstaller ^
    --name="AbCS" ^
    --onefile ^
    --windowed ^
    --add-data="data/abcdDB_def.sql;data" ^
    --add-data="data/abcs.db;data" ^
    --hidden-import="PySide6.QtCore" ^
    --hidden-import="PySide6.QtGui" ^
    --hidden-import="PySide6.QtWidgets" ^
    --hidden-import="mutagen" ^
    --hidden-import="mutagen.mp3" ^
    --hidden-import="mutagen.mp4" ^
    --hidden-import="mutagen.flac" ^
    --hidden-import="mutagen.oggvorbis" ^
    --hidden-import="mutagen.wave" ^
    --collect-all="PySide6" ^
    --noconsole ^
    src/main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Copy database files alongside the exe for easy distribution
if not exist dist\data mkdir dist\data
copy /y data\abcs.db dist\data\abcs.db >nul
copy /y data\abcdDB_def.sql dist\data\abcdDB_def.sql >nul

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\AbCS.exe
echo Database files copied to: dist\data\
echo.
echo You can now distribute dist\AbCS.exe to your friend.
echo.
echo Note: The first run will create a new database if one doesn't exist.
echo.

pause
