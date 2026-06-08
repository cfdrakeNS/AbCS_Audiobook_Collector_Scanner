# AbCS Code Inventory — June 08, 2026

Inventory of Python source modules in the AbCS (Audio Book Collector Scanner) project. Line counts include all lines in each file (blank lines and comments included). Last modified dates are from the local filesystem.

## Summary

| Area | Modules | Lines |
|------|---------|------:|
| `src/` (application) | 52 | 28,291 |
| `test/` | 33 | 4,277 |
| `scripts/` | 2 | 514 |
| Project root utilities | 2 | 36 |
| **Total** | **89** | **33,118** |

---

## `src/` — Application source (52 modules)

### `src/` (root)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `main.py` | 271 | 2026-06-06 | Application entry point; initializes Qt app, theme, scaling, and main window |
| `app_paths.py` | 34 | 2026-06-06 | Cross-platform writable user data directory paths |
| `build_config.py` | 7 | 2026-06-07 | Build-time version and trial-build flags (patched by build scripts) |
| `__init__.py` | 1 | 2026-04-15 | Package marker |

### `src/accessibility/` (16 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `accessible_events.py` | 196 | 2026-06-05 | Status bar announcements and accessibility event helpers for screen readers |
| `graphics_paths.py` | 73 | 2026-06-06 | Resolves Graphics asset paths for dev and PyInstaller bundles |
| `icon_helper.py` | 138 | 2026-06-07 | Application icon loading for windows and message boxes |
| `key_filters.py` | 18 | 2026-03-23 | Shared key-event filters (Alt+letter hygiene, combo anti-noise) |
| `linux_fusion_style.py` | 8 | 2026-06-06 | Linux Fusion style tweaks for combo popups |
| `linux_qt_compat.py` | 46 | 2026-06-06 | Linux Qt logging noise reduction and stylesheet strategy |
| `scaling.py` | 257 | 2026-06-06 | UI zoom/scaling (UIScaler) for high-DPI and user zoom preferences |
| `screen_reader.py` | 49 | 2026-06-08 | Detects active screen reader (JAWS, NVDA, Narrator, Orca) and focus timing |
| `shortcut_helpers.py` | 39 | 2026-05-15 | Accessible F1 shortcut-list popup styling |
| `shortcuts.py` | 315 | 2026-06-08 | Centralized Alt+key shortcut registration and conflict detection |
| `style_helpers.py` | 598 | 2026-06-07 | Shared accessible stylesheets, message boxes, combo/button builders |
| `theme_manager.py` | 595 | 2026-06-06 | Theme loading, high-contrast palettes, and application-wide styling |
| `theme_picker.py` | 251 | 2026-06-06 | Theme selection UI used by Preferences |
| `windows_theme_detector.py` | 82 | 2026-04-29 | Detects Windows light/dark/high-contrast system theme |
| `__init__.py` | 9 | 2026-01-16 | Package marker |

### `src/core/` (6 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `import_rules.py` | 334 | 2026-06-05 | Rule engine for import validation scenarios |
| `import_scanner.py` | 326 | 2026-06-08 | Applies import scenario, fallbacks, and field normalization to scanned metadata |
| `tag_reader.py` | 574 | 2026-06-05 | Reads audio file tags (mutagen) for folder import |
| `validator.py` | 372 | 2026-06-05 | Validates imported book metadata; flags errors, warnings, corrections |
| `__init__.py` | 9 | 2026-02-15 | Package marker |

### `src/database/` (6 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `connection.py` | 588 | 2026-06-08 | SQLite connection manager, pragmas, migrations, and query execution |
| `models.py` | 162 | 2026-06-07 | Dataclass models for books, authors, series, collections, etc. |
| `queries.py` | 628 | 2026-06-07 | CRUD query classes for all main database tables |
| `reading_queries.py` | 301 | 2026-04-16 | Reading history and statistics SQL queries |
| `__init__.py` | 37 | 2026-04-06 | Package exports for database layer |

### `src/ui/` (20 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `main_window.py` | 3,579 | 2026-06-08 | Primary book list, filters, menus, duplicate mode, and window orchestration |
| `book_details.py` | 2,183 | 2026-06-07 | View/edit single book; navigation, save, delete, web fetch |
| `import_window.py` | 2,593 | 2026-06-08 | Folder scan import dialog with review table and error filtering |
| `book_list_import_window.py` | 1,794 | 2026-06-08 | Spreadsheet (CSV/Excel/ODS) book list import |
| `preferences_window.py` | 1,916 | 2026-06-08 | Display, import, fallback, and validation preferences |
| `import_detail_window.py` | 1,432 | 2026-06-07 | Per-file import review and edit before adding to library |
| `web_metadata.py` | 1,302 | 2026-06-08 | Web metadata fetch review window and save logic |
| `name_list_window.py` | 1,175 | 2026-06-05 | Reusable Authors, Series, Genre manager window |
| `reading_history_window.py` | 803 | 2026-06-05 | Reading history tabs (General, Year, Month, Date Range) |
| `collection_window.py` | 714 | 2026-06-05 | Collection create/edit/delete manager |
| `backup_restore_window.py` | 633 | 2026-06-08 | Database backup, restore, delete, and full reset |
| `update_window.py` | 874 | 2026-06-05 | Bulk update selected books (series, genre, collection) |
| `import_progress_window.py` | 481 | 2026-06-05 | Accessible progress dialog during folder scan |
| `statistics_dialog.py` | 199 | 2026-06-05 | Read-only library statistics popup |
| `about_dialogue.py` | 122 | 2026-06-06 | About AbCS dialog |
| `web_fetch_progress.py` | 119 | 2026-06-05 | Modal progress while searching online sources |
| `setup_dialogue.py` | 96 | 2026-06-06 | First-run setup dialog |
| `license_dialogue.py` | 83 | 2026-04-15 | License text dialog |
| `__init__.py` | 10 | 2026-04-03 | Package marker |

### `src/utils/` (2 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `settings_helpers.py` | 37 | 2026-06-08 | Legacy QSettings reader for import/web preference keys |
| `text_utils.py` | 91 | 2026-04-27 | Text normalization and fuzzy similarity for duplicate matching |

### `src/web/` (2 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `web_book_api.py` | 1,736 | 2026-06-07 | Open Library, Google Books, and WikiData fetch and match logic |
| `__init__.py` | 1 | 2026-04-15 | Package marker |

---

## `test/` — Automated tests (33 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `test_update_import_regressions.py` | 646 | 2026-06-08 | Import and update workflow regression tests |
| `test_web_book_api_matching.py` | 549 | 2026-06-05 | Web API title/author matching tests |
| `test_web_book_details.py` | 271 | 2026-06-07 | Web metadata integration with book details |
| `test_reading_history_final_integration.py` | 259 | 2026-06-05 | Reading history end-to-end integration |
| `test_accessibility_regression.py` | 213 | 2026-06-05 | Accessibility pattern regression checks |
| `test_main_window_shortcuts_and_menus.py` | 169 | 2026-06-08 | Main window shortcuts and menu structure |
| `test_shortcut_integration.py` | 168 | 2026-06-05 | Cross-window shortcut integration |
| `test_reading_history_accessibility.py` | 164 | 2026-06-05 | Reading history accessibility |
| `test_web_series.py` | 145 | 2026-06-07 | Web series parsing and save |
| `test_status_bar_filter_summary.py` | 129 | 2026-06-08 | Filter summary and status bar text |
| `test_status_bar_readback.py` | 125 | 2026-06-05 | Alt+/ status bar readback |
| `test_web_search_improvements.py` | 120 | 2026-06-05 | Web search behavior improvements |
| `test_plot_filter.py` | 121 | 2026-06-08 | Plot filter toggle and menu |
| `accessibility_test_window.py` | 112 | 2026-05-16 | Manual accessibility test harness window |
| `test_name_list_find_matching.py` | 111 | 2026-06-05 | Name list find/search matching |
| `test_main_window_duplicate_mode.py` | 86 | 2026-06-08 | Duplicate mode activation and export |
| `test_sqlite_pragmas.py` | 86 | 2026-06-05 | Database pragma configuration |
| `test_list_backups.py` | 77 | 2026-06-06 | Backup list and restore paths |
| `test_book_details_accessibility.py` | 74 | 2026-06-08 | Book Details accessible names and shortcuts |
| `test_window_initial_focus.py` | 75 | 2026-06-05 | Initial focus on window open |
| `test_graphics_paths.py` | 53 | 2026-06-06 | Graphics path resolution |
| `conftest.py` | 52 | 2026-06-08 | Pytest fixtures and shared test setup |
| `test_screen_reader_detection.py` | 50 | 2026-06-08 | Screen reader detection utility |
| `test_import_scanner_fallbacks.py` | 54 | 2026-03-21 | Import scanner author/title fallbacks |
| `test_message_box_button_icons.py` | 56 | 2026-06-05 | Styled message box button icons |
| `test_book_import.py` | 51 | 2026-06-05 | Basic book import flow |
| `test_accessibility.py` | 36 | 2026-05-16 | General accessibility smoke tests |
| `test_name_list_accessibility.py` | 35 | 2026-06-05 | Name list window accessibility |
| `test_web_fetch_progress.py` | 37 | 2026-06-05 | Web fetch progress dialog |
| `test_series_from_filename_parsing.py` | 39 | 2026-03-10 | Series number parsing from filenames |
| `test_title_sort_summary.py` | 41 | 2026-06-08 | Sort summary text in status/filter area |
| `test_name_list_status_formatting.py` | 45 | 2026-03-10 | Name list status message formatting |
| `test_app_paths.py` | 28 | 2026-06-06 | App data path resolution |

---

## `scripts/` — Maintenance scripts (2 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `update_series_from_catalog.py` | 418 | 2026-06-05 | One-time catalog CSV to database series/title update |
| `fix_title_articles.py` | 96 | 2026-04-25 | Moves trailing ", The" articles to title start for a collection |

---

## Project root utilities (2 modules)

| Module | Lines | Modified | Description |
|--------|------:|------------|-------------|
| `make_icon.py` | 30 | 2026-06-06 | Builds ICO/PNG icon assets from source graphics |
| `get_version.py` | 6 | 2026-04-25 | Reads APP_VERSION from build_config for build scripts |

---

## Not included in this inventory

The following are part of the project but are **not** Python application modules:

| Item | Notes |
|------|-------|
| `archive/` | Archived demos, old tests, and retired scripts — not active source |
| `build/`, `dist/` | PyInstaller build output |
| `data/` | SQLite database and backups (runtime data) |
| `Graphics/` | Icons, splash, and image assets |
| `test/fixtures/abcdDB_def.sql` | SQL schema fixture for tests |
| `build_installer.bat`, `build_installer.iss` | Windows installer build |
| `AbCS.spec`, `requirements.txt` | Packaging and dependency config |
| `AbCS_Shortcut_June07.csv` | Shortcut reference spreadsheet |
| Documentation (`doc/`, `README.md`, etc.) | Markdown guides, not code modules |

If you want a future inventory pass to cover **build scripts**, **SQL fixtures**, or **archived code**, say which areas to add.

---

## Largest modules (top 10)

| Rank | Module | Lines | Folder |
|------|--------|------:|--------|
| 1 | `main_window.py` | 3,579 | `src/ui/` |
| 2 | `import_window.py` | 2,593 | `src/ui/` |
| 3 | `book_details.py` | 2,183 | `src/ui/` |
| 4 | `preferences_window.py` | 1,916 | `src/ui/` |
| 5 | `book_list_import_window.py` | 1,794 | `src/ui/` |
| 6 | `web_book_api.py` | 1,736 | `src/web/` |
| 7 | `import_detail_window.py` | 1,432 | `src/ui/` |
| 8 | `web_metadata.py` | 1,302 | `src/ui/` |
| 9 | `name_list_window.py` | 1,175 | `src/ui/` |
| 10 | `update_window.py` | 874 | `src/ui/` |

These ten files account for roughly **55%** of all `src/` Python lines.
