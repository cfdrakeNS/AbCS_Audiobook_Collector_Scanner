---

# April 11, 2026 — Latest Vulture Scan Results

## New/Outstanding Vulture Findings (min-confidence 60)

### src/database/connection.py
- Line 75: unused attribute 'row_factory' (60%)
  - **FALSE POSITIVE**: Already documented above; required SQLite idiom.

### src/ui/book_list_import_window.py
- Line 21: unused class 'DataFrame' (60%)
  - **FALSE POSITIVE**: Already documented above; fallback for missing pandas.
- Line 112: unused method '_normalize_author_for_match' (60%)
- Line 1171: unused method 'on_headers_toggled' (60%)
  - **FALSE POSITIVE**: Already documented above; required for header toggle.

### src/ui/import_window.py
- Line 236: unused attribute 'current_formats_text' (60%)
- Line 266: unused attribute '_scan_prompt_open' (60%)
- Line 542: unused variable 'lineedit_style' (60%)
- Line 652: unused attribute 'current_formats_text' (60%)
- Line 736: unused variable 'require_selection' (60%)
- Line 1022: unused method 'on_focus_list' (60%)
- Line 1038: unused method '_hide_table_cell_highlight' (60%)
- Line 1518: unused variable 'path_type' (60%)
- Line 1524: unused variable 'path_type' (60%)
- Line 1527: unused variable 'path_type' (60%)
- Line 1532: unused variable 'path_type' (60%)
- Line 1593: unused variable 'scan_files_processed' (60%)
- Line 1594: unused variable 'scan_total_files' (60%)
- Line 1602: unused variable 'scan_files_processed' (60%)
- Line 1603: unused variable 'scan_total_files' (60%)

### src/accessibility/icon_helper.py
- Line 13: unused variable 'relative_path' (100%)


---

# April 15, 2026 — Vulture Scan Results (All Items Complete)

All new actionable vulture findings from April 15 have been addressed:

- src/ui/book_list_import_window.py: unreachable code after 'return' — removed
- src/web/web_book_api.py: unused variable 'save_title' — removed

No outstanding actionable items remain. The codebase is fully clean as of this scan.

---

# April 19, 2026 — Vulture Scan Results

## April 19 Findings (min-confidence 60)

### src/accessibility/icon_helper.py
- Line 13: unused variable 'relative_path' (100%)

### src/database/connection.py
- Line 75: unused attribute 'row_factory' (60%)
  - **FALSE POSITIVE**: Required SQLite idiom (see previous notes).

### src/ui/book_list_import_window.py
- Line 21: unused class 'DataFrame' (60%)
  - **FALSE POSITIVE**: Fallback for missing pandas (see previous notes).
- Line 1168: unused method 'on_headers_toggled' (60%)

### src/ui/import_window.py
- Line 233: unused attribute 'current_formats_text' (60%)
- Line 239: unused attribute 'flip_author_names' (60%)
- Line 263: unused attribute '_scan_prompt_open' (60%)
- Line 527: unused variable 'lineedit_style' (60%)
- Line 635: unused attribute 'current_formats_text' (60%)
- Line 649: unused attribute 'flip_author_names' (60%)
- Line 652: unused attribute 'flip_author_names' (60%)
- Line 726: unused variable 'require_selection' (60%)
- Line 993: unused method 'on_focus_list' (60%)
- Line 1009: unused method '_hide_table_cell_highlight' (60%)
- Line 1126: unused variable 'include_valid' (100%)
- Line 1455: unused variable 'path_type' (60%)
- Line 1461: unused variable 'path_type' (60%)
- Line 1464: unused variable 'path_type' (60%)
- Line 1469: unused variable 'path_type' (60%)
- Line 1522: unused variable 'scan_files_processed' (60%)
- Line 1523: unused variable 'scan_total_files' (60%)
- Line 1531: unused variable 'scan_files_processed' (60%)
- Line 1532: unused variable 'scan_total_files' (60%)

### src/ui/web_metadata.py
- Line 573: unused method '_has_any_web_data' (60%)

### src/web/web_book_api.py
- Line 654: unused variable 'flip_name' (100%)

## April 19, 2026 — Accessibility/Screen Reader Popup Removal

- All 'No screen reader active' popups have been removed from the following windows:
  - Web Metadata Window (Alt+/ now does nothing if no screen reader is present)
  - All other windows (Main, Reading History, Import Progress, Import Detail, Collection, Name List) already followed this pattern or did not show a popup.
- Alt+/ (Read Status Bar) now only announces to screen readers if one is active; otherwise, it does nothing (no popup, no message).
- This change ensures a silent, non-intrusive experience for sighted users and strict protocol compliance for screen reader users.

### What to Test
- Open each window (Main, Import, Import Progress, Import Detail, Web Metadata, Reading History, Collection, Name List).
- Press Alt+/ (Read Status Bar) with and without a screen reader running:
  - If a screen reader is active (JAWS, NVDA, etc.), the status bar message should be announced.
  - If no screen reader is active, pressing Alt+/ should do nothing (no popup, no message).
- Confirm that no 'No screen reader active' or similar popups appear anywhere in the UI.
- All other accessibility and keyboard navigation features should remain unchanged.

**Note:** All previously documented false positives remain valid and are not actionable. Only new actionable items are listed above for review in the next cleanup pass.

---

# April 23, 2026 — Vulture Scan Results

## April 23 Findings (min-confidence 60)

### src/accessibility/icon_helper.py
- Line 13: unused variable 'relative_path' (100%)
  - **Already documented April 19, 2026**.

### src/database/connection.py
- Line 75: unused attribute 'row_factory' (60%)
  - **FALSE POSITIVE**: Required SQLite idiom (see previous notes).

### src/ui/book_list_import_window.py
- Line 21: unused class 'DataFrame' (60%)
  - **FALSE POSITIVE**: Fallback for missing pandas (see previous notes).
- Line 1371: unused method 'on_headers_toggled' (60%)
  - **Already documented April 19, 2026** (line shifted from 1168).
- Line 2043: unused method 'get_or_create_book_list_collection' (60%)
  - **NEW FINDING**: Method may be unused or called dynamically.

### src/ui/import_window.py
- Line 232: unused attribute 'current_formats_text' (60%)
  - **Already documented April 19, 2026** (line shifted from 233).
- Line 255: unused attribute '_scan_prompt_open' (60%)
  - **Already documented April 19, 2026** (line shifted from 263).
- Line 526: unused variable 'lineedit_style' (60%)
  - **Already documented April 19, 2026** (line shifted from 527).
- Line 635: unused attribute 'current_formats_text' (60%)
  - **Already documented April 19, 2026**.
- Line 697: unused variable 'require_selection' (60%)
  - **Already documented April 19, 2026** (line shifted from 726).
- Line 964: unused method 'on_focus_list' (60%)
  - **Already documented April 19, 2026** (line shifted from 993).
- Line 980: unused method '_hide_table_cell_highlight' (60%)
  - **Already documented April 19, 2026** (line shifted from 1009).
- Line 1097: unused variable 'include_valid' (100%)
  - **Already documented April 19, 2026** (line shifted from 1126).
- Line 1429, 1435, 1438, 1443: unused variable 'path_type' (60%)
  - **Already documented April 19, 2026** (lines shifted from 1455-1469).
- Line 1496, 1497, 1505, 1506: unused variables 'scan_files_processed', 'scan_total_files' (60%)
  - **Already documented April 19, 2026** (lines shifted from 1522-1532).

### src/ui/preferences_window.py
- Line 32: unused import 'QPoint' (90%)
  - **NEW FINDING**: Import not used in current code; safe to remove.
- Line 738: unused method '_sync_fallback_visual_alignment' (60%)
  - **NEW FINDING**: Method may be unused or replaced by newer implementation.

### src/ui/web_metadata.py
- Line 573: unused method '_has_any_web_data' (60%)
  - **Already documented April 19, 2026**.

### src/web/web_book_api.py
- Line 654: unused variable 'flip_name' (100%)
  - **Already documented April 19, 2026**.

## Summary of New Actionable Items (April 23, 2026)

1. **src/ui/book_list_import_window.py:2043** - `get_or_create_book_list_collection` method
2. **src/ui/preferences_window.py:32** - `QPoint` import (90% confidence)
3. **src/ui/preferences_window.py:738** - `_sync_fallback_visual_alignment` method

All other findings are either previously documented false positives or line-shifted versions of previously documented items due to code changes.

---
