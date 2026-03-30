# Comprehensive Accessibility Changes - Window by Window

## Overview
This document organizes all accessibility changes by window, with all required changes for each window consolidated in one section for clarity.

---

## ✅ COMPLETED WINDOWS

### 1. src/ui/book_details.py - COMPLETED ✅
**Status:** All accessibility issues resolved

**Completed Changes:**
- ✅ Cancel button removed and replaced with Escape key functionality
- ✅ Alt+L removed (no table to focus)
- ✅ ALLOWED_ALT_KEYS updated to remove unused letters
- ✅ F1 help dialog updated with current shortcuts
- ✅ Escape shows proper save dialog with Yes/No options
- ✅ Button text updated: "Get web info" → "Fetch Web Info"
- ✅ Alt+B preserved for bitrate field
- ✅ All accessibility patterns properly implemented

**Remaining Issues:**
- ⚠️ ALLOWED_ALT_KEYS may contain unused letters (audit needed)

---

### 2. src/ui/preferences_window.py - COMPLETED ✅
**Status:** All accessibility issues resolved

**Completed Changes:**
- ✅ Cancel button removed and replaced with Escape key functionality
- ✅ Alt+L removed (no table to focus)
- ✅ ALLOWED_ALT_LETTERS updated
- ✅ Shortcut manager callback map updated
- ✅ F1 help dialog updated
- ✅ Escape shows proper save dialog with Yes/No/Cancel options
- ✅ Button text simplified to "Yes", "No", "Cancel"
- ✅ All accessibility patterns properly implemented

**Remaining Issues:**
- ⚠️ ALLOWED_ALT_LETTERS may contain unused letters (audit needed)

---

### 3. src/ui/name_list_window.py - COMPLETED ✅
**Status:** All accessibility issues resolved

**Completed Changes:**
- ✅ Cancel button removed and replaced with Escape key functionality
- ✅ Alt+L changed from Cancel to table focus
- ✅ Alt+B removed (functionality moved to Alt+L)
- ✅ ALLOWED_ALT_LETTERS updated (remove B, keep L)
- ✅ Shortcut manager callback map updated
- ✅ NAMELIST_WINDOW_SHORTCUTS updated in shortcuts.py
- ✅ F1 help dialog updated
- ✅ Initial focus fixed - table gets focus when window opens
- ✅ All accessibility patterns properly implemented

**Remaining Issues:**
- ✅ None identified

---

### 4. src/ui/update_window.py - COMPLETED ✅
**Status:** All accessibility issues resolved

**Completed Changes:**
- ✅ All accessibility patterns properly implemented
- ✅ Combo anti-noise pattern implemented
- ✅ Good error focus movement
- ✅ All shortcuts properly documented

**Remaining Issues:**
- ⚠️ May have unused Alt+letter definitions (audit needed)

---

### 5. src/ui/import_detail_window.py - COMPLETED ✅
**Status:** All accessibility issues resolved

**Completed Changes:**
- ✅ All accessibility patterns properly implemented
- ✅ Combo anti-noise pattern implemented
- ✅ Good error focus movement
- ✅ All shortcuts properly documented

**Remaining Issues:**
- ⚠️ May have unused Alt+letter definitions (audit needed)

---

### 6. src/ui/main_window.py - COMPLETED ✅
**Status:** All accessibility issues resolved

**Completed Changes:**
- ✅ **Combo anti-noise pattern added:** Find combo now blocks plain arrow keys
- ✅ **Plain arrow keys blocked:** Up/Down keys now beep and are blocked on find combo
- ✅ **Alt+Arrow keys work:** Alt+Up/Down opens dropdown as expected
- ✅ **Enter handling improved:** Enter commits selection and selects all text
- ✅ **Alt+letter filtering:** Already properly implemented for find dialog
- ✅ **No global Enter shortcuts:** Confirmed - uses proper keyPressEvent handling
- ✅ **Button accessibility preserved:** Enter works on all buttons

**Remaining Issues:**
- ✅ None - all issues resolved

**Files Modified:**
- `src/ui/main_window.py` (eventFilter method - added combo anti-noise pattern)

**What Was Fixed:**
- **Find combo box** now follows accessibility pattern used in other windows
- **Plain Up/Down arrows** are blocked with beep feedback
- **Alt+Up/Down** opens dropdown (Qt default behavior preserved)
- **Enter key** commits selection and selects text for easy editing

---

### 7. src/ui/import_window.py - COMPLETED ✅
**Status:** All accessibility issues resolved

**Completed Changes:**
- ✅ **Combo anti-noise pattern added:** Error filter combo now blocks plain arrow keys
- ✅ **Plain arrow keys blocked:** Up/Down keys now beep and are blocked on error filter combo
- ✅ **Alt+Arrow keys work:** Alt+Up/Down opens dropdown as expected
- ✅ **Enter handling improved:** Enter commits selection and selects all text
- ✅ **Unused Alt+letters removed:** Cleaned up ALLOWED_ALT_LETTERS to only implemented shortcuts
- ✅ **Alt+letter filtering:** Properly implemented with cleaned allowlist

**Removed Unused Shortcuts:**
- ❌ **Alt+A, Alt+I, Alt+N** - Not implemented, removed from ALLOWED_ALT_LETTERS
- ✅ **Kept:** Alt+C, Alt+F, Alt+B, Alt+E, Alt+L, Alt+S, Alt+V, Alt+X, Alt+W

**Remaining Issues:**
- ✅ None - all issues resolved

**Files Modified:**
- `src/ui/import_window.py` (eventFilter method - added combo anti-noise pattern)
- `src/ui/import_window.py` (ALLOWED_ALT_LETTERS - removed unused shortcuts)

**What Was Fixed:**
- **Error filter combo box** now follows accessibility pattern used in other windows
- **Plain Up/Down arrows** are blocked with beep feedback
- **Alt+Up/Down** opens dropdown (Qt default behavior preserved)
- **Enter key** commits selection and selects text for easy editing
- **Cleaned up unused Alt+letters** to prevent "dead keys"

---

### 8. src/ui/web_metadata.py - COMPLETED ✅
**Status:** All accessibility issues resolved

**Completed Changes:**
- ✅ **Button renamed:** "Fetch Web Data" → "Refresh Web Info" for clarity
- ✅ **ALLOWED_ALT_KEYS updated:** Added 'W' for Refresh Web Info, '/' and 'F1' for standard shortcuts
- ✅ **Alt+letter filtering:** Already properly implemented with updated allowlist
- ✅ **Event filter working:** Blocks unused Alt+letters with beep feedback
- ✅ **No combo boxes:** No anti-noise pattern needed
- ✅ **Help dialog updated:** Reflects new "Refresh Web Info" button name

**Button Naming Fix:**
- ✅ **Clear purpose:** Button now indicates refreshing already-fetched data
- ✅ **Consistent behavior:** Auto-fetches on open, button refreshes data
- ✅ **No confusion:** Users understand button re-fetches vs initial fetch

**Remaining Issues:**
- ✅ None - all issues resolved

**Files Modified:**
- `src/ui/web_metadata.py` (button text and accessible name)
- `src/ui/web_metadata.py` (ALLOWED_ALT_KEYS - added W, /, F1)
- `src/ui/web_metadata.py` (help dialog - updated shortcut description)

**What Was Fixed:**
- **Button clarity** - "Refresh Web Info" clearly indicates re-fetching data
- **Complete Alt+letter support** - all shortcuts now properly allowed
- **Accessibility compliance** - follows all established patterns

---

## 🟡 WINDOWS NEEDING CHANGES

### 9. src/ui/reading_history_window.py - MEDIUM PRIORITY 🟡
**Status:** Missing accessibility patterns

**Required Changes:**

**Missing Patterns:**
- ❌ **ALLOWED_ALT_LETTERS:** Missing entirely
- ❌ **Combo anti-noise pattern:** Add for date combo boxes
- ✅ **Current shortcuts:** Alt+G (General tab), Alt+Y (Year tab)

**Files to Modify:**
- `src/ui/reading_history_window.py` (add ALLOWED_ALT_LETTERS and combo anti-noise)

---

### 10. src/ui/collection_window.py - LOW PRIORITY 🟡
**Status:** Needs audit and cleanup

**Required Changes:**

**Alt+Letter Cleanup:**
- ⚠️ **Audit ALLOWED_ALT_LETTERS:** May contain unused letters
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
