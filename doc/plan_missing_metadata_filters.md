# Missing Metadata Filters — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [plan_ratings.md](plan_ratings.md), [Plan_covers.md](Plan_covers.md), [main window plot/read filters](../src/ui/main_window.py)

---

## What this is

Toolbar or **View** menu filters to show books **missing** common metadata — similar to existing Plot and Read filters.

---

## Problem

Hard to find books needing web fetch or manual cleanup without scanning the whole library.

---

## Design

Extend [`SearchFilter`](../src/database/models.py) with optional flags (v1 pick 2–3):

| Filter | SQL idea |
|--------|----------|
| No plot | `LENGTH(TRIM(comments)) < PLOT_MIN_LENGTH` (reuse plot filter logic) |
| No cover | `cover_path IS NULL OR cover_path = ''` (after covers ship) |
| No rating | `rating IS NULL` (after ratings ship) |
| No path | `path IS NULL OR TRIM(path) = ''` |

UI: checkable toolbar actions or View submenu — mirror `plot_filter_action` / `read_filter_action`.

**Dependency:** No cover/rating filters until Wave 2 schema exists.

---

## Implementation

[`queries.py`](../src/database/queries.py) filter clauses; [`main_window.py`](../src/ui/main_window.py) toolbar + filter summary text.

**Estimate:** 2–3 days (after ratings/covers)

---

## Tests

Filter SQL unit tests; toolbar toggle sync.

---

## Accessibility

Announce filter on/off; include in filter summary label.

---

## Out of scope v1

Combined “any missing” single toggle; saved filter presets.
