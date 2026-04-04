# AbCS Dead Code Cleanup - Vulture Findings
**Created:** April 3, 2026  
**Last Updated:** April 4, 2026 — Phase 1 + 90% imports complete and tested  
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

## 60% Confidence - Unused Methods/Attributes (~40+ items)

**Warning:** These may be:
- Qt signal callbacks (invoked indirectly by Qt framework)
- Plugin entry points
- Dynamic method lookups
- Base class methods required for subclass contract
- API methods meant for external use

**Common patterns observed:**
- `on_*_clicked()` - Qt button click handlers (likely needed despite vulture warning)
- `setup_*()` - Setup methods called dynamically or by framework
- `__*__()` - Dunder methods (protocol methods)
- Accessibility callbacks from TextEdit, LineEdit, ComboBox, etc.

**Action:** Manual review required per item. Flag false positives for future vulture configuration via `.vultureignore`.

### Likely False Positives (Qt Slot Decorators)
- Button click handlers in UI windows
- Combo box activation handlers
- Line edit text changed handlers
- Table double-click handlers
- Menu action triggered handlers

### Candidates for Removal (after manual verification)
- Orphaned utility methods not called by any other function
- Old feature methods superseded by new implementations
- Debug-only methods with no production callers
- Stub implementations left as placeholders

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

