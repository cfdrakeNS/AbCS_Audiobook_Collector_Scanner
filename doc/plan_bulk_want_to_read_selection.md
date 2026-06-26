# Bulk Want to Read on Selection — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [plan_want_to_read.md](plan_want_to_read.md)

---

## What this is

Mark or clear **want_to_read** for all **selected books** on the main window without opening Book Details for each.

---

## Problem

TBR flag is per-book in Book Details. Adding many books to a reading queue is tedious.

---

## Design

- Footer or Update menu: **Mark want to read** / **Clear want to read** when `selected_book_ids` non-empty.
- [`BookQueries`](../src/database/queries.py) bulk update `want_to_read`.
- Status: `N books marked want to read` with `announce=True`.
- Clearing read date does not auto-set want_to_read.

**Estimate:** ~1 day (after want_to_read column)

---

## Tests

`bulk_set_want_to_read` SQL; empty selection disabled.

---

## Accessibility

Button accessible names; announce count.
