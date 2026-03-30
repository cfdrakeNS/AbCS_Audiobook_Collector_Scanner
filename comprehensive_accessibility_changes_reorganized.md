# Accessibility Work Needed

## Windows Requiring Standardization

### 1. src/ui/reading_history_window.py - MEDIUM PRIORITY 🟡
**Missing Accessibility Standards:**
- ❌ ALLOWED_ALT_LETTERS: Missing entirely
- ❌ Date edit anti-noise pattern: Add for QDateEdit fields (not combo boxes)

**Current Shortcuts:**
- ✅ Alt+G (General tab)
- ✅ Alt+Y (Year tab)  
- ✅ Alt+M (Month tab)
- ✅ Alt+R (Date Range tab)
- ✅ Alt+F (From date field)

**Issues to Fix:**
- ❌ Status bar shows "books read between" message on all tabs (should only show on Date Range tab)
- ❌ Start date remembers last date used (should default to 12 months ago, not saved value)
- ✅ End date correctly defaults to today's date

**Files to Modify:**
- `src/ui/reading_history_window.py`

---

### 2. src/ui/collection_window.py - LOW PRIORITY 🟡
**Orphaned Shortcuts:**
- ⚠️ ALLOWED_ALT_LETTERS: May contain unused letters (needs audit)

**Files to Modify:**
- `src/ui/collection_window.py`

---

## Summary
- **2 windows** need accessibility standardization
- **1 window** needs orphaned shortcut cleanup
- ✅ **Note:** Already has basic accessibility patterns

**Files to Modify:**
- `src/ui/collection_window.py` (audit ALLOWED_ALT_LETTERS)

---

### 11. src/ui/backup_restore_window.py - LOW PRIORITY 🟡
**Status:** Needs audit and cleanup

**Required Changes:**

**Alt+Letter Cleanup:**
- ⚠️ **Audit ALLOWED_ALT_LETTERS:** May contain unused letters
- ✅ **Note:** Already has basic accessibility patterns

**Files to Modify:**
- `src/ui/backup_restore_window.py` (audit ALLOWED_ALT_LETTERS)

---

## 🔴 WINDOWS NOT YET ASSESSED

### 12. src/ui/name_list_window.py - NEEDS ASSESSMENT 🔴
**Status:** Not yet reviewed for accessibility patterns

**Required Assessment:**
- ❌ **ALLOWED_ALT_LETTERS:** Missing entirely
- ❌ **Combo anti-noise pattern:** Missing for search/filter combos
- ❌ **Full accessibility audit needed**

**Files to Modify:**
- `src/ui/name_list_window.py` (add ALLOWED_ALT_LETTERS and combo anti-noise)

---

### 13. src/ui/accessible_window_skeleton.py - NEEDS ASSESSMENT 🔴
**Status:** Example template - needs review

**Required Assessment:**
- ❌ **ALLOWED_ALT_LETTERS:** Missing entirely
- ❌ **Combo anti-noise pattern:** Missing - needs example
- ❌ **Template review needed:** Ensure it demonstrates best practices

**Files to Modify:**
- `src/ui/accessible_window_skeleton.py` (add accessibility examples)

---

## 📋 SUMMARY STATISTICS

**Total Windows:** 13
**✅ Completed:** 8 (62%)
**🟡 In Progress:** 3 (23%)
**🔴 Not Assessed:** 2 (15%)

**Critical Issues Requiring Immediate Attention:**
1. **reading_history_window.py** - Missing ALLOWED_ALT_LETTERS entirely

**Common Issues Across Multiple Windows:**
1. **Unused Alt+Letter Shortcuts** - Most windows need audit of ALLOWED_ALT_KEYS/ALLOWED_ALT_LETTERS
2. **Missing Combo Anti-Noise Pattern** - Several windows need this for combo boxes
3. **Missing ALLOWED_ALT_LETTERS** - Some windows missing this entirely

---

## 🎯 RECOMMENDED ACTION ORDER

### Phase 1: Critical Fixes (Do These First)
1. **reading_history_window.py** - Add ALLOWED_ALT_LETTERS

### Phase 2: Standardization (Medium Priority)
2. **All windows** - Audit and clean up unused Alt+letter shortcuts
3. **book_details.py** - Audit ALLOWED_ALT_KEYS for unused letters (low priority)
4. **preferences_window.py** - Audit ALLOWED_ALT_LETTERS for unused letters (low priority)

### Phase 3: Assessment (Low Priority)
6. **name_list_window.py** - Full accessibility assessment
7. **accessible_window_skeleton.py** - Template review and improvement

---

## 🔧 ALT+LETTER CLEANUP GUIDELINES

For each window, follow these steps to clean up Alt+letter shortcuts:

1. **List current ALLOWED_ALT_KEYS/ALLOWED_ALT_LETTERS**
2. **List actual implemented shortcuts** (from callback_map or shortcut definitions)
3. **Compare lists** - identify unused letters
4. **Remove unused letters** from ALLOWED sets
5. **Test that unused letters are now blocked** by `is_unmapped_alt_letter()`

**Goal:** No "dead keys" - every Alt+letter either does something useful or gets blocked with a beep.
