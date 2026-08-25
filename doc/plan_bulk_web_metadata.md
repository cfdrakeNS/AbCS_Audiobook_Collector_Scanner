# Bulk Web Metadata Fetch — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Web Metadata](help_docs/07_web_metadata.md), [plan_ratings.md](plan_ratings.md), [Plan_covers.md](Plan_covers.md)

---

## What this is

Queue **web metadata fetch** for multiple selected books (or all visible filtered books) with progress, cancel, and per-book review — not one-at-a-time only.

---

## Problem

Help states fetch works on **one book at a time**. Large libraries need batch enrichment for plot, rating, cover.

---

## Design

- Entry: main window when 2+ books selected — **Fetch web info for selection** (confirm count).
- Worker: sequential fetch via existing [`WebBookAPI`](../src/web/web_book_api.py) (respect cache); optional delay between requests.
- UI: progress window (reuse [`ImportProgressWindow`](../src/ui/import_progress_window.py) pattern) — current title, N/M, cancel.
- After each fetch: open simplified review **or** auto-apply safe fields only — **v1 recommend manual review queue** (open Web Metadata for each with pre-fetched data, user saves or skips).
- Network errors: log row, continue queue.

---

## Risks

- API rate limits; slow on 100+ books.
- User expectation of unattended auto-fill — document clearly.

**Estimate:** 1–2 weeks

---

## Tests

Mock API; queue cancel; cache hit skips network.

---

## Accessibility

Announce progress; cancel restores focus.

---

## Out of scope v1

Fully unattended auto-save all fields; parallel HTTP threads.
