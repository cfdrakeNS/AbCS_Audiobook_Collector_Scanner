# Path Health Report — Version 3 Phase 25 / F01

**Status:** Complete  
**Created:** June 2026  
**Related:** [plan_enhancements_version3_release.md](../plan_enhancements_version3_release.md), [plan_book_details_path_browse.md](plan_book_details_path_browse.md), [plan_check_books_path_progress.md](plan_check_books_path_progress.md), [plan_rescan_and_library_folders.md](../plan_rescan_and_library_folders.md), [plan_audiobook_preview.md](plan_audiobook_preview.md)

---

## What this is

**Manage → Check Books Path…** scans one collection and reports books whose stored `path` is blank, missing on disk, or not under the collection library root.

---

## Shipped

- `src/core/path_health.py` — Empty/Missing (not playable after Play remap) vs Incorrect (remap or off library root) vs OK; exclusive filters missing | incorrect | all; per-book roots for All Collections
- `src/ui/path_health_window.py` — Collection combo (All Collections + names), Filter (default All), Scan (Alt+S) only on button press, Import-style progress with live Missing / Incorrect / Valid, Author/Title/Path table, Export, Enter opens Book Details
- Manage menu: **Check Books Path**; blocked in selection or duplicate mode; opens with main-window collection (or All)
- Help: `24_path_health.md`, shortcuts, overview link, Shift+F1 map
- Tests: `test/test_path_health.py`

---

## Gate

Passed. Report lists empty and missing paths; Export CSV works; Open Book Details can fix path via Browse; no silent path rewrites.

**Follow-up:** Phase 26 progress — **complete** — [plan_check_books_path_progress.md](plan_check_books_path_progress.md).
