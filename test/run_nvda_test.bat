@echo off
REM Test with NVDA instead of JAWS
echo ============================================================
echo NVDA Comparison Test
echo ============================================================
echo.
echo This test compares NVDA behavior with JAWS behavior.
echo.
echo BEFORE RUNNING:
echo   1. CLOSE JAWS completely
echo   2. Download NVDA from: https://www.nvaccess.org/download/
echo   3. Install and START NVDA
echo.
echo With NVDA running:
echo   - Tab should announce widgets
echo   - NVDA+T reads title
echo   - Insert+Up/Down for navigation
echo.
pause
echo.
echo Running test...
echo.

python test\test_nvda_comparison.py
