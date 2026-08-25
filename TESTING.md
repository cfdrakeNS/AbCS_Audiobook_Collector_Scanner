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

That runs all tests under `test/` (currently ~257 tests). Debug scripts in `test/` that do not follow pytest naming (for example `debug_*.py`) are not collected.

## CI-style run (quiet)

GitHub Actions uses:

```bash
python -m pytest test/ -q --tb=line
```

- `-q` / `--quiet` — less output (progress dots and a short summary)
- `--tb=line` — one-line tracebacks on failures

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

### Which tests to run

| Switch / argument | Purpose |
|-------------------|---------|
| `-k "pattern"` | Run tests whose name contains `pattern` |
| `-m mark` | Run tests with a given `@pytest.mark` |
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
# Full suite, quiet (same as CI)
python -m pytest test/ -q --tb=line

# Verbose, stop on first failure
python -m pytest test/ -v -x

# One topic or file
python -m pytest test/ -k "accessibility" -v
python -m pytest test/test_screen_reader_detection.py -v
python -m pytest test/test_tag_reader.py -v

# See what would run
python -m pytest test/ --co -q
```

## Prerequisites

Install dependencies first:

```bash
pip install -r requirements.txt
```

Test-related packages include `pytest` and `pytest-qt` (see `requirements.txt`).

## Configuration

| File | Role |
|------|------|
| `pytest.ini` | Sets `pythonpath = src` and `testpaths = test` |
| `.github/workflows/pytest.yml` | CI workflow (Python 3.14, Windows, offscreen Qt) |
| `test/` | All automated tests |
| `test/conftest.py` | Shared `qapp` and `temp_db` fixtures |
| `test/fixtures/abcdDB_def.sql` | Committed schema for fresh clones without `data/abcs.db` |

## Database fixtures

UI tests use the shared `temp_db` fixture from `test/conftest.py`:

- If `data/abcs.db` exists locally, tests copy it (richer dev data).
- Otherwise tests create a fresh database with `initialize_database()`, using `test/fixtures/abcdDB_def.sql`.

No manual database setup is required for pytest on a clean clone.

## Core logic tests (no UI)

| File | Covers |
|------|--------|
| `test/test_tag_reader.py` | ID3 tag parsing, narrator extraction, supported formats, `read_file` error paths |
| `test/test_import_scanner_fallbacks.py` | Import scenario folder/title fallbacks |
| `test/test_list_backups.py` | Backup discovery, restore, WAL sidecar cleanup |
| `test/test_text_utils_import_compare.py` | Title/author normalization and fuzzy compare |

## Related docs

- [README.md](README.md) — project overview and development section
- [AGENTS.md](AGENTS.md) — agent conventions (note: test folder is `test/`, not `tests/`)
- [doc/BUILD.md](doc/BUILD.md) — packaging and gitignored build files
