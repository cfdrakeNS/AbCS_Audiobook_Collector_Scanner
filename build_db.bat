@echo off
REM Build AbCS executable with bundled database for distribution

echo ========================================
echo Building AbCS Executable (with DB)
echo ========================================
echo.
echo ACCESSIBILITY: AbCS build_db script has started.
echo ACCESSIBILITY: Python add-on checks and installs may begin next.
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    echo Please run setup.bat first
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
        exit /b 1
    )
    echo PyInstaller installed successfully
)
echo.

REM Determine DB file to bundle
set "DB_SOURCE="
if exist "data\abcs.db" set "DB_SOURCE=data/abcs.db"
if "%DB_SOURCE%"=="" if exist "data\AbCS.db" set "DB_SOURCE=data/AbCS.db"

if "%DB_SOURCE%"=="" (
    echo ERROR: Could not find database file to bundle.
    echo Expected one of:
    echo   data\abcs.db
    echo   data\AbCS.db
    exit /b 1
)

REM Clean previous build_db artifacts
echo Cleaning previous build_db artifacts...
echo Stopping running AbCS processes if any...
taskkill /F /IM AbCS.exe >nul 2>&1
timeout /t 1 /nobreak >nul

if exist build\build_db rmdir /s /q build\build_db
if exist dist\build_db rmdir /s /q dist\build_db

REM Build executable into dist\build_db
echo.
echo Building executable with bundled database...
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
    --distpath="dist/build_db" ^
    --workpath="build/build_db" ^
    --add-data="data/abcdDB_def.sql;data" ^
    --add-data="%DB_SOURCE%;data" ^
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
    echo ERROR: build_db failed!
    exit /b 1
)

echo.
echo ========================================
echo build_db Complete!
echo ========================================
echo.
echo Executable location: dist\build_db\AbCS.exe
echo Bundled files:
echo   - data\abcdDB_def.sql
echo   - %DB_SOURCE%
echo.
echo On first run, existing local DB (if any) is removed and replaced from bundled DB at:
echo   %%LOCALAPPDATA%%\AbCS\abcs.db
echo.
