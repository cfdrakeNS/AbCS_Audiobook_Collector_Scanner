# Check Books Path progress — Version 3 Phase 26

**Status:** Complete  
**Estimate:** 0.5–1 day  
**Related:** [plan_path_health_report.md](plan_path_health_report.md), [plan_enhancements_version3_release.md](../plan_enhancements_version3_release.md), Import progress ([import_progress_window.py](../../src/ui/import_progress_window.py))

---

## Goal

Keep **Manage → Check Books Path** as shipped in Phase 25. On **Scan**, show an Import-style progress window so large collections and NAS paths do not freeze the UI with no feedback. Live counters for **Missing**, **Incorrect**, and **Valid (OK)** keep the user informed while the scan runs.

Non-modal “use the main window during scan” stays out of scope (same risk as deferred non-modal web fetch).

---

## Problem

Phase 25 scans on the GUI thread with no progress. Thousands of books or paths on a local network device can stall Check Books Path with no Escape cancel and no count feedback.

---

## Design

### Progress window (Import-like)

- Open a compact progress dialog when Scan starts (reuse patterns from `ImportProgressWindow`: bar, elapsed, Escape cancel, Alt+/, status).
- Prefer reusing or lightly adapting Import progress rather than inventing a third progress style.
- Check Books Path window stays open behind it (collection, filter, results table unchanged).

### Live counters (amuse / inform)

While scanning, show running totals:

| Count | Meaning |
|-------|---------|
| **Missing** | Blank path, or not playable after the same remap Play uses |
| **Incorrect** | Playable via remap, or on disk but not under the library root |
| **Valid** | OK — stored path exists (and under root when a root is set) |

Also show **N of M** books processed and elapsed time. Update often enough to feel alive (Import uses ~0.15 s throttle); do not announce every tick to screen readers — announce start, cancel, and completion (or meaningful milestones only).

### Cancel and completion

- Escape cancels cooperatively (finish current book, stop the queue).
- On finish or cancel: close progress, fill the results table from the scan so far (respect current filter), announce the same status line Phase 25 already uses.
- Filter still applies to the **results table** after the scan; progress always tallies all three buckets for the full pass so Valid counts even when the filter is Missing/Incorrect/All.

### Threading / responsiveness

- Process books with UI yield so Escape and counter updates work (worker thread with queued progress signals, or Import-style loop with `processEvents` between books). Prefer the pattern that matches Import most closely unless a worker is clearly safer for NAS stalls.
- Path checks stay in `path_health.check_book_path` / `scan_book_paths` — refactor to a per-book callback or iterator so progress can update without duplicating Play-align logic.

---

## Implementation

| Area | Change |
|------|--------|
| New or reuse | Progress UI (Import progress compact mode or thin wrapper) |
| [`path_health.py`](../../src/core/path_health.py) | Iterator / callback API for one book at a time + running counts |
| [`path_health_window.py`](../../src/ui/path_health_window.py) | Scan opens progress; updates Missing / Incorrect / Valid; cancel; then fill table |
| Help | [`24_path_health.md`](../../help_docs/24_path_health.md) — Scan shows progress with live counts |

**Out of scope:** Non-modal scan; auto-fix paths; changing Phase 25 filter semantics.

---

## Tests

- Unit: running counts after a mixed list (empty, missing, incorrect, OK).
- UI smoke: Scan opens progress; cancel leaves partial or empty results without freeze; completion fills table.

---

## Accessibility

- Progress dialog: accessible name/description; Alt+/ status; Escape cancel (confirm if Import does).
- Do not spam JAWS on every book; completion announces Missing / Incorrect / Valid summary.
- Restore focus to Check Books Path list or Scan after progress closes.

---

## Gate

**Passed.** Progress shows Missing, Incorrect, and Valid while scanning (`N books scanned: …`); Escape cancels; All Collections and default All filter; results match Phase 25 Play-aligned rules. Collection submenu deferred (window stays as shipped).
