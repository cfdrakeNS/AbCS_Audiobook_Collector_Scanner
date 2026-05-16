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

## Status

- **Fixed:** Browse button text no longer uses a Qt button mnemonic.
- **Fixed:** `Alt+W` is handled explicitly by the Backup / Restore window and calls Browse directly.
- **Result:** `Alt+W` triggers Browse; `Alt+O` no longer belongs to Browse.

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

## Status

- **Fixed:** Time label changed from `&Time:` to `Ti&me:`.
- **Result:** `Alt+T` remains Title; `Alt+M` moves to Time.

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

## Status

- **Fixed:** Top-level Main Window now has an accessible name and accessible description.
- **Fixed:** Main Window now has a `book_list` alias for the book table used by accessibility tests.
- **Fixed:** Main Window `Alt+L` moves focus to the book list table.
- **Fixed:** Main Window does not use `Alt+B` as a book list shortcut.
- **Fixed:** Main Window sort label now uses `Sorted by:` wording consistently.
- **Fixed:** Shortcut registry dictionaries are exposed on `ShortcutManager` for compatibility checks.
- **Fixed:** Reading History menu action text now remains discoverable by both expected test strings.
- **Fixed:** Reading History window focus policy set to `StrongFocus` for top-level focusability.
- **Verified:** Targeted Main Window accessibility and shortcut tests passed.

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

## Status

- **Fixed:** Reading History status bar now has an accessible name and accessible description.
- **Fixed:** Reading History tabs now expose plain tab names: `General`, `Year`, `Month`, and `Date Range`.
- **Fixed:** Added `load_general_stats` compatibility method for data-loading checks.
- **Fixed:** Shortcut registry uses `Alt+L` for focusing the current table; `Alt+B` is not used.
- **Verified:** Targeted Reading History accessibility, layout, data access, and shortcut tests passed.

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

## Status

- **Fixed:** Restored `NameListWindow.on_alt_f_pressed`.
- **Result:** `Alt+F` remains mapped to clear/start a new find search through the existing `on_clear_find` behavior.
- **Fixed:** Enter/Return on the list table is ignored so it does not enter edit mode.
- **Result:** Edit mode is only triggered by `Alt+E` or the Edit button.
- **Verified:** Targeted Name List shortcut integration test passed.

---

# Collection Window

## Issue 1: Enter Should Not Invoke New

- **Problem:** Pressing Enter/Return on the collection list can invoke New.
- **Expected:** New should only be triggered by `Alt+N` or the New button.

## Status

- **Fixed:** Enter/Return on the collection list table is ignored.
- **Fixed:** Collection action buttons are no longer default/auto-default buttons.
- **Result:** New is only triggered by `Alt+N` or the New button.

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

## Status

- **Fixed:** Minimal accessibility test window title now uses `Accessibility Test Window`.
- **Fixed:** Minimal accessibility test window accessible name remains `Accessibility Test Window`.
- **Fixed:** Test expectation updated to match the window title and accessible name.
- **Verified:** Accessibility test module passed.

---

# Preferences Window

## Current Notes

- Recently removed `Unknown/Various` author validation preference.
- Recently added minimum and maximum book length validation preferences.

## Planned Checks

- Verify no duplicate `Alt+letter` shortcuts were introduced.
- Verify all new book length controls have accessible names and descriptions.
- Defer tooltip work to a later visual polish project.

## Verification

- Open Preferences with keyboard only.
- Tab through all controls.
- Confirm `Alt+/` re-reads status.
- Confirm Restore Defaults sets book length rules to disabled.

## Status

- **Checked:** Preferences shortcut registry has no duplicate `Alt+letter` shortcuts.
- **Fixed:** Minimum book length value control now has an accessible description.
- **Fixed:** Maximum book length value control now has an accessible description.
- **Verified:** Preferences syntax and shortcut registry checks passed.

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

## Status

- **Checked:** Import Window already handles `Alt+W` explicitly and calls Browse directly.
- **Fixed:** Browse button text no longer uses a Qt mnemonic.
- **Fixed:** Export button text no longer uses a Qt mnemonic.
- **Fixed:** Import Window action buttons are no longer auto-default buttons.
- **Verified:** Targeted import regression tests passed.

---

# Button Mnemonic Audit

## Current Findings

These controls still use `&` in button or dialog button text. They need keyboard testing because Qt mnemonics can sometimes move focus instead of triggering the intended action, depending on the control and shortcut handling.

## Preferences Window

- **Status:** Fixed in current pass. Restore Defaults no longer uses `&` in button text.
- **Result:** `Alt+R` is handled by the shortcut manager and triggers Restore Defaults directly.
- **Also fixed:** Preferences Save button is no longer default/auto-default.

## Main Window

- **Status:** Fixed in current pass. Export Duplicates no longer uses `&` in button text.
- **Result:** `Alt+X` is wired through the shortcut manager and triggers Export Duplicates directly.
- **Also fixed:** Main Window action buttons are no longer default/auto-default.
- **Also fixed:** Enter/Return activates Update, Delete, or Export Duplicates when that button has focus.

## Import Window

- **Status:** Fixed in current pass. Browse and Export no longer use `&` in button text.
- **Result:** `Alt+W` and `Alt+X` are handled by explicit shortcuts instead of Qt button mnemonics.

## Import Detail Window

- **Control:** `&Save`
- **Expected shortcut:** `Alt+S`
- **Planned check:** Verify `Alt+S` saves directly and does not only move focus.
- **Possible fix:** Remove `&` from button text and rely on centralized shortcut handling.

- **Control:** `&Discard`
- **Expected shortcut:** `Alt+D`
- **Planned check:** Verify `Alt+D` discards directly and does not only move focus.
- **Possible fix:** Remove `&` from button text and rely on centralized shortcut handling.

## Dialog Buttons

- **Controls found:** `&Yes`, `&No`, `&Cancel`, `&Yes - Save`, `&No - Continue editing`, `Cance&l - Discard and close`
- **Files observed:** `name_list_window.py`, `import_detail_window.py`
- **Planned check:** Verify dialog mnemonics behave as expected inside modal message boxes.
- **Possible fix:** Usually keep standard dialog mnemonics unless they conflict with window-level accessibility rules.

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
