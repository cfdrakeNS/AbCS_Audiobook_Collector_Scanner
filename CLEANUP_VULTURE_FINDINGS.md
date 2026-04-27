# Vulture Cleanup Process

1. Read this document noting the false positives that are documented.
2. Do a vulture scan of the code.
3. Update the doc with your findings.
4. Do not remove existing text; add your findings under the 'Actionable Items' section.

---

# Actionable Items (Current - April 26, 2026)

Items that need verification or cleanup, organized by file:

## src/build_config.py
- **Line 2**: `TRIAL_BUILD` - Removed from build_trial.bat (unused legacy flag)
- **Line 3**: `TRIAL_DAYS` - Removed from build_trial.bat (unused legacy flag)

## src/database/queries.py
- **Line 669**: `total_time_hours` attribute - Keep (used by statistics display)
- **Line 675**: `total_hours_read` attribute - Keep (used by statistics display)

## src/ui/book_list_import_window.py
- **Line 2043**: `get_or_create_book_list_collection` method - Not found in current code (may have been removed already)
- **Line 1294**: `on_headers_toggled` method - Removed (orphaned slot method, never connected to checkbox)

## src/ui/import_window.py
- **Line 522**: `checkbox_style` variable - Removed (unused stylesheet definition)
- **Line 563**: `table_style` variable - Removed (unused stylesheet definition)

## src/ui/preferences_window.py
- **Line 738**: `_sync_fallback_visual_alignment` method - Not found in current code (may have been removed already)
- **Line 1199**: `focus_autocorrect_section` method - Removed (not connected to any keyboard shortcuts)

## src/utils/book_helpers.py
- **Line 14**: `apply_web_field` function - File deleted (entire module unused)
- **Line 55**: `apply_author_field` function - File deleted (entire module unused)
- **Line 90**: `apply_series_field` function - File deleted (entire module unused)

## src/utils/text_utils.py
- **Line 104**: `is_fuzzy_match` function - Removed (unused fuzzy matching utility)

## src/web/web_book_api.py
- **Line 65**: `_title_matches` method - Keep (well-tested helper, intentionally reserved for future use)
- **Line 578**: `page_id` variable - Removed (changed loop to `for _, page_data in pages.items():`)

## Review Notes
- `src/build_config.py` uses `TRIAL_BUILD_DATE` in `build_trial.bat`; do not remove.
- `src/database/queries.py` attributes `total_time_hours` and `total_hours_read` are used by statistics display logic; keep.
- `src/ui/book_list_import_window.py` `on_headers_toggled` is a real checkbox slot and is confirmed not to be a false positive. `get_or_create_book_list_collection` still requires dynamic usage search.
- `src/ui/import_window.py` `checkbox_style` is used by `apply_control_styles()` and should remain.
- `src/ui/preferences_window.py` methods `_sync_fallback_visual_alignment` and `focus_autocorrect_section` both appear to support layout/focus behavior and should be verified before removal.
- `src/utils/book_helpers.py` helper functions are probably used as shared metadata helpers; reference search is required.
- `src/utils/text_utils.py` `is_fuzzy_match` is a valid fuzzy matching utility; confirm call sites before deleting.
- `src/web/web_book_api.py` `_title_matches` is an internal matching helper; `page_id` is a lint-only unused loop variable.

---

# False Positives (Do Not Remove)

These items are flagged by vulture but are actually used or required:

## src/database/connection.py
- **Line 75**: `row_factory` attribute - Required SQLite idiom

## src/ui/book_list_import_window.py
- **Line 21**: `DataFrame` class - Fallback for missing pandas
- **Line 1294**: `on_headers_toggled` method - Required for header toggle functionality

## src/ui/import_window.py
- **Lines 1455-1465**: `scan_files_processed`, `scan_total_files` - Used via `nonlocal` in nested `on_progress` function

---

# Cleanup History

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
- `_title_matches` method (well-tested helper, reserved for future use)

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
