# AbCS — Installation and Quick Start

Step-by-step setup for running AbCS from source. For project overview and features, see [README.md](README.md). For workflow guides, see [help_docs/01_overview.md](help_docs/01_overview.md).

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
- **Help topics:** `help_docs/` in the project folder (loaded dynamically; see [README.md](README.md#user-documentation))
- **Preferences:** stored via Qt `QSettings` (registry on Windows, config files on Linux/macOS)

### Bundled executable (installer build)

- **Database:** per-user data directory (writable copy of the bundled template)
  - Windows: `%LOCALAPPDATA%\AbCS\abcs.db`
  - Linux: `~/.local/share/AbCS/abcs.db` (or `$XDG_DATA_HOME/AbCS`)
  - macOS: `~/Library/Application Support/AbCS/abcs.db`
- On first run of a fresh install, the app copies the embedded database template into that location.
- **Help topics:** bundled inside the application
  - Windows: `help_docs\` next to the installed executable (see `build_installer.iss`)
  - Linux: `help_docs/` embedded in the PyInstaller build via `build_linux.sh` (extracted at runtime from the bundle)
- **In-app help:** **Help → Help...**, **Shift+F1** (context help), **F1** (shortcuts). Overview: [help_docs/01_overview.md](help_docs/01_overview.md)

## First-time workflow

1. **Launch** — `python src/main.py`
2. **Import books** — **File → Import** (Ctrl+I) to scan audiobook folders (a default **Audio Books** collection is created with the database)
3. **Set preferences** (optional) — **Manage → Preferences** — default zoom is **150%**; see [Default preferences](help_docs/17_default_preferences.md)
4. **Browse** — use Find, filters, and sort on the main window
5. **Manage collections** (optional) — **Manage → Collections** to rename the default collection or add more
6. **Back up** — **Manage → Backup/Restore** when you have data worth protecting

Suggested guide order: [help_docs/01_overview.md](help_docs/01_overview.md).

## Tester build expiry

Tester builds expire **30 days** after the build date. If AbCS refuses to start, download a newer build. Source runs honor the same check when `TRIAL_BUILD_DATE` is set in `src/build_config.py`.

## Running tests

```bash
python -m pytest test/
```

For headless CI-style runs and pytest options, see [TESTING.md](TESTING.md).

## Building an installer

- **Windows:** run `build_installer.bat` (requires local `AbCS.spec` and PyInstaller; see [doc/BUILD.md](doc/BUILD.md)). The Inno Setup script copies `help_docs\` into the install folder.
- **Linux:** follow [linux_build.md](linux_build.md). `build_linux.sh` and `build_linux_debug.sh` bundle `help_docs/` into the executable automatically (see `build_linux_common.sh`).

When adding a help topic, create `help_docs/nn_topic_name.md` in the repository before building; no code change is required for it to appear in **All Help Topics**. See [README.md](README.md#adding-or-changing-help-topics-dynamic-topics).

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| `ModuleNotFoundError` for PySide6 | Run `pip install -r requirements.txt` again |
| Database errors on first run | Delete `data/abcs.db` and restart (you lose local dev data) |
| UI too small or large | **Manage → Preferences** or Ctrl+/Ctrl- for zoom |
| Import finds no files | Check **Preferences → Import Settings** audio formats and folder path |
| Help topics missing in built app | Rebuild after confirming `help_docs/` exists; Linux builds need `./build_linux.sh` (bundles help via PyInstaller) |
| Tester build expired | Obtain a newer build or clear `TRIAL_BUILD_DATE` in source for local dev only |

## Related documentation

- [README.md](README.md) — features, structure, license
- [help_docs/01_overview.md](help_docs/01_overview.md) — user workflow guides
- [help_docs/18_import_preferences.md](help_docs/18_import_preferences.md) — import scenarios and validation rules
- [TESTING.md](TESTING.md) — automated test guide
- [linux_build.md](linux_build.md) — Linux packaging
