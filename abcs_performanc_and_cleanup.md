# AbCS Performance and Cleanup Plan

This document combines the performance optimization plan with code cleanup tasks. Performance work takes priority to fix broken features first.

---

## Executive Summary

**Priority Order:**
1. Performance Tuning (fixes crashes and hangs)
2. Code Cleanup (removes dead code and duplication)
3. Accessibility Compliance Audit

**Estimated Effort:**
- Performance: 15 hours
- Cleanup: 12 hours
- **Total: 27 hours**

---

# Part 1: Performance Optimization

## Phase 0: Benchmarking (Complete)
*Status: Baseline Established with 34,679 records*

### Baseline Results:
| Feature | Current Time | Status |
|---------|--------------|--------|
| Library Load (34.7k) | ~0.58s - 0.63s | Acceptable |
| SQL Sort | ~0.62s | Acceptable |
| Search (Filter) | ~0.55s | Acceptable |
| Import (Scan) | ~0.56s | Acceptable |
| **Folder Import (Add)** | **9.14s for 6 books** | **CRITICAL** |
| **Book List Import (XLS)** | **CRASHED** | **BROKEN** |

**Root Cause:** Fuzzy duplicate check is the bottleneck. Setting fuzzy threshold to 0 resolves the primary hang.

---

## Phase 1: Quick Wins (QTableWidget Optimization)

### Core Problem
`QTableWidget` creates a Python object for every single cell. 30,000 books × 5 columns = 150,000 objects. This causes screen reader lag and "Not Responding" issues.

### Technique 1: Clean Slate Strategy
When updating the table, never remove rows one by one. It forces the GUI to reflow 30,000 times.

```python
# Fast - drops entire dataset instantly
self.tableWidget.setRowCount(0)

# Slow - reflows layout for each deletion
for row in range(self.tableWidget.rowCount()):
    self.tableWidget.removeRow(0)
```

### Technique 2: Block Repaint Signals
Most effective single optimization. Prevents Qt from redrawing after every `setItem()` call.

```python
self.tableWidget.setUpdatesEnabled(False)
# ... run your loop to add 30,000 rows ...
self.tableWidget.setUpdatesEnabled(True)
```

**Impact:** 10-second stutter becomes 1-second instant load.

### Technique 3: Pre-Size the Table
Allocate memory once instead of 30,000 times during loop.

```python
self.tableWidget.setRowCount(total_books)
# ... now populate with setItem ...
```

### Technique 4: Turn Off Sorting During Loads
If sorting is enabled, Qt re-sorts the entire library after every single book addition.

```python
self.tableWidget.setSortingEnabled(False)
# ... load all data ...
self.tableWidget.setSortingEnabled(True)
```

### Technique 5: Threading for Data Crunch
If windows feel "frozen" while opening, the GUI thread is waiting for database/disk.

```python
# Use QThread or QRunnable to fetch 30,000 records in background
# 1. Window opens immediately (blank or "Loading")
# 2. Background thread fetches data
# 3. Thread signals GUI to fill the list
```

**Benefit:** Keeps interface responsive. JAWS won't report "Not Responding."

---

## Phase 2: Module-by-Module Implementation

### Module 1: Main Library View (`src/ui/main_window.py`)
*Priority: Critical*

#### Changes:
1. **Lightweight Data:** Modify `BookTableModel` to use tuples/dictionaries instead of full `Book` dataclasses.
2. **Pagination/Chunking:** Update `BookQueries.get_all` to support `LIMIT`/`OFFSET` or `fetchmany`.
3. **Sorting:** Move to SQL level (`ORDER BY`) or use `QSortFilterProxyModel`.
4. **Repaint Control:** Wrap initial load in `setUpdatesEnabled(False/True)` blocks.

#### Testing Strategy:
- Verify JAWS can navigate rows/columns via arrow keys.
- Measure "Time to Open" with 30,000 rows.

---

### Module 2: Import System (`src/ui/import_window.py`)
*Priority: High - Fixes 9.14s bottleneck*

#### Changes:
1. **Background Scanning:** Move file system crawler and ID3 tag extractor into `QThread`.
2. **Pre-Sizing:** Calculate file count before populating table and use `setRowCount(total)`.
3. **Batch Updates:** Timer-based UI refresh (every 100 books) instead of per-file updates.
4. **Sorting:** `setSortingEnabled(False)` before scan, `True` after.

#### Testing Strategy:
- Ensure "Cancel" button remains responsive during large folder scan.
- Confirm Status Bar announces "Scan Complete" via `Alt+/`.

---

### Module 3: Reading History (`src/ui/history_window.py`)
*Priority: Medium*

#### Changes:
1. **Clean Slate:** Replace row-by-row deletion with `table.setRowCount(0)` when changing date filters.
2. **Layout Fixes:** Replace `layout.addStretch()` inside loops with fixed spacers (`QSpacerItem`) or use simpler layouts (`QFormLayout`, `QGridLayout`).

#### Testing Strategy:
- Toggle between "3 Months" and "All Time" - verify instantaneous refresh.
- Ensure layout stability after changes.

---

### Module 4: Database Manager (`src/database/db_manager.py`)
*Priority: Medium*

#### Changes:
1. **Indexed Queries:** Add indexes on `books` table columns: `Title`, `Author_id`, `Series_id`, `Genre_id`, `Collection_id`.
2. **Fetch Optimization:** Use `cursor.fetchmany(N)` (e.g., `N=1000`) instead of `cursor.fetchall()`.
3. **WAL Mode:** Set `PRAGMA journal_mode=WAL` for improved write performance and concurrency.

#### Testing Strategy:
- Run `EXPLAIN QUERY PLAN` on search/sort queries.
- Measure memory usage during large data loads.
- Verify INSERT/UPDATE/DELETE operations remain correct.

---

## Phase 3: The "Down the Road" Choice (QTableView)

If Quick Wins don't achieve target speed, migrate from `QTableWidget` to `QTableView`.

### Comparison:
| Feature | QTableWidget | QTableView |
|---------|--------------|------------|
| Memory | 150,000 objects | 15 rows only |
| Speed at 30k books | 9+ seconds | Same as 3 books |
| Screen Reader | Works, but lags | Fully compatible with JAWS |

### How It Works:
`QTableView` with `QAbstractTableModel` doesn't push data to the table. The table "asks" the model only for visible rows. Memory footprint stays tiny; window opens instantly.

---

## Target Gains

| Feature | Current State | Target State |
|---------|---------------|--------------|
| **30k Library Load** | 5-10 Seconds (Stuttering) | < 1 Second (Instant) |
| **Folder Import** | 9.14s for 6 books | < 2 seconds |
| **Book List Import (XLS)** | Crashes | Works without hang |
| **RAM Usage** | High (Object Overhead) | Low (Data-only) |
| **JAWS Response** | "Not Responding" during load | Continuous Speech |

---

# Part 2: Code Cleanup

**Status:** Mixed compliance with accessibility standards. Several issues found.

**Scope:** 17 UI modules reviewed.

---

## 1. Dead Code

### web_metadata.py
- Lines 6-13: `sys.path.insert` block for running standalone - not needed in production
- Line 605: Comment `# fetch_web_data removed - now handled in main_window.py`
- Lines 1158-1180: `test_web_metadata()` function at module level - test code in production file

### import_window.py
- Lines 730-732: `_update_cancel_button_state()` is empty (Cancel button removed)
- Line 877: Commented shortcut `# self.new_button.setShortcut(QKeySequence("Alt+N"))`
- Line 890: Same pattern for Save button
- Line 903: Same pattern for Delete button

### book_details.py
- Multiple commented-out `setShortcut` lines (pattern repeated)

---

## 2. Duplicated Code

### Pattern 1: Preference Reading with Legacy Fallback
**Files:** web_metadata.py, main_window.py  
**Issue:** Same 20-line block for reading `flip_author` and `move_articles` settings.

**web_metadata.py lines 580-603:**
```python
if not settings.contains("import/flip_author_name"):
    legacy_settings = QSettings("AbCS", "AbCS")
    flip_author = legacy_settings.value(...)
else:
    flip_author = settings.value(...)
```

**main_window.py lines 2827-2845:** Same code.

**Fix:** Extract to `src/accessibility/settings_helpers.py`.

### Pattern 2: Duplicate Book Application Logic
**File:** web_metadata.py  
**Lines:** 951-1155  
**Issue:** 200+ line block repeats same pattern for Title, Author, Year, Series, Genre.

```python
if "field" in self.field_differences:
    if row_widget._checkbox.isVisible():
        if checkbox.isChecked():
            # apply value
    else:
        # auto-apply
```

**Fix:** Extract to 30-line helper method.

### Pattern 3: Fuzzy/Duplicate Checking
**Files:** book_list_import_window.py, validator.py  
**Issue:** Both implement `_calculate_similarity()` using `difflib.SequenceMatcher`. The book_list_import_window duplicates logic from ImportValidator.

---

## 3. Accessibility Compliance Issues

### Status Announcement Pattern
- **Compliant:** main_window.py, import_window.py, web_metadata.py
- **Needs fix:** reading_history_window.py (uses `QStatusBar.showMessage()` directly)

### Combo Anti-Noise Pattern
- **Compliant:** book_details.py, preferences_window.py, update_window.py
- **Needs verification:** name_list_window.py

### Alt-Key Hygiene Pattern
- **Compliant:** main_window.py, import_window.py, web_metadata.py
- **Manual filtering:** collection_window.py (may not use `is_unmapped_alt_letter`)

### Keyboard Shortcuts Pattern
- **Issues:** book_details.py has commented `setShortcut` lines; statistics_dialog.py unknown

---

## 4. Cleanup Priority

### High Priority (Fix After Performance)
1. Remove test code from web_metadata.py
2. Extract duplicate preference reading to helper
3. Refactor web_metadata.py book application logic (200 lines → 30 lines)

### Medium Priority
4. Verify all windows have Alt+/ support
5. Standardize combo anti-noise
6. Clean commented shortcut code

### Low Priority
7. Remove empty methods
8. Unify fuzzy matching between book_list_import_window and validator

---

## 5. Accessibility Quick Check

| Window | Alt+/ | F1 | Alt-Keys | Status Ann. | Combo Anti-Noise |
|--------|-------|-----|----------|-------------|------------------|
| main_window.py | Yes | Yes | Yes | Yes | N/A |
| import_window.py | Yes | Yes | Yes | Yes | N/A |
| book_details.py | Unknown | Unknown | Unknown | Unknown | Yes |
| web_metadata.py | Yes | Yes | Yes | Yes | N/A |
| preferences_window.py | Unknown | Unknown | Unknown | Unknown | Yes |
| reading_history_window.py | Unknown | Unknown | Unknown | Needs fix | N/A |
| statistics_dialog.py | Unknown | Unknown | Unknown | Unknown | N/A |
| setup_dialogue.py | Unknown | Unknown | Unknown | Unknown | Unknown |
| name_list_window.py | Unknown | Unknown | Unknown | Unknown | Unknown |
| collection_window.py | Unknown | Unknown | Manual | Unknown | Unknown |
| backup_restore_window.py | Unknown | Unknown | Unknown | Unknown | Unknown |
| import_detail_window.py | Unknown | Unknown | Unknown | Unknown | Yes |
| book_list_import_window.py | Unknown | Unknown | Unknown | Unknown | Unknown |

---

## 6. Estimated Effort

| Task | Hours |
|------|-------|
| Performance Tuning | 15 |
| Remove dead code | 1 |
| Extract preference helper | 2 |
| Refactor web_metadata.py | 3 |
| Accessibility compliance audit | 4 |
| Testing with screen reader | 2 |
| **Total** | **27 hours** |

---

# Part 3: Execution Order

## Week 1: Performance (Priority 1)
- Implement Quick Wins (Techniques 1-5)
- Module 2 Import System (fixes 9.14s bottleneck)
- Test with JAWS

## Week 2: Performance + High Priority Cleanup
- Module 1 Main Library View
- Module 4 Database Manager
- Remove dead code from web_metadata.py
- Extract preference helper

## Week 3: Remaining Work
- Module 3 Reading History
- Refactor web_metadata.py
- Accessibility compliance audit
- Final testing

---

**Note:** Performance work fixes broken features. Cleanup improves maintainability. Do performance first.
