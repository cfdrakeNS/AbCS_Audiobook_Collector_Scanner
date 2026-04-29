# Commit Note - April 29, 2026 (Morning)

## Summary
Consistency updates to keyboard shortcuts, debug code cleanup, and text sanitization improvements.

---

## Changes

### 1. Import Window Shortcut Migration (Ctrl+I → Alt+I)
**Files Modified:**
- `src/accessibility/shortcuts.py`
- `src/ui/import_window.py`

**Changes:**
- Added `"I": ("Import", "scan_button")` to `IMPORT_WINDOW_SHORTCUTS` for Alt+I activation
- Removed explicit `setShortcut("Ctrl+I")` binding from scan button
- Removed `&` mnemonic from import button label (`"&Import"` → `"Import"`) to prevent Qt mnemonic interference
- Updated import button accessible description: `Ctrl+I` → `Alt+I`
- Updated both F1 help shortcut lists to reflect `Alt+I`
- Added `scan_button` callback to centralized shortcut registration

**Rationale:**
Consistent Alt+key convention across the application. Centralized shortcut manager now controls the binding.

---

### 2. Debug Code Cleanup
**Files Modified:**
- `src/ui/import_window.py`
- `src/core/validator.py`

**Changes:**
- **import_window.py**: Removed timing `print()` statement and debug comment from scan results
- **validator.py**: Removed three `print()` statements from `is_duplicate_fast()` method (duplicate check debug output)

**Rationale:**
Removed runtime debug artifacts to clean up code and console output.

---

### 3. Text Sanitization - Apostrophe Capitalization Fix
**Files Modified:**
- `src/core/validator.py`
- `src/core/import_scanner.py`

**Changes:**
- Replaced `str.title()` with custom proper-case logic in both files
- Implements `proper_case_word()` regex helper:
  - Capitalizes first letter after whitespace, hyphen, or start of string
  - Preserves apostrophe-owned words (e.g., `john's` instead of `John'S`)
  - Handles special cases like `O'Connor` correctly
  
**Before:**
```
"john's book" → "John'S Book"  # Incorrect
```

**After:**
```
"john's book" → "John's Book"  # Correct
```

**Rationale:**
Improves metadata quality by preventing improper capitalization of possessive apostrophes while maintaining proper title case formatting.

---

### 4. File Menu Update - Removed Ctrl+U
**Files Modified:**
- `src/ui/main_window.py`

**Changes:**
- Removed `setShortcut("Ctrl+U")` from Update menu action
- Updated menu action display text: `"&Update\tCtrl+U"` → `"&Update\tAlt+U"`
- Centralized `Alt+U` shortcut remains registered via `ShortcutManager`

**Rationale:**
Consistency with Alt+key convention. Removed redundant/duplicate shortcut binding.

---

## Testing Notes
- Alt+I now triggers import in Import Window
- Alt+U triggers update in Main Window
- Possessive text like "Mary's book" sanitizes correctly without forced `'S` capitalization
- No debug output in terminal during normal operation
- All shortcuts accessible via F1 help

---

## Files Changed
1. `src/accessibility/shortcuts.py` — Added Alt+I mapping
2. `src/ui/import_window.py` — Shortcut binding, button label, debug cleanup
3. `src/core/validator.py` — Proper-case logic, debug cleanup
4. `src/core/import_scanner.py` — Proper-case logic
5. `src/ui/main_window.py` — Removed Ctrl+U binding
