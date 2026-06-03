# Vulture Cleanup Process

1. Read this document noting the false positives that are documented.
2. Do a vulture scan of the code.
3. Update the doc with your findings.
4. Remove stale actionable entries after confirming they were already addressed; keep history and false-positive notes.

---

# Actionable Items (Current - June 3, 2026)

Items that need verification or cleanup, organized by file:

## Production Code

- No current production cleanup items after removing `refresh_view` and `focus_first_card` (see Cleanup History).

## Tests
- `test/test_reading_history_accessibility.py`: `date_range_layout` variable - Test-only Vulture finding; review before changing.
- `test/test_reading_history_final_integration.py`: `alt_slush_works` and `operation_works` variables - Test-only findings; review before changing.
- `test/test_shortcut_integration.py`: `shortcut_manager` fixture/variable - Test-only finding; may be pytest fixture behavior.
- `test/test_update_import_regressions.py`: `suppress_import_confirmations`, `isolated_qsettings`, and repeated `isolated_qsettings` parameters - Test-only findings; likely pytest fixtures and should be handled carefully.
- `test/test_web_book_api_matching.py`: `return_value` and `side_effect` attributes on `@patch.object` mocks — Test-only mock configuration; do not remove.

## Review Notes
- `src/build_config.py` uses `TRIAL_BUILD_DATE` in `src/main.py`; do not remove.
- `src/database/queries.py` attributes `total_time_hours` and `total_hours_read` are used by statistics display/model logic; keep.
- `src/ui/book_list_import_window.py` pandas fallback `DataFrame` remains a valid false positive.
- `src/accessibility/shortcuts.py` `READING_HISTORY_SHORTCUTS` is a compatibility alias; used by `test/test_shortcut_integration.py`.
- `src/ui/main_window.py` `book_list` is a compatibility/accessibility alias for the table; used by `test/test_accessibility_regression.py`.
- `src/ui/name_list_window.py` `on_alt_f_pressed` wraps `on_clear_find`; shortcut wiring uses `on_clear_find` directly but tests assert the alias exists.
- `src/ui/name_list_window.py` `_format_status_message` is exercised by `test/test_name_list_status_formatting.py`, not from production callers.
- `src/ui/reading_history_window.py` `load_general_stats` is a compatibility alias for `load_summary_data`; keep unless tests and callers are updated.
- `src/accessibility/theme_picker.py` `paintEvent` on `ThemeMiniPreview` is a Qt widget override invoked by the framework, not application code.
- Test-only Vulture findings should not be removed without confirming pytest fixture use and test intent.

---

# False Positives (Do Not Remove)

These items are flagged by vulture but are actually used or required:

## src/database/connection.py
- **Line 75**: `row_factory` attribute - Required SQLite idiom

## src/ui/book_list_import_window.py
- **Line 21**: `DataFrame` class - Fallback for missing pandas

## Tests
- **pytest fixtures and fixture parameters**: Vulture may report fixtures or fixture arguments as unused even when pytest injects them for setup side effects.
- **`test/test_web_book_api_matching.py`: mock `return_value` and `side_effect` attributes** - Standard unittest.mock patch configuration.
- **`test/test_message_box_button_icons.py`: inner `Parent` class** - Minimal stub used only to satisfy a test signature pattern; not production code.

## Compatibility and callback references
- **`src/accessibility/shortcuts.py`: `READING_HISTORY_SHORTCUTS`** - Compatibility alias.
- **`src/ui/main_window.py`: `book_list`** - Compatibility/accessibility alias for the main table.
- **`src/ui/name_list_window.py`: `on_alt_f_pressed`** - Shortcut callback alias; tests assert presence.
- **`src/ui/name_list_window.py`: `_format_status_message`** - Static helper called from unit tests.
- **`src/ui/reading_history_window.py`: `load_general_stats`** - Compatibility alias for `load_summary_data`.

## Qt framework callbacks
- **`src/accessibility/theme_picker.py`: `ThemeMiniPreview.paintEvent`** - Qt paint callback; not called directly from app code.

---

# Cleanup History

### June 3, 2026 — Dead-code cleanup (vulture actionable items)

**Removed:**
- `src/ui/import_window.py`: `_apply_detail_edits` unused parameter `refresh_view`.
- `src/ui/import_detail_window.py`: `refresh_view=False` keyword at `_save_to_parent` call site.
- `src/accessibility/theme_picker.py`: `ThemePreviewPicker.focus_first_card` (unused; no callers).

**Post-cleanup:** production actionable section cleared; `paintEvent` remains documented false positive.

### June 3, 2026 — Vulture Scan

**Scan run:**
- `python -m vulture src test --min-confidence 60`
- `python -m vulture src --min-confidence 60`

**New actionable items (production):**
- `src/ui/import_window.py`: `_apply_detail_edits` unused parameter `refresh_view` (100% confidence).
- `src/accessibility/theme_picker.py`: `ThemePreviewPicker.focus_first_card` — unused method (60% confidence).

**New actionable items (tests):**
- None beyond existing test-only list; scan still reports the same pytest/mock patterns.

**New test-only findings (document as false positives / do not remove):**
- `test/test_message_box_button_icons.py`: inner class `Parent` (60% confidence) — harmless test stub.
- `test/test_web_book_api_matching.py`: additional `side_effect` mock attributes (line ~107) alongside existing `return_value` reports.

**Stale actionable items removed from Production section:**
- June 2 note “No current production cleanup items” — superseded by `refresh_view` and `focus_first_card` above.

**Existing actionable items unchanged (tests):**
- `test/test_reading_history_accessibility.py`: `date_range_layout`
- `test/test_reading_history_final_integration.py`: `alt_slush_works`, `operation_works`
- `test/test_shortcut_integration.py`: `shortcut_manager` fixture
- `test/test_update_import_regressions.py`: `suppress_import_confirmations`, `isolated_qsettings`
- `test/test_web_book_api_matching.py`: mock `return_value` / `side_effect` attributes

**Existing false positives confirmed (src-only scan):**
- `src/database/connection.py`: `row_factory`
- `src/ui/book_list_import_window.py`: fallback `DataFrame`
- `src/accessibility/theme_picker.py`: `ThemeMiniPreview.paintEvent` (Qt callback)
- `src/accessibility/shortcuts.py`: `READING_HISTORY_SHORTCUTS` (compatibility alias; used by shortcut tests)
- `src/ui/main_window.py`: `book_list` (compatibility alias)
- `src/ui/name_list_window.py`: `on_alt_f_pressed`, `_format_status_message`
- `src/ui/reading_history_window.py`: `load_general_stats`

**Review notes still valid (not reported this scan):**
- `src/build_config.py`: `TRIAL_BUILD_DATE` (used by `src/main.py`)
- `src/database/queries.py`: `total_time_hours`, `total_hours_read`

**`.vultureignore`:** no changes required this scan (`set_preset`, `get_current_theme_display_name`, `row_factory`, `DataFrame` entries remain).

### June 2, 2026 — Dead-code cleanup (vulture actionable items)

**Removed:**
- `src/ui/book_details.py`: `_navigation_announce_message` (orphaned after paging moved to `_focus_title_after_navigation`).
- `src/accessibility/theme_picker.py`: `ThemeMiniPreview.set_colors` (colors set only in `__init__`).
- `src/ui/preferences_window.py`: `focus_source_scope_section` (orphan alias; `focus_import_section` remains wired).

**Post-cleanup scan:** production actionable items cleared; `paintEvent` remains documented false positive.

### June 2, 2026 — Vulture Scan (post book-details / theme-picker changes)

**Scan run:**
- `python -m vulture src test --min-confidence 60`
- `python -m vulture src --min-confidence 60`

**New actionable items (production):**
- `src/ui/book_details.py`: `_navigation_announce_message` — dead helper after Page Up/Down paging moved to `_focus_title_after_navigation`.
- `src/accessibility/theme_picker.py`: `ThemeMiniPreview.set_colors` — unused; colors passed at construction only.
- `src/ui/preferences_window.py`: `focus_source_scope_section` — orphan shortcut alias; `focus_import_section` is wired instead.

**New false positives documented:**
- `src/accessibility/theme_picker.py`: `ThemeMiniPreview.paintEvent` — Qt framework callback.

**Existing actionable items unchanged (tests):**
- `test/test_reading_history_accessibility.py`: `date_range_layout`
- `test/test_reading_history_final_integration.py`: `alt_slush_works`, `operation_works`
- `test/test_shortcut_integration.py`: `shortcut_manager` fixture
- `test/test_update_import_regressions.py`: `suppress_import_confirmations`, `isolated_qsettings`
- `test/test_web_book_api_matching.py`: mock `return_value` attributes

**Existing false positives confirmed:**
- `src/database/connection.py`: `row_factory`
- `src/ui/book_list_import_window.py`: fallback `DataFrame`
- `src/build_config.py`: `TRIAL_BUILD_DATE` (used by `src/main.py`)
- `src/database/queries.py`: `total_time_hours`, `total_hours_read`
- `src/accessibility/shortcuts.py`: `READING_HISTORY_SHORTCUTS`
- `src/ui/main_window.py`: `book_list`
- `src/ui/name_list_window.py`: `on_alt_f_pressed`, `_format_status_message`
- `src/ui/reading_history_window.py`: `load_general_stats`

**`.vultureignore`:** no changes required this scan.

### June 2, 2026 — Vulture Findings Document Refresh

**Scan run:**
- `python -m vulture src test --min-confidence 60`
- `python -m vulture src --min-confidence 60`

**New actionable items:**
- None after removing `src/ui/import_window.py` `scan_files_processed` and `scan_total_files` dead state.

**Items addressed during this refresh:**
- `src/ui/import_window.py`: removed `scan_files_processed` and `scan_total_files` (assigned-only dead state in nested `on_progress`).

**New test-only findings:**
- `test/test_web_book_api_matching.py`: mock `return_value` attributes on patched fetch methods.

**New false positives documented:**
- `src/ui/name_list_window.py`: `_format_status_message` (called from `test/test_name_list_status_formatting.py`).

**Items addressed and removed from False Positives / Review Notes:**
- `src/ui/book_list_import_window.py`: `on_headers_toggled` — method no longer present in source.
- `src/web/web_book_api.py`: `_title_matches` — no longer reported by source-only scan; confirmed used internally by `get_book_metadata`.

**Existing false positives confirmed:**
- `src/database/connection.py`: `row_factory` remains a required SQLite idiom.
- `src/ui/book_list_import_window.py`: fallback `DataFrame` class remains required when pandas is unavailable.
- `src/build_config.py`: `TRIAL_BUILD_DATE` remains active startup/trial logic and is used by `src/main.py`.
- `src/database/models.py` / `src/database/queries.py`: `total_time_hours` and `total_hours_read` remain active statistics fields.
- Source-only scan callback/compatibility findings remain documented as keep/review items.

**`.vultureignore` updated:** removed stale `on_headers_toggled` entry.

### May 17, 2026 — Vulture Findings Document Refresh

**Scan run:**
- `python -m vulture src test --min-confidence 60`
- `python -m vulture src --min-confidence 60`

**Actionable section refreshed:**
- Removed stale actionable entries that were already documented as removed or already verified as keep/do-not-remove.
- Removed current production findings from `src/ui/import_window.py` where timing variables were assigned but not read.
- Kept test-only findings separate because pytest fixtures and test setup variables can be false positives.

**Existing false positives confirmed:**
- `src/database/connection.py`: `row_factory` remains a required SQLite idiom.
- `src/ui/book_list_import_window.py`: fallback `DataFrame` class remains required when pandas is unavailable.
- `src/build_config.py`: `TRIAL_BUILD_DATE` remains active startup/trial logic and is used by `src/main.py`.
- `src/database/models.py` / `src/database/queries.py`: `total_time_hours` and `total_hours_read` remain active statistics fields.
- Source-only scan callback/compatibility findings were documented as keep/review items instead of removed.

**Items already addressed and removed from Actionable Items:**
- May 17 Import Window timing variables: `repopulate_start`, `index_build_time`, `table_opt_elapsed`, `auto_add_elapsed`, `total_elapsed`, `manual_add_elapsed`, `auto_add_start`, `table_opt_start`, and `manual_add_start`.
- Legacy trial flags `TRIAL_BUILD` and `TRIAL_DAYS`.
- Deleted `src/utils/book_helpers.py` module.
- Removed `src/utils/text_utils.py:is_fuzzy_match`.
- Removed old Import Window style/focus variables and methods documented below in cleanup history.
- Removed old Preferences and Book List Import methods documented below in cleanup history.
- Removed production `src/web/web_book_api.py:page_id`; remaining `page_id` references are in test/debug code.

**Note (corrected June 2, 2026):** `scan_files_processed` and `scan_total_files` were previously documented as false positives but are assigned-only dead state; see June 2 actionable items.

### April 27, 2026 — Web Fetch Bug Fix

**Issue Found:** Web fetch was failing because main window checked wrong field names
- Main window checked for `description`, `published_year`, `pages`, `language`
- API actually returns `plot`, `year`, `rating`, `ratings_count`
- Fixed field name mismatches in `main_window.py` meaningful fields check

**Result:** Web fetch now properly detects when real data is found and opens the metadata window

### Items Removed:

**src/ui/preferences_window.py**
- Line 1199: `focus_autocorrect_section` method (orphaned focus method)

**src/ui/import_window.py**
- Line 522: `checkbox_style` variable (unused stylesheet)
- Line 563: `table_style` variable (unused stylesheet)

**src/ui/book_list_import_window.py**
- Line 1294: `on_headers_toggled` method (orphaned slot method)

**src/web/web_book_api.py**
- Line 578: `page_id` variable (changed loop to `for _, page_data in pages.items():`)

**src/utils/book_helpers.py**
- Entire file deleted (unused module with `apply_web_field`, `apply_author_field`, `apply_series_field`)

**src/utils/text_utils.py**
- Line 104: `is_fuzzy_match` function (unused fuzzy matching utility)

**build_trial.bat**
- Lines 46-47: `TRIAL_BUILD` and `TRIAL_DAYS` echo statements (unused legacy flags)

### Items Verified as Used (Kept):

**src/database/queries.py**
- `total_time_hours`, `total_hours_read` (statistics display)

**src/web/web_book_api.py**
- `_title_matches` method (well-tested helper, used by `get_book_metadata`)

**src/build_config.py**
- `TRIAL_BUILD_DATE` (active trial mechanism)

### Items Removed:

**src/accessibility/icon_helper.py**
- Line 13: `relative_path` variable

**src/ui/import_window.py**
- Line 232: `current_formats_text` attribute
- Line 255: `_scan_prompt_open` attribute
- Line 526: `lineedit_style` variable
- Line 697: `require_selection` variable
- Line 964: `on_focus_list` method
- Line 980: `_hide_table_cell_highlight` method
- Line 1097: `include_valid` variable (parameter removed from `_configure_error_filter_options`)
- Lines 1429-1443: `path_type` variables (simplified path validation logic)

**src/ui/preferences_window.py**
- Line 32: `QPoint` import

**src/ui/web_metadata.py**
- Line 573: `_has_any_web_data` method

**src/web/web_book_api.py**
- Line 654: `flip_name` variable (parameter removed from `_apply_author_transformations`)

---

## April 19, 2026 — Accessibility/Screen Reader Popup Removal

All 'No screen reader active' popups have been removed from the following windows:
- Web Metadata Window (Alt+/ now does nothing if no screen reader is present)
- All other windows (Main, Reading History, Import Progress, Import Detail, Collection, Name List) already followed this pattern or did not show a popup.

Alt+/ (Read Status Bar) now only announces to screen readers if one is active; otherwise, it does nothing (no popup, no message).

---
