@echo off
REM Simple JAWS test - minimal PySide6 application
echo ============================================================
echo Running Simple JAWS Basic Test
echo ============================================================
echo.
echo This is the simplest possible PySide6 application to test
echo if JAWS can read Qt applications at all.
echo.
echo Make sure JAWS is running BEFORE you started this script!
echo.
echo With JAWS running, try:
echo   Insert+T       - Read window title
echo   Tab            - Navigate to button
echo   Insert+Tab     - Read current control
echo   Space          - Click button
echo.

python test\test_jaws_basic.py
