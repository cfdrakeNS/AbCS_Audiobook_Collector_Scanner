@echo off
REM Run test with explicit accessibility roles
echo ============================================================
echo Running Test with Explicit Accessibility Roles
echo ============================================================
echo.
echo This explicitly tells JAWS what each widget is (button, label, etc.)
echo.
echo Make sure JAWS is running BEFORE you started this script!
echo.
echo Try Tab navigation - JAWS should announce widget types!
echo.

python test\test_jaws_with_roles.py
