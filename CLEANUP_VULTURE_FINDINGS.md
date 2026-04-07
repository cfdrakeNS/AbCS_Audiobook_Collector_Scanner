# stuff the AI deleted without asking 
#### Database Module 1b: src/database/connection.py — row_factory
**Status: FALSE POSITIVE (Required SQLite idiom)**

- `row_factory` is set on the SQLite connection to allow dictionary-like access to query results (row['column']).
- This is a standard and required pattern for readable database code in Python/Qt apps.
- **Do not remove.**

> Note for future reviewers: Removing or altering this will break named column access throughout the database layer.

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| **100% Confidence - Unreachable Code** | 2 | DONE (April 4, 2026) |
| **90% Confidence - Unused Imports** | 7 | DONE (April 4, 2026) |
| **100% Confidence - Unused Local Variables** | 7 | DONE (April 4, 2026) |
| **60% Confidence - Unused Methods/Attributes** | 15 (latest full rerun) | Narrowed to targeted review list |
| **TOTAL** | 24 | Phase 1 complete; Phase 2 narrowed |

**Phase 1 net line reduction: -111 lines** (dead code and imports/locals cleanup)  
**Validation status:** Completed manual smoke checks for impacted windows and workflows; full rerun completed on April 6, 2026.

---

## 100% Confidence - Unreachable Code DONE

### 1. src/main.py:386
**Issue:** Unreachable code block  
**Context:** Code after `return self.qt_app.exec()` in `run()` that could never execute  
**Result:** Removed

### 2. src/ui/name_list_window.py:913
**Issue:** Unreachable code block  
**Context:** Dialog/shortcut help build block placed after return in `_build_read_status_message()`  
**Result:** Removed

---

## 90% Confidence - Unused Imports DONE

All 7 unused imports removed.

| # | Symbol | File | Result |
|---|--------|------|--------|
| 1 | EasyID3 | src/core/tag_reader.py | Removed |
| 2 | QSplashScreen | src/main.py | Removed |
| 3 | QFont | src/main.py | Removed |
| 4 | QPixmap | src/main.py | Removed |
| 5 | announce_form_field | src/ui/book_details.py | Removed |
| 6 | QButtonGroup | src/ui/book_list_import_window.py | Removed |
| 7 | QRadioButton | src/ui/book_list_import_window.py | Removed |

---

## 100% Confidence - Unused Local Variables DONE

7 confirmed instances addressed.

| File | Line | Variable | Fix |
|------|------|----------|-----|
| src/accessibility/accessible_events.py | 73 | announcement_widget param | Renamed to `_announcement_widget` |
| src/ui/book_list_import_window.py | 33 | filepath param in read_csv | Renamed to `_filepath` |
| src/ui/book_list_import_window.py | 37 | filepath param in read_excel | Renamed to `_filepath` |
| src/ui/book_list_import_window.py | 804 | icon_type param in show_accessible_message | Removed unused param |
| src/ui/collection_window.py | 325 | prev_row, prev_col params | Renamed to `_prev_row`, `_prev_col` |
| src/ui/import_progress_window.py | 319 | issues_text kwarg in update_current_item | Removed unused kwarg |
| src/ui/main_window.py | 2475 | previous param in on_current_cell_changed | Renamed to `_previous` |

---

## 60% Confidence - Window-by-Window Review Plan (One Window at a Time)

Updated from current vulture run (April 5, 2026). This section is organized for sequential testing: complete one window, test it, then move to the next.

### Review Rule for Every Window

For each flagged item below:
1. Verify if connected via Qt signal/slot, shortcut registration, menu action, or dynamic call.
2. Keep and mark as false positive if it is used indirectly.
3. Remove or refactor only if there are no callers and no framework wiring.
4. Run the window-specific smoke test before moving to the next window.

### Window Queue (Test in This Order)

#### Window 1: Main Window (src/ui/main_window.py)
**Status: TESTED & PASSED on April 6, 2026** ✅

Completed removals:
- removed attribute `_web_fetch_cancelled`
- removed attribute `filtered_books`
- removed unused locals `filter_info` and `collection_info` in `refresh_books`
- removed method `focus_book_title`
- removed method `move_cursor_to_row`
- removed method `announce_current_cell`
- removed method `select_range_to_current_row`
- additional cleanup: removed unused `columns` local, unused `QObject` import, unused `ReadingQueries` import, and renamed `previous` to `_previous`

Remaining vulture findings after this pass:
- `unused class MainWindow` (60%) - expected false positive when scanning single file
- `unused method on_collection_changed` (60%) - keep for now pending signal/wiring confirmation

Test focus after changes:
- Table navigation and cell announcements
- Search, filtering, and returning to previous row
- Multi-select behavior (Shift+Click and Ctrl+Click)

#### Window 2: Book Details (src/ui/book_details.py)
**Status: TESTED & PASSED on April 5, 2026** ✅

Completed removals:
- removed attribute `shortcut_manager`
- removed unused local `lineedit_style` in `apply_control_styles`
- removed now-unused top-level `ShortcutManager`/`ShortcutContext` import
- fixed Size label alignment to right-justify with vertical center

Remaining vulture findings after this pass:
- `unused class BookDetailsWindow` (60%) - expected false positive when scanning single file
- additional 60% candidates remain in this file and will be reviewed only after Window 2 UI test is complete

Test focus after changes:
- Open, edit, save, and navigate Prev/Next
- Keyboard shortcuts in form fields

#### Window 3: Name List Window (src/ui/name_list_window.py)
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unreachable dialog code block after return statement (lines 913-962)
- removed method `find_next_match` 
- removed method `find_previous_match`
- removed helper method `_find_direction` (no longer called)
- removed unused attribute `_last_find_row` (init + assignment in `find_first_match`)

Tests completed (April 6):
- All four list types (Authors, Series, Genres, Collections) open correctly ✓
- Find/search behavior and match announcement unchanged ✓
- Edit/save/discard flow and focus return confirmed ✓
- Arrow-key navigation and status announcements working ✓

Current state:
- targeted `vulture` now reports only `NameListWindow` class as a false positive (expected)

#### Window 4: Import Window (src/ui/import_window.py)
**Status: TESTED & PASSED on April 5, 2026** ✅

Removals completed:
- **April 5 fixes:** added `time_hours` and `time_minutes` to `_apply_detail_edits()` key list for time persistence
- **April 5 fixes:** removed duplicate shortcut `setShortcut()` calls in ImportDetailWindow (ShortcutManager is now sole authority)
- **April 5 BookDetails update:** added input mask and time normalization methods (matching ImportDetail pattern)
- **April 6 cleanup:** removed unused methods `on_focus_list`, `_hide_table_cell_highlight`, `jump_to_column`, and `announce_selection`
- **April 6 cleanup:** removed unused `_apply_detail_edits(..., resolve_errors=...)` parameter
- **April 6 cleanup:** removed dead scan counter locals `scan_files_processed` and `scan_total_files`
- **April 6 cleanup:** removed now-unused import `QModelIndex` and helper `_row_title`

Tests completed (April 5):
- Time field: type "1234" → normalizes to "12:34" on focus-out ✓
- Save button only visible when dirty ✓
- Alt+S save properly triggers without conflicts ✓
- PgUp/PgDn navigation preserves edits ✓

Current state after April 6 cleanup:
- targeted `vulture` now reports only `ImportWindow` class as a false positive
- no remaining import-window dead helpers or locals from this set

Additional tests completed (April 6):
- Scan folder/file flow: no issues ✓
- Import progress window and summary updates: no issues ✓
- Detail edit/save flow: no issues ✓
- Selection, Add Selected/Add Valid, filter, and export regression checks: no issues ✓

Test focus after changes:
- Scan folder/file selection and validation flow
- Import summary display and progress window
- Detail editing functionality (click on error items)
- Button focus and keyboard navigation

#### Window 5: Book List Import Window (src/ui/book_list_import_window.py)
**Status: TESTED & PASSED on April 5, 2026** ✅

Removals completed:
- line 125: removed attribute `_last_csv_encoding` (initialization, never read)
- line 944: removed attribute `_last_csv_encoding` (assignment, never read)
- line 696: removed method `toggle_mode` (never called)
- line 709: removed method `focus_mapping_row` (never called)
- line 802: removed method `show_accessible_message` (never called)
- line 1086: removed method `on_new_books_toggled` (never connected as signal handler)
- line 1136: removed method `on_read_date_toggled` (never connected as signal handler)

False positives retained:
- line 21: class `DataFrame` inside DummyPandas (used as fallback when pandas unavailable - confirmed used)

Tests completed:
- CSV/XLSX mapping workflow functional ✓
- File reload and column mapping work ✓
- Import mode toggle handled by on_headers_toggled ✓

Compilation: ✓ Passes py_compile check

#### Window 6: Import Progress Window (src/ui/import_progress_window.py)
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused local `lineedit_style` in `apply_control_styles`
- removed unused method `update_current_item`
- removed unused method `mark_add_complete`

Validation completed:
- workspace diagnostics: no errors in `src/ui/import_progress_window.py` ✓
- symbol search confirms removed items no longer exist ✓

Tests completed (April 6):
- ImportProgress window flow tested by user: no issues ✓
- Completion state and status messaging verified ✓

#### Window 7: Import Detail Window (src/ui/import_detail_window.py)
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused local `lineedit_style` in `apply_control_styles`

Validation completed:
- workspace diagnostics: no errors in `src/ui/import_detail_window.py` ✓

Tests completed (April 6):
- Open item details, edit fields, save/discard behavior ✓
- Alt+letter handling in text fields verified ✓

#### Window 8: Preferences Window (src/ui/preferences_window.py)
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused method `_sync_reader_keywords_width`
- removed unused local `lineedit_style` in `apply_control_styles`
- removed unused method `on_run_display_audit`
- removed unused helper `_collect_display_audit_rows` (only used by removed audit method)

Validation completed:
- workspace diagnostics: no errors in `src/ui/preferences_window.py` ✓

Tests completed (April 6):
- Theme/scaling controls ✓
- Reader keywords controls ✓

#### Window 9: Backup/Restore Window (src/ui/backup_restore_window.py)
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused method `_is_backup_list_focused`
- removed now-unused `QApplication` import

Validation completed:
- workspace diagnostics: no errors in `src/ui/backup_restore_window.py` ✓

Tests completed (April 6):
- Backup list keyboard focus ✓
- Backup/restore action buttons ✓

#### Window 10: Web Metadata Window (src/ui/web_metadata.py)
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused attribute `refresh_count`
- removed unused method `_adjust_plot_height`
- removed unused method `generate_realistic_plot`
- removed unused method `clear_web_indicators`
- removed unused method `show_changes_popup`

Validation completed:
- workspace diagnostics: no errors in `src/ui/web_metadata.py` ✓
- removed now-unused `QFrame` import and local `build_accessible_message_box_style` import ✓

Tests completed (April 6):
- Metadata fetch/refresh cycle ✓
- Plot field Tab and Alt+P focus now land on the field instead of the label ✓
- Any chart/popup behavior tied to scrape results ✓


### Non-Window 60% Items (Track Separately)

These are important but should be handled outside the window sequence:
- accessibility modules (`accessible_events.py`, `shortcuts.py`, `scaling.py`, `theme_manager.py`)
- core modules (`import_scanner.py`, `tag_reader.py`, `validator.py`)
- database modules (`connection.py`, `models.py`, `queries.py`, `reading_queries.py`)
- app entry (`main.py`), web API (`src/web/web_book_api.py`)

#### Accessibility Module 3b: src/accessibility/theme_manager.py — get_current_theme_display_name
**Status: FALSE POSITIVE (Public API, runtime use)**

- `get_current_theme_display_name` is flagged by vulture as unused, but is a public API intended for runtime use (e.g., Preferences window, dynamic UI updates).
- No direct static usage found, but retained for runtime/reflective access and future-proofing.
- **Do not remove.**

> Note for future reviewers: If refactoring theme display logic, check for dynamic or indirect usage before considering removal.

#### Accessibility Module 1: src/accessibility/accessible_events.py
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused helper `get_announcement_widget`
- removed unused helper `check_accessibility_support`
- removed unused helper `announce_table_selection`
- removed unused helper `announce_table_action`
- removed unused helper `announce_form_field`
- removed unused helper `announce_focus_change`
- removed now-unused module state `_announcement_widget`
- removed now-unused imports `QWidget`, `QTableWidget`, and `QLabel`

Validation completed:
- workspace diagnostics: no errors in `src/accessibility/accessible_events.py` ✓

Tests completed (April 6):
- Status bar announcements in major windows ✓
- Dialog open/close announcements ✓

#### Accessibility Module 2: src/accessibility/shortcuts.py
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused enum value `ShortcutContext.GLOBAL`
- removed unused enum value `ShortcutContext.IMPORT_PROGRESS_WINDOW`
- removed unused class member `ZOOM_SHORTCUTS`
- removed unused method `register_zoom_shortcuts`
- removed unused method `get_shortcut_help`
- removed unused method `set_widget_shortcut_hint`

Validation completed:
- workspace diagnostics: no errors in `src/accessibility/shortcuts.py` ✓

Tests completed (April 6):
- Alt+letter shortcuts across main windows still trigger expected controls ✓
- Duplicate dialog and collection window shortcut mappings still work ✓

#### Accessibility Module 3: src/accessibility/scaling.py
**Status: REVIEWED - NO SAFE REMOVALS on April 6, 2026**

Review outcome:
- Ran targeted `vulture` and cross-file symbol checks.
- All flagged symbols are used by active windows and startup wiring; findings are false positives from static analysis limits.

Verified in-use symbols kept:
- `current_scale`, `increase_scale`, `decrease_scale`, `reset_scale`
- `set_preset`, `get_preset_name`, `get_scaled_size`
- `get_scaler`

Validation completed:
- workspace diagnostics: no errors in `src/accessibility/scaling.py` ✓

Next action:
- proceed to accessibility module 4 (`src/accessibility/theme_manager.py`)

#### Accessibility Module 4: src/accessibility/theme_manager.py
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused private method `_is_system_theme_broken`
- removed unused private method `_apply_system_theme_workaround`

Validation completed:
- workspace diagnostics: no errors in `src/accessibility/theme_manager.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `current_theme_name`, `set_theme`, `get_theme_names`, `get_current_theme_display_name`
- `get_theme_manager`

Tests completed (April 6):
- Theme switching in Preferences (including restore/cancel behavior) ✓
- Dark/light/high-contrast palette application ✓
- Existing group box title visibility in dark themes ✓

#### Core Module 1: src/core/import_scanner.py
**Status: CLEANUP APPLIED on April 6, 2026 (module smoke test pending)**

Removals completed:
- removed unused static helper `_series_from_filename`

Validation completed:
- workspace diagnostics: no errors in `src/core/import_scanner.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `ImportScanner`, `configure`, `apply_preferences`

Test focus after changes:
- ImportWindow scan + preference-application flow
- Scenario-based series extraction from directory and filename
- Author/title fallback behavior and correction flags

#### Core Module 2: src/core/tag_reader.py
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused `AudioFileInfo` fields `title`, `track_number`, and `total_tracks`
- removed unused MP3/FLAC/MP4 tag assignments for title/track fields
- renamed unused os.walk variable `dirs` to `_dirs`

Validation completed:
- workspace diagnostics: no errors in `src/core/tag_reader.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `BookScanner`, `scan_folder`

Tests completed (April 6):
- ImportWindow folder scan and single-file scan both populate book rows ✓
- Duration/size/bitrate/author/title/genre fields still load correctly ✓
- No regressions in duplicate detection and import list population ✓

#### Core Module 3: src/core/validator.py
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused import `re`
- removed unused method `normalize_title`

Validation completed:
- workspace diagnostics: no errors in `src/core/validator.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `ImportValidator`, `append_flag_once`, `validate_book`, `is_duplicate`, `flip_author_name`, `format_error_summary`

Tests completed (April 6):
- Validation/duplicate detection behavior in ImportWindow scan flow ✓
- Error category and summary formatting in import list ✓
- Fallback/correction flag appending from `ImportScanner` ✓

#### Database Module 1: src/database/connection.py
**Status: CLEANUP APPLIED on April 6, 2026 (module smoke test pending)**

Removals completed:
- removed unused method `transaction`
- removed unused method `execute_many`
- removed unused method `get_table_count`
- removed now-unused import `contextmanager`

Validation completed:
- workspace diagnostics: no errors in `src/database/connection.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `schema_repair_performed`, `schema_repair_message`, `fetch_all`, `list_backups`, `restore_from_backup`, `delete_backup_file`, `full_reset_database`, `vacuum`, `get_db`, `close_db`

Test focus after changes:
- App startup DB initialization and schema-repair message flow
- Import/main query flows that rely on `fetch_all`
- Backup/restore/full-reset actions in Backup/Restore window

#### Database Module 2: src/database/models.py
**Status: CLEANUP APPLIED on April 6, 2026 (module smoke test pending)**

Removals completed:
- removed unused `Book.is_read` property
- removed unused `Book.has_substantial_comment` property
- removed unused `ImportRecord` dataclass
- removed unused `ImportRecord` export from `src/database/__init__.py`

Validation completed:
- workspace diagnostics: no errors in `src/database/models.py` or `src/database/__init__.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere or known dataclass false positives):
- `Author`, `Series`, `Genre`, `Collection`, `Book`, `SearchFilter`, `Statistics`
- `time_display`, `size_display`, `has_search`, `total_time_display`

Test focus after changes:
- App startup and any import path that imports `src.database`
- Main window and Book Details displays that use book/time/size formatting helpers
- Query/filter flows that construct `SearchFilter` and `Statistics`

#### Database Module 3: src/database/queries.py
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused import `Tuple`
- removed unused method `find_duplicates`

Validation completed:
- workspace diagnostics: no errors in `src/database/queries.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `BookQueries`, `AuthorQueries`, `SeriesQueries`, `GenreQueries`, `CollectionQueries`, `StatisticsQueries`
- active query methods including `get_all`, `get_by_id`, `get_or_create`, `update`, `delete`, `delete_many`, `cleanup_unused`, `bulk_update_*`, and `get_statistics`

Review outcome:
- module is overwhelmingly static-analysis false positives because query APIs are called from UI windows, startup, and import/update workflows
- one additional safe removal identified and applied (`find_duplicates`)

Tests completed (April 6):
- App startup and main book list load: no issues ✓
- Book edit/save, single delete, and multi-delete flows: no issues ✓
- Bulk update Series/Genre/Collection flows: no issues ✓
- Quick import/list refresh regression check: no issues ✓

#### Database Module 4: src/database/reading_queries.py
**Status: CLEANUP APPLIED on April 6, 2026 (module smoke test pending)**

Removals completed:
- removed unused method `get_books_read_on_date`

Validation completed:
- workspace diagnostics: no errors in `src/database/reading_queries.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `ReadingQueries`
- `get_reading_statistics`, `get_reading_history`

Test focus after changes:
- Reading History window General tab statistics load
- Date range history search and table population
- Any import path that constructs `ReadingQueries`

#### App Entry: src/main.py
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused import `build_accessible_button_style`
- removed unused import `os`
- removed unused method `show_splash`
- removed unused constant `APP_BUILD_DATE`

Validation completed:
- workspace diagnostics: no errors in `src/main.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `APP_VERSION` via runtime import in `src/ui/main_window.py`

Test focus after changes:
- Normal app startup and shutdown
- Empty-database startup dialog flow
- Schema-repair and startup dependency status messages

Tests completed (April 6):
- Normal app startup and shutdown: no issues ✓
- Empty-database startup dialog flow and status messaging: no issues ✓

#### Web Module 1: src/web/web_book_api.py
**Status: TESTED & PASSED on April 6, 2026** ✅

Removals completed:
- removed unused import `Book`
- removed unused helper `_get_open_library_work_details`

Validation completed:
- workspace diagnostics: no errors in `src/web/web_book_api.py` ✓
- re-ran `vulture` for module after cleanup ✓

Remaining vulture findings kept (verified in-use elsewhere):
- `WebBookAPI`
- `get_book_metadata`
- `clean_web_data_for_storage`

Test focus after changes:
- Web metadata fetch from Book Details and Main Window
- Web Metadata window cleanup/transform flow before save

Tests completed (April 6):
- Web metadata fetch and cleanup flow: no issues ✓

## Latest Full Rerun Snapshot (April 6, 2026)

Remaining findings from `python -m vulture src`:
- `src/accessibility/scaling.py`: `set_preset`
- `src/accessibility/theme_manager.py`: `get_current_theme_display_name`
- `src/database/connection.py`: `row_factory`
- `src/ui/book_list_import_window.py`: `DataFrame`, `on_headers_toggled`
- `src/ui/import_window.py`: `on_focus_list`, `_hide_table_cell_highlight`, `scan_files_processed`, `scan_total_files` (two occurrences)
- `src/ui/name_list_window.py`: `_last_find_row` (two occurrences)

Interpretation:
- most remaining items are already-known false positives or deferred feature-level decisions
- `QItemSelection` in `src/ui/reading_history_window.py` has been removed after this rerun

Targeted follow-up scan (`src/ui/reading_history_window.py`) after removing `QItemSelection`:
- additional 90% candidates found: `QLineEdit`, `QItemSelectionModel`, `QSettings`, `QAction`, `SearchFilter`, `build_accessible_button_style`, `exec_styled_message_box`, `is_unmapped_alt_letter`
- all above import candidates removed and validated on April 6, 2026
- remaining file-level findings are 60% only: `ReadingHistoryWindow`, `ALLOWED_ALT_LETTERS`, `book_queries`

### Execution Mode for This Cleanup

- Only one window per cycle.
- For each cycle: inspect -> edit -> run smoke test -> record result.
- Do not batch multiple windows in one edit set.
- Add confirmed indirect Qt callbacks to `.vultureignore` after verification.

---

## Cleanup Strategy

### Phase 1: Quick Wins DONE (April 4, 2026)
1. Removed 2 unreachable code blocks.
2. Removed 7 unused imports.
3. Removed/renamed 7 unused local variable findings.
4. Completed smoke testing for touched workflows.

### Phase 2: Targeted 60% Review IN PROGRESS
1. Use fresh `vulture` output as source of truth.
2. Process each window/module in isolated cleanup cycles.
3. Record keep/remove decision and test result for each item.
4. Maintain `.vultureignore` for verified indirect-use symbols.

### Phase 3: Final Validation
1. Run regression smoke tests across major windows.
2. Re-run `python -m vulture src` and compare trend.
3. Confirm accessibility and shortcut behavior remains intact.

---

## Notes

- odfpy import addition is complete and not part of dead-code removals.
- accessible_date_field.py was archived on April 3, 2026.
- Import fixes (time parsing, CSV encoding, label width, ODS support) are complete and not blocked by vulture findings.
- 100% and 90% buckets are complete and should be treated as closed.

---

## Phase 2 Complete — April 6, 2026 ✅

`python -m vulture src .vultureignore` → **zero findings**

### `.vultureignore` — confirmed false positives (all suppressed)

| Symbol | File | Reason |
|--------|------|--------|
| `set_preset` | `src/accessibility/scaling.py` | Public API, called from preferences window at runtime |
| `get_current_theme_display_name` | `src/accessibility/theme_manager.py` | Public API, called from preferences window at runtime |
| `row_factory` | `src/database/connection.py` | SQLite built-in attribute assigned to `connection.row_factory`, not called directly |
| `DataFrame` | `src/ui/book_list_import_window.py` | Fallback stub class in `except ImportError` block when pandas is unavailable |
| `on_headers_toggled` | `src/ui/book_list_import_window.py` | Qt signal handler connected via `QHeaderView.sectionClicked` — invisible to static analysis |


## April 7, 2026 — VULTURE Cleanup Progress (Today)

### Accessibility: scaling.py
- **Flagged:** set_preset (unused method)
- **Action:** Removed (confirmed not used anywhere)
- **Tested:** All scaling/zoom features tested and working after removal
- **Status:** DONE

### Accessibility: theme_manager.py
- **Flagged:** get_current_theme_display_name (unused method)
- **Action:** Marked as FALSE POSITIVE (public API, used at runtime)
- **Tested:** Theme switching and display tested, no issues
- **Status:** DONE

### Database: connection.py
- **Flagged:** row_factory (unused attribute)
- **Action:** Marked as FALSE POSITIVE (required SQLite idiom)
- **Tested:** Database access and queries tested, no issues
- **Status:** DONE

### Book List Import Window: book_list_import_window.py
- **Flagged:** DataFrame (unused class), on_headers_toggled (unused method)
- **Action:**
  - DataFrame: Confirmed as fallback for missing pandas, required for import error handling (FALSE POSITIVE)
  - on_headers_toggled: Confirmed connected to checkbox, required for header toggle (FALSE POSITIVE)
- **Tested:** Import window header toggle and fallback tested, no issues
- **Status:** DONE

### What’s Left
- Review any new vulture findings after next code changes
- Continue window-by-window review for any new flagged items

---

**This section summarizes only the work done today. Use this for quick navigation with JAWS.**

