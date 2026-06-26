# Plot Full-Text Search — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Search on main window](../src/ui/main_window.py), [`PLOT_MIN_LENGTH`](../src/database/models.py)

---

## What this is

Faster, richer **plot/comments search** using SQLite FTS5 (full-text search) instead of `LIKE` on large libraries.

---

## Problem

Plot keyword search may slow on 30k+ books with long comments. `LIKE '%term%'` cannot use index well.

---

## Design

- FTS5 virtual table `books_fts` synced with `books.comments` (and optionally title/author for unified search — scope decision at implement time).
- Migrate on startup or rebuild from menu **Rebuild search index**.
- [`BookQueries.get_all`](../src/database/queries.py) plot search path uses FTS when keyword mode active.
- Fallback to LIKE if FTS unavailable (older SQLite builds — rare).

**Estimate:** 3–5 days

---

## Tests

FTS match ranking; sync on book update/delete; rebuild.

---

## Accessibility

Search behavior unchanged for user — same Find dialog; announce result count.

---

## Out of scope v1

Fuzzy/phonetic search; search outside plot field.
