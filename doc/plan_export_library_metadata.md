# Export Library Metadata — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Import Book List](help_docs/20_import_book_list_explained.md), [Book list import window](../src/ui/book_list_import_window.py)

---

## What this is

Export the current library (or filtered subset) to **CSV** or **JSON** for backup, spreadsheets, and migration. Complement to book list **import**.

---

## Problem

No full-library export of metadata. Users rely on SQLite backup only.

---

## Design

- **Manage → Export library…** or main window **Export** when books selected / all visible.
- Columns: title, author, year, series, genre, collection, reader, time, path, read_date, comments (optional truncate), rating/want_to_read when those columns exist.
- Respect active filters (collection, search, read, plot, want_to_read).
- UTF-8 CSV with BOM for Excel; optional JSON array of objects.
- File dialog default: Documents folder, timestamped filename.

---

## Implementation

| Area | Change |
|------|--------|
| New | `src/core/library_export.py` — build rows from `Book` list |
| [`main_window.py`](../src/ui/main_window.py) | Menu/toolbar action |

**Estimate:** ~2 days

---

## Tests

`test/test_library_export.py` — column headers, filter respect, empty library.

---

## Accessibility

Progress/status for large exports; announce row count on complete.

---

## Out of scope v1

Export audio files; incremental/sync export.
