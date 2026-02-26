@echo off
setlocal

cd /d "%~dp0.."

echo Running shortcut/accessibility checks...
echo.

python test\check_shortcut_mnemonics.py
if errorlevel 1 goto :fail

python -m pytest ^
  test\test_import_window_collection_rules.py ^
  test\test_name_list_find_matching.py ^
  test\test_name_list_status_formatting.py ^
  test\test_update_import_regressions.py -q
if errorlevel 1 goto :fail

echo.
echo All shortcut/accessibility checks passed.
exit /b 0

:fail
echo.
echo One or more checks failed.
exit /b 1
