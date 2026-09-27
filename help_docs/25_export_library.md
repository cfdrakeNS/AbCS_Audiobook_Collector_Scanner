# Export Library Process

## What this is

**Export Library** saves the books in the main list to a **CSV** file (for Excel or another spreadsheet) or a **JSON** file (for other programs). It exports metadata only — no audio files.

## When to use it

- Keep a readable copy of your library outside the database.
- Open your library in a spreadsheet to sort, print, or share.
- Move book information to another program.

## Before you start

- Export uses the main list **as it is shown now**. Set the collection filter, Find, Read, Plot, Want to read, In progress, or Recently added filters first to export only part of the library.
- If books are **selected**, only the selected books are exported.
- Rows are in the same order as the main list.

## How to export

1. Open **File → Export Library** (**Alt+F**, then **X**).
2. In the save dialog, type a file name. The suggested name is `abcs_library_` plus the date and time, in your Documents folder.
3. Choose the file type: **CSV Files** or **JSON Files**. A name ending in `.json` is always saved as JSON; a name ending in `.csv` is always saved as CSV.
4. Press **Enter** to save, or **Escape** to cancel.
5. The status bar says how many books were exported and the file name. Focus returns to the book list.

## What is in the file

Title, Author, Year, Series, Series Number, Genre, Collection, Reader, Time, Tracks, Size MB, Bitrate, Format, Path, Read Date, Date Added, Want to Read, Listen Position, Listen File, and Comments.

- Title is the stored title, without the ` - nn` series number shown on the main list. The number is in **Series Number**.
- Dates are written as year-month-day, for example `2026-03-04`.
- In CSV, **Want to Read** is Yes or No, and **Listen Position** is hours:minutes:seconds. Blank means the book has not been started.
- CSV is saved as UTF-8 with a marker so Excel shows accented names correctly.
- Spreadsheets cannot hold more than 32,767 characters in one cell. In CSV, longer text (usually Comments) is shortened and ends with **[truncated]**. The status bar says how many books were shortened. JSON always keeps the full text.
- JSON uses lower-case names with underscores (for example `series_number`, `listen_position_ms`) and keeps numbers as numbers.

## Mouse, shortcuts, and accessibility

- Click **File**, then **Export Library...**.
- Press **Alt+/** to re-read the export result.

| Shortcut | Action |
|----------|--------|
| Alt+F, X | Open Export Library (File menu) |
| Escape | Cancel the save dialog |
| Alt+/ | Re-read status |

## Common confusion

**Why did only some books export?**
A filter or search was active, or books were selected. Clear filters (and press **Escape** to clear a selection) to export the whole library.

**Why do some Comments end with [truncated]?**
That text was longer than a spreadsheet cell allows. Without shortening, Excel and LibreOffice Calc refuse to load the file completely. Export to JSON if you need the full text.

**Can I import the CSV back into AbCS?**
Yes. Use **Import Book List** and map Title, Author, and the other columns. The column names match the Import Book List fields.

**Is this the same as Backup?**
No. **Backup & Restore** saves the whole database so AbCS can restore it. Export is a readable copy for other programs; AbCS cannot restore from it.

**Why is Export Library unavailable in Duplicate mode?**
Duplicate mode has its own **Export Duplicates** button (**Alt+X**). Leave Duplicate mode to export the library.

## Related documentation

- [Find and Filters](03_find_filters.md)
- [Import Book List](11_import_book_list.md)
- [Backup and Restore](09_backup_restore.md)
- [Keyboard shortcuts by window](16_shortcuts.md)
