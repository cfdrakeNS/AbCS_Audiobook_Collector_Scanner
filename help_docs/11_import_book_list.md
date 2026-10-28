# Import Book List (Spreadsheet)

## What this is

Import Book List brings book information into AbCS from a spreadsheet file: CSV, Excel, or ODS. It reads the text in the sheet, not audio file tags. Use it when you already have a list of titles and authors in a table. Your spreadsheet file stays as it is.

For a walkthrough, see [Import Book List explained](20_import_book_list_explained.md).

To scan audio files in folders instead, use [Import (Folder Scan)](02_import.md).

## When to use it

- You have a spreadsheet exported from another app, or a reading list.
- You want to add many books without audio files attached.
- You want to set read dates on books already in AbCS.

## Before you start

- At least one **active collection** must exist.
- Have your spreadsheet ready. Supported formats: `.csv`, `.xlsx`, `.xls`, and `.ods`.
- Your sheet needs **Title** and **Author** columns.
- For read-date updates, the books must already be in the selected collection.

## Window layout

- **Header row:** **Collection** combo, **File** field (filled by Browse), and **Browse...** button.
- **Middle row, left:** the **Instructions** panel.
- **Middle row, center:** the **Options** group with two checkboxes, **Add Book From List** and **Add Read Date from List**. Checking one unchecks the other. Below them is the **My file Has Header** checkbox.
- **Middle row, right:** the **Field Mapping** table, with one row per book field (Title, Author, Year, Series, Series #, Genre, Narrator, Read Date, Time, Files, Plot), each with a **Column** combo.
- **Buttons:** **Import** and **Export Errors**. Export Errors is grayed out until an import has errors.
- Status bar at the bottom.

Focus starts on **Collection** when the window opens.

## Import from a spreadsheet

1. Open **File → Import Book List**, or press **Ctrl+Shift+I**.
2. Choose a **Collection** (**Alt+C**).
3. Press **Browse** (**Alt+B**) and select your spreadsheet file.
4. After the file loads, the status bar reports how many rows and columns were found.
5. If the first row of your sheet holds column names, check **My file Has Header**. AbCS then tries to match the columns to book fields.
6. Under **Options** (**Alt+O**), check one import mode. **Add Book From List** (the default) adds new books. **Add Read Date from List** sets read dates on existing books.
7. In the **Field Mapping** table, choose a spreadsheet column (A, B, C, and so on) for each book field. Each field has an Alt key, for example **Alt+T** Title, **Alt+A** Author, and **Alt+E** Read Date. Press **F1** for the full list.
8. New books need Title and Author. Read-date mode needs Title, Author, and Read Date, and the other mapping rows are grayed out.
9. Press **Import** (**Alt+I**).
10. A **Confirm Import** message shows the row count, mode, and mapping. Press **Yes** to go ahead or **No** to stop.
11. An **Import Progress** window shows the current title and author and the counts while rows are processed. Press **Escape** there to cancel; books already added are kept and the remaining rows are skipped.
12. When the import finishes, the progress window closes and a message says **Import completed** with an **OK** button. If you canceled, the progress window stays open with the counts; press **Escape** to close it.
13. If some rows failed, the status bar reminds you to press **Export Errors** (**Alt+X**) to save a CSV of the failed rows. Press **Alt+/** to hear the status.
14. The window stays open so you can import another file. Press **Escape** when finished. The main book list refreshes.

## What happens next

- New books appear in the main list for the collection you chose.
- In read-date mode, the Read column changes on matched books. Books are matched by title and author within the collection.
- Rows missing a required field, or matching a book already in the collection, are skipped and listed in the error export.
- Imported books start with no file path. **Listen** finds each book in the collection folder and saves the path. See [Import Book List explained](20_import_book_list_explained.md) for where Listen looks.

## Settings that affect this

Import Book List uses the **duplicate match** and **fuzzy duplicate percent** settings from **Preferences → Validation Rules**, the same as folder Import.

The import scenario, fallbacks, and validation rules apply to folder Import only.

## Mouse, shortcuts, and accessibility

- Click **Browse** to select your spreadsheet, map the columns, then click **Import**.
- In the mapping table, click each dropdown to choose a spreadsheet column.
- Click **Yes** or **No** in the confirm message, and **Export Errors** if any rows failed.

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift+I | Open Import Book List (main window) |
| Alt+C | Collection |
| Alt+B | Browse for file |
| Alt+H | Instructions |
| Alt+O | Options section |
| Alt+T | Title |
| Alt+A | Author |
| Alt+Y | Year |
| Alt+P | Plot |
| Alt+S | Series |
| Alt+N | Series number |
| Alt+G | Genre |
| Alt+R | Narrator |
| Alt+E | Read Date |
| Alt+M | Time |
| Alt+F | Files |
| Alt+I | Import books |
| Alt+X | Export errors to CSV |
| Escape | Close window |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Import or Import Book List — which do I use?**
Use **Import** (**Ctrl+I**) for audio files in folders. Use **Import Book List** (**Ctrl+Shift+I**) for a spreadsheet.

**Why did some rows fail?**
Common reasons: a blank title or author, a book already in the collection, or in read-date mode, no matching book or a date AbCS cannot read. Export Errors lists the reason for each row.

**What happens after an import finishes?**
The window stays open so you can import another file. Close it with **Escape**; the main list updates then.

## Related help

- Re-importing an exported list: [Export Library](25_export_library.md)
- Playing imported books: [Listen to a book](26_listen_to_a_book.md)
- Setting the collection folder: [Collections](06_collections.md)
