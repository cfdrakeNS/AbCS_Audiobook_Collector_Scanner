# Import Explained

## What this is

This guide describes what AbCS does after you press **Import** (**Alt+I**) in the Import window. For the steps and shortcuts, see [Import (Folder Scan)](02_import.md). For the settings, see [Import preferences](18_import_preferences.md).

Import only reads your audio files. They stay in the same folders, with the same names, and AbCS stores the book information inside the app.

## Starting the scan

AbCS checks that everything is ready:

- A **collection** is selected. New books are added to that collection.
- A **folder**, or a single file in single-item mode, is chosen and exists.

Then the scan starts:

- The collection is locked for this scan, so every book goes to the same collection.
- Any earlier review list in the window is cleared.
- The **Import** button is grayed out and the **progress window** opens.
- AbCS reads your latest saved import preferences: file types, scenario, fallbacks, validation rules, and duplicate settings.

If a check fails, a warning explains what is missing, and the scan waits until you fix it.

## Finding audio files

AbCS starts at the folder you chose and searches every folder below it.

A file counts as an audiobook when its type is checked in **Preferences → Import Settings → Audio formats**:

| Format | File endings |
|--------|--------------|
| MP3 | `.mp3` |
| M4A / M4B | `.m4a`, `.m4b` |
| FLAC | `.flac` |
| OGG | `.ogg`, `.oga` |
| WAV | `.wav` |
| WMA | `.wma` |
| AAC | `.aac` |
| OPUS | `.opus` |

Files of other types are skipped.

### How files become one book

As each audio file is found, AbCS reads its tags and groups the files that belong to the same book:

- Files with the same **album** and **album artist** tags are one book, whatever subfolders they are in. Folder names such as CD1 or Disc 2 are not used for grouping.
- A file with no album tag groups with the other files in its own folder.
- A file that cannot be read joins the book whose files share its folder. Its read error stays on that book.
- Two different books with the same album and album artist tags become one book. Give them different album tags to keep them apart.
- In **single-item** mode, one file is one book. When the album tag is empty, the title comes from the file name.

The folder that holds the files is stored as the book's location.

### Progress during the scan

- The progress bar shows files scanned against the total found.
- The status text reads like "Scanning 12/48 | Elapsed 00:35". Updates are spaced out so a screen reader keeps up.
- Press **Escape** in the progress window to cancel. After you confirm, the scan stops and keeps the books found so far.

## Reading the tags

AbCS opens each audio file and reads its tags. Your file stays exactly as it was.

| Book field | Where it comes from |
|------------|---------------------|
| **Title** | The Album tag by default. Tag mapping in Preferences can use Track title, or Album then track title |
| **Author** | Album artist, then Artist, by default. Tag mapping can use Album artist only, or Artist only |
| **Year** | The year or date tag (the first four digits) |
| **Genre** | The genre tag |
| **Narrator** | The composer tag first. When it is empty, the comment text after words such as "read by" or "narrated by" |
| **Plot** | The comment tag, without lines that only name the reader |
| **Time** | The length of the audio |
| **Bitrate** | The quality of the recording |
| **Format** | The file type, such as MP3, M4B, or FLAC |
| **Size** | The file size |

When several files make up one book:

- **Time** and **Size** are added up across the files.
- **Files** is the number of files in the book.
- **Plot** combines the comment tags of all the files, without repeats.
- When a file cannot be opened, a note such as "Error reading file: can't sync to MPEG frame. File: part03.mp3" is added to the book. The reason comes first and the file name last.

## Applying your preferences

After all files are read, AbCS applies your **import scenario** and **fallback** settings to each book.

### Import scenario

| Scenario | What AbCS does with folder names |
|----------|----------------------------------|
| **Mass Standard Import** | Uses the tags. Standard fallbacks and corrections apply |
| **Mass Import - Series From Directory** | The series comes from the book's folder, and the author from the folder above it. A leading number on the book file name, such as 03, is stored as the series number |
| **Mass Import - Series From Directory (Nested Books)** | The series and title come from the nested folders under the author. A leading number on the book folder name, such as 1- Title, is stored as the series number |
| **Mass Import - Series From File Name** | The series comes from the text in parentheses in the file name. A trailing number such as 04 or 6.5 is stored as the series number |
| **Single Author / Book Import** | One file or folder is treated as one book |

### Fallbacks when tags are missing

A fallback runs only when it is checked in Preferences (**Author fallback to folder** or **Title fallback to file**). When it is unchecked, the field stays blank and validation reports an error.

When a tag is blank or a placeholder such as "unknown", "untitled", or "n/a", and the fallback is checked:

- **Title fallback** uses the file name, without leading track numbers such as `01 `.
- **Author fallback** looks up the folder path for an author name.

Each fallback is marked with **F:** so you can review it.

### Auto-corrections

Each correction runs only when its main checkbox is checked in Preferences:

- Trim extra spaces.
- Remove leading punctuation.
- Remove non-printable characters.
- Apply proper case.

Each correction is marked with **C:**. When **Skip review** is checked for that correction, the book can still be added automatically.

### Other adjustments

- **Narrator from comment** — when there is no narrator tag, AbCS looks in the comment for your reader keywords. The defaults are "reader", "read by", "narrator", and "narrated by".
- **Author equals title** — when the author and title are the same text and **Author fallback to folder** is checked, the author is replaced with the parent folder name and marked as a fallback.

## Checking each book

AbCS runs your **validation rules**. Each rule is set to **Error** or **Warning**, or turned off, in Preferences. The values Restore Defaults sets are in [Default preferences](17_default_preferences.md).

| Rule | What it checks |
|------|----------------|
| Title blank | No title after the tags and fallbacks (always an error) |
| Author blank | No author after the tags and fallbacks (always an error) |
| Author starts with non-letter | The author does not begin with a letter |
| Author name in title | The author text appears inside the title |
| Title in author name | The title text appears inside the author, for example **Anna Sewell Black Beauty** |
| Unknown or Various author | The author contains "unknown" or "various" |
| Unreadable audio length | The files exist but the total time is zero |
| Year out of range | The year is not a number, or is outside 1801 to the current year |
| Minimum title length | The title is shorter than the set minimum (3 characters by default) |
| File structure | The folder path does not match the expected Author/Title or Year/Author/Title pattern |
| Minimum book length | The total time is below the set minutes (off by default) |
| Maximum book length | The total time is above the set hours (off by default) |

A file that could not be read is always an error.

## Checking for duplicates

Before adding a book, AbCS compares it with the books **already in your library**, and with the books added earlier in the same scan.

The **Duplicate match** setting decides which fields must match:

| Match | Treated as a duplicate when |
|-------|-----------------------------|
| Title + Author + Year + Collection | All four match |
| Title + Author + Year | The title, author, and year match anywhere in the library |
| Title + Author + Collection | The title, author, and collection match |
| Title + Author | The title and author match; the year is ignored |

Before comparing, AbCS removes trailing series numbers from both titles, so `The Moonstone - 01` compares as `The Moonstone`. When both titles have a series number and the numbers differ (01 and 02), the books are treated as different, so a whole series can be imported at once. A title with no series number still matches a library title that has one.

When a **fuzzy** percentage is set, near-matches count too. Both the title and the author must reach that percentage. At 0%, only exact matches count.

A duplicate is always held in the review table with the status **Duplicate**.

## Added or held for review

A book is **added immediately** only when all of these are true:

- It is not a duplicate.
- Its files could be read.
- It has no validation error or warning.
- No fallback was used (no **F:** flag).
- No auto-correction was applied, or Skip review is checked for it (no **C:** flag).

Every other book is **held for review** in the Import table, with a status:

| Status | Reason |
|--------|--------|
| **Duplicate** | Already in the library |
| **Error** | Unreadable file, blank title or author, or another serious problem |
| **Warning** | A validation warning, fallback, or correction |

## Saving the added books

For each added book, AbCS:

1. Finds the author, or adds a new author name.
2. Finds the genre and series, or adds new names, when the book has them.
3. Saves the book with its title, author, year, series, genre, collection, narrator, time, number of files, size, bitrate, format, folder path, plot, and the date added.

AbCS stores the folder path and the number of files, not a list of each file. All the books added in one scan are saved together at the end.

## When the scan finishes

- The progress window closes.
- A message says **Import completed** with an **OK** button.
- The status bar has the summary, for example "Scanned: 48 | Added: 32 | Corrected: 8 | Errors: 2 | Warnings: 4 | Duplicates: 2 | Elapsed: 01:12". Press **Alt+/** to hear it.
- The **Import** button is available again.
- The collection stays locked until the review list is empty or you close Import.
- After **OK**, focus moves to the review table, or to Import when the list is empty.

When no audio files are found, the summary says so.

## The review table

Books held for review appear in the **review table** in the Import window.

- **Error filter** (**Alt+E**) — show only duplicates, errors, warnings, fallbacks, or corrections.
- **Enter** on a row — open Import Detail to edit the title, author, year, and other fields.
- **Add Selected** (**Alt+S**) — add the selected rows with status OK or Warning to your collection.
- **Export** (**Alt+X**) — save the review list to a spreadsheet.

Add Selected skips duplicates. Edit a duplicate in Import Detail so it no longer matches, or discard it.

These controls are grayed out until a scan holds books for review. The error filter is available while at least one row has an issue. When the last issue is fixed, the filter goes back to All.

| Preference | Effect on the review |
|------------|----------------------|
| Skip review for a correction | The correction still applies, and the book can be added automatically |
| Duplicate match | Which books in your library count as duplicates |
| Fuzzy threshold | How close a near-match must be to count as a duplicate |
| Validation rule severity | Whether a book is an Error or a Warning, and so whether Add Selected can add it |

When you close Import (**Escape**), the main book list refreshes, and every added book appears in the collection you chose.

## Related help

- Steps and shortcuts: [Import (Folder Scan)](02_import.md)
- Settings detail: [Import preferences](18_import_preferences.md)
- Spreadsheet import: [Import Book List explained](20_import_book_list_explained.md)
- Online plot lookup: [Web metadata explained](21_web_metadata_explained.md)
