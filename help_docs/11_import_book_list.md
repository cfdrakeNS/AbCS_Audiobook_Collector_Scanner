# Import Book List Process (Spreadsheet)

## What this is

Import Book List brings book information into AbCS from a spreadsheet file (CSV, Excel, or ODS). It does not read audio file tags. Use it when you already have a list of titles and authors in a table.

This is separate from folder Import (Ctrl+I). See [Import](02_import.md) for scanning audio files.

## When to use it

- You have a spreadsheet export from another app or a reading list.
- You want to bulk-add books without audio files attached.
- You want to update read dates on books that are already in AbCS.

## Before you start

- At least one **active collection** must exist.
- Have your spreadsheet ready. Supported formats: `.csv`, `.xlsx`, `.xls`, `.ods`.
- For new books, **Title** and **Author** columns are required.
- For read-date updates, books must already exist in the selected collection.

## Steps

1. Open **File → Import Book List**, or press **Ctrl+Shift+I**.
2. Choose a **Collection** (Alt+C). Focus starts on this field when the window opens.
3. Click **Browse** (Alt+B) and select your spreadsheet file.
4. After the file loads, the status bar reports how many rows and columns were found.
5. If your spreadsheet has a header row in the first line, click **My file Has Header** to check or uncheck it.
6. Choose an import mode under **Options** (click a radio button, or press **Alt+O**):
   - **Add Book From List** (default) — insert new book records.
   - **Add Read Date from List** — update read dates on existing books only.
7. In the **Field Mapping** table, open each dropdown and choose a spreadsheet column (A, B, C, and so on). Keyboard users can use **Alt+T** Title, **Alt+A** Author, **Alt+E** Read Date, and other **Alt+** keys for each mapping row (press **Alt+H** for the full mapping list).
   - New books: Title and Author are required.
   - Read-date mode: Title, Author, and Read Date are required. Other mapping fields are disabled.
8. Click **Import** (Alt+I).
9. A **Confirm Import** dialog shows the row count, mode, and mapping summary. Click **Yes** to proceed or **No** to cancel.
10. When import finishes, an **Import Complete** message shows success and error counts.
11. If there were errors, click **Export Errors** (Alt+X) to save a CSV listing failed rows.
12. The window stays open so you can import another file. Press **Escape** when finished.
13. The main book list refreshes when you close the window.

## What happens next

- New books appear in the main list for the collection you chose.
- Read-date updates change the Read column on matched books (matched by title and author within the collection).
- Rows missing required fields or failing duplicate checks are skipped and listed in the error export.

## Settings that affect this

Import Book List uses the same **duplicate match** and **fuzzy duplicate percent** settings as folder Import. Find these under **Preferences → Validation Rules**. See [Import](02_import.md) for an explanation of duplicate settings.

Other import preferences (scenarios, fallbacks, validation rules) do **not** apply to spreadsheet import.

## Mouse, shortcuts, and accessibility

- Click **Browse** to select your spreadsheet; click **Import** to start after mapping columns.
- In the mapping table, click each dropdown to assign spreadsheet columns to book fields.
- Click **Yes** or **No** on the confirm dialog; click **Export Errors** if any rows failed.

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift+I | Open Import Book List |
| Alt+C | Collection |
| Alt+B | Browse for file |
| Alt+O | Options section |
| Alt+I | Start import |
| Alt+T | Title column mapping |
| Alt+A | Author column mapping |
| Alt+E | Read Date column mapping |
| Alt+X | Export errors to CSV |
| Alt+H | Instructions panel |
| F1 | Help for this window |
| Alt+/ | Re-read status |
| Escape | Close window |
## Common confusion

**Import vs Import Book List — which do I use?**
Use **Import** (Ctrl+I) for audio files in folders. Use **Import Book List** (Ctrl+Shift+I) for spreadsheet data.

**Why did some rows fail?**
Common reasons: missing title or author, duplicate already in the collection, or (in read-date mode) no matching book or invalid date.

**Does the dialog close after import?**
No. It stays open so you can import more files. Close it with Escape when done; the main list updates then.
