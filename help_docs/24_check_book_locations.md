# Check Book Locations

## What this is

**Check Book Locations** scans the books in a collection and checks each stored **Path**. When it finds a book in the collection folder, it saves that path and counts the book as **Corrected**. The list then shows only the books that still need attention.

A short guide at the top of the window explains this. Press **Alt+I**, or Tab after Scan, to read it.

## Quick steps

1. Open **Manage → Check Book Locations** (**Alt+M**, then **L**).
2. Choose the **Collection** (**Alt+C**).
3. Press **Scan** (**Alt+S**) and wait for **Check completed**.
4. For each listed book, press **Enter** to open Book Details, fix the path, and save.
5. Press **Escape** to close.

## When to use it

- A folder moved and the paths in AbCS are out of date.
- Books were imported with no path, and you want to fill the paths from the collection folder.
- You want a list of books with broken paths before a cleanup.
- You want a CSV of the problem paths.

## Before you start

- Set the collection folder for each collection in [Collections](06_collections.md). The scan searches that folder.
- Choose **All Collections** to scan every book, or one collection.

## Window layout

- **Header row:** **Collection** combo, **Filter** combo, and **Scan** button.
- **Guide:** a short explanation of the scan (**Alt+I**).
- **Book list:** columns Author, Title, Error, and Path. Blank paths show as `(empty)`.
- **Footer:** status bar, then the **Export** button. Export is available after a scan.

Tab order: Collection, Filter, Scan, the guide, the book list, Export.

In Collection and Filter, plain Up and Down arrows beep and leave the choice as it is. Press **Alt+Down** to open the list, then **Enter** to choose.

## Check book locations

1. Open **Manage → Check Book Locations** (**Alt+M**, then **L**).
2. Choose **Collection** (**Alt+C**): **All Collections** or one collection.
3. Choose **Filter** (**Alt+F**). **All** (the default) shows every problem. The other choices are **Author not found**, **Book not found**, and **Incorrect**.
4. Press **Scan** (**Alt+S**), or press **Enter** on Scan.
5. If a collection's folder is not set, is missing, or has no audiobook files, a warning explains how to fix it in Collections. Press **Enter** to close the warning; the scan goes on.
6. A progress window shows the counts for Author not found, Book not found, Corrected, Incorrect, and Valid, plus how many books are done. Press **Escape** to cancel; AbCS asks to confirm and keeps the results so far.
7. When the scan finishes, a message says **Check completed** with an **OK** button. The status bar starts with how many paths were corrected, for example "12 book paths corrected."
8. The list shows the books that still need attention. The **Error** cell says what is wrong, and the **Path** cell shows the stored path.

Changing **Filter** after a scan refilters the last results right away. Changing **Collection** clears the list until you scan again.

## Fix a listed book

1. Move to the list (**Alt+L**) and select the book.
2. Press **Enter**, or double-click the row. Book Details opens in edit mode.
3. The **Errors** field shows the same problem as the list, in red.
4. Press **Browse** (**Alt+B**), or type the path. When the author folder is in the collection folder, Browse opens in that author folder.
5. Press **Save** (**Ctrl+S**).
6. Press **Page Up** or **Page Down** to move to the previous or next listed book.
7. Close Book Details. Check Book Locations checks the books you edited again and refreshes the list. A fixed book leaves the list, and focus moves to the next book.

To keep a record, press **Export** (**Alt+X**). The CSV columns are Author, Title, Series, Series No, Status, Reason, Collection, and Path.

## What the errors mean

- **Author not found in** the collection folder: no folder with the author's name is directly in the collection folder.
- **Book not found in author**: the author folder exists, and the book is not in it.
- **Series not found in author**: the book has a series, and no series folder with that name is in the author folder. This shows under the **Book not found** filter.
- **Incorrect**: the stored path is on disk outside the collection folder, Listen cannot play it, and the book is not in the collection folder.
- **Collection folder missing or not set**: shows under **All**. Fix it in Collections.

## How books are found

The scan tries the stored path first. When the stored path is blank or gone, it searches the collection folder in this order:

1. The author folder: a title folder, then a single audio file named for the title.
2. When the book has a series: the series folder inside the author folder, the same way.
3. When the book has no series: one folder down inside the author folder. That folder is used only if it is the only match.
4. When the book has a series but is not in its series folder: one folder down inside the author folder. A book found this way is listed under **Book not found**, with its path left as it was. The Error cell ends with **found in** and the folder where the book is. Move the book into its series folder, or fix its path or series in Book Details.

More matching rules:

- When the author has several names separated by commas, such as `Charles Dickens, Wilkie Collins`, a folder with the full name is tried first, then a folder for the first author, `Charles Dickens`.
- A stored path from an old drive letter or a moved folder that still matches a folder under the collection folder counts as **Valid**, for example a USB drive that now has a different letter. The stored path is kept, so the drive stays portable.
- A stored path outside the collection folder is checked too. When the book is in the collection folder, the path is corrected. When it is not, and Listen can play the stored path, the book is **Valid**.
- Title folders and files may have a number before or after the title, such as `3 - The Moonstone` or `2 Whose Body`.
- A series tag at the end of the name also works, such as `1 Whose Body(Lord Peter Wimsey 01).m4b`. A tag with no number, such as `(Unabridged)`, is ignored.
- Listen uses the same rules. See [Listen to a book](26_listen_to_a_book.md).

## What happens next

- Corrected and saved paths stay in the database.
- Closing Check Book Locations refreshes the main book list.

## Mouse, shortcuts, and accessibility

- Open **Manage → Check Book Locations**.
- Double-click a row to open Book Details.
- Right-click a cell to copy it.

| Shortcut | Action |
|----------|--------|
| Alt+M, L | Open Check Book Locations (main window) |
| Alt+C | Collection |
| Alt+F | Filter |
| Alt+Down | Open the Collection or Filter list |
| Alt+I | Info instructions |
| Alt+S | Scan |
| Alt+L | Jump to list |
| Enter | Open Book Details |
| Ctrl+C | Copy focused cell |
| Right-click | Copy cell |
| Page Up/Down in Book Details | Previous or next listed book |
| Alt+X | Export list to CSV |
| Escape | Cancel scan or close window |
| Alt+/ | Re-read status (during a scan, the progress window status) |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Where did some books go after a scan?**
Books found in the collection folder had their path corrected, and they leave the list. The status bar says how many were corrected.

**Is the collection folder itself checked?**
Yes. Before scanning, a warning appears when a collection folder is not set, is missing, or has no audiobook files. Fix the folder in Collections.

**What happens to books in the list?**
They stay in your library. Check Book Locations corrects the paths it can find and lists the rest. To delete a book, use the main window.

## Related help

- Fixing one book: [Book Details](04_book_details.md)
- Setting the collection folder: [Collections](06_collections.md)
- Playing books: [Listen to a book](26_listen_to_a_book.md)
- All shortcuts: [Keyboard shortcuts by window](16_shortcuts.md)
