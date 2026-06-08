# AbCS — Installation and Quick Start

Step-by-step setup for running AbCS from source. For project overview and features, see [README.md](README.md). For workflow guides, see [doc/abcs_user_index.md](doc/abcs_user_index.md).

## Prerequisites

- **Python 3.9+** — check with `python --version` (3.12 recommended)
- **pip** — Python package installer
- **Git** (optional) — if cloning the repository

### Platform notes

- **Windows** — primary development and test platform
- **Linux** — see [linux_build.md](linux_build.md) for build and packaging
- **macOS** — run from source with the same steps below

## Install dependencies

Open a terminal in the project root and run:

```bash
pip install -r requirements.txt
```

This installs PySide6, mutagen, python-dateutil, Send2Trash, and other runtime libraries. Pytest and pytest-qt are included for development testing.

### Virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Run the application

```bash
python src/main.py
```

AbCS creates the database and tables automatically on first launch. You do not need to run SQL scripts manually.

## Where your data lives

### Development (running from source)

- **Database:** `data/abcs.db` in the project folder (created on first run)
- **Backups:** `backups/` in the project folder
- **Preferences:** stored via Qt `QSettings` (registry on Windows, config files on Linux/macOS)

### Bundled executable (installer build)

- **Database:** per-user data directory (writable copy of the bundled template)
  - Windows: `%LOCALAPPDATA%\AbCS\abcs.db`
  - Linux: `~/.local/share/AbCS/abcs.db` (or `$XDG_DATA_HOME/AbCS`)
  - macOS: `~/Library/Application Support/AbCS/abcs.db`
- On first run of a fresh install, the app copies the embedded database template into that location.

## First-time workflow

1. **Launch** — `python src/main.py`
2. **Create a collection** — **Manage → Collections** (at least one active collection is required before import)
3. **Set preferences** (optional) — **Manage → Preferences** — default zoom is **150%**; see [Default preferences](doc/abCS_default_preference.md)
4. **Import books** — **File → Import** (Ctrl+I) to scan audiobook folders
5. **Browse** — use Find, filters, and sort on the main window
6. **Back up** — **Manage → Backup/Restore** when you have data worth protecting

Suggested guide order: [doc/abcs_user_index.md](doc/abcs_user_index.md).

## Tester build expiry

Tester builds expire **30 days** after the build date. If AbCS refuses to start, download a newer build. Source runs honor the same check when `TRIAL_BUILD_DATE` is set in `src/build_config.py`.

## Running tests

```bash
python -m pytest test/
```

For headless CI-style runs and pytest options, see [TESTING.md](TESTING.md).

## Building an installer

- **Windows:** run `build_installer.bat` (requires local `AbCS.spec` and PyInstaller; see [doc/BUILD.md](doc/BUILD.md))
- **Linux:** follow [linux_build.md](linux_build.md)

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| `ModuleNotFoundError` for PySide6 | Run `pip install -r requirements.txt` again |
| Database errors on first run | Delete `data/abcs.db` and restart (you lose local dev data) |
| UI too small or large | **Manage → Preferences** or Ctrl+/Ctrl- for zoom |
| Import finds no files | Check **Preferences → Import Settings** audio formats and folder path |
| Tester build expired | Obtain a newer build or clear `TRIAL_BUILD_DATE` in source for local dev only |

## Related documentation

- [README.md](README.md) — features, structure, license
- [doc/abcs_user_index.md](doc/abcs_user_index.md) — user workflow guides
- [doc/Import_preferences.md](doc/Import_preferences.md) — import scenarios and validation rules
- [TESTING.md](TESTING.md) — automated test guide
- [linux_build.md](linux_build.md) — Linux packaging
