# Smart Collections (Saved Filters) — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Collections](help_docs/06_collections.md), [SearchFilter](../src/database/models.py)

---

## What this is

**Saved dynamic filters** — e.g. "Unread sci-fi with plot" — that update as library changes. Not the same as static `collection_id`.

---

## Problem

[`collection_id`](../src/database/models.py) is one shelf per book. Users want virtual lists combining read status, genre, plot, TBR, etc.

---

## Design

- New table `saved_filters` (name, JSON criteria) or QSettings list.
- **View → Saved filters** — apply loads `SearchFilter` preset.
- Optional: pin to toolbar dropdown.

**Estimate:** 1–2 weeks

---

## Tests

Save/load criteria JSON; apply refreshes book list.

---

## Risks

Overlap confusion with collections — clear help text required.

---

## Out of scope v1

Auto-assign books to saved filters; nested boolean logic UI.
