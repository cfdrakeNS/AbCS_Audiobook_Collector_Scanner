# Series Number in Database — Version 3 Phase 10 / F10

**Status:** In tester build 2.17. Book Details display confirmed. Version 3 Phase 10.  
**Created:** June 2026  
**Updated:** September 2026 — shipped behavior below. Phase 9 schema accepted.  
**Related:** [plan_schema_batch.md](plan_schema_batch.md) (v3 Phase 9), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [scripts/update_series_from_catalog.py](../scripts/update_series_from_catalog.py)

---

## What this is

Persist **series number** (for example book 3, or 6.5) in SQLite as a real number. The only place it shows in the UI is **Book Details**, a text box to the right of Series. There is no shortcut for that box. Alt+I focuses Series, then Tab moves to Series #. When a book is shown and Series # is blank, a number at the end of the title is stored. The title stays as it is. There is no status message. A stored Series # is left as it is. A year such as 1999 stays on the title. **Book List Import** stores a mapped Series # and appends it to the title. **Series From File Name** does the same for a number in the file name, including 6.5. Import Detail, the main table, and the Update window do not show a series-number field. The main-window **Series** sort is series name, then series number, then title.

**Scope note (2026-09):** Fetch Web Info does not retrieve or display series or series number. Series entry is **manual only** on Book Details. Import Detail, the main book table, and the Update window do not show a series-number field. The main-window **Series** sort orders by series name, then series number.

---

## Problem

Series number is not stored on `Book`. Title sometimes carries a `" - 3"` suffix instead (`split_series_number` / `append_series_suffix` in [`src/utils/text_utils.py`](../src/utils/text_utils.py)). Book List Import can map a Series # column into the title suffix; folder Import Detail has Series name only.

How books are stored today (relevant bits):

- `books` has `series_id` (FK to `series.name`) and `title`. Phase 9 added nullable `series_number REAL`. Phase 10 shows it on Book Details.
- Series number in titles is parsed for duplicate matching only (`ImportValidator`).
- Book List Import appends the Series # onto `title` and also stores `series_number`.

---

## Design

### Schema (Phase 9 — first start, existing DBs)

Column added by [plan_schema_batch.md](plan_schema_batch.md) on first start of a build that includes C01:

- `series_number REAL` nullable on `books`

This runs through `_ensure_legacy_schema_compatibility` for **existing** libraries (in-place `ALTER TABLE` after a `schema_repair` backup), not only new installs. Map on `Book` with default `None`. First start adds the column only. It does not parse numbers out of existing titles.

### UI — Book Details ([`src/ui/book_details.py`](../src/ui/book_details.py))

The only series-number control. Place a text box on the Series row, **to the right of Series**. Save/load `book.series_number` as a real number, so `3` and `6.5` both store. Blank means no number. When a book is shown and Series # is blank, if the title ends with a series suffix, store that number. Leave the title as it is. No status message. The form stays clean. A stored series number is left as it is. A year such as `1999` stays in the title.

### Book List Import ([`src/ui/book_list_import_window.py`](../src/ui/book_list_import_window.py))

Keep the existing Series and Series # column mapping. When Series # has a value, store it on `book.series_number` and append it to the title with `append_series_suffix`. Series name still sets `series_id` as it does today.

### Folder Import — Series From File Name

[`import_scanner.py`](../src/core/import_scanner.py) scenario `series_from_filename` still appends the number to the title. It also stores that number on `book.series_number`, including a decimal such as `6.5`. Import Detail does not gain a series-number field. The other folder-import scenarios are unchanged.

### Sort — main window

The existing **Series** sort (Sort menu and the Series column header) changes. Today it is series name, then year, then title (`ORDER BY s.name, b.year, b.title` in [`queries.py`](../src/database/queries.py)). It becomes series name, then series number, then title.

Books with no series number sort after numbered books in that series. The sort label that now says “Series, Year, Title” becomes “Series, Series number, Title”. No new sort item. No series-number column on the main table.

### Optional offline

[`scripts/update_series_from_catalog.py`](../scripts/update_series_from_catalog.py) may write the column once it exists — keep in sync with field name.

**Estimate:** 2–3 days (after Phase 9)

---

## Tests

- Save/load from Book Details; field is to the right of Series
- Showing a book with a blank Series # and a title suffix stores that number, leaves the title unchanged, and does not mark the form dirty
- A Series # that is already stored is left as it is
- Book List Import with Series and Series # mapped saves the number on `series_number` and appends it to the title
- Series sort order is series name, then series number, then title
- Books with an empty series number come after numbered books in the same series
- Title/number split does not drop or duplicate existing titles
- Main table, Import Detail, and Update window have no series-number field

---

## Accessibility

Text box with a label and buddy, to the right of Series. Type a number such as 3 or 6.5, or leave it blank. No shortcut of its own. Alt+I focuses Series, then Tab moves to Series number. Sort menu text stays “Series”.

---

## Out of scope for v3

- Showing series number on the folder Import window, Import Detail, the main table, the Update window, or web fetch
- A separate “sort by series number” menu item (the existing Series sort changes instead)
- Bulk Update series-number field
- Series reading order across multiple authors
