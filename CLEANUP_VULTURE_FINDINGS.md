# AbCS Dead Code Cleanup - Vulture Findings
**Created:** April 3, 2026  
**Last Updated:** April 4, 2026  
**Tool:** vulture (AST-based dead code detection)  
**Generated:** `python -m vulture src`

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| **100% Confidence - Unreachable Code** | 2 | ✅ DONE (April 4, 2026) |
| **90% Confidence - Unused Imports** | 7 | Pending (Phase 2) |
| **100% Confidence - Unused Local Variables** | 7 | ✅ DONE (April 4, 2026) |
| **60% Confidence - Unused Methods/Attributes** | ~40+ | Needs manual review |
| **TOTAL** | ~56+ | Phase 1 complete |

**Phase 1 net line reduction: −107 lines** (7 added, 114 deleted across 7 files)

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

## 90% Confidence - Unused Imports (SAFE TO REMOVE)

These imports are never referenced in their respective files:

### 1. EasyID3 - `src/core/tag_reader.py`
```python
from mutagen.id3 import EasyID3
```
**Usage:** Never called directly (mutagen.ID3 is used instead)  
**Action:** Remove import

### 2. QSplashScreen - `src/main.py`
```python
from PySide6.QtWidgets import QSplashScreen
```
**Usage:** Possibly replaced by alternative splash implementation  
**Action:** Remove import

### 3. QFont - Location TBD
**Usage:** Never instantiated  
**Action:** Remove import

### 4. QPixmap - Location TBD
**Usage:** Never created  
**Action:** Remove import

### 5. announce_form_field - `src/accessibility/` (likely)
**Usage:** Never called  
**Action:** Remove import

### 6. QButtonGroup - `src/ui/` (likely)
**Usage:** Never used for grouping buttons  
**Action:** Remove import

### 7. QRadioButton - `src/ui/` (likely)
**Usage:** Never instantiated  
**Action:** Remove import

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
2. Remove 7 unused imports from respective files ← **next**
3. ✅ Removed 7 unused local variables (renamed to `_` prefix or removed unused params)
4. **Net reduction: −107 lines** across 7 files; no behavior change; all lint checks pass

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
- **No regression risk:** Changes are additive or fixing known bugs; no dead code removal yet

---

## Next Steps

When ready to proceed:
1. Run `python -m vulture src > vulture_detailed_output.txt` for complete line-number details
2. Review Phase 1 items first (fastest, safest)
3. Tag removal PRs with label "cleanup/dead-code" for tracking
4. Test thoroughly before merging

