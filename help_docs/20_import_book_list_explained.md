# Import Book List Explained

## What this is

This guide describes what AbCS does after you press **Import** (**Alt+I**) in the Import Book List window. For the steps and shortcuts, see [Import Book List (Spreadsheet)](11_import_book_list.md).

Import Book List reads a **spreadsheet** you already have and stores the book information inside AbCS. Your spreadsheet file stays exactly as it was, and AbCS reads no audio files during this import.

## Starting the import

Before any row is processed, AbCS checks that everything is ready:

- A **collection** is selected.
- A **spreadsheet** has been loaded with Browse.
- The **field mapping** is complete: Title and Author are mapped, and in read-date mode, Read Date is mapped too. At least two fields must be mapped.

If a check fails, a warning explains what is missing.

### Confirm Import

When the checks pass, a **Confirm Import** message shows:

- How many rows will be processed.
- Which mode is checked: new books or read dates.
- Which spreadsheet columns go to which book fields.

**Yes** starts the import, and **No** returns to the window. While rows are processed, an **Import Progress** window shows the current title and author and the counts. Press **Escape** there to cancel.

## The two modes

You choose the mode with the **Options** checkboxes before you import:

| Mode | What happens to each row |
|------|--------------------------|
| **Add Book From List** (default) | Adds a **new** book to the selected collection |
| **Add Read Date from List** | Finds a book **already in the collection** and sets its **read date** |

Only one mode runs per import.

## Adding new books

### Getting ready

Before reading the first row, AbCS:

1. Clears the error list and the counts.
2. Reads your **duplicate settings** from Preferences, the same ones folder Import uses: the duplicate match and the fuzzy duplicate percent.
3. Loads the books already in your library, for the duplicate check.

All new books from one import are saved together at the end.

### For each row

AbCS goes through the rows from top to bottom and reads the columns you mapped:

| Book field | Spreadsheet column |
|------------|--------------------|
| Title | Required |
| Author | Required |
| Year | Optional |
| Plot | Optional; stored in comments |
| Series | Optional |
| Series # | Optional; stored as the series number. The main table shows ` - 03` or ` - 6.5` after the title |
| Genre | Optional |
| Narrator | Optional (a CSV column may be named Reader) |
| Read Date | Optional |
| Time | Optional; stored as hours and minutes |
| Files | Optional; the number of files |

Title and author text are cleaned up: extra spaces are removed and proper case is applied.

A row with a blank title or author after cleanup is skipped, with the error "Missing title or author".

### Duplicate check

Each row is compared with the books already in your library and with the rows already accepted from this spreadsheet. The **Duplicate match** setting decides which fields must match:

| Match | Treated as a duplicate when |
|-------|-----------------------------|
| Title + Author + Year + Collection | The title, author, year, and collection match |
| Title + Author + Year | The title, author, and year match |
| Title + Author + Collection | The title, author, and collection match |
| Title + Author | The title and author match; the year is ignored |

When **fuzzy matching** is set, near-matches count when both the title and the author reach the percentage.

Titles are compared without trailing series numbers. The same title with two different series numbers, such as `The Moonstone - 01` and `The Moonstone - 02`, counts as two books. A title with no series number still matches a library title that has one.

A duplicate row is skipped with the error "Duplicate - book already exists", and counted separately.

### Saving the book

For each accepted row, AbCS finds the author, series, and genre, or adds new names, and saves the book with its title, author, year, series, genre, collection, plot, narrator, read date, time, and number of files.

An accepted row is remembered, so the same book repeated later in the spreadsheet is caught as a duplicate.

When a single row has an unexpected problem, it is listed with its row number and reason, and the import goes on to the next row.

## When the import finishes

- Every added book is saved, including the books added before a cancel.
- When the import finishes, the progress window closes and a message says **Import completed** with an **OK** button.
- When you cancel, the progress window stays open, and its status bar starts with "Import canceled". Press **Escape** to close it.
- The status bar of the Import Book List window has the summary, for example "32 books added to Audiobooks collection, 2 duplicates skipped, 3 errors". After a cancel, it adds how many rows were skipped. Press **Alt+/** to hear it.
- When some rows failed, the status bar also reminds you to use **Export Errors** (**Alt+X**).
- After **OK**, focus returns to the file field.
- The main book list refreshes when you close the Import Book List window.

### Export Errors

Press **Export Errors** (**Alt+X**) to save a CSV of the failed rows, with the row number, title, author, and reason:

| Reason | Cause |
|--------|-------|
| Missing title or author | A blank cell in a required column |
| Duplicate - book already exists | The book is in the library, or earlier in this file |
| Other message | An unexpected data problem on that row |

## Setting read dates

This mode sets the read date on books that are already in the collection.

### Getting ready

- AbCS clears the error list and the counts.
- Each read date is saved as soon as its row is processed.

### Title and author matching

For each row, AbCS:

1. Reads the title and author from the mapped columns, with the same cleanup as new-book mode.
2. Skips the row when either is blank.
3. Looks for the book in the selected collection. The title is compared without regard to spacing and capital letters, and the author without regard to capital letters. The first exact match is used.
4. When no book matches, the row is skipped with the error "Book not found in selected collection", followed by the title and author.

### Reading the date

The date comes from the mapped **Read Date** column. Many formats work, for example 2024-03-15, 15/03/2024, March 15 2024, and Excel date numbers.

- A valid date sets the book's read date.
- An empty cell gives the error "Read date is empty".
- A date AbCS cannot read gives the error "Invalid date format".

When the import finishes, the same **Import completed** message appears, and the status bar says how many read dates were added and how many rows failed. **Export Errors** is available for failed rows.

## What is stored

In new-book mode, each book is stored with the fields you mapped, in the collection you chose. A **Path** column in the sheet is not imported, so each book starts with no file path. Listen finds the book later; see **Playing book-list books with Listen** below.

In read-date mode, only the read date changes on each matched book.

## Playing book-list books with Listen

Books added from a list start with no file path. When you press **Listen** (**Ctrl+L**), AbCS looks for the book in the collection's **collection folder**. Set that folder in **Manage → Collections**.

### Where Listen looks

Listen checks a few folders under the collection folder, in this order. Folder names match without regard to capital letters, or to characters Windows does not allow in names. The Preferences import scenario is not used.

| Step | Folders checked under the collection folder |
|------|---------------------------------------------|
| 1 | Author, then Title (a title folder, or a single audio file named for the title) |
| 2 | When the book has a series: Author, then Series, then Title (folder or file) |
| 3 | When the book has no series: one folder down inside Author, then Title (used only if exactly one matches) |

When the book is found, it plays, and its folder is saved as the book's path. The next Listen goes straight to it.

### When the book is not found

Listen says what was missing and where it looked, then offers **Browse**. The folder you choose is saved on the book when it has playable audio. Press **Escape** to close and keep the book as it was.

| Message starts with | Meaning |
|---------------------|---------|
| The collection folder is missing | The collection folder cannot be reached, for example a drive that is not connected |
| Author folder "…" was not found | No folder with the author's name is directly in the collection folder. When no author is found at all, the collection folder may point to the wrong place |
| Author folder found. Book title "…" was not found | The author folder exists, and no folder or file in it matches the title |
| Author folder found. Series folder "…" was not found | The book has a series, the title is not in the author folder, and no series folder with that name is in the author folder |
| This book has no file path and the collection folder is not set | The collection has no collection folder |

For the first and last messages, open **Manage → Collections**, edit the collection, and set the **Collection folder**. See [Listen to a book](26_listen_to_a_book.md) for the player controls.

## How preferences affect this import

| Preference | Used for |
|------------|----------|
| Duplicate match | New-book mode |
| Fuzzy duplicate percent | New-book mode |
| Import scenario, fallbacks, validation rules | Folder Import only |

## Related help

- Steps and shortcuts: [Import Book List (Spreadsheet)](11_import_book_list.md)
- Scanning audio files: [Import explained](19_import_explained.md)
- Duplicate settings: [Import preferences](18_import_preferences.md)
- Playing imported books: [Listen to a book](26_listen_to_a_book.md)
- Setting the collection folder: [Collections](06_collections.md)
