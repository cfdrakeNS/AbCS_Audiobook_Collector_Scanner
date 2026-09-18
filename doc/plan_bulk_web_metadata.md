# Bulk Web Metadata Fetch — Version 3 Phase 2

**Status:** Planned — **Version 3 Phase 2** (not post-v3)  
**Created:** June 2026  
**Updated:** September 2026  
**Related:** [Web Metadata](../help_docs/07_web_metadata.md), [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

Queue **web metadata fetch** for multiple selected books with progress, cancel, an accessible summary dialog, and Apply all / Review each — not one-at-a-time only.

Depends on **Phase 1** (background worker). Does **not** wait on ratings or covers; v3 applies fields AbCS already stores (title, author, plot, year, genre, narrator, comments).

---

## Problem

Help states fetch works on **one book at a time**. Large libraries need batch enrichment. Calibre’s completion prompt is silent to JAWS because it uses a non-modal NoFocus overlay — AbCS must not copy that pattern.

---

## Design

### Entry point

- Main window when **two or more** books are selected: footer button **Web fetch** (same pattern as Update / Delete via `update_selection_ui()`).
- Suggested shortcut **Alt+B** (free). Do not reuse the dead Alt+A entry.
- **Alt+W stays single-book**: fetch focused book and open review immediately. No accumulation across Alt+W presses. Alt+W already returns early when multi-select is active.

### Progress

Reuse the Phase 1 worker, driven by a queue. Presentation like [`import_progress_window.py`](../src/ui/import_progress_window.py): current title, N of M, cancel. Per-book failures log a row; queue continues.

### Summary dialog (accessibility centrepiece)

After the queue drains, modal [`AccessibleDialog`](../src/ui/accessible_dialog.py) with `exec()`:

- `raise_()` and `activateWindow()` first (user may have Alt+Tab’d away).
- Explicit focus on the default button.
- Full summary text as accessible description so it is spoken on open.

Content:

- Totals: fetched, with new information, no match, errored.
- Keyboard-reachable details list of books with no match.
- Buttons: **Apply all**, **Review each**, **Cancel** (discard results).

Prefer `exec_styled_message_box` if three custom buttons fit; otherwise a small dedicated dialog.

### Apply all

Apply only fields existing diff helpers report as changed (`compute_field_differences` / `web_data_offers_changes`). Announce applied count on the main status bar (`announce=True`). Restore focus to the table.

### Review each

[`WebMetadataWindow`](../src/ui/web_metadata.py) already accepts pre-fetched `web_data`. Add queue navigation: next / skip, announce “book 2 of 5”. Save or skip advances the queue.

---

## Risks

- API rate limits; slow on 100+ books.
- User expectation of unattended auto-fill — document clearly.

**Estimate:** 1–2 weeks

---

## Tests

Mock API; queue cancel; cache hit skips network; summary dialog focus; Apply all field selection.

---

## Accessibility

- Announce progress; cancel restores focus.
- Completion always modal `AccessibleDialog` — never Calibre’s NoFocus overlay.
- Status announce after Apply all.

---

## Out of scope v1

Fully unattended auto-save all fields; parallel HTTP per book; “all visible filtered books” entry (multi-select only); ratings/covers (deferred features).
