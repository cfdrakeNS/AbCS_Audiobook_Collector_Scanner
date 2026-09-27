# Export Library Metadata — Version 3 Phase 27

**Status:** Implemented (September 2026) — awaiting JAWS/NVDA smoke  
**Created:** June 2026  
**Related:** [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [Import Book List](../help_docs/20_import_book_list_explained.md), [Book list import window](../src/ui/book_list_import_window.py), [Export Library help](../help_docs/25_export_library.md)

---

## What this is

Export the current library (or filtered subset) to **CSV** or **JSON** for backup, spreadsheets, and migration. Complement to book list **import**.

---

## Problem

No full-library export of metadata. Users rely on SQLite backup only.

---

## Design (as built)

- **File → Export Library...** (Alt+F, X). No toolbar button and no new Alt shortcut (Alt+X stays Export Duplicates in duplicate mode).
- Exports the main list **as shown** (`self.books` after filters, search, and sort), so all active filters are respected: collection, search, read, plot, want to read, in progress, recently added.
- With books selected, exports only the selection, in list order. Allowed during selection mode.
- Blocked in duplicate mode with a spoken status; duplicate mode keeps its own Export Duplicates.
- Save dialog: Documents folder (falls back to home), `abcs_library_YYYYMMDD_HHMM.csv`, filters **CSV Files** and **JSON Files**. The extension wins over the chosen filter; a name with no extension gets one from the filter.
- CSV: UTF-8 with BOM (`utf-8-sig`) for Excel. Headers: Title, Author, Year, Series, Series Number, Genre, Collection, Reader, Time, Tracks, Size MB, Bitrate, Format, Path, Read Date, Date Added, Want to Read, Listen Position, Listen File, Comments. Headers match Book List Import field names where one exists; Book List Import reads `utf-8-sig` first, so the file re-imports.
- Title is the stored title (no ` - nn` display suffix); the number is in Series Number (`3`, `6.5`). Dates are `YYYY-MM-DD`. Want to Read is Yes/No. Listen Position is `H:MM:SS`, blank when not started. CSV quoting handles commas and line breaks. Any CSV cell over 32,767 characters (the Excel and LibreOffice Calc cell limit) is cut to that length and ends with ` [truncated]`; the spoken status adds how many books were shortened and suggests JSON. Kept after the Phase 28 comment cleanup (decided Sept 27, 2026). Found in testing: LibreOffice Calc reported "maximum number of characters per cell was exceeded" on a real library where five Comments held 35,000–81,000 characters of imported iTunes technical tags (iTunNORM / iTunSMPB hex blocks).
- JSON: array of objects with snake_case keys (`series_number`, `want_to_read`, `listen_position_ms`, ...); numbers stay numbers, booleans stay booleans, empty dates are `null`.
- Ratings and tags are not exported (out of v3; no columns).

***Add to plan put a popup msg after the export with nn exported list active filters to path file name 

---

## Implementation

| Area | Change |
|------|--------|
| New | `src/core/library_export.py` — field table, `export_books`, `format_for_path`, `ensure_extension` |
| [`main_window.py`](../src/ui/main_window.py) | Manage menu **E&xport Library...**; `on_export_library` |
| New | `help_docs/25_export_library.md`; row added to `help_docs/01_overview.md` |

**Estimate:** ~2 days (done)

---

## Tests

`test/test_library_export.py` (14 tests) — CSV headers and values, BOM, blank optional fields, decimal series number, non-ASCII names, JSON typed values, row order kept, empty library (CSV headers only; JSON `[]`), format choice from extension/filter, extension added when missing, CSV cell cut over the limit, cell exactly at the limit kept, JSON keeps long text.

---

## Follow-up (not in Phase 27)

- Import stored iTunes technical tags (iTunNORM / iTunSMPB hex blocks) in Comments. Fixed in v3 Phase 28: [plan_itunes_comment_cleanup.md](plan_itunes_comment_cleanup.md).
- An Export Library window to choose collection, author, series, read-date range, or date-added range, plus filters. See [plan_export_library_options_window.md](plan_export_library_options_window.md).

---

## Accessibility

- Menu item uses menu text only (no `setAccessibleName` on `QAction`).
- Result spoken with `set_status(..., announce=True)`: "Exported N shown book(s) to file name" (or "selected"). Alt+/ re-reads it.
- Empty list: "No books to export." spoken. Duplicate mode: "Export Library is unavailable in duplicate mode." spoken. Cancel is silent.
- Focus returns to the book table after save, cancel, or failure.
- No progress window: writing is a single synchronous pass (a wait cursor shows); thousands of rows finish well under a second. Add a progress window only if a tester reports a delay.

**Gate (JAWS smoke):** Alt+F, X opens the save dialog; filtered view exports only visible rows; selection exports only selected rows; status speaks the count; focus lands on the book list; CSV opens in Excel with accents intact.

---

## Out of scope v1

Export audio files; incremental/sync export; ratings and tags; choosing columns.
