@echo off
REM Run test with native window flags
echo ============================================================
echo Running Test with Native Window Flags
echo ============================================================
echo.
echo This forces Qt to create proper Windows native windows
echo instead of using lightweight window representations.
echo.
echo Make sure JAWS is running BEFORE you started this script!
echo.
echo Check Insert+Ctrl+F1 to see if window class changed!
echo.

python test\test_jaws_native_window.py
