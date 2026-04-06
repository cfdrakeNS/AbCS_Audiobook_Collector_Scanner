@echo off
setlocal EnableExtensions
REM Build AbCS_Trial executable using PyInstaller
REM Patches build_config.py to enable the trial expiry check, builds,
REM then restores build_config.py to the original (TRIAL_BUILD=False) state.

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
    pause
    exit /b 1
)
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

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
(
    echo # build_config.py -- TRIAL BUILD ^(patched by build_trial.bat^)
    echo TRIAL_BUILD = True
    echo TRIAL_DAYS = 30
    echo TRIAL_BUILD_DATE = "%TODAY%"
) > "%BUILD_CONFIG%"

echo Step 1/3: Checking PyInstaller...
"%PYTHON_EXE%" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    "%PYTHON_EXE%" -m pip install pyinstaller >>"%BUILD_LOG%" 2>&1
)

REM Clean previous trial build
echo Step 2/3: Cleaning old trial build files...
taskkill /F /IM AbCS_Trial.exe >nul 2>&1
timeout /t 1 /nobreak >nul
if exist dist\AbCS_Trial rmdir /s /q dist\AbCS_Trial
if exist build\AbCS_Trial rmdir /s /q build\AbCS_Trial

REM Build
echo Step 3/3: Building trial executable...
echo Please wait...

"%PYTHON_EXE%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --log-level=WARN ^
    AbCS_trial.spec >>"%BUILD_LOG%" 2>&1

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
echo Executable location: dist\AbCS_Trial\AbCS_Trial.exe
echo Build date embedded: %TODAY%
echo Expires after: 30 days (on %TODAY% + 30 days)
echo Log: %BUILD_LOG%
echo.
pause
