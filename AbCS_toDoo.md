# AbCS Outstanding Items (Prioritized)

Source reviewed: `AbCS Quick Guide(ms access).md`  
Comparison baseline: current Python app in `src/ui`

**Last updated:** 2026-02-25 (Import baseline SSD comparison + JAWS status-read verification)

## COMPLETED (2026-02-25)

- [x] Improve import scan responsiveness/accessibility (counters-first progress updates)
  - [x] Throttle progress updates to interval-based refresh (reduce UI churn)
  - [x] Keep scan-time feedback focused on counters/status during active scan
  - [x] Add compact/counters-only mode for Import Progress window during scan

- [x] Fix startup/runtime Qt tab-order warnings in Import Window
  - [x] Resolve `QWidget::setTabOrder: 'first' and 'second' must be in the same window`
  - [x] Move tab-order wiring to run after footer layout widgets are attached to dialog

- [x] Align Import Window collection mnemonic with tests/accessibility checks
  - [x] Update label from `&Collection:` to `Co&llection:`
  - [x] Verify import window collection rules test suite passes

- [x] Import Detail `Edit Tag` integration (Mp3Tag/TagScanner detection + launch)
  - [x] Add Import Detail footer action `Launch Tag` (Alt+L)
  - [x] Auto-detect Mp3tag/TagScanner from PATH and common Windows install locations
  - [x] Launch editor for current item file/folder path with accessible status feedback
  - [x] Show clear message when supported tag editor is not installed

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
  - [x] Comprehensive test coverage (6 passing tests in test_high_volume_import_flow.py)

- [x] Add Import Window filter options for Fallback and Corrected flags
  - [x] Add "Fallback" option to error filter combo
  - [x] Add "Corrected" option to error filter combo
  - [x] Update filter logic to match F: and C: prefixes

- [x] Add import session summary view/report
  - [x] Show final totals: scanned, added, warnings, errors, duplicates, read errors, elapsed time
  - [x] Show partial summary on cancel
  - [x] Ensure summary is accessible to keyboard/screen readers

## NOW (next priorities: import refinements + workflow enhancements)

- [x] Import footer `Export` (error list to spreadsheet)
  - [x] Added footer Export action in Import Window
  - [x] Exports current visible import review/error list to CSV spreadsheet
  - [x] Includes Author, Title, Year, Error Type, File/Folder columns
  - [x] Default export filename includes datetime stamp

- [x] Document duplicate-policy behavior in import UI/help
  - [x] Clarify default: duplicates remain in review list unless policy allows auto-add
  - [x] Add tests for duplicate matching edge cases
    - [x] Case/whitespace-insensitive duplicate match test
    - [x] Year-sensitivity by duplicate match mode test

## LATER (legacy parity refinements)

- [ ] Performance tuning for large imports
  - [x] Throttle progress UI repaint frequency without losing counter accuracy
  - [ ] Validate responsiveness with thousand-file test sets (external dataset)
    - [ ] Handoff test execution to Wayne/QA with large real audiobook library
    - [ ] Capture baseline: elapsed scan time, responsiveness notes, and screen-reader announcement quality
    - [ ] Optional local fallback: run same checks with synthetic/duplicated audio sample set when large library is unavailable
  - [x] Record baseline timing metrics for regression checks (tooling)
    - [x] Added baseline capture script: `test/import_scan_baseline.py`
    - [x] Example command: `python test/import_scan_baseline.py --folder <path> --subfolders --repeats 3 --json-out test/results/import_scan_baseline.json`
    - [x] Run against large real dataset and attach output JSON to handoff notes
      - [x] Dataset: USB external drive `F:\Audio Books testing` (8,658 files, 652 folders; 108 GB)
      - [x] Scan result: 18,076 audio files detected; 541 books found
      - [x] Timing (3 runs): avg 149.6416s / min 148.1508s / max 152.0696s
      - [x] Output JSON: `test/results/import_scan_baseline_usb.json`
    - [x] Re-run same baseline on local SSD copy to isolate USB I/O impact
      - [x] Dataset: laptop SSD `E:\Audio Books testing`
      - [x] Scan result: 17,131 audio files detected; 517 books found
      - [x] Timing (3 runs): avg 44.2779s / min 43.9335s / max 44.6817s
      - [x] Output JSON: `test/results/import_scan_baseline.json`
      - [x] Compare avg/min/max vs USB baseline and record delta
        - [x] Avg delta vs USB: 105.3637s faster on SSD (149.6416s → 44.2779s)
        - [x] Relative improvement: ~70.4% faster (~3.38x speedup)

- [ ] Database performance with 34k-book dataset (Wayne's real library)
  - [x] Created database swap script: `test/swap_test_database.py`
  - [x] Swapped test database for Wayne's 34k-book database (D:\_Wip\abcs test\wh\abcs_wh.db)
  - [x] Verified schema: date_added column present (DATETIME type)
  - [x] Ran database repair: all 12 indexes created + VACUUM + ANALYZE
  - [x] Manual performance testing: Switch sort orders and record real timings
    - [x] Measured (2026-02-25): Title → Author = 14s
    - [x] Measured (2026-02-25): Author → Title = 13s
    - [x] Result: Not acceptable for UX (target < 1 second)
    - [x] Re-tested after optimizations (2026-02-25): App startup = 8.8s
    - [x] Re-tested after optimizations (2026-02-25): Title → Author = 3.8s
    - [x] Re-tested after optimizations (2026-02-25): Author → Title = 3.8s
    - [x] Result: Significant improvement, still above target (< 1 second)
  - [x] Run automated performance test: `python test/perf_test_34k_books.py`
    - [x] Captured timing for Title/Author/Genre/Series (3 runs each)
    - [x] Output generated: `perf_results_34k_books.json`
    - [x] DB query timings are excellent (Title 0.046s, Author 0.068s, Genre 0.062s, Series 0.064s avg)
  - [x] Investigate UI table rendering bottleneck on sort switch (query layer appears healthy)
    - [x] Profile `MainWindow.refresh_books()` population path with 34k rows
    - [x] Implement targeted optimization passes (selection repaint, column sizing, date hydration)
    - [x] Implement model-based table path (`QTableView` + model) for large datasets
    - [x] Re-test manual sort switch target: < 1 second
      - [x] Measured (2026-02-25): App startup = 0.9s
      - [x] Measured (2026-02-25): Title → Author = 0.5s
      - [x] Measured (2026-02-25): Author → Title = 0.5s
      - [x] Result: Performance target met (< 1 second)
    - [x] Manual keyboard navigation regression pass (2026-02-25)
      - [x] Arrow keys, Shift+Space + Shift+Arrows, Ctrl+Space, Ctrl+Enter, ESC all OK
  - [x] If performance is acceptable (< 1 sec), schedule handoff to Wayne
  - [x] If performance is still slow after UI optimization, investigate deeper rendering hot paths (not required; performance target met)

- [x] Add automation coverage for new import flow
  - [x] Mixed dataset routing test (valid + duplicate + warning + error)
  - [x] Keyboard-only progress window interaction test
  - [x] JAWS/NVDA smoke checks for progress announcements

## Handoff Test Script (Wayne/QA)

- [ ] Prepare dataset and environment
  - [ ] Use a real library with ~1,000+ audio files (or largest available set)
  - [ ] Confirm target collection exists in AbCS
  - [ ] Enable JAWS or NVDA before scan starts

- [ ] Execute import scan
  - [ ] Open Import Window and select collection + folder
  - [ ] Start scan and keep focus in Import Progress window
  - [ ] Verify compact progress behavior: counters update smoothly and window remains responsive

- [ ] Accessibility checks during scan
  - [ ] Confirm Alt+F/Alt+M/Alt+B/Alt+R read useful counter values
  - [x] Confirm Alt+/ reads current status bar message clearly (JAWS verified in progress window)
  - [ ] Confirm Cancel/Close controls are keyboard reachable and correctly announced

- [ ] Capture and report results
  - [ ] Record elapsed scan time and files scanned
  - [ ] Note any lag, freezes, delayed keyboard response, or missed announcements
  - [x] Attach summary outcome: Needs Work (JAWS Alt+/ status-read PASS; import progress counter/status focus fixes applied, final QA re-test pending)

## Notes

- Several legacy items are already implemented in modernized form (for example, many Alt+shortcuts, duplicate check action, import detail navigation, and add-selected flow).
- Import window UX simplified: `Add All Valid` removed; valid records auto-add during scan, and `Add Selected` remains for manual add of review-list items.
- This list tracks items still not implemented or not parity-matched from the old MS Access guide.
- **Accessibility validation:** Run `python test/check_shortcut_mnemonics.py` to verify all Alt+letter shortcuts are properly registered in ALLOWED_ALT_LETTERS for windows using event filters.
