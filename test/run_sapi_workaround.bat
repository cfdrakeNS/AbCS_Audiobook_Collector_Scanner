@echo off
REM Test SAPI workaround for broken Qt accessibility
echo ============================================================
echo SAPI Workaround Test
echo ============================================================
echo.
echo This test uses Windows SAPI to speak directly, bypassing
echo Qt's accessibility bridge entirely.
echo.
echo This requires pywin32. If not installed, run:
echo   pip install pywin32
echo.
echo Make sure JAWS is running!
echo.

REM Check if pywin32 is installed
python -c "import win32com.client" 2>nul
if errorlevel 1 (
    echo [ERROR] pywin32 not installed
    echo.
    echo Installing pywin32...
    pip install pywin32
    echo.
)

python test\test_jaws_sapi_workaround.py
