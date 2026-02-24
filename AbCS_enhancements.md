# AbCS Potential Enhancements

This document defines enhancements for AbCS import behavior, with a focus on accessibility and large-library workflows.

## 1) Problem Statement

Current import flow can require manual review before records are written, which is slow for users importing very large collections.

Requested improvement: **add valid books to the database immediately during scanning**, while keeping only review-needed items in the import list.

## 2) Goals

1. Improve throughput for large imports (thousands of books).
2. Preserve quality controls for problematic records.
3. Keep full keyboard/screen-reader accessibility (JAWS/NVDA).
4. Provide clear, real-time status during scanning.

## 3) In Scope

### A. Import checking flags

1. Flag books with `F:` when a fallback value is used for **Title** or **Author**.
	- Example: `F: Title fallback from folder used`
2. Flag books with `F:` when auto-correction is applied.
	- Example: `F: Author auto-correct applied`

### B. Import processing behavior

1. Add **valid books** to the database as they are scanned.
2. Keep records in the import review list when they have any of the following:
	- warnings
	- errors
	- duplicates
	- fallback used
	- auto-correction used

### C. Import progress window (new/updated UI)

Display a process/progress window similar to the MS Access version, with:

- Current Title (Alt+T)
- Current Author (Alt+A)
- Issues summary (Alt+I), shown only when current item has issues
- Files scanned counter (Alt+F)
- Elapsed time (Alt+M)
- Books added counter (Alt+B)
- Read errors counter (Alt+R) — keep this counter
- Current message/status text (screen-reader friendly)
- Cancel button (Alt+L) with confirmation dialog
- On completion: hide Cancel and show Close (Alt+C)

## 4) Accessibility Requirements (Required)

1. Use application scaling for all fonts (no hardcoded small font sizes).
2. Status updates must be sent to the status/message channel used by screen readers.
3. All interactive controls in the progress window must have keyboard shortcuts.
4. Ensure shortcut uniqueness in the import window context.
5. Confirmation and completion messages must use accessible message dialogs.

## 5) Functional Rules

1. “Valid” means no blocking validation errors.
2. Duplicate handling:
	- Do not auto-add confirmed duplicates unless duplicate policy explicitly allows it.
	- Keep duplicates in review list by default.
3. Cancel behavior:
	- Cancel stops scanning safely.
	- Already-added books remain saved.
	- Partial import summary is shown.
4. Import must not freeze UI; progress updates should remain responsive.

## 6) Data/Logging Requirements

1. Track per-record import outcome:
	- added
	- skipped
	- duplicate
	- warning
	- error
	- fallback_used
	- autocorrect_used
2. Keep enough detail to explain *why* a record was not auto-added.
3. Include final session totals:
	- files scanned
	- books added
	- warnings
	- errors
	- duplicates
	- read errors
	- elapsed time

## 7) Suggested UX Flow

1. User selects folder and starts import.
2. Scan begins; valid items are inserted immediately.
3. Progress window updates continuously.
4. Problematic items accumulate in review list.
5. On completion, show summary and enable Close.
6. User can open Import Detail for remaining flagged items.

## 8) Acceptance Criteria

1. During a scan, valid books appear in the database before scan completion.
2. Any record with fallback/auto-correct/duplicate/warning/error remains reviewable.
3. Progress counters update correctly and are announced/readable by assistive tech.
4. Cancel stops additional scanning without corrupting saved data.
5. Completion view replaces Cancel with Close and shows final totals.

## 9) Testing Checklist (Add to phase tests)

1. Import folder with mixed good/bad/duplicate files and verify routing logic.
2. Validate fallback and auto-correct `F:` labels.
3. Validate keyboard-only use of all controls and shortcuts.
4. Validate JAWS/NVDA announcements for key progress messages.
5. Validate cancel mid-run and recovery behavior.
6. Performance test with large folder (target: thousands of files).

## 10) Risks and Mitigations

- Risk: duplicate false positives/negatives.
  - Mitigation: document and centralize duplicate matching rules.
- Risk: accessibility regressions in new progress UI.
  - Mitigation: run accessibility harness and screen-reader smoke tests.
- Risk: long imports overwhelm UI updates.
  - Mitigation: throttle UI refresh frequency while preserving counters.

## 11) Reason for Change

A stakeholder serving blind and visually impaired audiobook users reports very large uncatalogued libraries. This enhancement supports high-volume import with accessibility-first review, reducing manual effort while preserving data quality.

## 12) Latest Update Notes

See [AbCS_Enhancement_Update.md](AbCS_Enhancement_Update.md) for the consolidated update log and implementation status from the latest `## update` notes.

## 13) Implementation Status Summary

### Completed (2026-02-24)
- ✅ Flag generation: Fallback flags use `F:` prefix, auto-correction flags use `C:` prefix
- ✅ Message formats:
  - `F: Title fallback from file used`
  - `F: Title fallback from folder used`
  - `F: Author fallback from folder used`
  - `C: Auto-correct applied to [Field, Field]`
- ✅ Warning categorization: Both `F:` and `C:` flags are treated as warnings (not blocking errors)
- ✅ Prefix preservation: Validator displays `F:` and `C:` exactly as emitted (not converted to `W:`/`E:`)
- ✅ Test coverage: Focused tests for all flag scenarios

### Pending (To Be Implemented)
- ⏳ Import window filter: Add `Fallback` and `Corrected` filter options alongside existing filters
- ⏳ Import processing behavior (item B): Auto-add valid books during scan, keep flagged items in review list
- ⏳ Valid book classification: When item B is implemented, treat fallback/corrected items as valid (can be auto-added)
- ⏳ Optional preference: User-controlled auto-add policy for corrected books

F: Author Fallback folder 

auto-correction messages
C: Trimmed whitespace
C: Skipped leading punctuation 
C: Removed Special characters 
C: Trimmed whitespace

these will be like warning that can be added by selecting them 
import window add corrected and fallback to the filter 

Once we implement item B Import processing behavior we will consider fallback and corrected as valid books in the import window 

Optionally, we could add a choice to auto add corrected books directly  







