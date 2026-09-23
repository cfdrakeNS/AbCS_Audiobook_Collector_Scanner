# Keep current book on sort and filter — Version 3 Phase 8

**Status:** Complete — tester accepted  
**Created:** September 2026  
**Related:** [main window](../src/ui/main_window.py), [Find and filters](../help_docs/03_find_filters.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

After **Sort** (menu or column header), the book that had keyboard and screen-reader focus stays the current book. The same applies to **filters** when that book is still in the list. If a filter drops the book, focus moves to the first remaining row.

---

## Problem

`refresh_books` and in-memory sort already captured a row index and tried to restore it. Screen readers still landed on the first row because:

- `BookTableModel.set_books` resets the model and the accessibility tree
- Restore used `TabFocusReason`, which often sounds like entering the table at the top
- A missing `currentRow` fell back to the **old row number**, which is a different book after sort
- `processEvents()` after restore could move current index again

---

## Behavior

- Remember the focused book by `book_id` on current-cell change (`_last_table_book_id`)
- After sort: if that book is still listed, make it current, scroll it into view, focus with `OtherFocusReason`. Do not reuse the old row index
- After a filter that still includes that book (collection, Read, Plot, Find, Recently added): same restore
- After a filter that drops that book: first remaining row. Empty list unchanged
- Multi-select: keep selected IDs that are still in the list; current index stays on the focused book when it remains
- Duplicate mode: same rules inside the duplicate subset
- Sort does not re-speak the filter summary

---

## Files

- [`src/ui/main_window.py`](../src/ui/main_window.py) — capture before reload, restore by `book_id` after model reset
- [`test/test_main_window_keep_book_focus.py`](../test/test_main_window_keep_book_focus.py)
- [`help_docs/03_find_filters.md`](../help_docs/03_find_filters.md)

---

## Tests

- SQL sort (Author/Title) and in-memory sort (Year/Time) keep `book_id` as current
- Read filter that still includes the book keeps it
- Read filter that excludes the book focuses the first remaining row

---

## Accessibility

- Restore uses `Qt.OtherFocusReason`, not Tab
- Restore runs after `processEvents` so Qt’s model-reset current index does not win
- JAWS gate: arrow to a middle book, sort by author, still that title; Unread while unread stays; Read while unread moves to the first remaining book
