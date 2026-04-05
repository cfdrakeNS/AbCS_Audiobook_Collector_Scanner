# AbCS Build Guide (Windows + Linux)

This document is a step-by-step runbook for creating release binaries on both platforms.

## Goal

Produce:
- Windows portable test build: `dist\AbCS.exe` (onefile, for testers)
- Windows release installer: `releases\AbCS-Setup-x.x.x.exe` (standard install, for users)
- Linux executable: `dist/AbCS`

Recommended build strategy:
- Build Windows binary and installer on Windows (Sections 2 and 8)
- Build Linux binary inside Ubuntu VM (or native Ubuntu) (Section 3)

---

## 1) Pre-Build Checklist (Do This First)

Required tools before you begin:
- Git: **Required** on both Windows and Linux (for `git pull`, cloning, branch checks).
- Python 3.9+: **Required** (3.12 recommended for this project).
- pip: **Required** (used to install dependencies).
- PyInstaller: **Required** for packaging binaries.
- VS Code: **Optional**. Helpful for editing and integrated terminal use, but builds can be done from PowerShell/Command Prompt (Windows) or terminal (Linux) without VS Code.

1. Pull latest code:
   - `git pull`
2. Confirm you are on intended branch/tag:
   - `git branch --show-current`
3. Confirm Python version (3.9+):
   - `python --version`
4. Install/update dependencies:
   - `pip install -r requirements.txt`
5. Install PyInstaller (if needed):
   - `pip install pyinstaller`

Optional but strongly recommended before packaging:
- `pytest test/`

---

## 2) Windows Build (Current Official Flow)

Run from repository root.

### 2.0 Windows App Setup (First-Time Machine Setup)

Use these steps when setting up a brand-new Windows machine for AbCS builds.

Prerequisite notes for Windows:
- Git is required. If `git --version` fails, install Git for Windows from https://git-scm.com/download/win
- VS Code is optional. Use it if you prefer, but all build scripts run fine from PowerShell or Command Prompt.

0. Install Git for Windows (if not already installed):
   - Download from https://git-scm.com/download/win
   - Verify: `git --version`

1. Install Python 3.12 (recommended for this project):
   - Download from https://www.python.org/downloads/windows/
   - During install, enable: `Add python.exe to PATH`

Alternative (PowerShell with winget):
- `winget install -e --id Python.Python.3.12`

2. Verify Python and pip:
   - `python --version`
   - `python -m pip --version`

3. Create and activate virtual environment:
   - `python -m venv .venv`
   - `.venv\Scripts\Activate.ps1`

4. Upgrade packaging tools:
   - `python -m pip install --upgrade pip setuptools wheel`

5. Install project dependencies:
   - `python -m pip install -r requirements.txt`

6. Install PyInstaller:
   - `python -m pip install pyinstaller`

7. Verify PyInstaller install:
   - `python -m PyInstaller --version`

If script execution is blocked in PowerShell, run:
- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

Then activate again:
- `.venv\Scripts\Activate.ps1`

If you use VS Code (optional):
- Open the project folder in VS Code.
- Open integrated terminal (Terminal -> New Terminal).
- Select PowerShell terminal profile.
- Run the same commands from this guide unchanged.

### Option A: Standard build (schema only, no bundled user DB)

1. Open PowerShell in project root.
2. Activate venv (if needed):
   - `.venv\Scripts\Activate.ps1`
3. Run:
   - `build.bat`
4. Output:
   - `dist\AbCS.exe`

This is the preferred release artifact for most users.

### Option B: Build with bundled database

Use this only when you intentionally want to ship a pre-populated DB.

1. Ensure one of these exists:
   - `data\abcs.db` or `data\AbCS.db`
2. Run:
   - `build_db.bat`
3. Output:
   - `dist\build_db\AbCS.exe`

---

## 3) Linux Build (Ubuntu VM / Linux Mint VM)

Build Linux binary inside Ubuntu. Do not build Linux executable on Windows.

Linux Mint note:
- Linux Mint is fully supported for this build flow.
- Because Mint is Ubuntu-based, the same commands usually work as-is.
- If a package install fails, run `sudo apt update` and retry.

### 3.0 Linux Mint quick start (if your VM is Mint)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

python3 --version
git --version

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install pyinstaller

chmod +x build_linux.sh
./build_linux.sh
```

Expected output:
- `dist/AbCS`

If launch fails on Mint after build, run:

```bash
chmod +x build_linux_debug.sh
./build_linux_debug.sh
tail -n 120 abcs_linux_build.log
```

### 3.1 Prepare Ubuntu VM

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

### 3.2 Get source

```bash
git clone <your-repo-url>
cd abcs
```

### 3.3 Create environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
```

If startup fails with this message:
- `Incompatible processor. This Qt build requires the following features: sse4.2 popcnt`

Run the legacy CPU repair script:

```bash
chmod +x fix_linux_legacy_cpu_env.sh
./fix_linux_legacy_cpu_env.sh
```

This recreates `.venv` with Python 3.12 and installs a Qt build compatible with older CPUs.

### 3.4 Clean old build artifacts

```bash
rm -rf build dist
```

### 3.5 Build Linux executable

Recommended (short copy/paste):

```bash
chmod +x build_linux.sh
./build_linux.sh
```

Manual fallback (same build, expanded command):

```bash
python -m PyInstaller \
  --name="AbCS" \
  --onefile \
  --windowed \
  --log-level=WARN \
  --clean \
  --noconfirm \
  --add-data="data/abcdDB_def.sql:data" \
  --hidden-import="PySide6.QtCore" \
  --hidden-import="PySide6.QtGui" \
  --hidden-import="PySide6.QtWidgets" \
  --hidden-import="mutagen" \
  --hidden-import="mutagen.mp3" \
  --hidden-import="mutagen.mp4" \
  --hidden-import="mutagen.flac" \
  --hidden-import="mutagen.oggvorbis" \
  --hidden-import="mutagen.wave" \
  --exclude-module="PySide6.QtSql" \
  --exclude-module="PySide6.QtQml" \
  --exclude-module="PySide6.QtQuick" \
  --exclude-module="PySide6.QtQuickShapes" \
  --noconsole \
  src/main.py
```

Output:
- `dist/AbCS`

If the app does not launch on Linux, run the debug flow:

```bash
chmod +x build_linux_debug.sh
./build_linux_debug.sh
```

This builds a console-enabled binary and writes runtime output to:
- `abcs_linux_run.log`

The script also writes setup/build output to:
- `abcs_linux_build.log`

If `abcs_linux_run.log` does not exist, the app never launched. Check:

```bash
tail -n 120 abcs_linux_build.log
```

Important platform difference:
- Windows uses `--add-data="source;dest"`
- Linux/macOS uses `--add-data="source:dest"`

---

## 4) Quick Self-Test Checklist (No Linux Tester Yet)

Use this checklist yourself before sharing artifacts.

### 4.1 Windows self-test

1. Launch `dist\AbCS.exe`
2. Verify app opens to main window without crash.cls
3. Verify keyboard basics:
   - `F1` shows shortcuts
   - `Alt+S` focuses search
   - `Ctrl+0` resets zoom
4. Add and save one test book.
5. Reopen app and verify saved book persists.

### 4.2 Linux self-test (Ubuntu VM)

1. Make executable if needed:
   - `chmod +x dist/AbCS`
2. Launch:
   - `./dist/AbCS`
3. Verify app opens and UI renders correctly.
4. Verify same keyboard basics (`F1`, `Alt+S`, `Ctrl+0`).
5. Add/save one test book and verify persistence after restart.

If launch fails due to missing Qt runtime libraries, install required system packages and retest in the same VM snapshot.

---

## 5) Package the Artifacts for Sharing

Recommended naming pattern:
- `AbCS-windows-x64-YYYYMMDD.zip`
- `AbCS-linux-x64-YYYYMMDD.tar.gz`

Include with each package:
- Executable (`AbCS.exe` or `AbCS`)
- `README.md`
- `INSTALL.md`
- Short release notes (what changed + known issues)

---

## 6) Suggested Release Order While Waiting for Tester Feedback

1. Build both artifacts now (Windows + Ubuntu VM).
2. Run the self-test checklist above.
3. Keep artifacts as release-candidate builds.
4. Publish final installers only after tester sign-off.

This saves time and lets you release immediately once feedback is complete.

---

## 7) Build Strategy: Test Builds vs. Release Installer

| Artifact | Script | Use For |
|---|---|---|
| `dist\AbCS.exe` | `build.bat` | Testers — quick portable drop, no install needed |
| `releases\AbCS-Setup-x.x.x.exe` | `build_installer.bat` | Real users — standard Windows install |
| `dist/AbCS` | `build_linux.sh` | Linux testers |

For active tester feedback cycles, use `build.bat` (faster iteration, no install friction).
For user-facing releases, use `build_installer.bat` (see Section 8 below).

---

## 8) Windows Installer Build (Inno Setup)

This produces a standard Windows installer (`AbCS-Setup-x.x.x.exe`) that:
- Installs to `C:\Program Files\AbCS\`
- Creates a Start Menu entry
- Registers in Add/Remove Programs with an uninstaller
- Optionally adds a Desktop shortcut (user chooses during install)
- User data (database) is stored in `%LOCALAPPDATA%\AbCS\` — separate from the install, survives uninstall

### 8.1 One-Time Setup: Install Inno Setup 6

1. Download from: https://jrsoftware.org/isdl.php
2. Run the installer and accept defaults.
3. No configuration needed — the build script finds ISCC.exe automatically.

### 8.2 Build the Installer

1. Open PowerShell or Command Prompt in the project root.
2. Run:
   - `build_installer.bat`
3. Output:
   - `releases\AbCS-Setup-1.9.4.exe`

The script does two things automatically:
- Runs PyInstaller in **onedir** mode (creates `dist\AbCS\` folder)
- Runs Inno Setup Compiler (`ISCC.exe`) on `AbCS_installer.iss`

onedir mode is used here (instead of onefile) because it gives faster app startup and better antivirus compatibility for installed software.

### 8.3 What the Installer Does

When the user runs `AbCS-Setup-x.x.x.exe`:
1. License / welcome screen (standard Windows wizard)
2. Destination folder selection (default: `C:\Program Files\AbCS`)
3. Optional Desktop shortcut (unchecked by default)
4. Installation progress
5. Offer to launch AbCS immediately

Uninstall: Control Panel → Add/Remove Programs → AbCS → Uninstall

### 8.4 Updating the Version Number

When releasing a new version:
1. Update `APP_VERSION` in `src/main.py`
2. Update `MyAppVersion` in `AbCS_installer.iss` (line 16) to match
3. Run `build_installer.bat`
4. New output: `releases\AbCS-Setup-x.x.x.exe`

### 8.5 Adding an App Icon (Optional)

If you have an `.ico` file (32x32 or 256x256 recommended):
1. Place it at `data\abcs.ico`
2. In `AbCS_installer.iss`, uncomment these two lines:
   ```ini
   SetupIconFile=data\abcs.ico
   UninstallDisplayIcon={app}\AbCS.exe 
   ```
3. In `build_installer.bat`, add `--icon=data\abcs.ico` to the PyInstaller command.

### 8.6 Packaging for Distribution

Share the installer directly:
- `releases\AbCS-Setup-1.9.4.exe`

Or zip it with release notes:
- `AbCS-windows-x64-1.9.4.zip` containing:
  - `AbCS-Setup-1.9.4.exe`
  - `README.md`
  - `INSTALL.md`
  - Release notes
