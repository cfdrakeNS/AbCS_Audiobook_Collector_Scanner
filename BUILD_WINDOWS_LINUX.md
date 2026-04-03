# AbCS Build Guide (Windows + Linux)

This document is a step-by-step runbook for creating release binaries on both platforms.

## Goal

Produce:
- Windows executable: `AbCS.exe`
- Linux executable: `AbCS`

Recommended build strategy:
- Build Windows binary on Windows
- Build Linux binary inside Ubuntu VM (or native Ubuntu)

Testing-phase policy (current):
- Keep using portable one-file builds (`dist\AbCS.exe` and `dist/AbCS`)
- Do not create permanent installers during active tester feedback
- Revisit installer packaging only after tester sign-off

---

## 1) Pre-Build Checklist (Do This First)

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

## 3) Linux Build (Ubuntu VM)

Build Linux binary inside Ubuntu. Do not build Linux executable on Windows.

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
2. Verify app opens to main window without crash.
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

## 7) Installer Decision (After Testing)

Current recommendation:
- Stay on the existing build scripts for test drops.
- Share zipped portable binaries with testers.
- Do not switch to Program Files installer flow until feedback is stable.

Reason:
- Faster turnaround for test fixes.
- No uninstall/reinstall friction for each test iteration.
- Avoids introducing installer-specific issues while still validating core app behavior.
