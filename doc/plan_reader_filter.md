# Reader / Narrator Filter — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [plan_want_to_read.md](plan_want_to_read.md), [main window filters](../src/ui/main_window.py)

---

## What this is

Filter main book list by **reader/narrator** — combo or search on distinct `books.reader` values.

---

## Problem

Reader is stored and shown in Book Details but not a filter dimension. Libraries with favorite narrators need quick subset views.

---

## Design

- **View → Reader** submenu or filter combo on main window (distinct readers from DB, cached refresh).
- [`SearchFilter`](../src/database/models.py): `reader_filter: str = ""` (empty = all).
- SQL: `AND b.reader = ? COLLATE NOCASE` when set.
- Filter summary: `Reader: {name}`.

**Estimate:** 2 days

---

## Tests

Filter query; empty reader handling.

---

## Accessibility

Combo accessible name; announce filter applied.

---

## Out of scope v1

Multi-select readers; partial text match (use main Find for that).
