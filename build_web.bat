@echo off
echo Building Web Enhancement Package...
echo.

REM Create build directory
if not exist "build" mkdir build
if not exist "build\web_enhancement" mkdir build\web_enhancement

REM Copy web metadata files
echo Copying web metadata files...
copy "src\ui\web_metadata.py" "build\web_enhancement\"
copy "src\ui\web_metadata_backup.py" "build\web_enhancement\"

REM Copy database files if they exist
if exist "src\database\*.py" copy "src\database\*.py" "build\web_enhancement\"

REM Copy accessibility files
echo Copying accessibility files...
if exist "src\accessibility\*.py" copy "src\accessibility\*.py" "build\web_enhancement\"

REM Create documentation
echo Creating documentation...
echo # Web Enhancement Build > build\web_enhancement\README.md
echo. >> build\web_enhancement\README.md
echo ## Files Included: >> build\web_enhancement\README.md
echo - web_metadata.py - Main web metadata window >> build\web_enhancement\README.md
echo - web_metadata_backup.py - Backup reference implementation >> build\web_enhancement\README.md
echo. >> build\web_enhancement\README.md
echo ## Features: >> build\web_enhancement\README.md
echo - Real web data fetching from Google Books API >> build\web_enhancement\README.md
echo - Field validation and matching >> build\web_enhancement\README.md
echo - Popup for field changes >> build\web_enhancement\README.md
echo - Auto-save in book details >> build\web_enhancement\README.md
echo - Accessibility support (JAWS/NVDA) >> build\web_enhancement\README.md
echo. >> build\web_enhancement\README.md
echo ## Installation: >> build\web_enhancement\README.md
echo 1. Backup your current files >> build\web_enhancement\README.md
echo 2. Copy files to src\ui\ directory >> build\web_enhancement\README.md
echo 3. Install requests: pip install requests >> build\web_enhancement\README.md
echo 4. Restart application >> build\web_enhancement\README.md

REM Create version info
echo Web Enhancement Build > build\web_enhancement\VERSION.txt
echo Date: %date% %time% >> build\web_enhancement\VERSION.txt
echo Branch: web-metadata-integration >> build\web_enhancement\VERSION.txt

echo.
echo Build complete! Files are in build\web_enhancement\
echo.
pause
