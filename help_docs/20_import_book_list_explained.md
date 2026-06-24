# Import Book List Explained — Under the Hood

What AbCS does internally after you press **Import** (Alt+I) in the Import Book List window. This is not a how-to guide — for steps and shortcuts see [Import Book List](11_import_book_list.md).

**Important:** Import Book List does **not** read audio files, scan folders, or create folders on your computer. It only reads a **spreadsheet** you already have and writes book information inside AbCS. Your spreadsheet file on disk is never changed.

---

## 1. Once Import is activated

Before any row is processed, the app checks that everything is ready:

- A **collection** must be selected.
- A **spreadsheet** must already be loaded in memory (from Browse).
- **Field mapping** must be valid:
  - Title column mapped (required)
  - Author column mapped (required)
  - In **read-date mode**: Read Date column mapped (required)
  - At least two fields mapped in total

If any check fails, a warning appears and nothing is written.

### Confirm dialog

If checks pass, a **Confirm Import** dialog summarizes:

- How many rows will be processed
- Which mode is active (new books or read-date update)
- Which spreadsheet columns map to which book fields

**No** cancels the import. **Yes** starts processing.

The status bar shows `Importing books...` while rows are handled. There is no progress bar — only a final count when finished.

---

## 2. Which mode runs

Controlled by the **Options** checkboxes you set before Import:

| Mode | What happens to each row |
|------|--------------------------|
| **Add Book From List** (default) | Creates a **new** book record in the selected collection |
| **Add Read Date from List** | Finds an **existing** book and updates its **read date** only |

Only one mode runs per import. The two paths are completely separate after this point.

---

## 3. Add Book From List — setup before the row loop

Before reading row 1, the app prepares:

1. Resets error list and success/fail counters.
2. Loads **duplicate settings** from preferences (same as folder Import):
   - Duplicate match mode (title + author + year + collection, etc.)
   - Fuzzy duplicate percentage (0 = exact match only)
3. Loads **all existing books** in the library into memory for fast duplicate checks.
4. Creates a text cleanup helper (trim spaces, proper case, strip odd characters from author names).

All new books from this import will be saved together in **one database transaction** at the end — not one commit per row.

---

## 4. Add Book From List — for each spreadsheet row

The app walks every row in the loaded table, top to bottom.

### Read the mapped columns

For each row, values are pulled from the spreadsheet columns you mapped:

| Book field | Spreadsheet column (if mapped) |
|------------|-------------------------------|
| Title | Required |
| Author | Required |
| Year | Optional |
| Plot | Optional → stored as comments |
| Series | Optional |
| Series # | Optional — may be appended to title as `(Series #N)` |
| Genre | Optional |
| Reader | Optional |
| Read Date | Optional |
| Time | Optional → hours and minutes |
| Files | Optional → track count |

Title and author text are cleaned up (extra spaces removed, proper case applied).

### Skip if title or author is missing

If either is blank after cleanup, the row is skipped and recorded as an error: `Missing title or author`.

### Duplicate check

The row is compared against:

- Books already in your library (loaded at start), **and**
- Rows already accepted earlier in **this same import**

Match rules follow your duplicate preferences:

| Match mode | Treated as duplicate when |
|------------|---------------------------|
| Title + Author + Year + Collection | Same title, author, year, and collection |
| Title + Author + Year | Same title, author, and year |
| Title + Author only | Same title and author (year ignored) |

If **fuzzy matching** is enabled, near-matches count when both title and author reach the similarity percentage you set.

**Duplicate found** → row skipped, error: `Duplicate - book already exists`.

### Build and save the book record

If the row passes, the app creates records **inside AbCS only**:

1. **Author** — looked up or created.
2. **Series** — looked up or created if series was mapped.
3. **Genre** — looked up or created if genre was mapped.
4. **Book record** — written with:
   - Title (may include series number suffix)
   - Author, year, series, genre, collection
   - Plot → comments field
   - Reader, read date, duration, track count
   - Source = `Bookh_list`
   - **No audio folder path** — unless you mapped time/tracks, these are metadata-only records

The row is added to the in-memory duplicate list so a repeated row in the same spreadsheet is caught later.

### Row-level errors

Any unexpected problem on a single row is caught, logged with the row number and reason, and the loop continues to the next row.

---

## 5. Add Book From List — once all rows are done

- **One commit** saves every successful insert to the database.
- An **Import Complete** dialog shows how many rows succeeded and how many failed.
- Status bar shows something like `32 books added to Audiobooks collection, 3 errors`.
- Focus returns to the file path field.
- The **main book list does not refresh yet** — that happens when you close the Import Book List window.

### If errors occurred

Failed rows are kept in an internal error list. Press **Export Errors** (Alt+X) to save a CSV with:

- Row number
- Title
- Author
- Error reason

Common reasons:

| Reason | Cause |
|--------|-------|
| Missing title or author | Blank cell in a required column |
| Duplicate - book already exists | Matches a book in the library or an earlier row in this file |
| Exception message | Unexpected data problem on that row |

---

## 6. Add Read Date from List — for each spreadsheet row

This mode **never creates new books**. It only updates the read date on books that already exist.

### Setup

- Resets error list and counters.
- Does **not** use duplicate settings or fuzzy matching.
- Each successful update commits **immediately** (not batched).

### Per row

1. **Read title and author** from mapped columns (same cleanup as new-book mode).
2. **Skip** if either is missing.
3. **Look up the book** in the selected collection:
   - Compare normalized title (spacing and case ignored)
   - Compare author name (trimmed, case-insensitive)
   - First exact match wins
4. **Not found** → row skipped: `Book not found in selected collection: Title by Author`.
5. **Read the date** from the mapped Read Date column:
   - Supports many formats: `2024-03-15`, `15/03/2024`, `March 15 2024`, Excel date numbers, and others
   - **Valid date** → updates the book's read date in the database
   - **Empty cell** → `Read date is empty`
   - **Unrecognized format** → `Invalid date format...`

Year column mapping is available in the UI but is **not used** for book lookup in this mode.

---

## 7. Add Read Date from List — once all rows are done

Same completion flow as new-book mode:

- Import Complete dialog with success and error counts
- Status bar summary
- Error export available for failed rows

---

## 8. What gets written to the library

### New-book mode

| What | Where it goes |
|------|---------------|
| Title, year, reader, read date, duration, track count | `books` table |
| Author | `authors` table (looked up or created) |
| Series | `series` table (if mapped) |
| Genre | `genres` table (if mapped) |
| Plot | `books.comments` |
| Collection | Attached to the collection you selected |
| Source | `Bookh_list` |

No audio file paths, bitrates, or folder locations are set unless you later attach them through folder Import.

### Read-date mode

Only `read_date` on an existing `books` row is changed. Nothing else is touched.

---

## What Import Book List does not do

| Assumption | Reality |
|------------|---------|
| Reads audio file tags | No — only spreadsheet text |
| Uses folder import scenario settings | No — scenarios and tag fallbacks do not apply |
| Creates folders on your computer | No |
| Changes your spreadsheet file | No — read only |
| Updates all fields on existing books (read-date mode) | No — only read date changes |
| Shows a per-row progress bar | No — status messages only |

---

## How preferences affect this import

| Preference | Applies to |
|------------|------------|
| Duplicate match mode | New-book mode only |
| Fuzzy duplicate percent | New-book mode only |
| Import scenario, fallbacks, validation rules | **Not used** — folder Import only |

---

## Related guides

- Step-by-step with shortcuts: [Import Book List](11_import_book_list.md)
- Scanning audio files: [Import explained](19_import_explained.md)
- Duplicate settings detail: [Import preferences](18_import_preferences.md)
- Fill in plot/series from the web: [Web metadata explained](21_web_metadata_explained.md)
