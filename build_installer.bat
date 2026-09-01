
@echo off
setlocal EnableExtensions
REM Minimal output for screen reader accessibility
if not defined PYTHON_EXE set PYTHON_EXE=python
if not exist get_version.py (
    echo ERROR: get_version.py missing.
    pause
    exit /b 1
)
if not exist src\main.py (
    echo ERROR: src\main.py missing.
    pause
    exit /b 1
)
set "BUILD_LOG=build_installer.log"
if exist "%BUILD_LOG%" del "%BUILD_LOG%"
set "VER="
for /f "usebackq delims=" %%V in (`"%PYTHON_EXE%" get_version.py src/main.py`) do (
    set "VER=%%V"
)
for /f "delims=" %%A in ("%VER%") do set VER=%%A
if not defined VER (
    echo ERROR: Could not get version.
    pause
    exit /b 1
)
echo Building AbCS version %VER%...

REM ------------------------------------------------------------
REM  Check / install PyInstaller
REM ------------------------------------------------------------
echo Checking PyInstaller...
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

rem goto step2

REM ------------------------------------------------------------
REM  Step 1: Clean previous build artifacts
REM ------------------------------------------------------------
echo Cleaning old build files...
taskkill /F /IM AbCS.exe >nul 2>&1
timeout /t 1 /nobreak >nul

if exist build    rmdir /s /q build
if exist dist     rmdir /s /q dist


REM ------------------------------------------------------------
REM  Step 1 (cont): Build with PyInstaller in onedir mode
REM  onedir is used (not onefile) so Inno Setup can package
REM  individual files - faster app startup and better antivirus
REM  compatibility than onefile extraction to temp.
REM ------------------------------------------------------------
echo Building app files...

"%PYTHON_EXE%" -m PyInstaller AbCS.spec >>"%BUILD_LOG%" 2>&1

if errorlevel 1 (
    echo ERROR: App build failed.
    echo See %BUILD_LOG% for details.
    pause
    exit /b 1
)

echo App build complete.

REM Copy graphics to dist output
if exist "dist\AbCS" (
    if exist "graphics" (
        if not exist "dist\AbCS\_internal\Graphics" mkdir "dist\AbCS\_internal\Graphics"
        xcopy /E /I /Y "graphics\*" "dist\AbCS\_internal\Graphics" >nul 2>&1
        echo Graphics files copied.
    )
)
:step2
REM ------------------------------------------------------------
REM  Step 2: Locate Inno Setup Compiler (ISCC.exe)
REM  Prefer Inno Setup 7 (64-bit Program Files, then 32-bit), then 6
REM ------------------------------------------------------------
echo Creating installer package...

set ISCC=

if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
    goto found_iscc
)
if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
    goto found_iscc
)
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    goto found_iscc
)
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    goto found_iscc
)

for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do (
    set "ISCC=%%I"
    goto found_iscc
)

REM Not found
echo.
echo ERROR: Inno Setup compiler (ISCC.exe) not found on this machine.
echo Install Inno Setup 7 from: https://jrsoftware.org/isdl.php
pause
exit /b 1

:found_iscc
REM Inno Setup found.
if not exist releases mkdir releases

REM ------------------------------------------------------------

REM  Step 2 (cont): Compile the installer
REM  (Icon and splash PNGs are referenced in build_installer.iss)
"%ISCC%" /Qp /DMyAppVersion=%VER% build_installer.iss >>"%BUILD_LOG%" 2>&1

if errorlevel 1 (
    echo ERROR: Installer packaging failed.
    echo See %BUILD_LOG% for details.
    pause
    exit /b 1
)

echo Installer build complete.
echo Output: releases\AbCS-Setup-%VER%.exe
pause
