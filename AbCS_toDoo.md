# AbCS Outstanding Items (Prioritized)

Source reviewed: `AbCS Quick Guide(ms access).md`  
Comparison baseline: current Python app in `src/ui`

**Last updated:** 2026-02-24

## COMPLETED (2026-02-24)

- [x] Implement import flag labeling for fallback/autocorrect
  - [x] Add `F:` marker for title/author fallback usage (folder/filename fallback)
  - [x] Add `C:` marker for auto-correct usage (trim, punctuation, special chars)
  - [x] Suppress `C:` when `F:` exists for same field (no redundant flags)
  - [x] Limit `C:` flags to Title/Author only (Genre/Series corrections are silent)
  - [x] Exclude proper case and "The" movement from `C:` flagging
  - [x] Specific correction messages (e.g., "C: Title trimmed" not generic "Auto-correct applied")
  - [x] Comprehensive test coverage (7 passing tests in test_import_scanner_fallbacks.py)

- [x] Import window UI fixes
  - [x] Fixed keyboard shortcuts: Alt+C (Collection), Alt+L (Close), Alt+N (Cancel)
  - [x] Added 'N' to ALLOWED_ALT_LETTERS for Alt+N support
  - [x] Fixed Close button default state (Enter key works when not scanning)
  - [x] Cancel button properly configured during scan mode

- [x] Import detail window UI fixes
  - [x] Fixed Year/Time field spacing (Year 110px, 40px spacing between groups)
  - [x] Fixed Time label positioning (removed sub-layout wrapper)
  - [x] Collection field made tabbable/read-only (editable combo with read-only line edit)

- [x] Enhanced accessibility checker (test/check_shortcut_mnemonics.py)
  - [x] Added ALLOWED_ALT_LETTERS validation
  - [x] Detects mnemonics missing from allowed set
  - [x] Found and fixed Alt+W in preferences_window

## NOW (highest impact: accessibility + daily workflow)

- [x] Implement Backup/Restore window
  - [x] Backup list/browse/restore file textbox UI
  - [x] Backup action
  - [x] Restore action
  - [x] Full Reset action

- [x] Build accessible Import Progress window (MS Access parity + AbCS standards)
  - [x] Add fields: current Title (Alt+T), current Author (Alt+A), Issues (Alt+I, conditional)
  - [x] Add counters: Files scanned (Alt+F), Elapsed time (Alt+M), Books added (Alt+B), Read errors (Alt+R)
  - [x] Add Cancel (Alt+L) with confirmation dialog
  - [x] On completion, hide Cancel and show Close (Alt+C)
  - [x] Route all status/progress messages to screen-reader-friendly status channel
  - [x] Validate font scaling/theme compliance (no hardcoded small fonts)
  - [x] Show scan completion summary in progress status bar (no popup)

- [x] Implement high-volume import flow (auto-add valid while scanning)
  - [x] Update import pipeline to insert valid books immediately during scan
  - [x] Keep flagged records in import review list (warnings/errors/duplicates/fallback/autocorrect)
  - [x] Add per-record outcome state (`added`, `skipped`, `duplicate`, `warning`, `error`, `fallback_used`, `autocorrect_used`)
  - [x] Preserve safe cancel semantics (stop scanning, keep already-added records)

- [x] Add Import Window filter options for Fallback and Corrected flags
  - [x] Add "Fallback" option to error filter combo
  - [x] Add "Corrected" option to error filter combo
  - [x] Update filter logic to match F: and C: prefixes

## NEXT (important parity, moderate impact)

- [ ] Import footer `Export` (error list to spreadsheet) 

- [ ] Add import session summary view/report
  - [ ] Show final totals: scanned, added, warnings, errors, duplicates, read errors, elapsed time
  - [ ] Show partial summary on cancel
  - [ ] Ensure summary is accessible to keyboard/screen readers

- [ ] Document duplicate-policy behavior in import UI/help
  - [ ] Clarify default: duplicates remain in review list unless policy allows auto-add
  - [ ] Add tests for duplicate matching edge cases

## LATER (legacy parity refinements)

- [ ] Import Detail `Edit Tag` integration (Mp3Tag/TagScanner detection + launch)

- [ ] Performance tuning for large imports
  - [ ] Throttle progress UI repaint frequency without losing counter accuracy
  - [ ] Validate responsiveness with thousand-file test sets
  - [ ] Record baseline timing metrics for regression checks

- [ ] Add automation coverage for new import flow
  - [ ] Mixed dataset routing test (valid + duplicate + warning + error)
  - [ ] Keyboard-only progress window interaction test
  - [ ] JAWS/NVDA smoke checks for progress announcements

## Notes

- Several legacy items are already implemented in modernized form (for example, many Alt+shortcuts, duplicate check action, import detail navigation, and add-selected/add-all flows).
- This list tracks items still not implemented or not parity-matched from the old MS Access guide.
- **Accessibility validation:** Run `python test/check_shortcut_mnemonics.py` to verify all Alt+letter shortcuts are properly registered in ALLOWED_ALT_LETTERS for windows using event filters.
