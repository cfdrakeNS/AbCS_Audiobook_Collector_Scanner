# Vulture Cleanup Process

1. Read this document noting the false positives that are documented.
2. Do a vulture scan of the code.
3. Update the doc with your findings.
4. Do not remove existing text; add your findings under the 'Actionable Items' section.

---

# Actionable Items (Current - April 26, 2026)

Items that need verification or cleanup, organized by file:

## src/build_config.py
- **Line 2**: `TRIAL_BUILD` - Trial build flag, verify if used in build process
- **Line 3**: `TRIAL_DAYS` - Trial days setting, verify if used in build process

## src/database/queries.py
- **Line 669**: `total_time_hours` attribute - May be used for reading statistics display
- **Line 675**: `total_hours_read` attribute - May be used for reading statistics display

## src/ui/book_list_import_window.py
- **Line 2043**: `get_or_create_book_list_collection` method - Verify if dynamically called

## src/ui/import_window.py
- **Line 522**: `checkbox_style` variable - Defined but not used; safe to remove

## src/ui/preferences_window.py
- **Line 738**: `_sync_fallback_visual_alignment` method - Verify if unused or replaced
- **Line 1199**: `focus_autocorrect_section` method - Verify if unused or called dynamically

## src/utils/book_helpers.py
- **Line 14**: `apply_web_field` function - Verify if unused or reserved for future use
- **Line 55**: `apply_author_field` function - Verify if unused or reserved for future use
- **Line 90**: `apply_series_field` function - Verify if unused or reserved for future use

## src/utils/text_utils.py
- **Line 104**: `is_fuzzy_match` function - Verify if unused or reserved for future use

## src/web/web_book_api.py
- **Line 65**: `_title_matches` method - Verify if unused or reserved for future use
- **Line 578**: `page_id` variable - Extracted but not used; safe to remove

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

## April 23, 2026 — Cleanup Complete

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
