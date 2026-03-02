# Mar 02 TODO

## Review Mode for Clean Books Before Adding

### Current State (verified in code)
- [x] Preferences UI already has "Review clean books before adding" and persists `import/auto_add_clean_books` in `src/ui/preferences_window.py`.
- [x] Import flow in `src/ui/import_window.py` no longer auto-adds clean rows when review mode is enabled.
- [x] Dedicated "Add Valid" action is implemented.
- [x] Error filter includes a "Valid" option when review mode is enabled.

### Scope Decision
- This change should be implemented in `src/ui/import_window.py` only for runtime behavior.
- `src/core/validator.py` and `src/core/import_scanner.py` should remain unchanged unless a real blocker appears.

### Implementation Plan (delta only)

#### 1) Wire preference into Import Window
- [x] Add `self.auto_add_clean_books` state and load it in `load_preferences()` from `import/auto_add_clean_books`.
- [x] Add a helper to determine "clean valid" row (no duplicate, no warning, no hard error, no fallback, no correction).

#### 2) Change scan behavior
- [x] In scan/add loop, gate current auto-add logic behind `not self.auto_add_clean_books`.
- [x] When `self.auto_add_clean_books` is enabled, keep clean valid rows in review table instead of inserting into DB immediately.
- [x] Keep duplicate behavior unchanged (duplicates stay in review list and are never auto-added).

#### 3) Add review actions
- [x] Add footer button `Add Valid` (Alt+V) in `ImportWindow`.
- [x] Hook button to `on_add_valid()` that imports all currently displayed clean valid rows.
- [x] Reuse existing row import pipeline (`_import_rows`) where possible.
- [x] After add, refresh table, counters, and status text.

#### 4) Add filter support
- [x] Add `("Valid", "valid")` to error filter options.
- [x] Update `_matches_error_filter()` to support `valid` by using the same clean-valid helper.
- [x] Keep all existing filters unchanged.

#### 5) Accessibility + keyboard
- [x] Update `ALLOWED_ALT_LETTERS` to include `V`.
- [x] Add `Alt+V` shortcut registration in `setup_shortcuts()`.
- [x] Add accessible name/description for `Add Valid` and update shortcut help text (`on_show_shortcuts`).
- [x] Update error-filter accessible description so it mentions `Valid` when enabled.

#### 6) Counter and close-confirm behavior
- [x] Update `_get_valid_import_count()` to count clean valid rows (not warning rows).
- [x] Ensure close confirmation message reports pending clean valid rows correctly.
- [x] Ensure summary/status messaging remains accurate after scan and after Add Valid.

### Acceptance Checklist
- [x] With `import/auto_add_clean_books = False`: clean rows auto-add during scan (current behavior preserved).
- [x] With `import/auto_add_clean_books = True`: clean rows stay in table, no auto-add during scan.
- [x] `Add Valid` adds only clean valid rows, skips warnings/errors/duplicates/fallback/corrected rows.
- [x] `Valid` filter shows only clean valid rows.
- [x] All shortcuts and accessible descriptions are announced correctly by screen readers.
- [x] With review mode enabled, `Valid` count appears and updates in both Import status summary and Import Progress counters.

### Quick Test Pass (manual)
- [x] Scan folder with mixed outcomes: clean, warning, duplicate, fallback, corrected, error.
- [x] Verify counts before/after `Add Valid`.
- [x] Verify `Alt+V`, `Alt+E`, and F1 shortcut list updates.
- [x] Verify close warning reflects remaining clean valid rows.
- [x] Verify `Valid` count is shown in Import status line and Import Progress window while scanning.

### Post-Test Notes (Mar 02)
- [x] With review mode enabled, `Valid` count behavior passed.
- [x] Minor adjustment requested: hide `Valid` counts when review mode is disabled.
- [x] Minor adjustment requested: place `Valid` immediately after `Added` in Import and Progress displays when shown.

### Implementation Complete (Mar 02)
- [x] Review Mode for Import is complete and validated.
- [x] Major behavior updates implemented: review gating, Add Valid action, Valid filter, accessibility/shortcuts, and counter consistency.
- [x] Counter behavior finalized for both review modes, including Add Selected/Add Valid recalculation path.
- [x] Manual validation and regression test passes completed.

