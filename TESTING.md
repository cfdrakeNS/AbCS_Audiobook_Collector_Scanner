# AbCS Testing Guide

Quick reference for running the automated test suite locally and in CI.

## Run the full suite

From the project root:

```bash
python -m pytest test/
```

Because `pytest.ini` sets `testpaths = test`, this is equivalent:

```bash
pytest
```

That runs all tests under `test/` (currently ~440 tests). Only files matching
`test_*.py` are collected (see `python_files` in `pytest.ini`), so scratch
scripts such as `z_test.py` are ignored. Debug harnesses that do not follow
that naming (for example `accessibility_test_window.py`) are not collected.

## CI-style run (quiet)

GitHub Actions uses:

```bash
python -m pytest test/ -q --tb=line --durations=15 --cov=src/core --cov=src/database --cov-report=term-missing:skip-covered
```

- `-q` / `--quiet` — less output (progress dots and a short summary)
- `--tb=line` — one-line tracebacks on failures
- `--durations=15` — print the 15 slowest tests (guards against suite regressions)
- `--cov=src/core --cov=src/database` — advisory coverage for core logic packages

## Headless / off-screen Qt

On machines without a display, or to match CI on Windows:

```cmd
set QT_QPA_PLATFORM=offscreen
python -m pytest test/
```

PowerShell:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest test/
```

## Useful pytest switches

### Output

| Switch | Purpose |
|--------|---------|
| `-q` / `--quiet` | Less noise |
| `-v` / `--verbose` | Print each test name as it runs |
| `-s` | Do not capture stdout/stderr (show `print` output) |
| `--tb=style` | Traceback style: `auto`, `long`, `short`, `line`, `native`, `no` |
| `--durations=N` | Show the N slowest tests |

### Which tests to run

| Switch / argument | Purpose |
|-------------------|---------|
| `-k "pattern"` | Run tests whose name contains `pattern` |
| `-m mark` | Run tests with a given `@pytest.mark` (`slow`, `network`, `ui`) |
| `test/test_foo.py` | Run one file |
| `test/test_foo.py::test_bar` | Run one test |

### Stop early

| Switch | Purpose |
|--------|---------|
| `-x` / `--exitfirst` | Stop on the first failure |
| `--maxfail=N` | Stop after N failures |

### Re-run failures

| Switch | Purpose |
|--------|---------|
| `--lf` / `--last-failed` | Run only tests that failed last time |
| `--ff` / `--failed-first` | Run failed tests first, then the rest |

### Inspect without running

| Switch | Purpose |
|--------|---------|
| `--co` / `--collect-only` | List tests without executing them |

## Common command combinations

```bash
# Full suite, quiet (same as CI, without coverage)
python -m pytest test/ -q --tb=line

# Verbose, stop on first failure
python -m pytest test/ -v -x

# One topic or file
python -m pytest test/ -k "accessibility" -v
python -m pytest test/test_tag_reader.py -v
python -m pytest test/test_web_api_fetch.py -v

# Coverage for core + database packages
python -m pytest test/ --cov=src/core --cov=src/database --cov-report=term-missing

# See what would run
python -m pytest test/ --co -q
```

## Prerequisites

Install dependencies first:

```bash
pip install -r requirements.txt
```

Test-related packages include `pytest`, `pytest-qt`, and `pytest-cov` (see `requirements.txt`).

## Configuration

| File | Role |
|------|------|
| `pytest.ini` | `pythonpath`, `testpaths`, `python_files = test_*.py`, markers, `--durations=15` |
| `.github/workflows/pytest.yml` | CI workflow (Python 3.14, Windows, offscreen Qt, durations + advisory cov) |
| `test/` | All automated tests |
| `test/conftest.py` | Shared `qapp`, `ui_scaler`, `theme_manager`, `temp_db`, `main_window`, network block |
| `test/helpers/` | Shared helpers for import-window tests |
| `test/fixtures/abcdDB_def.sql` | Committed schema for fresh clones without `data/abcs.db` |

## Database fixtures

UI tests use the shared `temp_db` fixture from `test/conftest.py`:

- If `data/abcs.db` exists locally, tests copy it (richer dev data).
- Otherwise tests create a fresh database with `initialize_database()`, using `test/fixtures/abcdDB_def.sql`.

No manual database setup is required for pytest on a clean clone.

Session-scoped `ui_scaler` and `theme_manager` fixtures avoid re-applying the
application stylesheet on every window test (that used to make the suite take
tens of minutes). Live HTTP from `web_book_api` is blocked by default; mock
`urlopen` or mark a test `@pytest.mark.network` to opt in.

## Test layout (by topic)

| Area | Files |
|------|-------|
| Main window menus / shortcuts / filters | `test_main_window_menus_shortcuts.py`, `test_main_window_filters_status.py`, `test_main_window_duplicate_mode.py` |
| Book query filters (no UI) | `test_book_query_filters.py` |
| Reading history | `test_reading_history_window.py`, `test_reading_queries.py` |
| Import scan / detail / progress | `test_import_window_*.py`, `test_import_detail_window.py`, `test_import_progress_window.py`, `test_import_scanner_scenarios.py` |
| Import matching / rules / tags | `test_import_title_matching.py`, `test_import_rules.py`, `test_tag_reader.py`, `test_text_utils_import_compare.py` |
| Web metadata | `test_web_api_unit.py`, `test_web_api_fetch.py`, `test_web_api_series.py`, `test_web_metadata_window.py`, `test_web_fetch_ui.py` |
| Accessibility helpers | `test_accessibility_utilities.py`, `test_key_filters.py`, `test_status_bar_readback.py` |
| Backup / DB | `test_list_backups.py`, `test_backup_restore.py`, `test_sqlite_pragmas.py`, `test_named_queries.py` |
| Other windows | `test_collection_window.py`, `test_preferences_persistence.py`, `test_small_dialogs.py`, `test_book_list_import_content.py` |

## Manual harnesses (not collected)

| File | Purpose |
|------|---------|
| `test/accessibility_test_window.py` | Manual F1 / Alt+/ shortcut harness |
| `scripts/manual_book_list_import.py` | Manual book-list import window smoke |

## Related docs

- [README.md](README.md) — project overview and development section
- [AGENTS.md](AGENTS.md) — agent conventions (note: test folder is `test/`, not `tests/`)
- [doc/BUILD.md](doc/BUILD.md) — packaging and gitignored build files
- [doc/plan_ci_test_hardening.md](doc/plan_ci_test_hardening.md) — longer-term CI / coverage plans
