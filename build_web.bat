@echo off
echo Building Web Enhancement Package...
echo.

REM Create build directory
if not exist "releases" mkdir releases
if not exist "releases\web_enhancement" mkdir releases\web_enhancement

REM Clean previous build
if exist "releases\web_enhancement\*" del /Q "releases\web_enhancement\*"

REM Copy web metadata files
echo Copying web metadata files...
copy "src\ui\web_metadata.py" "releases\web_enhancement\"
copy "src\ui\web_metadata_backup.py" "releases\web_enhancement\"

REM Copy database files if they exist
if exist "src\database\*.py" copy "src\database\*.py" "releases\web_enhancement\"

REM Copy accessibility files
echo Copying accessibility files...
if exist "src\accessibility\*.py" copy "src\accessibility\*.py" "releases\web_enhancement\"

REM Create documentation
echo Creating documentation...
echo # Web Enhancement Build > "releases\web_enhancement\README.md"
echo. >> "releases\web_enhancement\README.md"
echo ## Files Included: >> "releases\web_enhancement\README.md"
echo - web_metadata.py - Main web metadata window >> "releases\web_enhancement\README.md"
echo - web_metadata_backup.py - Backup reference implementation >> "releases\web_enhancement\README.md"
echo. >> "releases\web_enhancement\README.md"
echo ## Features: >> "releases\web_enhancement\README.md"
echo - Real web data fetching from Google Books API >> "releases\web_enhancement\README.md"
echo - Field validation and matching >> "releases\web_enhancement\README.md"
echo - Popup for field changes >> "releases\web_enhancement\README.md"
echo - Auto-save in book details >> "releases\web_enhancement\README.md"
echo - Accessibility support (JAWS/NVDA) >> "releases\web_enhancement\README.md"
echo. >> "releases\web_enhancement\README.md"
echo ## Installation: >> "releases\web_enhancement\README.md"
echo 1. Backup your current files >> "releases\web_enhancement\README.md"
echo 2. Copy files to src\ui\ directory >> "releases\web_enhancement\README.md"
echo 3. Install requests: pip install requests >> "releases\web_enhancement\README.md"
echo 4. Restart application >> "releases\web_enhancement\README.md"

REM Create version info
echo Web Enhancement Build > "releases\web_enhancement\VERSION.txt"
echo Date: %date% %time% >> "releases\web_enhancement\VERSION.txt"
echo Branch: web-metadata-integration >> "releases\web_enhancement\VERSION.txt"

REM List files created
echo.
echo Files created:
dir "releases\web_enhancement\"

echo.
echo Build complete! Files are in releases\web_enhancement\
echo.
pause
