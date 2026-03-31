# Accessibility Compliance Review (March 30, 2026)

This document summarizes findings of noncompliance or partial compliance with AbCS accessibility patterns and PySide6 accessibility best practices, based on a review of the codebase and the following reference documents:
- accessibility_app_patterns.md
- Accessibility_best-practice_ rules (PySide6).md
- Screen_Reader_and_PySide6_best_practices.md

## Review Scope
- Status bar and status announcement patterns
- Combo box anti-noise (arrow key) pattern
- Alt-letter shortcut hygiene
- JAWS/NVDA input stability
- Modal messaging and error focus
- Quiet-mode/read-only info fields
- Keyboard help dialog (F1)
- Tab order and focus management
- Table row number suppression
- Accessible names/descriptions
- Shortcut conflicts and global Enter anti-pattern


## Windows Needing Accessibility Fixes (with Required Fixes)

### 1. `src/ui/import_window.py`
- **Missing:** `is_unmapped_alt_letter` event filtering for Alt+letter hygiene.
- **Missing:** Use of `exec_styled_message_box` for all modal dialogs.
- **Missing:** `Alt+/` status readback shortcut.
- **Action:** Add event filter for Alt+letter, replace all error/info dialogs with styled message box, implement Alt+/ shortcut for status.

### 2. `src/ui/import_progress_window.py`
- **Missing:** `Alt+/` shortcut for status readback.
- **Missing:** Keyboard help dialog (`F1`).
- **Action:** Add Alt+/ shortcut and F1 help dialog listing all shortcuts.

### 3. `src/ui/import_detail_window.py`
- **Missing:** Alt+letter hygiene check in eventFilter.
- **Action:** Add event filter to block unmapped Alt+letters.

### 4. `src/ui/book_details.py`
- **Missing:** `setAccessibleName`/`setAccessibleDescription` for several input fields.
- **Action:** Audit all widgets and set accessible names/descriptions.

### 5. `src/ui/preferences_window.py`
- **Missing:** Combo box "anti-noise" pattern (blocking plain Up/Down arrow keys without Alt).
- **Action:** Add event filter to block plain arrow keys in editable combos.

### 6. `src/ui/main_window.py`
- **Missing:** F1 help dialog may not include all registered shortcuts from `ShortcutManager`.
- **Action:** Update F1 help dialog to list all shortcuts, including any new or context-specific ones.

### 7. `src/ui/collection_window.py`
- **Missing:** Some Alt+<letter> shortcuts in the table view are not explicitly documented in the F1 help content.
- **Action:** Ensure all shortcuts are listed in the F1 help dialog.

### 8. `src/ui/backup_restore_window.py`
- **Missing:** `Alt+T` (Focus restore file) is registered but sometimes omitted from help dialog.
- **Action:** Ensure all registered shortcuts are documented in F1 help.

### 9. `src/ui/reading_history_window.py`
- **Missing:** `Alt+H` (focus history table) not consistently documented in help dialogs.
- **Action:** Add to F1 help dialog.

---

## Orphan Shortcuts (Defined but Not Documented or Implemented)

Orphan shortcuts are those defined in `ShortcutManager` or via `QShortcut` but not present in the window's F1 help dialog or not mapped to any action:

- **Backup/Restore Window:** `Alt+T` (Focus restore file) sometimes missing from help.
- **Collection Window:** Several Alt+<letter> shortcuts in the table view not listed in F1 help.
- **Reading History Window:** `Alt+H` (focus history table) not always documented.
- **Main Window:** Some context-specific shortcuts may be missing from F1 help.

**Action:** Audit all F1 help dialogs and ensure every registered shortcut is listed and mapped to an action.

---

## Updated Next Steps
- Address the specific fixes above for each window/dialog.
- Audit all F1 help dialogs for orphan shortcuts and update as needed.
- Use `src/ui/accessible_window_skeleton.py` as the reference for all new UI work.
- Test with both JAWS and NVDA after changes.
