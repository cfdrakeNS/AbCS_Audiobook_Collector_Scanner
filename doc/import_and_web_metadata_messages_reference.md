# Import and Web Metadata — Messages and Error Codes Reference

Technical reference for user-visible messages, status-bar text, dialog text, and per-item error strings produced by:

1. **Folder/file import** — Import window, scan pipeline, Import Detail, Import Progress
2. **Book list import** — spreadsheet import window and row-level import errors
3. **Web metadata fetch** — main-window fetch, progress dialog, Web Metadata review window

This document lists **current behavior** as implemented in the codebase. Severity for folder import validation rules can be changed in Preferences (error vs warning); defaults are noted below.

**Primary source files**

| Area | Files |
|------|-------|
| Folder import UI | `src/ui/import_window.py`, `src/ui/import_detail_window.py`, `src/ui/import_progress_window.py` |
| Scan / tags | `src/core/tag_reader.py` (`BookScanner`), `src/core/import_scanner.py` |
| Validation rules | `src/core/import_rules.py`, `src/core/validator.py` |
| Book list import | `src/ui/book_list_import_window.py` |
| Web fetch | `src/web/web_book_api.py`, `src/ui/web_fetch_progress.py`, `src/ui/web_metadata.py`, `src/ui/main_window.py` (`on_get_web_info_clicked`) |

**Related user guides:** [19_import_explained.md](../help_docs/19_import_explained.md), [20_import_book_list_explained.md](../help_docs/20_import_book_list_explained.md), [07_web_metadata.md](../help_docs/07_web_metadata.md), [21_web_metadata_explained.md](../help_docs/21_web_metadata_explained.md)

---

## 1. Shared prefix system (folder import only)

Folder import stores per-book issues in an `errors` list. The Import window **Error** column and Import Detail **Errors** field show these through `ImportValidator.format_error_message()`, which adds compact prefixes:

| Prefix | Meaning | Category | Typical use |
|--------|---------|----------|-------------|
| **E:** | Error | `parse` or `read` | Blank title/author, DB insert failure, unreadable file |
| **W:** | Warning | `warning` | Suspicious metadata, length/year/structure checks |
| **F:** | Fallback | `warning` (display) | Title/author inferred from file or folder path |
| **C:** | Correction | `warning` (display) | Auto-trim, proper-case, punctuation cleanup, ZIP duration fix |
| *(none)* | Duplicate | `duplicate` | Shown as **Duplicate** (no prefix) |

Multiple issues on one row are joined with `; ` in the import list **Error** column.

**Read-error detection:** messages whose normalized text contains `error reading file`, `file not found`, or `corrupted` are treated as **read** errors (from tag reading, not validation rules).

---

## 2. Folder / file import

### 2.1 Review-list row status

Each scanned item gets a **status** used for filtering and add eligibility:

| Status | Meaning |
|--------|---------|
| `OK` | No duplicate, hard error, or non-fixed warning |
| `Warning` | Has warning-level issue(s), no hard error |
| `Error` | Has parse/read error |
| `Duplicate` | Matches existing book per duplicate preferences |
| `Failed` | Manual add attempted but DB insert failed |
| `Added` | Auto-added during scan or successfully added manually |

**Add eligibility:** only `OK` and `Warning` rows with non-empty title and author can be added manually.

### 2.2 Validation rule messages (`import_rules.py`)

These strings are produced by `ImportRulesEngine.validate()`. Default severity is shown; each rule can be disabled or switched to warning/error in Preferences.

| Rule key | Message text | Default severity |
|----------|--------------|------------------|
| `title_blank` | `Title Blank` | error |
| `author_blank` | `Author Blank` | error |
| `author_non_alpha_start` | `Author Name Starts with non-alphabetic character` | warning |
| `author_name_in_title` | `Author name in Title` | warning |
| `title_in_author_name` | `Title in Author name` | warning |
| `unknown_or_various_author` | `Author contains Unknown or Various` | warning |
| `minimum_title_length` | `Title below minimum length ({N})` | warning (rule off by default) |
| `file_structure` | `Folder path does not match expected structure ({pattern})` | warning (rule off by default) |
| | `{pattern}` is `Author/Title`, `Year/Author/Title`, or `Author/Title or Year/Author/Title` | |
| `unreadable_audio_length` | `Could not read length from audio files` | warning |
| `minimum_book_length` | `Book length below minimum ({N} minutes)` | warning (rule off by default) |
| `maximum_book_length` | `Book length above maximum ({N} hours)` | warning (rule off by default) |
| `year_out_of_range` | `Year is not a valid number` | warning (rule off by default) |
| | `Year outside allowed range ({min}-{max})` — currently 1801 through current year | |

### 2.3 Fallback flags (`import_scanner.py`)

Applied during scan when metadata is inferred from paths or files. Stored with **F:** prefix.

| Message |
|---------|
| `F: Title fallback from file used` |
| `F: Title fallback from folder used` |
| `F: Author fallback from folder used` |

### 2.4 Series-from-directory warnings

When series-from-directory scenario cannot derive a series name:

| Message pattern |
|-----------------|
| `W: Series from directory skipped ({reason})` |

**`{reason}` values:**

- `missing folder path`
- `missing series folder name`
- `missing author folder name`
- `series folder matches author`
- `folder does not match author/series pattern`
- `author not found in path`
- `path too shallow`
- `no folders after author`

### 2.5 Auto-correction flags (`import_scanner.py`)

When import preferences auto-correct fields (and the correction is not configured to skip review):

| Message pattern |
|-----------------|
| `C: {Field} {correction}` |

**`{Field}`:** `Title`, `Author`, `Series`, `Genre`, or `Narrator`

**`{correction}`** (one or more, comma-separated):

- `whitespace trimmed`
- `punctuation removed`
- `non-printable characters removed`
- `proper case applied`

**ZIP-in-MP3 duration** (`tag_reader.py`):

| Message |
|---------|
| `C: Duration corrected from embedded ZIP audio` |

### 2.6 Tag / file read errors (`tag_reader.py`)

Per-file errors are appended as `{filename}: {detail}`:

| `{detail}` |
|------------|
| `Unrecognized audio format` |
| `Error reading file: {exception text}` |

These categorize as **read** errors. In the Error column they display as **E:** messages.

### 2.7 Other per-item errors

| Source | Message |
|--------|---------|
| Duplicate detection | `Duplicate` |
| Auto-add or manual add DB failure | `E: {exception text}` |
| Build book without collection | `E: No collection selected` (internal; raised as exception) |

### 2.8 Import window — dialog boxes

| Title | When | Text (summary) |
|-------|------|----------------|
| Collection Selection | Collection cleared in combo | `Please select a collection to import books.` |
| Collection Required | Scan without collection | `Please select a collection before scanning.` |
| Folder Required | Scan with empty path | `Please select a folder or file before scanning.` |
| Invalid Path | Path does not exist | Single-item: folder or file must exist. Other modes: folder must exist. |
| Close Import Window? | Close with items in list | Confirm close |
| Add Complete | After manual add | `Books added: {N}` / `Left in import list: {M}` |

### 2.9 Import window — status bar messages

| Message | When |
|---------|------|
| `Scan canceled` | User canceled scan |
| `Browse canceled: scan is in progress` | Browse during active scan |
| `Selected path does not exist` | Invalid scan path |
| `Scan started` | Scan begins |
| `Single file scan: {N} book(s) found` | Single-file mode after scan |
| `Scan canceled. No partial results found. Elapsed: {time}` | Canceled, no books |
| `No audio found. Selected file may be unsupported or inaccessible. Elapsed: {time}` | Single file, no results |
| `No audio files found. Elapsed: {time}` | Folder scan, no results |
| `Scanned: {n} \| Added: {a} \| Corrected: {c} \| Errors: {e} \| Warnings: {w} \| Duplicates: {d} \| Elapsed: {time}` | Scan complete summary |
| `Scan canceled \| {summary}` | Canceled with partial results |
| `No scanned items to add` | Add with empty list |
| `Select one or more rows to add` | Add with no selection |
| `Add canceled. No books were added \| Skipped: {s} \| Failed: {f}` | Add canceled mid-operation |
| `No import rows to export` | CSV export, empty table |
| `No visible rows to export for current filter` | Export with filter hiding all rows |
| `Export canceled` | User canceled save dialog |
| `Export failed: {error}` | CSV write error |
| `Exported {N} row(s) to CSV: {filename}` | Export success |
| `Import collection: {name}` | Collection changed |
| `No items to view` | Open detail with empty list |
| `Select a valid row` | Detail with invalid row |
| `Changes applied to import item` | Detail save applied |
| `Import item discarded` | Row discarded from detail |
| `Import item discarded. No items remain` | Last row discarded |
| `Canceling scan...` / `Continuing scan` | Progress window cancel prompt |
| `Stopping add operation...` / `Continuing add operation` | Add cancel prompt |
| `Close canceled` | User kept window open |

**Summary line** (also used as default status):  
`Scanned: … \| Added: … \| Corrected: … \| Errors: … \| Warnings: … \| Duplicates: …`  
With active error filter: appends ` \| Filter: {filter name}` and `Showing: {count}`.

### 2.10 Import Detail window — status messages

| Message | When |
|---------|------|
| `Title is required.` | Save with empty title |
| `Author is required.` | Save with empty author |
| `Changes saved` | Successful save |
| `Duplicate item loaded. Edit fields to resolve and save.` | Opening duplicate row |
| `Viewing item {i} of {total}` | Navigate between items |
| `{Field} changed.` | Field edited (e.g. `Title changed.`) |
| `Continue editing` | Unsaved-close dialog: No |
| `Canceled: changes discarded, window closed.` | Unsaved-close: Cancel |
| `Close canceled` | Close-with-changes dialog dismissed |

### 2.11 Import Progress window — status messages

| Message | When |
|---------|------|
| `Scanning {processed}/{total} \| Elapsed {time}` | During file scan |
| `Scanning {processed} \| Elapsed {time}` | Scan with unknown total |
| `Adding started.` | Manual add phase begins |
| `Adding {processed}/{total} \| Added {n} \| …` | During add phase |
| `Cancel Scan: scan stopped, partial results kept.` | User confirmed cancel |
| `Continuing: scan not canceled.` | User declined cancel |
| `Scan complete. Elapsed: {time}. Esc to close.` | Scan finished |
| `Scan canceled! Elapsed: {time}. Esc to close.` | Scan canceled |
| `Add complete. {N} book(s) added. Esc to close.` | Manual add finished |
| Full scan summary (same counters as Import window) | On `mark_scan_complete` |

---

## 3. Book list import

Book list import does **not** use the E:/W:/F:/C: prefix system. Row failures are stored in `import_errors` with a **`reason`** string and exported to CSV (columns: row, title, author, reason).

### 3.1 Startup and file loading

| Type | Title / status | Text |
|------|----------------|------|
| Dialog | Missing Dependencies | `Book List Import requires pandas and openpyxl.` + install hint |
| Dialog | Missing Dependency | `.ods` without odfpy: install `pip install odfpy` |
| Dialog | File Error | `Could not load file:\n{error}` |
| Status | `Loading file...` | While parsing |
| Status | `Loaded {rows} rows with {cols} columns` | Success |
| Status | `Missing dependency: odfpy` | ODS load blocked |
| Status | `File loading failed` | Generic load failure |
| Status | `Error reloading file: {error}` | Header toggle reload failed |

### 3.2 Pre-import validation (dialogs + status)

| Dialog title | Message | Status if applicable |
|--------------|---------|-------------------|
| Collection Required | `Please select a collection before importing.` | `No collection selected. Please select a collection.` |
| File Required | `Select a spreadsheet file before importing.` | `No file loaded. Select a spreadsheet file first.` |
| Mapping Error | See table below | *(focus moves to field combo)* |
| Confirm Import | Preview text (rows, mode, mapping) | `Import cancelled` if No |
| Import Complete | Success count + error hint | See §3.4 |
| Import Error | `Import failed:\n{error}` | `Import failed` |

**Mapping validation messages** (`validate_mapping()`):

| Message | Focus field |
|---------|-------------|
| `Title field is required` | title |
| `Author field is required` | author |
| `Read Date field is required when Add Read Date from List is selected` | read_date |
| `At least Title and Author must be mapped` | — |

### 3.3 Per-row import error reasons

**Add Books From List mode** (`import_new_books`):

| Reason | When |
|--------|------|
| `Missing title or author` | Empty, `nan`, or missing after sanitize |
| `Duplicate - book already exists` | Matches existing book per duplicate preferences |
| `{exception text}` | Unexpected error on row (DB, etc.) |

**Add Read Date mode** (`update_read_dates`):

| Reason | When |
|--------|------|
| `Missing title or author` | Same as above |
| `Book not found in selected collection: {collection name}` | No title/author match in collection |
| `Could not load book record` | Book ID lookup failed |
| `Invalid date format. Supported examples: YYYY-MM-DD, DD-MM-YY, DD/MM/YYYY` | Unparseable read date |
| `Read date is empty` | Mapped column empty for row |
| `Read Date column not mapped` | Mode requires read date mapping |
| `{exception text}` | Unexpected error on row |

### 3.4 Import result status messages

| Mode | Status pattern |
|------|----------------|
| New books | `{success} books added to {collection} collection, {errors} errors` |
| Read dates | `{success} read dates added to books in {collection} collection, {errors} errors` |
| During import | `Importing books...` |
| No collection (internal) | `Error: No collection selected` |

**Import Complete dialog** adds, when `error_count > 0`:

- `{error_count} books had errors`
- `Use Export Errors (Alt+X) to save error details to CSV`

### 3.5 Export errors CSV

| Status | When |
|--------|------|
| `No errors to export` | Empty error list |
| `Export cancelled` | Save dialog canceled |
| `Export failed: {error}` | Write error |
| `Exported {N} error(s) to CSV: {filename}` | Success |

Default export filename: `Import_Book_list_errors_{timestamp}.csv`

---

## 4. Web metadata fetch

Web fetch uses a separate error model: `_fetch_errors` on the metadata dict (strings like `open_library: {exception}`), plus human-readable status lines from `format_web_fetch_status_message()`.

### 4.1 Progress dialog messages (`web_fetch_progress.py`, `web_book_api._source_progress_message`)

Initial text: `Preparing web search…`

| Phase | Message pattern |
|-------|-----------------|
| Primary search | `Trying source 1: Open Library…` |
| | `Trying source 2: Google Books…` |
| | `Trying source 3: WikiData…` |
| Broadened search | `Broadened search, {source name}…` |
| Title-only search | `Title-only search, {source name}…` |
| Other | `Trying {source name}…` |
| Series resolved | `Series found: {series}` or `Series found: {series}; book {number}` |

Source order: Open Library → Google Books → WikiData.

### 4.2 Fetch error storage (`_fetch_errors`)

When all attempted sources fail, metadata may contain:

```text
_fetch_errors: ["open_library: …", "google_books: …", "wikidata: …"]
_no_result: True
```

Only errors from sources actually queried are present (depends on `refresh` level).

### 4.3 Formatted status messages (`format_web_fetch_status_message`)

Used on the main window status bar and Web Metadata re-fetch:

| Condition | Status text |
|-----------|-------------|
| Empty error list | `Web fetch failed: unable to reach web sources.` |
| Google rate limit (`429` / `too many requests`) | `Google Books rate limited. Try again later or use Re-fetch (Alt+F).` |
| `open_library` in first error | `Open Library unavailable. {detail after colon}` |
| `google_books` in first error | `Google Books unavailable. {detail after colon}` |
| `wikidata` in first error | `WikiData unavailable. {detail after colon}` |
| Other | `Web fetch failed: {first error}` |

### 4.4 Main window — fetch web info (`on_get_web_info_clicked`)

| Type | Title / message |
|------|-----------------|
| Status | `No book available for web info fetch` — no focused book |
| Dialog | **No Web Data Found** — see below |
| Status (no match) | `No web data found for this book.` |
| Status (up to date) | `No new web information found for this book.` |
| Status (network) | From `format_web_fetch_status_message` |

**No Web Data Found dialog text variants:**

- Network: `Unable to reach one or more web sources.` + bullet list of up to 3 `_fetch_errors` + retry hint
- Up to date: web searched but no new fields to offer
- Clean miss: `No information found for this book in any web source.`
- Appends `Last error: {text}` when an exception was caught outside `_fetch_errors`

### 4.5 Web Metadata review window — status messages

| Message pattern | When |
|-----------------|------|
| `Web data found - Plot found` / `… - No plot` | Window opened with pre-fetched data and field differences |
| `No new web data - Plot found` / `… - No plot` | Pre-fetched but nothing differs from DB |
| Optional suffix | ` - Difference - Title, Author, …` (capitalized field names) |
| `Re-fetch complete - Plot found` / `… - No plot` | Re-fetch found differing fields |
| `Re-fetch: no new data found.` | Re-fetch returned data but no differences |
| `Re-fetch: no data found.` | Re-fetch clean miss |
| Re-fetch network | Same as `format_web_fetch_status_message` |
| `Re-fetch error: {exception}` | Unexpected re-fetch failure |
| `No book loaded for re-fetch.` | Re-fetch with no book |
| `Updated: {fields}` | Save applied selected fields |
| `No changes applied` | Save with nothing checked |
| `Error saving: {exception}` | DB save failure |

**Re-fetch** uses `refresh=1` (skips Open Library on first pass; tries Google Books and WikiData per cascade logic).

---

## 5. Quick comparison

| Feature | Folder import | Book list import | Web metadata |
|---------|---------------|------------------|--------------|
| Error prefixes | E / W / F / C | Plain `reason` text | `_fetch_errors` + formatted status |
| Per-item storage | `errors[]` on scanned book | `import_errors[]` dicts | `_fetch_errors` on API result |
| User export | Import list CSV | Error CSV (Alt+X) | — |
| Configurable severity | Import validation rules | — | — |

---

## 6. Maintenance notes

- When adding a new validation rule, update `ImportRulesEngine` and this document’s §2.2 table.
- When adding book-list failure paths, append a consistent `reason` string in `book_list_import_window.py` and document it in §3.3.
- When adding a web source, extend `_SOURCE_PROGRESS_LABELS`, the cascade in `_fetch_metadata_from_sources`, and §4.1–4.3.
- Folder import message formatting is centralized in `ImportValidator.format_error_message()`; book list and web fetch use their own formats.

*Last reviewed against codebase: July 2026.*
