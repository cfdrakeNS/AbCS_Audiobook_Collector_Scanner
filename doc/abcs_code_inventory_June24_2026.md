# AbCS Code Inventory — June 24, 2026

Inventory of Python source modules in the AbCS (Audio Book Collector Scanner) project. Line counts include all lines in each file (blank lines and comments included). Last modified dates are from the local filesystem.

Previous inventory: [abcs_code_inventory_June08_2026.md](abcs_code_inventory_June08_2026.md)

## Summary

| Area | Modules | Lines |
|------|---------|------:|
| `src/` (application) | 59 | 35,422 |
| `test/` | 40 | 6,448 |
| `scripts/` | 3 | 758 |
| Project root utilities | 2 | 46 |
| **Total** | **104** | **42,674** |

---

## `src/` — Application source (59 modules)

### src/ (root) (4 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `__init__.py` | Package marker | 1 | 2026-04-15 |
| `app_paths.py` | Cross-platform writable user data directory paths | 46 | 2026-06-06 |
| `build_config.py` | Build-time version and trial-build flags (patched by build scripts) | 8 | 2026-06-22 |
| `main.py` | Application entry point; initializes Qt app, theme, scaling, and main window | 336 | 2026-06-24 |

### src/accessibility/ (19 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `__init__.py` | Package marker | 11 | 2026-01-16 |
| `accessible_events.py` | Status bar announcements and accessibility event helpers for screen readers | 232 | 2026-06-05 |
| `dialog_prose.py` | HTML prose blocks for accessible About, License, and Setup dialogs | 78 | 2026-06-22 |
| `graphics_paths.py` | Resolves Graphics asset paths for dev and PyInstaller bundles | 94 | 2026-06-06 |
| `help_paths.py` | Help topic discovery and path resolution for in-app help | 93 | 2026-06-23 |
| `help_scaling.py` | Help-window-only zoom independent of global UI scale | 102 | 2026-06-24 |
| `icon_helper.py` | Application icon loading for windows and message boxes | 159 | 2026-06-23 |
| `key_filters.py` | Shared key-event filters (Alt+letter hygiene, combo anti-noise) | 24 | 2026-03-23 |
| `linux_fusion_style.py` | Linux Fusion style tweaks for combo popups | 12 | 2026-06-06 |
| `linux_qt_compat.py` | Linux Qt logging noise reduction and stylesheet strategy | 56 | 2026-06-06 |
| `read_only_text.py` | Read-only and navigable text areas for JAWS/NVDA arrow-key review | 297 | 2026-06-23 |
| `scaling.py` | UI zoom/scaling (UIScaler) for high-DPI and user zoom preferences | 318 | 2026-06-06 |
| `screen_reader.py` | Detects active screen reader (JAWS, NVDA, Narrator, Orca) and focus timing | 59 | 2026-06-08 |
| `shortcut_helpers.py` | Accessible F1 shortcut-list popup styling | 53 | 2026-06-22 |
| `shortcuts.py` | Centralized Alt+key shortcut registration and conflict detection | 356 | 2026-06-23 |
| `style_helpers.py` | Shared accessible stylesheets, message boxes, combo/button builders | 665 | 2026-06-14 |
| `theme_manager.py` | Theme loading, high-contrast palettes, and application-wide styling | 658 | 2026-06-06 |
| `theme_picker.py` | Theme selection UI used by Preferences | 303 | 2026-06-06 |
| `windows_theme_detector.py` | Detects Windows light/dark/high-contrast system theme | 88 | 2026-04-29 |

### src/core/ (5 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `__init__.py` | Package marker | 11 | 2026-02-15 |
| `import_rules.py` | Rule engine for import validation scenarios | 372 | 2026-06-05 |
| `import_scanner.py` | Applies import scenario, fallbacks, and field normalization to scanned metadata | 536 | 2026-06-24 |
| `tag_reader.py` | Reads audio file tags (mutagen) for folder import | 675 | 2026-06-05 |
| `validator.py` | Validates imported book metadata; flags errors, warnings, corrections | 443 | 2026-06-05 |

### src/database/ (5 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `__init__.py` | Package exports for database layer | 39 | 2026-04-06 |
| `connection.py` | SQLite connection manager, pragmas, migrations, and query execution | 705 | 2026-06-10 |
| `models.py` | Dataclass models for books, authors, series, collections, etc. | 204 | 2026-06-14 |
| `queries.py` | CRUD query classes for all main database tables | 734 | 2026-06-14 |
| `reading_queries.py` | Reading history and statistics SQL queries | 358 | 2026-04-16 |

### src/ui/ (22 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `__init__.py` | Package marker | 11 | 2026-04-03 |
| `about_dialogue.py` | About AbCS dialog | 145 | 2026-06-24 |
| `accessible_dialog.py` | Base QDialog class fixing JAWS Insert+T window title reporting | 94 | 2026-06-24 |
| `backup_restore_window.py` | Database backup, restore, delete, and full reset | 742 | 2026-06-22 |
| `book_details.py` | View/edit single book; navigation, save, delete, web fetch | 2,456 | 2026-06-24 |
| `book_list_import_window.py` | Spreadsheet (CSV/Excel/ODS) book list import | 2,109 | 2026-06-24 |
| `collection_window.py` | Collection create/edit/delete manager | 870 | 2026-06-22 |
| `help_router.py` | Shift+F1 context-sensitive help routing per window | 84 | 2026-06-24 |
| `help_window.py` | In-app help browser with topic discovery and markdown rendering | 1,007 | 2026-06-24 |
| `import_detail_window.py` | Per-file import review and edit before adding to library | 1,629 | 2026-06-24 |
| `import_progress_window.py` | Accessible progress dialog during folder scan | 556 | 2026-06-22 |
| `import_window.py` | Folder scan import dialog with review table and error filtering | 3,031 | 2026-06-24 |
| `license_dialogue.py` | License text dialog | 111 | 2026-06-22 |
| `main_window.py` | Primary book list, filters, menus, duplicate mode, and window orchestration | 4,398 | 2026-06-24 |
| `name_list_window.py` | Reusable Authors, Series, Genre manager window | 1,367 | 2026-06-22 |
| `preferences_window.py` | Display, import, fallback, and validation preferences | 2,403 | 2026-06-24 |
| `reading_history_window.py` | Reading history tabs (General, Year, Month, Date Range) | 1,026 | 2026-06-22 |
| `setup_dialogue.py` | First-run setup dialog | 122 | 2026-06-22 |
| `statistics_dialog.py` | Read-only library statistics popup | 230 | 2026-06-22 |
| `update_window.py` | Bulk update selected books (series, genre, collection) | 1,021 | 2026-06-24 |
| `web_fetch_progress.py` | Modal progress while searching online sources | 141 | 2026-06-09 |
| `web_metadata.py` | Web metadata fetch review window and save logic | 1,472 | 2026-06-24 |

### src/utils/ (2 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `settings_helpers.py` | QSettings reader for import and web preference keys | 123 | 2026-06-24 |
| `text_utils.py` | Text normalization and fuzzy similarity for duplicate matching | 193 | 2026-06-22 |

### src/web/ (2 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `__init__.py` | Package marker | 1 | 2026-04-15 |
| `web_book_api.py` | Open Library, Google Books, and WikiData fetch and match logic | 1,954 | 2026-06-24 |

---

## `test/` — Automated tests (40 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `accessibility_test_window.py` | Manual accessibility test harness window | 118 | 2026-05-16 |
| `conftest.py` | Pytest fixtures and shared test setup | 65 | 2026-06-08 |
| `test_accessibility.py` | General accessibility smoke tests | 50 | 2026-05-16 |
| `test_accessibility_regression.py` | Accessibility pattern regression checks | 238 | 2026-06-10 |
| `test_app_paths.py` | App data path resolution | 39 | 2026-06-06 |
| `test_book_details_accessibility.py` | Book Details accessible names and shortcuts | 91 | 2026-06-08 |
| `test_book_import.py` | Basic book import flow | 72 | 2026-06-05 |
| `test_date_added_filter.py` | Date-added filter toggle and query behavior | 39 | 2026-06-14 |
| `test_graphics_paths.py` | Graphics path resolution | 71 | 2026-06-06 |
| `test_help_router.py` | Shift+F1 context help routing per window | 139 | 2026-06-23 |
| `test_help_scaling.py` | Help window independent zoom scaling | 130 | 2026-06-24 |
| `test_import_scanner_fallbacks.py` | Import scanner author/title fallbacks | 250 | 2026-06-23 |
| `test_list_backups.py` | Backup list and restore paths | 135 | 2026-06-10 |
| `test_main_window_duplicate_mode.py` | Duplicate mode activation and export | 120 | 2026-06-08 |
| `test_main_window_shortcuts_and_menus.py` | Main window shortcuts and menu structure | 228 | 2026-06-08 |
| `test_message_box_button_icons.py` | Styled message box button icons | 73 | 2026-06-05 |
| `test_name_list_accessibility.py` | Name list window accessibility | 50 | 2026-06-05 |
| `test_name_list_find_matching.py` | Name list find/search matching | 143 | 2026-06-05 |
| `test_name_list_status_formatting.py` | Name list status message formatting | 69 | 2026-03-10 |
| `test_plot_filter.py` | Plot filter toggle and menu | 169 | 2026-06-08 |
| `test_read_only_text.py` | Read-only text and list widgets for screen reader navigation | 95 | 2026-06-19 |
| `test_reading_history_accessibility.py` | Reading history accessibility | 182 | 2026-06-10 |
| `test_reading_history_final_integration.py` | Reading history end-to-end integration | 265 | 2026-06-05 |
| `test_screen_reader_detection.py` | Screen reader detection utility | 79 | 2026-06-08 |
| `test_series_from_filename_parsing.py` | Series number parsing from filenames | 59 | 2026-03-10 |
| `test_settings_helpers.py` | QSettings helper read/write tests | 149 | 2026-06-24 |
| `test_shortcut_integration.py` | Cross-window shortcut integration | 193 | 2026-06-05 |
| `test_sqlite_pragmas.py` | Database pragma configuration | 117 | 2026-06-05 |
| `test_status_bar_filter_summary.py` | Filter summary and status bar text | 198 | 2026-06-14 |
| `test_status_bar_readback.py` | Alt+/ status bar readback | 170 | 2026-06-05 |
| `test_tag_reader.py` | Audio tag reading and book grouping tests | 161 | 2026-06-23 |
| `test_text_utils_import_compare.py` | Text normalization for import duplicate comparison | 38 | 2026-06-22 |
| `test_title_sort_summary.py` | Sort summary text in status/filter area | 58 | 2026-06-08 |
| `test_update_import_regressions.py` | Import and update workflow regression tests | 941 | 2026-06-24 |
| `test_web_book_api_matching.py` | Web API title/author matching tests | 644 | 2026-06-05 |
| `test_web_book_details.py` | Web metadata integration with book details | 319 | 2026-06-07 |
| `test_web_fetch_progress.py` | Web fetch progress dialog | 47 | 2026-06-05 |
| `test_web_search_improvements.py` | Web search behavior improvements | 167 | 2026-06-05 |
| `test_web_series.py` | Web series parsing and save | 183 | 2026-06-07 |
| `test_window_initial_focus.py` | Initial focus on window open | 94 | 2026-06-05 |

---

## `scripts/` — Maintenance scripts (3 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `fix_title_articles.py` | Moves trailing article suffix to title start for a collection | 124 | 2026-04-25 |
| `generate_user_docs_odt.py` | Builds LibreOffice ODT user guides from numbered doc/*.md files | 135 | 2026-06-14 |
| `update_series_from_catalog.py` | One-time catalog CSV to database series/title update | 499 | 2026-06-05 |

---

## Project root utilities (2 modules)

| Module | Description | Lines | Modified |
|--------|-------------|------:|------------|
| `make_icon.py` | Builds ICO/PNG icon assets from source graphics | 39 | 2026-06-06 |
| `get_version.py` | Reads APP_VERSION from build_config for build scripts | 7 | 2026-04-25 |

---

## Changes since June 08, 2026 inventory

| Area | June 08 | June 24 | Delta |
|------|--------:|--------:|------:|
| `src/` modules | 52 | 59 | +7 |
| `src/` lines | 28,291 | 35,422 | +7,131 |
| `test/` modules | 33 | 40 | +7 |
| `test/` lines | 4,277 | 6,448 | +2,171 |
| `scripts/` modules | 2 | 3 | +1 |
| Total modules | 89 | 104 | +15 |
| Total lines | 33,118 | 42,674 | +9,556 |

**Notable new `src/` modules:** `help_window.py`, `help_router.py`, `help_paths.py`, `help_scaling.py`, `read_only_text.py`, `dialog_prose.py`, `accessible_dialog.py`.

---

## Not included in this inventory

The following are part of the project but are **not** Python application modules:

| Item | Notes |
|------|-------|
| `archive/` | Archived demos, old tests, and retired scripts — not active source |
| External: [pyside6-accessible-ui-reference](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference) | Standalone PySide6 accessibility reference (separate GitHub repo) |
| `build/`, `dist/` | PyInstaller build output |
| `data/` | SQLite database and backups (runtime data) |
| `Graphics/` | Icons, splash, and image assets |
| `test/fixtures/abcdDB_def.sql` | SQL schema fixture for tests |
| `build_installer.bat`, `build_installer.iss` | Windows installer build |
| `AbCS.spec`, `requirements.txt` | Packaging and dependency config |
| Documentation (`doc/`, `help_docs/`, `README.md`, etc.) | Markdown guides, not code modules |

If you want a future inventory pass to cover **build scripts**, **SQL fixtures**, or **archived code**, say which areas to add.

---

## Largest modules (top 10)

| Rank | Module | Lines | Folder |
|------|--------|------:|--------|
| 1 | `main_window.py` | 4,398 | `src/ui/` |
| 2 | `import_window.py` | 3,031 | `src/ui/` |
| 3 | `book_details.py` | 2,456 | `src/ui/` |
| 4 | `preferences_window.py` | 2,403 | `src/ui/` |
| 5 | `book_list_import_window.py` | 2,109 | `src/ui/` |
| 6 | `web_book_api.py` | 1,954 | `src/web/` |
| 7 | `import_detail_window.py` | 1,629 | `src/ui/` |
| 8 | `web_metadata.py` | 1,472 | `src/ui/` |
| 9 | `name_list_window.py` | 1,367 | `src/ui/` |
| 10 | `reading_history_window.py` | 1,026 | `src/ui/` |

These ten files account for roughly **62%** of all `src/` Python lines.
