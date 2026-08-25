# Update Window Extensions — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Update window](../src/ui/update_window.py), [plan_want_to_read.md](plan_want_to_read.md), [plan_ratings.md](plan_ratings.md)

---

## What this is

Extend bulk **Update** (Alt+U on selection) beyond series, genre, and collection — add fields that make sense for mass edit.

---

## Problem

[`UpdateWindow`](../src/ui/update_window.py) only updates series, genre, collection. No bulk clear/set for TBR, reader, or year.

---

## Design (v1 candidates)

| Field | Control | Behavior |
|-------|---------|----------|
| Want to read | Checkbox tri-state: Set / Clear / No change | After [`plan_want_to_read.md`](plan_want_to_read.md) |
| Reader | Combo + None | Same immediate-apply pattern |
| Year | Spin or None | Optional |
| Rating | Defer | User-editable per book; bulk rating risky |

Mirror existing combo immediate-update UX and accessible descriptions.

**Estimate:** 2–3 days (after want_to_read column)

---

## Tests

Bulk update SQL; UI apply to selected ids only.

---

## Accessibility

Announce field applied + count updated.

---

## Out of scope v1

Bulk plot edit; bulk web fetch.
