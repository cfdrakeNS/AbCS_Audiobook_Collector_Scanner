# Export Library

## What this is

**Export Library** saves the books in the main list to a **CSV** file, for Excel or another spreadsheet, or a **JSON** file, for other programs. It exports book information only; your audio files stay where they are.

Export Library is a File menu item that opens the standard save dialog. It has no window of its own.

## When to use it

- To keep a readable copy of your library outside the database.
- To open your library in a spreadsheet to sort, print, or share.
- To move book information to another program.

## Before you start

- Export uses the main list **as it is shown now**. Set the collection, Find, Read, Plot, Want to read, In progress, or Recently added filters first to export part of the library.
- If books are **selected**, only the selected books are exported.
- Rows are in the same order as the main list.

## How to export

1. Open **File → Export Library** (**Alt+F**, then **X**).
2. In the save dialog, type a file name. The suggested name is `abcs_library_` plus the date and time, in your Documents folder.
3. Choose the file type: **CSV Files** or **JSON Files**. A name ending in `.json` is saved as JSON, and a name ending in `.csv` as CSV.
4. Press **Enter** to save, or **Escape** to cancel.
5. A message lists how many books were exported, the active filters and sort, and the file name.
6. The status bar says how many books were exported. Focus returns to the book list.

## What is in the file

Title, Author, Year, Series, Series Number, Genre, Narrator, Read Date, Time, Tracks, Collection, Size MB, Bitrate, Format, Path, Date Added, Want to Read, Listen Position, Listen File, and Comments (plot).

- Title is the stored title. The ` - nn` series number shown on the main list is in **Series Number**.
- Dates are written as year-month-day, for example 2026-03-04.
- In CSV, **Want to Read** is Yes or No, and **Listen Position** is hours:minutes:seconds. A blank Listen Position means the book has not been started.
- CSV is saved as UTF-8 with a marker, so Excel shows accented names correctly.
- A spreadsheet cell holds up to 32,767 characters. In CSV, longer text, usually Comments, is shortened and ends with **[truncated]**. The status bar says how many books were shortened. JSON keeps the full text.
- JSON uses lower-case names with underscores, for example `series_number` and `listen_position_ms`, and keeps numbers as numbers.

## Mouse, shortcuts, and accessibility

- Click **File**, then **Export Library...**.
- Press **Alt+/** on the main window to re-read the export result.

| Shortcut | Action |
|----------|--------|
| Alt+F, X | Open Export Library (main window) |
| Escape | Cancel the save dialog |
| Alt+/ | Re-read status |

## Common confusion

**Why did only some books export?**
A filter or search was active, or books were selected. Clear the filters, and press **Escape** to clear a selection, to export the whole library.

**Why do some Comments end with [truncated]?**
That text was longer than a spreadsheet cell allows. Shortening it lets Excel and LibreOffice Calc load the whole file. Export to JSON when you need the full text.

**Can I import the CSV back into AbCS?**
Yes. Use **Import Book List** and map Title, Author, and the other columns. The column names match the Import Book List fields.

**Is this the same as Backup?**
No. **Backup & Restore** saves the whole database so AbCS can restore it. Export is a readable copy for other programs.

**Why is Export Library grayed out in duplicate mode?**
Duplicate mode has its own **Export Duplicates** button (**Alt+X**). Leave duplicate mode to export the library.

## Related help

- Main window filters: [Find and Filters (Main Window)](03_find_filters.md)
- Importing a list: [Import Book List](11_import_book_list.md)
- Database backup: [Backup and Restore](09_backup_restore.md)
- All shortcuts: [Keyboard shortcuts by window](16_shortcuts.md)
