# Mar 02 TODO

## Restore and Reapply: Review Clean Books Before Adding

## Implementation Breakdown (Mar 02)

## Implementation Breakdown (Mar 02) — With File/Module References

### 1. Preferences Window
- [ ] Add checkbox: "Review clean books before adding" (`auto_add_clean_books`)
  - **File:** src/ui/preferences_window.py (or wherever PreferencesWindow is implemented)
  - **Module/Class:** PreferencesWindow
- [ ] Save/load value to QSettings as "import/auto_add_clean_books"
  - **File:** src/ui/preferences_window.py
  - **Module/Class:** PreferencesWindow

### 2. Import Window
- [ ] Add `self.auto_add_clean_books` property, loaded from QSettings
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow
- [ ] Update error filter combo:
  - If `auto_add_clean_books` is enabled, add "Valid" filter option
  - Accessible description should mention "Valid" when present
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow
- [ ] Add "Add Valid" button:
  - Only visible/enabled when `auto_add_clean_books` is enabled
  - Accessible name/description: "Add all clean valid rows without warning, correction, fallback, or error flags - Alt+V"
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow
- [ ] Connect `add_valid_button.clicked` to `on_add_valid`
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow
- [ ] Implement `_update_add_valid_button_visibility()` to show/hide the button
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow
- [ ] Implement `_get_valid_import_count()` to count valid books for review
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow
- [ ] Adjust scan counters and summary to include valid count
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow

### 3. Import Scanner / Validator
- [ ] Ensure valid books are flagged appropriately for review and can be added via the "Add Valid" button
  - **File:** src/core/validator.py
  - **Module/Class:** Validator (and related import logic)
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow

### 4. Accessibility
- [ ] Confirm all controls have accessible names/descriptions and keyboard shortcuts
  - **File:** src/ui/import_window.py
  - **File:** src/ui/preferences_window.py
  - **File:** src/accessibility/shortcuts.py
  - **Module/Class:** ShortcutManager, ImportWindow, PreferencesWindow

### 5. Add Valid Handler & Counters
- [ ] Implement handler to add all valid books at once (`on_add_valid`)
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow
- [ ] After adding, refresh all summary counters and ensure status bar/table reflect new counts
  - **File:** src/ui/import_window.py
  - **Module/Class:** ImportWindow

---

---

## Large Import Compatibility (Threaded Scan)

- Ensure ImportScanWorker (QThread) and signal-based scan logic remain in src/ui/import_window.py for large import responsiveness.
- Progress and counters should be updated via signals (progress, result, finished, cancelled).
- The scan loop must not block the UI; results and progress should be emitted to the UI.
- The 'review clean books before adding' feature, error filter, and Add Valid button logic are compatible with threaded scan.
- No changes needed in src/core/import_scanner.py or src/core/tag_reader.py for large import compatibility.

---

# Mar 02 Summary

Today’s work focused on:

- Reviewing and fixing all import scenario logic and gaps (see Import_scenario_fixes.md)
- Ensuring proper case autocorrect works as intended, with accessibility and test coverage
- Removing legacy test and diagnostic code, streamlining the codebase
- Documenting all findings and improvements in Fdb28_finding-Full_review.md and import_improvement_Feb28.md
- Planning next steps for scenario implementation and enhancements

All tests now pass, accessibility is fully supported, and the codebase is clean and ready for further enhancements. Next session will begin with scenario implementation as outlined in Import_scenario_fixes.md.

---
End of day summary: all major goals for Mar 02 are complete.

