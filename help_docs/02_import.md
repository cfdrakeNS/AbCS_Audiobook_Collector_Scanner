# Import (Folder Scan)

## What this is

Import scans a folder of audiobook files, reads information from the audio file tags (such as title and author), and adds books to your chosen collection. This is the main way to build your library from files on your computer. Your audio files stay where they are; AbCS only reads them.

For a walkthrough of what happens during a scan, see [Import explained](19_import_explained.md).

## Quick steps

1. Press **Ctrl+I** to open Import.
2. Check the **Collection**, the **Scenario**, and the **Folder**.
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
- **Second row:** **Scenario** combo, below Collection.
- **Review table:** columns Author, Title, Year, Error Type, and File/Folder. It lists books held for review after a scan.
- **Footer:** status bar on the left, then the **Add Selected** and **Export** buttons.

**Add Selected**, **Export**, and the **Errors Filter** are grayed out until a scan finds books. The Errors Filter also stays grayed out when every scanned book is clean. While a control is grayed out, Tab skips it.

Tab order: Collection, Scenario, Folder, Browse, Import, Errors Filter, review table, Add Selected, Export.

While held books remain in the review table, **Collection** and **Scenario** are grayed out. They become available again when the review table is empty.

The **progress window** opens during a scan. It shows a progress bar and a status bar. Press **Escape** in the progress window to cancel the scan.

## Run the scan

1. Open **File → Import**, or press **Ctrl+I**.
2. Choose a **Collection** (**Alt+C**). If the main window shows a specific collection, it is pre-selected.
3. Check the **Scenario** (**Alt+N**). It starts as the Preferences **import scenario**. Press **Alt+Down** to open the list and choose a different one. The change applies only to this Import window; Preferences are not changed. The next time you open Import, it starts from Preferences again.
4. Check the **Folder** (**Alt+F**). It starts as the Preferences **default import directory**. Press **Browse** (**Alt+B**) to choose a different folder. With **Single Author / Book Import**, Browse picks one audio file; with the other scenarios it picks a folder. Subfolders are included. Changing the collection keeps the Folder as it is.
5. Press **Import** (**Alt+I**) to start the scan.
6. The progress window shows how many files are read. When the scan finishes, the progress window closes and a message says **Import completed** with an **OK** button.
7. Clean books are added automatically. Books with duplicates, errors, warnings, fallback guesses, or autocorrects are **held for review** in the review table.

## Review books that were not added

1. To show only some issue types, use the **Errors Filter** (**Alt+E**): All, Corrected, Duplicate, Error, Fallback, or Warning.
2. To work on one book, select its row and press **Enter**, or double-click the row. **Import Detail** opens, where you can edit fields, Keep, Discard, or move with Page Up and Page Down. A book whose files cannot be read shows a message instead of opening detail.
3. Select the rows to add, then press **Add Selected** (**Alt+S**).
4. Press **Escape** to close Import. If held books remain, AbCS asks you to confirm.

## Export the review list

Press **Export** (**Alt+X**) to save the review list to a spreadsheet. The columns are Author, Title, Year, Files, Time, Size MB, Error Type, and File/Folder.

## What happens next

- Added books appear in the main book list when Import closes.
- The status bar reports how many books were scanned, added, and held for review.
- If duplicate mode was active on the main window, it ends when Import opens.

## Settings that affect import

Open **Manage → Preferences**. Each scan uses the latest saved preferences, except the scenario, which comes from the Import **Scenario** combo.

- **Default directory** — the folder Import starts with. Choosing a collection in Import keeps this folder. With only one collection, an empty collection folder and an empty default directory fill from each other.
- **Audio formats** — which file types to scan: MP3, M4A, M4B, FLAC, OGG, WAV, WMA, AAC, and OPUS. All are checked by default.
- **Import scenario** — how your folders are organized. Import starts with this scenario in its **Scenario** combo. Changing the combo in Import does not change Preferences.
- The book title comes from the Album tag, and the author from the Album artist tag, then the Artist tag. Files are grouped into books by the album and album artist tags, and by the folder below the author folder. The same book in two series folders stays two books, and the later copy is held as a duplicate.

Fallbacks, auto-corrections, validation rules, and duplicate matching decide which books are held for review. Each scenario, with folder examples, and each rule are described in Import preferences. Choose **import preferences** from All Help Topics.

## Mouse, shortcuts, and accessibility

- Open **File → Import** from the menu bar.
- Click **Browse** to pick a folder, then click **Import** to start the scan.
- In the review table, click a row to select it. Use **Ctrl+click** or **Shift+click** to select several rows before **Add Selected**.

| Shortcut | Action |
|----------|--------|
| Ctrl+I | Open Import (main window) |
| Alt+C | Collection |
| Alt+N | Scenario |
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
| Escape | Clear selection first; otherwise cancel or close window (asks to confirm if held books remain) |
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
That scenario expects audio files directly in the series folder. When each book has its own folder under the series, choose **Mass Import - Series From Directory (Nested Books)** in the Import **Scenario** combo, or in Preferences to make it the starting choice.

## Related help

Click a guide name, or press Enter on its line, to open it. You can also open these from All Help Topics.

- One held book: [Import Detail](12_import_detail.md)
- What happens during a scan: [Import explained](19_import_explained.md)
- Scenario and rule detail: [Import preferences](18_import_preferences.md)
- Spreadsheet import: [Import Book List](11_import_book_list.md)
- Words such as held for review, fallback, and auto-correct: [Glossary](27_glossary.md)
