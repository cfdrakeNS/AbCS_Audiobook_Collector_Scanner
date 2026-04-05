# AbCS Dead Code Cleanup - Vulture Findings
**Created:** April 3, 2026  
**Last Updated:** April 5, 2026 — 60% section expanded to window-by-window review + test order  
**Tool:** vulture (AST-based dead code detection)  
**Generated:** `python -m vulture src`

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| **100% Confidence - Unreachable Code** | 2 | ✅ DONE (April 4, 2026) |
| **90% Confidence - Unused Imports** | 7 | ✅ DONE (April 4, 2026) |
| **100% Confidence - Unused Local Variables** | 7 | ✅ DONE (April 4, 2026) |
| **60% Confidence - Unused Methods/Attributes** | ~40+ | Needs manual review |
| **TOTAL** | ~56+ | Phase 1 complete + validated |

**Phase 1 net line reduction: −107 lines** (7 added, 114 deleted across 7 files)  
**90% imports net reduction: −4 lines** (2 added, 6 deleted across 4 files)

---

## 100% Confidence - Unreachable Code ✅ COMPLETE

### 1. src/main.py:386 ✅
**Issue:** Unreachable code block  
**Context:** Code after `return self.qt_app.exec()` inside `run()` — a dead fragment of the old `show_splash()` / duplicate `run()` body that could never execute.  
**Removed:** 56 lines deleted, 0 added

### 2. src/ui/name_list_window.py:913 ✅
**Issue:** Unreachable code block  
**Context:** Full `QDialog` shortcut-help build block after the `return` statement in `_build_read_status_message()`. The method already returned on the previous line so this dialog was never shown.  
**Removed:** 51 lines deleted, 0 added

---

## 90% Confidence - Unused Imports ✅ COMPLETE

All 7 unused imports removed (April 4, 2026). Net: −4 lines across 4 files.

| # | Symbol | File | Notes |
|---|--------|------|-------|
| 1 | `EasyID3` | `src/core/tag_reader.py` | `mutagen.ID3` used instead; easy-id3 import removed |
| 2 | `QSplashScreen` | `src/main.py` | Replaced by custom dialog splash; entire symbol removed |
| 3 | `QFont` | `src/main.py` | Never instantiated; inline on same line as QPixmap |
| 4 | `QPixmap` | `src/main.py` | Never created; entire `from PySide6.QtGui import …` line dropped |
| 5 | `announce_form_field` | `src/ui/book_details.py` | Never called in this file; removed from import list |
| 6 | `QButtonGroup` | `src/ui/book_list_import_window.py` | UI uses no radio-group logic; removed |
| 7 | `QRadioButton` | `src/ui/book_list_import_window.py` | No radio buttons in this window; removed |

---

## 100% Confidence - Unused Local Variables ✅ COMPLETE

7 confirmed instances addressed (actual vulture count; original estimate was ~15):

| File | Line | Variable | Fix |
|------|------|----------|-----|
| `src/accessibility/accessible_events.py` | 73 | `announcement_widget` param | Renamed to `_announcement_widget` |
| `src/ui/book_list_import_window.py` | 33 | `filepath` param in `read_csv` stub | Renamed to `_filepath` |
| `src/ui/book_list_import_window.py` | 37 | `filepath` param in `read_excel` stub | Renamed to `_filepath` |
| `src/ui/book_list_import_window.py` | 804 | `icon_type` param in `show_accessible_message` | Removed unused param |
| `src/ui/collection_window.py` | 325 | `prev_row`, `prev_col` params | Renamed to `_prev_row`, `_prev_col` |
| `src/ui/import_progress_window.py` | 319 | `issues_text` param in `update_current_item` | Removed unused kwarg |
| `src/ui/main_window.py` | 2475 | `previous` param in `on_current_cell_changed` | Renamed to `_previous` |

---

## 60% Confidence - Window-by-Window Review Plan (One Window at a Time)

Updated from current vulture run (April 5, 2026). This section is now organized for sequential testing: complete one window, test it, then move to the next.

### Review Rule for Every Window

For each flagged item below:
1. Verify if connected via Qt signal/slot, shortcut registration, menu action, or dynamic call.
2. Keep and mark as false positive if it is used indirectly.
3. Remove or refactor only if there are no callers and no framework wiring.
4. Run the window-specific smoke test before moving to the next window.

### Window Queue (Test in This Order)

#### Window 1: Main Window (src/ui/main_window.py)
Flagged items:
- line 360 and 2762: attribute `_web_fetch_cancelled`
- line 365: attribute `filtered_books`
- lines 1633, 1635, 1637: variable `filter_info`
- lines 1639, 1641: variable `collection_info`
- line 2304: method `focus_book_title`
- line 2469: method `move_cursor_to_row`
- line 2487: method `announce_current_cell`
- line 2557: method `select_range_to_current_row`

Test focus after changes:
- Table navigation and cell announcements
- Search, filtering, and returning to previous row
- Multi-select behavior (Shift+Click and Ctrl+Click)

#### Window 2: Book Details (src/ui/book_details.py)
Flagged items:
- line 176: attribute `shortcut_manager`
- line 347: variable `lineedit_style`

Test focus after changes:
- Open, edit, save, and navigate Prev/Next
- Keyboard shortcuts in form fields

#### Window 3: Name List Window (src/ui/name_list_window.py)
Flagged items:
- line 997: method `find_next_match`
- line 1000: method `find_previous_match`

Test focus after changes:
- Find next/previous behavior
- Arrow-key navigation and status announcements

#### Window 4: Import Window (src/ui/import_window.py)
Flagged items:
- line 236 and 651: attribute `current_formats_text`
- line 266: attribute `_scan_prompt_open`
- line 541: variable `lineedit_style`
- line 1023: method `on_focus_list`
- line 1039: method `_hide_table_cell_highlight`
- lines 1524, 1530, 1533, 1538: variable `path_type`
- lines 1598, 1607: variable `scan_files_processed`
- lines 1599, 1608: variable `scan_total_files`

Test focus after changes:
- Scan prompt flow
- Table focus/highlight behavior
- Start/stop scan and progress updates

#### Window 5: Book List Import Window (src/ui/book_list_import_window.py)
Flagged items:
- line 21: class `DataFrame`
- line 125 and 944: attribute `_last_csv_encoding`
- line 696: method `toggle_mode`
- line 709: method `focus_mapping_row`
- line 802: method `show_accessible_message`
- line 1086: method `on_new_books_toggled`
- line 1093: method `on_headers_toggled`
- line 1136: method `on_read_date_toggled`

Test focus after changes:
- CSV/XLSX mapping workflow
- Toggle options affecting mapping and preview
- Accessible message dialogs and keyboard flow

#### Window 6: Import Progress Window (src/ui/import_progress_window.py)
Flagged items:
- line 198: variable `lineedit_style`
- line 319: method `update_current_item`
- line 383: method `mark_add_complete`

Test focus after changes:
- Progress updates during scan/import
- Completion state and final status messaging

#### Window 7: Import Detail Window (src/ui/import_detail_window.py)
Flagged items:
- line 689: variable `lineedit_style`

Test focus after changes:
- Open item details, edit fields, save/discard behavior

#### Window 8: Preferences Window (src/ui/preferences_window.py)
Flagged items:
- line 622: method `_sync_reader_keywords_width`
- line 657: variable `lineedit_style`
- line 1428: method `on_run_display_audit`

Test focus after changes:
- Theme/scaling controls
- Reader keywords controls and display-audit action

#### Window 9: Backup/Restore Window (src/ui/backup_restore_window.py)
Flagged items:
- line 356: method `_is_backup_list_focused`

Test focus after changes:
- Backup list keyboard focus
- Backup/restore action buttons

#### Window 10: Web Metadata Window (src/ui/web_metadata.py)
Flagged items:
- line 73: attribute `refresh_count`
- line 429: method `_adjust_plot_height`
- line 557: method `generate_realistic_plot`
- line 758: method `clear_web_indicators`
- line 766: method `show_changes_popup`

Test focus after changes:
- Metadata fetch/refresh cycle
- Any chart/popup behavior tied to scrape results

### Non-Window 60% Items (Track Separately)

These are important but should be handled outside the window sequence:
- accessibility modules (`accessible_events.py`, `shortcuts.py`, `scaling.py`, `theme_manager.py`)
- core modules (`import_scanner.py`, `tag_reader.py`, `validator.py`)
- database modules (`connection.py`, `models.py`, `queries.py`, `reading_queries.py`)
- app entry (`main.py`), web API (`src/web/web_book_api.py`)

### Execution Mode for This Cleanup

- Only one window per cycle.
- For each cycle: inspect -> edit -> run smoke test -> record result.
- Do not batch multiple windows in one edit set.
- Add confirmed indirect Qt callbacks to `.vultureignore` after verification.

---

## Cleanup Strategy

### Phase 1: Quick Wins ✅ COMPLETE (April 4, 2026)
1. ✅ Removed 2 unreachable code blocks (src/main.py, src/ui/name_list_window.py)
2. ✅ Removed 7 unused imports (4 files) ← **done this session**
3. ✅ Removed 7 unused local variables (renamed to `_` prefix or removed unused params)
4. **Net reduction: −111 lines** across 9 files; no behavior change; all lint checks pass

### Phase 2: Targeted Review (1-2 hours)
1. Export full vulture output to separate detailed list with line numbers
2. For each 60% confidence item:
   - Check if it's a Qt slot (`@pyqtSlot` or implicit)
   - Check if called dynamically in any other file
   - Check if part of documented API
3. Create `.vultureignore` file for confirmed false positives
4. Move confirmed unused methods to archive
5. **Total risk:** Medium; requires code inspection

### Phase 3: Testing
1. Run full test suite (if available)
2. Launch app and test all major workflows
3. Check screen reader integration (JAWS/NVDA)
4. Verify accessibility shortcuts still work

---

## Notes

- **odfpy import addition:** Successfully added to requirements.txt (not a removal)
- **accessible_date_field.py:** Already archived (April 3, 2026)
- **Import fixes:** All four issues (time parsing, CSV encoding, label width, ODS support) COMPLETE and not flagged by vulture as problematic
- **No regression risk:** All changes are dead code removals; no behavior change; lint clean
- **Running total:** −111 lines removed across Phases 1 and 90% imports
- **Testing status:** 100% and 90% cleanup changes validated via manual checklist (April 4, 2026)

---

## Testing Checklist for 100% + 90% Changes ✅ COMPLETE (April 4, 2026)

Each area maps to a file that was edited. All checklist items were completed.

### App Startup (src/main.py — unreachable block + 3 imports removed)
- [x] App launches without crash on a populated database
- [x] App launches without crash on an empty database (shows the empty-library dialog)
- [x] Splash/statistics dialog appears and auto-closes or can be dismissed with Continue

### Name List Window — Authors / Series / Genre (src/ui/name_list_window.py — unreachable block removed)
- [x] Open Authors window; Alt+/ reads the status bar correctly
- [x] Navigate rows with arrow keys; status bar announces current name and book count
- [x] F1 shortcut help dialog opens and displays correctly (the dead duplicate block was the shortcut dialog)

### Status Bar Announcements — all windows (src/accessibility/accessible_events.py — param renamed)
- [x] Status bar messages appear in at least three different windows (main, book details, import)
- [x] With a screen reader active, messages are announced on status changes

### Collection Window (src/ui/collection_window.py — on_selection_changed signature)
- [x] Clicking or arrowing between rows loads the correct collection name into the editor
- [x] Selecting a row does not throw a TypeError

### Import Progress Window (src/ui/import_progress_window.py — issues_text kwarg removed)
- [x] Start a folder scan; the progress window opens and updates file/book counts
- [x] No crash or TypeError during the scan cycle

### Book List Import — CSV / XLSX (src/ui/book_list_import_window.py — 3 changes)
- [x] Browse for a CSV file; column mapping combos populate correctly
- [x] Browse for an XLSX file; same mapping flow works
- [x] Any accessible message dialogs in the window display without a TypeError (icon_type param removed)

### Book Details Window (src/ui/book_details.py — announce_form_field import removed)
- [x] Open a book; all fields are editable and save correctly
- [x] Tab through all fields; no ImportError or NameError in the console

### Audio Tag Import — MP3 / FLAC / M4A (src/core/tag_reader.py — EasyID3 import removed)
- [x] Scan a folder containing MP3 files; tags (title, author, year) are read correctly
- [x] Scan a folder with FLAC or M4A files; no import errors

### Main Window Cell Navigation (src/ui/main_window.py — previous param renamed)
- [x] Arrow up/down through the book table; last-focused book ID is tracked correctly
- [x] Press Escape after searching; cursor returns to the previously focused row

---

## Next Steps

1. Phase 2: Run `python -m vulture src` and review each 60% item manually
2. Create `.vultureignore` for confirmed Qt false positives
3. Archive or delete confirmed orphan methods
4. After Phase 2 removals, run targeted regression checks for impacted windows/workflows

