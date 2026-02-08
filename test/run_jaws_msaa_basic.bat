@echo off
REM Run basic test with MSAA mode (older accessibility API)
echo ============================================================
echo Running Basic Test in MSAA Mode
echo ============================================================
echo.
echo MSAA mode uses the older Microsoft Active Accessibility API.
echo This may work better than Windows UIA.
echo.
echo Make sure JAWS is running BEFORE you started this script!
echo.

set QT_ACCESSIBILITY_API_VERSION=1
python test\test_jaws_basic.py
