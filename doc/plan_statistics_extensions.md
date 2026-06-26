# Statistics Extensions — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Statistics](help_docs/14_statistics.md), [plan_want_to_read.md](plan_want_to_read.md), [plan_ratings.md](plan_ratings.md)

---

## What this is

Add rows to **Statistics** dialog for new metadata: want-to-read count, average rating, books with cover, etc.

---

## Problem

Statistics dialog does not reflect TBR, ratings, or covers after those features ship.

---

## Design

Extend [`statistics_dialog.py`](../src/ui/statistics_dialog.py) and query layer:

| Stat | After feature |
|------|----------------|
| Books want to read | want_to_read |
| Average rating (library) | rating column |
| Books with cover | cover_path |
| Books missing path | optional link to path health |

Accessible table — same pattern as existing stats rows.

**Estimate:** 1–2 days (after Wave 2)

---

## Tests

Stat queries with fixture DB.

---

## Out of scope v1

Charts/graphs; export stats.
