# Path Health Report — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md), [plan_audiobook_preview.md](plan_audiobook_preview.md)

---

## What this is

**Manage → Path health…** (or similar) scans the library and reports books whose stored `path` is missing, empty, or points to a non-existent file/folder on disk.

---

## Problem

After moves, renames, or drive changes, `books.path` becomes stale. Users discover this only when opening location or rescanning manually.

---

## Design

- Scope: current collection filter or all collections (user choice).
- For each book: check `os.path.exists(book.path)` (file or folder).
- Results table: Author, Title, Path, Status (`Missing`, `Empty`, `OK`).
- Actions: **Export CSV**; optional **Open Book Details** for selected row.
- No automatic path fix in v1 — pairs with rescan (user fixes via rescan or hand edit).

---

## Implementation

| Area | Change |
|------|--------|
| New | `src/core/path_health.py` — scan books, return result rows |
| New | `src/ui/path_health_window.py` — report UI |
| [`main_window.py`](../src/ui/main_window.py) | Manage menu entry |

**Estimate:** 2–3 days

---

## Tests

`test/test_path_health.py` — missing path, folder exists, file exists, empty path.

---

## Accessibility

Accessible table; status announcements with counts; Alt+/ on window.

---

## Out of scope v1

Auto-repair from rescan; batch delete missing-path books.
