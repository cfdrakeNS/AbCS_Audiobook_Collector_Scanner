# AbCS May 16 Accessibility Issues Plan

## Purpose

Track accessibility and shortcut issues by window so fixes can be implemented and verified without breaking JAWS/NVDA keyboard behavior.

---

# Global Rules for Fixes

- Keep `Alt+/` available to re-read the current status message.
- Do not add global Enter/Return shortcuts that override button activation.
- Do not assign duplicate `Alt+letter` shortcuts within the same window.
- Do not use unmapped `Alt+letter` keys in editable fields.
- Keep visible labels, tooltips, accessible names, and accessible descriptions aligned.
- Preserve intentional focus restoration after dialogs and operations.
- Test each window with keyboard only and screen reader-friendly status announcements.

---

# Backup / Restore Window

## Issue 1: Incorrect Browse Shortcut

- **Problem:** `Alt+O` should not be assigned to Browse.
- **Expected:** Browse should use `Alt+W`.
- **Reason:** `Alt+W` is the established browse/accessibility shortcut pattern in this project.

## Planned Fix

- Remove `Alt+O` from Browse.
- Ensure Browse is activated by `Alt+W` only.
- Update button text, tooltip, accessible name, and accessible description if needed.
- Verify `Alt+O` is either unused or assigned only to a clearly labeled control with an `O` mnemonic.

## Verification

- Press `Alt+W`; Browse dialog opens.
- Press `Alt+O`; Browse does not open unless another valid `O` control owns that shortcut.
- Screen reader announces Browse button correctly.

---

# Import Detail Window

## Issue 1: Time Shortcut Conflict

- **Problem:** `Alt+T` currently conflicts because Title uses `Alt+T` and Time also uses `Alt+T`.
- **Expected:**
  - Title should remain `Alt+T`.
  - Time should use `Alt+M`.

## Planned Fix

- Keep `Alt+T` for moving focus to Title.
- Change Time mnemonic/shortcut to `Alt+M`.
- Update visible label if needed so the mnemonic is discoverable.
- Update tooltip, accessible name, and accessible description if needed.
- Check that `Alt+M` does not conflict with another control in the Import Detail window.

## Verification

- Press `Alt+T`; focus moves to Title.
- Press `Alt+M`; focus moves to Time.
- No duplicate `Alt+letter` shortcuts exist in the Import Detail window.
- Screen reader announces the focused fields correctly.

---

# Main Window

## Test Failures / Issues

- Main window missing accessible name.
- Main window test reports missing book list.
- Shortcut registry tests expect `ShortcutManager.MAIN_WINDOW_SHORTCUTS`.
- Reading History menu item not found by shortcut/menu tests.
- Sort status label mismatch:
  - Expected: `Sorted by: Year (Ascending)`
  - Actual: `Sorted: Year (Ascending)`

## Planned Fixes

- Set a clear accessible name and accessible description on the main window.
- Verify the book list widget has a stable object name, accessible name, and accessible description.
- Restore or update shortcut registry constants used by tests.
- Verify menu text and accessible names for Reading History.
- Decide whether to update the app text or the test expectation for sort status wording.

## Verification

- Run main window shortcut/menu tests.
- Confirm all top-level menu actions have clear names and no duplicate shortcuts.
- Confirm book list is reachable by Tab and announced clearly.

---

# Reading History Window

## Test Failures / Issues

- Status bar accessible name is blank.
- Test expects a `General` tab.
- Reading history data loading regression failed.
- Shortcut registry tests expect `ShortcutManager.READING_HISTORY_WINDOW_SHORTCUTS`.

## Planned Fixes

- Set accessible name and accessible description on the status bar.
- Confirm current tab structure and decide whether the `General` tab should exist or tests should be updated.
- Verify data loading path for reading history.
- Restore or update reading history shortcut registry constant.

## Verification

- Run reading history accessibility tests.
- Confirm status messages are available to screen readers.
- Confirm `Alt+/` re-reads current status.

---

# Name List Window

## Test Failures / Issues

- Test expects `NameListWindow.on_alt_f_pressed`.

## Planned Fixes

- Determine whether `Alt+F` should still be supported in the Name List window.
- If yes, restore `on_alt_f_pressed` or connect the current equivalent method.
- If no, update tests and documentation to match current shortcuts.

## Verification

- Press `Alt+F`; expected target action occurs if retained.
- No conflict with text entry controls.
- Screen reader announces resulting focus/status.

---

# Accessibility Test Window / Test Utilities

## Test Failures / Issues

- Expected accessible title mismatch:
  - Expected: `Accessibility Test Window`
  - Actual: `Accessibility Test`

## Planned Fixes

- Decide whether the window title/accessibility name should be `Accessibility Test Window` or whether the test should expect `Accessibility Test`.
- Keep title, accessible name, and test expectation consistent.

## Verification

- Run accessibility test module.

---

# Preferences Window

## Current Notes

- Recently removed `Unknown/Various` author validation preference.
- Recently added minimum and maximum book length validation preferences.

## Planned Checks

- Verify no duplicate `Alt+letter` shortcuts were introduced.
- Verify all new book length controls have accessible names and descriptions.
- Add tooltips for sighted users while keeping accessible descriptions for screen readers.

## Verification

- Open Preferences with keyboard only.
- Tab through all controls.
- Confirm `Alt+/` re-reads status.
- Confirm Restore Defaults sets book length rules to disabled.

---

# Import Window

## Planned Checks

- Verify scan/browse shortcuts remain consistent.
- Browse should use `Alt+W` where applicable.
- Confirm error and warning flags use `E:` and `W:` for enabled validation severities.
- Confirm no validation blocks `Various`, `Various Artists`, or similar collection-style author names.

## Verification

- Run import tests.
- Scan sample imports with keyboard only.
- Confirm status messages are announced for meaningful state changes.

---

# Test Plan

## Targeted Tests

Run these after shortcut/accessibility fixes:

```text
python -m pytest test/test_accessibility.py test/test_accessibility_regression.py test/test_main_window_shortcuts_and_menus.py test/test_shortcut_integration.py test/test_reading_history_accessibility.py
```

## Import Tests

```text
python -m pytest test/test_book_import.py test/test_import_scanner_fallbacks.py test/test_update_import_regressions.py
```

## Full Active Test Suite

```text
python -m pytest test
```

## Notes

- The active full suite previously appeared to hang during collection or GUI test startup.
- If that repeats, run targeted files individually to identify the blocking module.
