@echo off
REM Run accessibility test harness with MSAA mode (older, more stable accessibility API)
echo ============================================================
echo Running Accessibility Test Harness in MSAA Mode
echo ============================================================
echo.
echo MSAA (Microsoft Active Accessibility) is older but more
echo stable than Windows UIA. If JAWS doesn't work with UIA,
echo try this mode.
echo.
echo Make sure JAWS is running BEFORE you started this script!
echo.

set QT_ACCESSIBILITY_API_VERSION=1
python test\accessibility_test_harness.py
