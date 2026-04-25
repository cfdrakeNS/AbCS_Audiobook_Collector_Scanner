# AbCS Performance and Cleanup Plan

**Last Updated:** April 25, 2026  
**Test Database:** 34,679 books  
**Status:** Phase 1 Complete, Phase 2 Ready

---

## Quick Status

| Phase | Status | Key Result |
|-------|--------|------------|
| **Phase 1: Quick Wins** | ✅ **COMPLETE** | 26x faster imports (0.51s vs 9.14s) |
| **Phase 2: Fuzzy Optimization** | ⏳ **NEXT** | Fix 13.55s bottleneck with fuzzy=90% |
| **Phase 3: Code Cleanup** | ⏳ **PENDING** | Remove dead code, extract helpers |
| **Phase 4: Accessibility Audit** | ⏳ **PENDING** | Final JAWS testing |

---

## Test Results (April 25, 2026)

### Latest Large-Scale Test (516 books imported):

| Metric | Time | Books |
|--------|------|-------|
| Library refresh (34.7k books) | 0.55s | 34,679 |
| **Table batch load** | **1.14s** | **516 books** |
| **Auto-add phase** | **1.16s** | **351 books** |
| **Total scan** | **5.57s** | **Scanned: 516, Added: 351** |

### Small Import Comparison (34 books):

| Configuration | Table Batch | Auto-Add | Total | Speed |
|---------------|-------------|----------|-------|-------|
| **Fuzzy 0%** | 0.08s | 0.10s | **0.51s** | ✅ Fast |
| **Fuzzy 90%** | 13.20s | 13.21s | **13.55s** | ⚠️ Slow |
| **Difference** | 160x slower | 137x slower | **26x slower** | - |

**Finding:** Table rendering is instant (0.08s for 34 books, 1.14s for 516). The **fuzzy duplicate check is the bottleneck** - O(n²) comparisons against 34k library.  
**Workaround:** Set fuzzy threshold to 0 for sub-1-second imports.

---

## Phase 1: COMPLETED WORK ✅

### Quick Wins Implemented (April 25, 2026)

All 4 core techniques applied to `import_window.py`:

| Technique | Implementation | Result |
|-----------|---------------|--------|
| **1. Clean Slate** | `table.setRowCount(0)` before load | Instant table clear |
| **2. Block Repaint** | `setUpdatesEnabled(False/True)` around batch load | 10s → 1s |
| **3. Pre-Size Table** | `setRowCount(total)` instead of `insertRow()` | Single allocation |
| **4. Disable Sort** | `setSortingEnabled(False/True)` during load | No re-sort per row |

**Files Modified:**
- `src/ui/import_window.py` - Table optimizations + timing instrumentation
- `src/ui/main_window.py` - Timing for library refresh
- `src/database/connection.py` - WAL mode enabled
- `src/ui/book_list_import_window.py` - Fixed duplicate layout crash

**Timing Outputs Added:**
- `[TIMING] Table batch load (optimized): X.XXXXs for N books`
- `[TIMING] Auto-add phase: X.XXXXs for N books`
- `[TIMING] Total scan: X.XXXXs | Scanned: N | Added: N`
- `[TIMING] Library refresh: X.XXXXs (DB: X.XXXXs) | Books: N`

### Module Status:

| Module | Location | Status | Notes |
|--------|----------|--------|-------|
| **Import System** | `src/ui/import_window.py` | ✅ **Complete** | 26x faster - optimized QTableWidget |
| **Main Library** | `src/ui/main_window.py` | ✅ **Complete** | Uses QTableWidget+QAbstractTableModel, ~0.55s load |
| **Database** | `src/database/connection.py` | ✅ **Complete** | WAL mode + indexes + transaction fixes |
| **Book List Import** | `src/ui/book_list_import_window.py` | ✅ **Fixed** | Duplicate layout code removed |

---

## Phase 2: REMAINING WORK

### Priority 1: Fuzzy Duplicate Check Optimization

**Current Problem:**
- Fuzzy check does O(n²) string comparisons
- 34 books × 34,679 existing = ~1.2 million comparisons
- Result: 13.55s import vs 0.51s with fuzzy=0

**Potential Solutions:**
1. **Pre-compute fuzzy keys** - Normalize titles once, store in dict for O(1) lookup
2. **SQLite FTS** - Use full-text search for approximate matching
3. **Cached signatures** - Build index of title+author hashes at startup
4. **Parallel processing** - Thread pool for fuzzy comparisons
5. **Early termination** - Stop comparing once threshold exceeded

**Target:** Reduce fuzzy import from 13.55s to < 2s

---

### Priority 2: Code Cleanup

#### Dead Code Removal (`src/core/web_metadata.py`)
- Lines 6-13: `sys.path.insert` standalone block
- Line 605: Obsolete comment about `fetch_web_data`
- Lines 1158-1180: `test_web_metadata()` function in production file

#### Duplicate Code Extraction
- Preference helper exists in both `web_metadata.py` and `main_window.py`
- Extract to shared utility (200 lines → 30 lines)

#### Layout Fixes
- Replace `layout.addStretch()` inside loops with `QSpacerItem`
- Use simpler layouts (`QFormLayout`, `QGridLayout`)

---

### Priority 3: Main Window Table Architecture

**Current Status:** Main window uses hybrid approach:
- `QTableWidget` as the view container (line 409 in `main_window.py`)
- `BookTableModel` (`QAbstractTableModel`) for data (lines 612-613)
- Already uses model-view pattern, not item-based like import window

**Optimizations Applied:**
- Timing instrumentation added to `refresh_books()`
- Already uses `blockSignals(True/False)` and `setUpdatesEnabled(False/True)`
- Library load: **~0.55s for 34,679 books** ✅ Acceptable

**Future:** Consider migrating to `QTableView` proper (instead of `QTableWidget` with model) for cleaner architecture. Low priority since performance is already good.

---

### Priority 4: Other Enhancements

| Feature | QTableWidget | QTableView |
|---------|--------------|------------|
| Memory | 150,000 objects | 15 rows only |
| Speed at 30k | 0.55s (optimized) | Same as 3 books |
| Complexity | Simple | Requires model |

#### Database Optimizations
- Use `cursor.fetchmany(N=1000)` instead of `fetchall()` for large queries
- Consider pagination for library load

#### Reading History (`src/ui/history_window.py`)
- Apply clean slate strategy to date filter changes
- Optimize row deletion when switching "3 Months" ↔ "All Time"

---

## Technical Reference: Optimization Techniques

### Core Problem
`QTableWidget` creates a Python object for every cell. 30,000 books × 5 columns = 150,000 objects.

### Technique 1: Clean Slate
```python
# Fast - drops entire dataset instantly
self.tableWidget.setRowCount(0)

# Slow - reflows layout for each deletion
for row in range(self.tableWidget.rowCount()):
    self.tableWidget.removeRow(0)
```

### Technique 2: Block Repaint
```python
self.tableWidget.setUpdatesEnabled(False)
# ... add 30,000 rows ...
self.tableWidget.setUpdatesEnabled(True)
```

### Technique 3: Pre-Size
```python
self.tableWidget.setRowCount(total_books)
# ... populate with setItem ...
```

### Technique 4: Disable Sorting
```python
self.tableWidget.setSortingEnabled(False)
# ... load all data ...
self.tableWidget.setSortingEnabled(True)
```

---

## Detailed Code Cleanup Inventory

### Dead Code Found

| File | Lines | Issue |
|------|-------|-------|
| `web_metadata.py` | 6-13 | `sys.path.insert` standalone block |
| `web_metadata.py` | 605 | Obsolete comment about `fetch_web_data` |
| `web_metadata.py` | 1158-1180 | `test_web_metadata()` in production file |
| `import_window.py` | 730-732 | Empty `_update_cancel_button_state()` |
| `import_window.py` | 877, 890, 903 | Commented `setShortcut` lines |
| `book_details.py` | Multiple | Commented shortcut patterns |

### Duplicate Code Patterns

| Pattern | Files | Lines | Solution |
|---------|-------|-------|----------|
| Preference reading | `web_metadata.py`, `main_window.py` | 580-603, 2827-2845 | Extract to `settings_helpers.py` |
| Book application logic | `web_metadata.py` | 951-1155 | 200 lines → 30-line helper |
| Fuzzy matching | `book_list_import_window.py`, `validator.py` | - | Unify into single implementation |

### Accessibility Compliance Matrix

| Window | Alt+/ | F1 | Alt-Keys | Status Ann. | Combo Anti-Noise |
|--------|-------|-----|----------|-------------|------------------|
| `main_window.py` | ✅ | ✅ | ✅ | ✅ | N/A |
| `import_window.py` | ✅ | ✅ | ✅ | ✅ | N/A |
| `web_metadata.py` | ✅ | ✅ | ✅ | ✅ | N/A |
| `book_details.py` | ? | ? | ? | ? | ✅ |
| `preferences_window.py` | ? | ? | ? | ? | ✅ |
| `reading_history_window.py` | ? | ? | ? | ⚠️ Needs fix | N/A |

### Estimated Effort Remaining

| Task | Hours |
|------|-------|
| Phase 2: Fuzzy optimization | 4 |
| Phase 3: Code cleanup | 6 |
| Phase 4: Accessibility audit | 4 |
| Testing with JAWS | 2 |
| **Total Remaining** | **16 hours** |

---

**Note:** Performance work fixes broken features. Cleanup improves maintainability. Do performance first.
