# Book Tags (Multi-Label) — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Collections](help_docs/06_collections.md), [plan_want_to_read.md](plan_want_to_read.md)

---

## What this is

Multiple **tags** per book (e.g. "gift", "re-read", "book club") — many-to-many, unlike single collection or single TBR flag.

---

## Problem

Collection is one-per-book. Tags express cross-cutting labels without moving books.

---

## Design

- Tables: `tags`, `book_tags` junction.
- UI: tag editor on Book Details; filter by tag on main window.
- Import/export tags in library export plan.

**Estimate:** 2–3 weeks

---

## Tests

Junction CRUD; filter by tag.

---

## Risks

Overlap with want_to_read and collections — document when to use each.

---

## Out of scope v1

Hierarchical tags; tag colors.
