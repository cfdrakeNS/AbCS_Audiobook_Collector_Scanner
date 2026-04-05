# AbCS Dead Code Cleanup - Vulture Findings
**Created:** April 3, 2026  
**Last Updated:** April 5, 2026 - 100% and 90% phases completed and validated  
**Tool:** vulture (AST-based dead code detection)  
**Generated:** `python -m vulture src`

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| **100% Confidence - Unreachable Code** | 2 | DONE (April 4, 2026) |
| **90% Confidence - Unused Imports** | 7 | DONE (April 4, 2026) |
| **100% Confidence - Unused Local Variables** | 7 | DONE (April 4, 2026) |
| **60% Confidence - Unused Methods/Attributes** | 80+ (latest scan) | In progress, manual review |
| **TOTAL** | 90+ | Phase 1 complete; Phase 2 active |

**Phase 1 net line reduction: -111 lines** (dead code and imports/locals cleanup)  
**Validation status:** Completed manual smoke checks for impacted windows and workflows.

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
Status: Code cleanup applied and manual smoke test PASSED on April 5, 2026.

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
Status: Code cleanup applied and manual smoke test PASSED on April 5, 2026.

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
Status: Code cleanup completed and syntax validated on April 5, 2026. Ready for manual UI test.

Removals completed:
- removed unreachable dialog code block after return statement (lines 913-962)
- removed method `find_next_match` 
- removed method `find_previous_match`
- removed helper method `_find_direction` (no longer called)

Remaining vulture findings after this pass:
- `unused class NameListWindow` (60%) - expected false positive when scanning single file
- `unused attribute _last_find_row` (60%) - may be retained; verify in UI test

Test focus after changes:
- Author/Series/Genre/Collection list navigation
- Arrow-key navigation and status announcements
- Edit mode behavior (Alt+E)
- Find/search behavior for remaining functionality

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

## Next Steps

1. Continue with the 60% window-by-window cleanup sequence.
2. For each window, commit only after inspect -> cleanup -> test is complete.
3. Keep this document updated with per-window decisions and outcomes.

