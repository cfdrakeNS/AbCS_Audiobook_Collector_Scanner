@echo off
REM AbCS with MSAA Accessibility Mode
REM This forces Qt to use MSAA (older but more stable) instead of UIA

echo Starting AbCS in MSAA accessibility mode...
echo This may work better with JAWS than the default UIA mode.
echo.

REM Set Qt to use MSAA instead of UIA for accessibility
set QT_QPA_PLATFORM=windows:accessibility=msaa

REM Enable accessibility debugging (optional - shows diagnostic messages)
REM set QT_LOGGING_RULES=qt.accessibility*=true

REM Run the application
python src\main.py

pause
