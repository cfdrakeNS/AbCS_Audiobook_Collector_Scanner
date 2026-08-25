# Want to Read on Import Detail — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [plan_want_to_read.md](plan_want_to_read.md), [Import Detail](help_docs/12_import_detail.md)

---

## What this is

**Want to read** checkbox on **Import Detail** so users can flag books during import review before they are added to the library.

---

## Problem

TBR only in Book Details after import. Users reviewing import rows may want to queue books immediately.

---

## Design

- Same checkbox as Book Details on [`import_detail_window.py`](../src/ui/import_detail_window.py).
- Store in `book_data["want_to_read"]` during review; pass to `Book` on insert in [`import_window.py`](../src/ui/import_window.py).
- If book not yet in DB, flag applies on add only.

**Estimate:** ~1 day (after want_to_read column)

---

## Tests

Import path persists `want_to_read=1`.

---

## Accessibility

Same checkbox pattern as Book Details.
