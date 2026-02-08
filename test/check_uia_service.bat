@echo off
REM Check Windows UI Automation service status
echo ============================================================
echo Windows UI Automation Service Check
echo ============================================================
echo.
echo Checking if Windows UI Automation Core Service is running...
echo.

sc query "UIAutomationCore" | findstr "STATE"
if errorlevel 1 (
    echo [WARNING] UIAutomationCore service not found or not running
    echo.
    echo Trying alternate service name...
    sc query "UIA" | findstr "STATE"
)

echo.
echo Checking UIAutomation service...
sc query "UIAutomation" 2>nul

echo.
echo ============================================================
echo If any services are STOPPED, this could cause the issue.
echo.
echo To start UIAutomation service:
echo   1. Press Win+R
echo   2. Type: services.msc
echo   3. Find "UI Automation Core" or "Windows UI Automation"
echo   4. Right-click, select Properties
echo   5. Set Startup type to "Automatic"
echo   6. Click "Start"
echo ============================================================
echo.
pause
