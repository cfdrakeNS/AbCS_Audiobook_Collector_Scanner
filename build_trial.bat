@echo off
setlocal EnableExtensions
REM Build AbCS_Trial executable using PyInstaller
REM Patches build_config.py to enable the trial expiry check, builds,
REM then restores build_config.py to the original (TRIAL_BUILD=False) state.
REM Output is a single-file executable like build.bat.

set "BUILD_CONFIG=src\build_config.py"
set "BUILD_CONFIG_BAK=src\build_config.py.bak"
set "BUILD_LOG=build_trial.log"
set "TODAY="

if exist "%BUILD_LOG%" del "%BUILD_LOG%"

REM Resolve Python
set "VENV_DIR="
if exist ".venv\Scripts\python.exe" set "VENV_DIR=.venv"
if not defined VENV_DIR if exist "venv\Scripts\python.exe" set "VENV_DIR=venv"
if not defined VENV_DIR (
    echo ERROR: No virtual environment found.
    echo Create .venv or venv and install requirements.
    pause
    exit /b 1
)
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
echo Using environment: %VENV_DIR%

REM Get today's date in YYYY-MM-DD format
for /f "tokens=*" %%D in ('%PYTHON_EXE% -c "import datetime; print(datetime.date.today().isoformat())"') do set "TODAY=%%D"
if "%TODAY%"=="" (
    echo ERROR: Could not determine today's date.
    pause
    exit /b 1
)
echo AbCS Trial build started.
echo Build date: %TODAY%
echo Log: %BUILD_LOG%
echo.

REM Back up original build_config.py
copy /y "%BUILD_CONFIG%" "%BUILD_CONFIG_BAK%" >nul

REM Patch build_config.py for trial
REM Set TRIAL_BUILD_DATE to a fixed old date for expiry testing, or use %TODAY% for normal builds
REM Set APP_VERSION to your current version
(
    echo # build_config.py -- TRIAL BUILD ^(patched by build_trial.bat^)
    echo APP_VERSION = "1.9.11"
    echo TRIAL_DAYS = 30
    echo TRIAL_BUILD_DATE = "2026-05-18"
) > "%BUILD_CONFIG%"

echo Step 1/3: Checking PyInstaller...
"%PYTHON_EXE%" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller. This may take a minute...
    "%PYTHON_EXE%" -m pip install pyinstaller >>"%BUILD_LOG%" 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        echo See %BUILD_LOG% for details.
        copy /y "%BUILD_CONFIG_BAK%" "%BUILD_CONFIG%" >nul 2>&1
        del /q "%BUILD_CONFIG_BAK%" >nul 2>&1
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
        copy /y "%BUILD_CONFIG_BAK%" "%BUILD_CONFIG%" >nul 2>&1
        del /q "%BUILD_CONFIG_BAK%" >nul 2>&1
        pause
        exit /b 1
    )
)
echo PyInstaller ready.

REM Clean previous trial build
echo Step 2/3: Cleaning old trial build files...
taskkill /F /IM AbCS_Trial.exe >nul 2>&1
timeout /t 1 /nobreak >nul

if exist dist\AbCS_Trial.exe (
    echo Removing existing dist\AbCS_Trial.exe...
    attrib -r dist\AbCS_Trial.exe >nul 2>&1
    del /f /q dist\AbCS_Trial.exe >nul 2>&1
    if exist dist\AbCS_Trial.exe (
        echo ERROR: dist\AbCS_Trial.exe is locked and cannot be replaced.
        echo Close any running AbCS_Trial window, File Explorer preview, or antivirus lock, then retry.
        copy /y "%BUILD_CONFIG_BAK%" "%BUILD_CONFIG%" >nul 2>&1
        del /q "%BUILD_CONFIG_BAK%" >nul 2>&1
        pause
        exit /b 1
    )
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AbCS_Trial.spec del AbCS_Trial.spec

REM Build
echo Step 3/3: Building trial executable...
echo Please wait...

"%PYTHON_EXE%" -m PyInstaller ^
    --name="AbCS_Trial" ^
    --onefile ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --log-level=WARN ^
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

set BUILD_ERR=%ERRORLEVEL%

REM Always restore build_config.py regardless of build outcome
copy /y "%BUILD_CONFIG_BAK%" "%BUILD_CONFIG%" >nul
del /q "%BUILD_CONFIG_BAK%" >nul

if %BUILD_ERR% neq 0 (
    echo ERROR: Trial build failed. See %BUILD_LOG% for details.
    pause
    exit /b 1
)

echo.
echo Trial build complete.
echo Executable location: dist\AbCS_Trial.exe
echo Build date embedded: %TODAY%
echo Expires after: 30 days (on %TODAY% + 30 days)
echo Log: %BUILD_LOG%
echo.
pause
