# Series Number in Database — Version 3 Phase 10 / F10

**Status:** Complete — tester accepted. Display-only ` - nn` on the main table, Book Details save, Book List Import, and Series From File Name. Tester build 2.17. Version 3 Phase 10.  
**Created:** June 2026  
**Updated:** September 2026 — display-only title suffix. Phase 9 schema accepted.  
**Related:** [plan_schema_batch.md](plan_schema_batch.md) (v3 Phase 9), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [scripts/strip_series_suffix_from_titles.py](../scripts/strip_series_suffix_from_titles.py), [scripts/update_series_number_from_title.py](../scripts/update_series_number_from_title.py), [scripts/update_series_from_catalog.py](../scripts/update_series_from_catalog.py)

---

## What this is

Persist **series number** (for example book 3, or 6.5) in SQLite as a real number. The only edit field is **Book Details**, a text box to the right of Series. There is no shortcut for that box. Alt+I focuses Series, then Tab moves to Series #. Saving stores Series # only. The title is not rewritten. The main-window Title column shows ` - 03` or ` - 6.5` from the column when the stored title has no suffix. When a book is shown and Series # is blank, a number at the end of the title is stored. The title stays as it is. A year such as 1999 stays on the title. **Book List Import** and **Series From File Name** store Series # and leave the title clean. Duplicate matching uses the column, then a title suffix. Import Detail and the Update window do not show a series-number field. The main-window **Series** sort is series name, then series number, then year, then title.

**Scope note (2026-09):** Fetch Web Info does not retrieve or display series or series number. Series entry is **manual only** on Book Details. Import Detail and the Update window do not show a series-number field. The main table shows the suffix in the Title cell only.

---

## Problem

Older libraries may still have a `" - 3"` suffix on `title`. New saves and imports store `series_number` only. The main table uses `title_for_display` so JAWS and sighted users still hear and see ` - nn`.

How books are stored today (relevant bits):

- `books` has `series_id` (FK to `series.name`) and `title`. Phase 9 added nullable `series_number REAL`. Phase 10 shows it on Book Details.
- Series number in titles is parsed for duplicate matching only (`ImportValidator`).
- Book List Import and Series From File Name store `series_number` and leave `title` without a suffix. The main table adds ` - nn` for display.

---

## Design

### Schema (Phase 9 — first start, existing DBs)

Column added by [plan_schema_batch.md](plan_schema_batch.md) on first start of a build that includes C01:

- `series_number REAL` nullable on `books`

This runs through `_ensure_legacy_schema_compatibility` for **existing** libraries (in-place `ALTER TABLE` after a `schema_repair` backup), not only new installs. Map on `Book` with default `None`. First start adds the column only. It does not parse numbers out of existing titles.

### UI — Book Details ([`src/ui/book_details.py`](../src/ui/book_details.py))

The only series-number control. Place a text box on the Series row, **to the right of Series**. Save/load `book.series_number` as a real number, so `3` and `6.5` both store. Blank means no number. Saving does not change the title. When a book is shown and Series # is blank, if the title ends with a series suffix, store that number. Leave the title as it is. No status message. The form stays clean. A stored series number is left as it is. A year such as `1999` stays in the title.

### Main table

[`title_for_display`](../src/utils/text_utils.py) adds ` - 03` or ` - 6.5` to the Title cell and spoken title when `series_number` is set and the stored title has no suffix. `books.title` is not written.

### Book List Import ([`src/ui/book_list_import_window.py`](../src/ui/book_list_import_window.py))

Keep the existing Series and Series # column mapping. When Series # has a value, store it on `book.series_number`. Do not append it to the title. Series name still sets `series_id` as it does today.

### Folder Import — Series From File Name

[`import_scanner.py`](../src/core/import_scanner.py) scenario `series_from_filename` stores the number on `book.series_number`, including a decimal such as `6.5`. It does not append the number to the title. Import Detail does not gain a series-number field. The other folder-import scenarios are unchanged.

### Sort — main window

The existing **Series** sort (Sort menu and the Series column header) is series name, then series number, then year, then title. Books with no series number sort after numbered books in that series. Within one series number, year is ascending and title breaks remaining ties. The sort label is “Series, Series #, Year, Title”. No new sort item. No series-number column on the main table.

### Optional offline

[`scripts/update_series_number_from_title.py`](../scripts/update_series_number_from_title.py) fills a blank `series_number` from a title suffix. The title is left as it is. Dry-run is the default. `--apply` copies the database to a timestamped backup first.

[`scripts/strip_series_suffix_from_titles.py`](../scripts/strip_series_suffix_from_titles.py) removes a suffix from the title after filling a blank `series_number`. A stored number that disagrees with the suffix is kept. Dry-run is the default.

[`scripts/update_series_from_catalog.py`](../scripts/update_series_from_catalog.py) writes `series_id` and `series_number` only. It does not rewrite the title.

**Estimate:** 2–3 days (after Phase 9)

---

## Tests

- Save/load from Book Details; field is to the right of Series
- Saving after Series # is added or changed stores the number and leaves the title as it is
- Main table Title cell shows ` - 03` or ` - 6.5` from `series_number`
- Showing a book with a blank Series # and a title suffix stores that number, leaves the title unchanged, and does not mark the form dirty
- A Series # that is already stored is left as it is
- Book List Import with Series and Series # mapped saves the number on `series_number` and leaves the title clean
- Series sort order is series name, then series number, then year, then title
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
