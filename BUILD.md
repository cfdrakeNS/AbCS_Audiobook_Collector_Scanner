# Build Instructions for AbCS Executable

## Quick Start

Simply run:
```
build.bat
```

This will create a standalone `AbCS.exe` file in the `dist` folder that you can send to your friend.

## What the Build Script Does

1. Activates your virtual environment
2. Installs PyInstaller if needed
3. Cleans previous builds
4. Creates a single executable file with all dependencies bundled
5. Includes the database schema files

## Distribution

After the build completes, you'll find:
- **dist/AbCS.exe** - The standalone executable
- **dist/data/abcs.db** - Bundled database copy for distribution
- **dist/data/abcdDB_def.sql** - Database schema

Send this file to your friend. They can run it without installing Python or any dependencies.

## First Run

When your friend runs the .exe for the first time:
- It will create a writable `abcs.db` in the user's AppData folder
- The build also ships a copy in `dist/data/abcs.db` for reference or seeding
- The splash screen will show statistics (should be 0 books initially)
- The main window will open ready to import audiobooks

## For JAWS Testing

The application is built with accessibility in mind:
- 14pt default fonts (scalable)
- High contrast themes available
- Complete keyboard navigation (Alt+letter shortcuts)
- F-key shortcuts (F3=search, F4=close, F9=import, etc.)
- Status bar announcements for screen readers
- Proper focus management

## Build Options Explained

- `--onefile`: Creates a single .exe (easier to distribute)
- `--windowed`: No console window (GUI only)
- `--noconsole`: Hides the console for a cleaner experience
- `--add-data`: Includes database files in the bundled executable
- `--hidden-import`: Ensures all dependencies are included
- `--collect-all PySide6`: Bundles all Qt/PySide6 files

## Troubleshooting

**Build fails:**
- Make sure virtual environment is activated
- Run `setup.bat` first to ensure all dependencies are installed

**Executable won't run:**
- Windows Defender might flag it (normal for PyInstaller apps)
- Add exception or use "Run anyway" option

**Missing features:**
- Check that all files in `data/` directory are included
- Verify database schema file is present

## Build Size

The executable will be approximately 100-150 MB because it bundles:
- Python runtime
- PySide6 (Qt framework)
- All application code and dependencies

This is normal for Python GUI applications bundled with PyInstaller.

## Updating

Every time you make changes to the code:
1. Run `build.bat` again
2. The new `dist/AbCS.exe` will have your changes
3. Send the updated exe to your friend for testing
