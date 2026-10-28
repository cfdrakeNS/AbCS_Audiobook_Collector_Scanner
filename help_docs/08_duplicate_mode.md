# Duplicate Mode

## What this is

Duplicate Mode is a library cleanup tool. It scans all books already in your database and finds groups that match on title and author, and optionally year and collection, depending on the rule you choose. The main list then shows only those books, so you can review, delete, or export them.

Duplicate Mode works on books already stored. Import has its own duplicate check for new books; see [Import](02_import.md).

## When to use it

- You suspect the same book was added more than once.
- You want to remove duplicate entries after importing from several sources.

## Before you start

- The scan covers your whole library, so there is no need to select books first.
- The default match type comes from **Preferences → Validation Rules → Duplicate Match**. You can change it in the Duplicate Check dialog.

## Window layout

**Duplicate Check** dialog:

- A line that says "Select duplicate match type:", and a line that says "Press Escape to close."
- **Duplicate match type** combo.
- **Start** button.

**Main window in duplicate mode:**

- The book table shows only duplicate books.
- The footer shows **Delete** and **Export Duplicates**.
- The status bar reports how many duplicates were found and which match type was used.

## Run duplicate check

1. Open **Manage → Duplicate Check** (**Alt+M**, then **D**).
2. Choose a **match type** (**Alt+M** moves to the combo):
   - Title + Author + Year + Collection
   - Title + Author + Year
   - Title + Author + Collection
   - Title + Author
3. Press **Start** (**Alt+R**) to run the scan, or press **Escape** to close the dialog.
4. **When no duplicates are found:** a message says so, and the normal book list stays.
5. **When duplicates are found:** a **Duplicate check complete** message reports the count. After you close it:
   - Duplicate mode starts.
   - Your current filters are saved and cleared, so every duplicate is visible.
   - The book table shows only duplicate books.
   - Focus moves to the first book in the list.

## Work in duplicate mode

1. **Listen** to the focused book (**Edit → Listen**, the **Listen** toolbar button, or **Ctrl+L**) to hear which copy to keep.
2. **Delete** removes the focused book and any selected books. Select extra rows, then press **Delete** in the footer or **Alt+D**.
3. **Export Duplicates** (**Alt+X**) saves a CSV with Author, Title, Year, Time, Collection, and Date Added.
4. Update and Fetch Web Info are turned off in duplicate mode.
5. After each delete, the duplicate list refreshes. When no duplicates remain, duplicate mode ends with a message.
6. To leave earlier, press **Escape**. If rows are selected, the first Escape clears the selection. The next Escape asks you to confirm leaving.
7. When duplicate mode ends, your previous filters come back and the full book list returns.

## What happens next

- Deleted books are removed from the database.
- Opening **Import** or **Import Book List** ends duplicate mode before those windows open.

## Settings that affect this

- **Duplicate Match** in Preferences sets the default match type shown in the Duplicate Check dialog.
- **Fuzzy duplicate percent** is used by Import only. Duplicate Mode uses exact matching on the fields in your chosen rule.

## Mouse, shortcuts, and accessibility

- Open **Manage → Duplicate Check** from the menu bar.
- In the dialog, choose a match type and click **Start**.
- In duplicate mode, click **Delete** or **Export Duplicates** in the footer.

Duplicate Check dialog:

| Shortcut | Action |
|----------|--------|
| Alt+M, D | Open Duplicate Check (main window) |
| Alt+M | Match type combo |
| Alt+R | Start duplicate check |
| Escape | Close the dialog |

Main window in duplicate mode:

| Shortcut | Action |
|----------|--------|
| Alt+D | Delete focused and selected books |
| Alt+X | Export duplicates to CSV |
| Ctrl+L | Listen to the focused duplicate |
| Escape | Clear selection, then confirm leaving duplicate mode |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Duplicate Mode or Import duplicates — what is the difference?**
Import checks new books while they are added, can use fuzzy matching, and holds a match in the review list. Duplicate Mode checks the books already in your library, uses exact matching, and filters the table to the duplicates.

**Why did my filters disappear?**
Duplicate mode clears filters so you see every duplicate across collections. Your filters come back when you leave.

**How do I leave duplicate mode?**
Press **Escape** and confirm, or delete duplicates until none remain. Opening Import also ends it.

**Is Export Library the same as Export Duplicates?**
No. **Export Duplicates** (**Alt+X** in duplicate mode) saves only the duplicate rows. **File → Export Library** exports the normal main list, and is available after you leave duplicate mode. See [Export Library](25_export_library.md).

## Related help

- Main window: [Find and Filters (Main Window)](03_find_filters.md)
- Import duplicate settings: [Import preferences](18_import_preferences.md)
- Saving the list: [Export Library](25_export_library.md)
