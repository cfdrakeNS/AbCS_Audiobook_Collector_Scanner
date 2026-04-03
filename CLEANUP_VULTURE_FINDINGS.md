# AbCS Dead Code Cleanup - Vulture Findings
**Date:** April 3, 2026  
**Tool:** vulture (AST-based dead code detection)  
**Generated:** `python -m vulture src`

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| **100% Confidence - Unreachable Code** | 2 | Ready to remove |
| **90% Confidence - Unused Imports** | 7 | Ready to remove |
| **100% Confidence - Unused Local Variables** | ~15 | Ready to remove |
| **60% Confidence - Unused Methods/Attributes** | ~40+ | Needs manual review |
| **TOTAL** | ~65+ | Pending review |

---

## 100% Confidence - Unreachable Code (SAFE TO REMOVE)

### 1. src/main.py:386
**Issue:** Unreachable code block  
**Context:** Code after return statement  
**Action:** Delete the unreachable block

### 2. src/ui/name_list_window.py:913
**Issue:** Unreachable code block  
**Context:** Code after return statement  
**Action:** Delete the unreachable block

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

## 100% Confidence - Unused Local Variables (SAFE TO REMOVE)

~15 instances of variables assigned but never used:

**Common patterns:**
- Loop variables that iterate but value is never read
- Return values captured but never used
- Intermediate calculations stored but not referenced
- Exception handlers storing exception object that doesn't use it

**Action:** Identify and remove via vulture line numbers; replace with `_` placeholder in Python where appropriate for loop variables.

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

### Phase 1: Quick Wins (30 minutes)
1. Remove 2 unreachable code blocks from src/main.py and src/ui/name_list_window.py
2. Remove 7 unused imports from respective files
3. Remove ~15 unused local variables (use grep to locate exact lines)
4. **Total risk:** Very low; syntax validation only needed

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

