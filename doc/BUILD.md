# AbCS Build and Packaging Notes

Developer reference for Windows and Linux builds. End users should use released installers when available.

## Prerequisites

- Python 3.9+ with dependencies: `pip install -r requirements.txt`
- **PyInstaller** — installed on demand by build scripts (`pip install pyinstaller`)
- **Windows installer:** [Inno Setup](https://jrsoftware.org/isinfo.php) for `build_installer.iss`

## Files not in git (local / machine-specific)

These paths are listed in `.gitignore` but required for full Windows installer builds:

| File | Purpose | Gitignore rule |
|------|---------|----------------|
| `AbCS.spec` | PyInstaller spec used by `build_installer.bat` | `*.spec` |
| `data/abcdDB_def.sql` | Schema SQL for new databases and bundled installs | `data/*.sql` |
| `data/abcs.db` | Development or template database (runtime) | `data/*.db` |

Linux builds pass `--add-data="data/abcdDB_def.sql:data"`; copy from `test/fixtures/abcdDB_def.sql` on a fresh clone before building.

### Schema for tests and fresh clones

A committed copy lives at [test/fixtures/abcdDB_def.sql](../test/fixtures/abcdDB_def.sql). `DatabaseManager` searches both `data/abcdDB_def.sql` and `test/fixtures/abcdDB_def.sql`.

`data/abcdDB_def.sql` is gitignored via `data/*.sql`. Copy from `test/fixtures/abcdDB_def.sql` when the schema changes or on a fresh clone before packaging.

`AbCS.spec` is gitignored via `*.spec` because it may contain machine-specific paths. To build on a new machine:

1. Copy an existing `AbCS.spec` from a prior build machine, or regenerate with `pyi-makespec` and tune for onedir output.
2. `build_installer.bat` expects the spec at the project root and produces `dist/AbCS/`.
3. An archived trial onefile spec may exist locally under `archive/AbCS_Trial.spec` (reference only).

## Windows release build

```cmd
build_installer.bat
```

Steps performed:

1. Read version from `src/build_config.py` via `get_version.py`
2. PyInstaller onedir build using `AbCS.spec`
3. Copy `graphics/` into `dist/AbCS/_internal/Graphics`
4. Inno Setup packages `releases/AbCS-Setup-{version}.exe`

Trial builds set `TRIAL_BUILD_DATE` in `src/build_config.py` (normally via `build_trial.bat` when present).

## Linux build

See [linux_build.md](linux_build.md) and `build_linux.sh`.

## Version alignment

- App version: `APP_VERSION` in [src/build_config.py](../src/build_config.py)
- Inno Setup IDE fallback in `build_installer.iss` matches `APP_VERSION` in `build_config.py` (bat build passes version via `/D`)

## Related documentation

- [INSTALL.md](../INSTALL.md) — run from source
- [TESTING.md](../TESTING.md) — automated tests
- [linux_build.md](linux_build.md) — Linux packaging
