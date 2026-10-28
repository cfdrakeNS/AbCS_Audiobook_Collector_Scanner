# Import (Folder Scan)

## What this is

Import scans a folder of audiobook files, reads information from the audio file tags (such as title and author), and adds books to your chosen collection. This is the main way to build your library from files on your computer. Your audio files stay where they are; AbCS only reads them.

For a walkthrough of what happens during a scan, see [Import explained](19_import_explained.md).

## Quick steps

1. Press **Ctrl+I** to open Import.
2. Check the **Collection** and the **Folder**.
3. Press **Import** (**Alt+I**) and wait for **Import completed**.
4. Review any held books in the review table, then press **Add Selected** (**Alt+S**).
5. Press **Escape** to close Import.

## When to use it

- You have audiobook files organized in folders and want to add them to AbCS.
- You are bringing in a batch of new titles after setting up a collection.

## Before you start

- At least one **active collection** must exist. See [Collections](06_collections.md).
- Know which folder contains your audiobooks.
- Optional: set up Preferences first (**Manage → Preferences**). Import depends heavily on these settings.

## Window layout

- **Header row:** **Collection** combo, **Folder** field (filled by Browse), **Browse** button, **Import** button, and **Errors Filter** combo.
- **Review table:** columns Author, Title, Year, Error Type, and File/Folder. It lists books held for review after a scan.
- **Footer:** status bar on the left, then the **Add Selected** and **Export** buttons.

**Add Selected**, **Export**, and the **Errors Filter** are grayed out until a scan finds books. The Errors Filter also stays grayed out when every scanned book is clean. While a control is grayed out, Tab skips it.

Tab order: Collection, Folder, Browse, Import, Errors Filter, review table, Add Selected, Export.

The **progress window** opens during a scan. It shows a progress bar and a status bar. Press **Escape** in the progress window to cancel the scan.

## Run folder import

1. Open **File → Import**, or press **Ctrl+I**.
2. Choose a **Collection** (**Alt+C**). If the main window shows a specific collection, it is pre-selected.
3. Check the **Folder** (**Alt+F**). It starts as the Preferences **default import directory**. Press **Browse** (**Alt+B**) to choose a different folder. Subfolders are included. Changing the collection keeps the Folder as it is.
4. Press **Import** (**Alt+I**) to start the scan.
5. The progress window shows how many files are read. When the scan finishes, the progress window closes and a message says **Import completed** with an **OK** button.
6. Clean books are added automatically. Books with duplicates, errors, warnings, fallback guesses, or autocorrects are **held for review** in the review table.
7. To show only some issue types, use the **Errors Filter** (**Alt+E**): All, Corrected, Duplicate, Error, Fallback, or Warning.
8. To work on one book, select its row and press **Enter**, or double-click the row. **Import Detail** opens, where you can edit fields, Keep, Discard, or move with Page Up and Page Down. A book whose files cannot be read shows a message instead of opening detail.
9. Select rows, then press **Add Selected** (**Alt+S**).
10. Optionally press **Export** (**Alt+X**) to save the review list to a spreadsheet. The columns are Author, Title, Year, Files, Time, Size MB, Error Type, and File/Folder.
11. Press **Escape** to close Import. If held books remain, AbCS asks you to confirm.

## What happens next

- Added books appear in the main book list when Import closes.
- The status bar reports how many books were scanned, added, and held for review.
- If duplicate mode was active on the main window, it ends when Import opens.

## Settings that affect import

Open **Manage → Preferences**. Import settings are on three tabs. Each scan uses the latest saved preferences.

### Import Settings

- **Default directory** — the folder Import starts with. Choosing a collection in Import keeps this folder. With only one collection, an empty collection folder and an empty default directory fill from each other.
- **Audio formats** — which file types to scan: MP3, M4A, M4B, FLAC, OGG, WAV, WMA, AAC, and OPUS. All are checked by default.
- **Import scenario** — how your folders are organized. The Import window shows the active scenario name in the status bar.
- **Tag mapping** — the Book title and Author tag choices. Defaults are Album, and Album artist then artist. Files are grouped into books by the album and album artist tags, whatever subfolders they are in.

| Scenario | Folder layout | When to use |
|----------|---------------|-------------|
| **Mass Standard Import** | Author, then title subfolders or files | The default. Most libraries. Series come from tags |
| **Mass Import - Series From Directory** | Author, then series folder, then audio files | One file or album per book directly inside the series folder. A leading number on the book file name, such as 03, is stored as the series number |
| **Mass Import - Series From Directory (Nested Books)** | Author, then series folder, then book folder, then audio files | Each book in its own subfolder under the series. Books directly under the author get no series. A leading number on the book folder name, such as 1- Title, is stored as the series number |
| **Mass Import - Series From File Name** | Any layout | The series name is in the file name inside parentheses. A trailing number such as 04 or 6.5 is stored as the series number |
| **Single Author / Book Import** | One author, book, or file | Import a single folder or file at a time |

Choosing between the two series-from-directory scenarios:

- **Series From Directory** — files sit directly in the series folder, for example `Sir Arthur Conan Doyle/Sherlock Holmes/The Hound of the Baskervilles.m4b`.
- **Series From Directory (Nested Books)** — each book has its own folder under the series, for example `Sir Arthur Conan Doyle/Sherlock Holmes/The Hound of the Baskervilles/01 The Hound of the Baskervilles.m4b`.

If you use Series From Directory on the nested layout, AbCS skips the series and marks those books with a **warning**. Switch to Nested Books for that layout.

See [Import preferences](18_import_preferences.md) for full scenario details, fallbacks, and validation rules.

### Fallback & Auto Correct

- **Author fallback to folder** — when the author tag is missing, use the folder name. When unchecked, the book is held with an error.
- **Title fallback to file** — when the title tag is missing, use the file name. When unchecked, the book is held with an error.
- **Reader keywords** — words that help find the narrator in comments, for example "narrator" or "read by".
- **Auto Correct** — optional text cleanup during the scan: proper case, trim extra spaces, remove leading punctuation, and remove non-printable characters. Accented letters are kept. Each option has an indented **Skip review** checkbox, available when the option is checked.

### Validation Rules

Each rule can be None, Warning, or Error:

- Author name appears in the title.
- Title appears in the author.
- Author is "Unknown" or "Various".
- Title is too short.
- Book is too short or too long.
- File or folder naming does not match the expected pattern.
- Year is out of a reasonable range.

Duplicate settings used during import:

- **Duplicate match** — which fields must match a book already in the database, for example title, author, and year.
- **Fuzzy duplicate percent** — how similar the title and author text must be. Both must pass. Set it to 0 for exact matching only.

## Mouse, shortcuts, and accessibility

- Open **File → Import** from the menu bar.
- Click **Browse** to pick a folder, then click **Import** to start the scan.
- In the review table, click a row to select it. Use **Ctrl+click** or **Shift+click** to select several rows before **Add Selected**.

| Shortcut | Action |
|----------|--------|
| Ctrl+I | Open Import (main window) |
| Alt+C | Collection |
| Alt+F | Folder |
| Alt+B | Browse |
| Alt+I | Import (start scan) |
| Alt+E | Error filter |
| Alt+L | Jump to table |
| Alt+1 | Jump to Author |
| Alt+2 | Jump to Title |
| Alt+3-5 | Jump to Year, Error Type, or File/Folder |
| Enter | Open import detail |
| Alt+S | Add selected |
| Alt+X | Export list to CSV |
| Escape | Cancel or close window (asks to confirm if held books remain) |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Why were some books added and others held?**
Clean books are added immediately. A book with a duplicate match, validation issue, or fallback guess waits in the review list until you add it. An autocorrect also holds a book unless **Skip review** is checked for that correction in Preferences.

**Is import duplicate detection the same as Duplicate Mode?**
No. Import checks new books as they come in, and can use fuzzy matching. Duplicate Mode (Manage menu) finds duplicates already in your library with exact matching. See [Duplicate Mode](08_duplicate_mode.md).

**Do I need to set preferences every time?**
No. Preferences are saved and apply to every import until you change them.

**Why does Series From Directory show warnings for my author folder?**
That scenario expects audio files directly in the series folder. When each book has its own folder under the series, choose **Mass Import - Series From Directory (Nested Books)** in Preferences.

## Related help

- One held book: [Import Detail](12_import_detail.md)
- What happens during a scan: [Import explained](19_import_explained.md)
- Scenario and rule detail: [Import preferences](18_import_preferences.md)
- Spreadsheet import: [Import Book List](11_import_book_list.md)
- Words such as held for review, fallback, and auto-correct: [Glossary](27_glossary.md)
