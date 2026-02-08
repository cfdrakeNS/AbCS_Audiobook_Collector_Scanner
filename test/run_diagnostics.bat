@echo off
REM Qt Accessibility Diagnostic Tool
echo ============================================================
echo Qt Accessibility Diagnostic Tool
echo ============================================================
echo.
echo This script checks your Qt configuration for common issues.
echo.
echo Running diagnostics...
echo.

python test\diagnostics.py

echo.
echo Press any key to exit...
pause > nul

