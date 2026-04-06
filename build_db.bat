@echo off
setlocal EnableExtensions
REM Build AbCS executable with bundled database for distribution

set "BUILD_LOG=build_db.log"
if exist "%BUILD_LOG%" del "%BUILD_LOG%"
echo AbCS build_db started.
echo Detailed log: %BUILD_LOG%
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    echo Ensure .venv exists and dependencies are installed.
    exit /b 1
)

REM Install PyInstaller if not already installed
echo Step 1/3: Checking PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller. This may take a minute...
    python -m pip install pyinstaller >>"%BUILD_LOG%" 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        echo See %BUILD_LOG% for details.
        exit /b 1
    )
)
echo PyInstaller ready.

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
echo Step 2/3: Cleaning old build files...
taskkill /F /IM AbCS.exe >nul 2>&1
timeout /t 1 /nobreak >nul

if exist build\build_db rmdir /s /q build\build_db
if exist dist\build_db rmdir /s /q dist\build_db

REM Build executable into dist\build_db
echo Step 3/3: Building executable with bundled DB...
echo Please wait...

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
    --hidden-import="openpyxl" ^
    --hidden-import="odf" ^
    --hidden-import="odf.opendocument" ^
    --exclude-module="PySide6.QtSql" ^
    --exclude-module="PySide6.QtQml" ^
    --exclude-module="PySide6.QtQuick" ^
    --exclude-module="PySide6.QtQuickShapes" ^
    --noconsole ^
    src/main.py >>"%BUILD_LOG%" 2>&1

if errorlevel 1 (
    echo ERROR: build_db failed.
    echo See %BUILD_LOG% for details.
    exit /b 1
)

echo build_db complete.
echo Executable location: dist\build_db\AbCS.exe
echo Bundled DB source: %DB_SOURCE%
echo Log file: %BUILD_LOG%
