# Check Book Locations Process

## What this is

**Check Book Locations** scans the books in a collection and checks each stored **Path**. It tries the path on disk, then looks under the collection folder: the author folder, then the series folder when the book has a series. The Preferences **Import scenario** is not used. When the book is found in the collection folder, the scan saves that path, does not list the book, and only counts it as **Corrected**. The table shows only books that still need attention: **Missing** (cannot be found) and **Incorrect** (on disk outside the collection folder, and not found in it). A short guide at the top of the window explains this; press **Alt+I** (or Tab after Scan) to reach it.

## When to use it

- A folder moved and paths in AbCS are stale.
- Books were imported with no path and you want to fill paths from the collection folder.
- You want a list of books with broken or off-root paths before a cleanup.
- Export a CSV of problem paths for reference.

## Before you start

- Each book's stored **Path** (file or folder) is checked first.
- When the stored path is blank or stale, the scan remaps under the collection folder or Preferences import folder, then searches the collection folder in this order:
  1. The author folder: a title folder, then a single audio file named for the title.
  2. When the book has a series: the series folder inside the author folder, the same way.
  3. When the book has no series: one folder down inside the author folder (used only if exactly one matches).
- A stored path from an old drive letter or moved folder that still matches a folder under the collection folder (for example a USB drive that now has a different letter) counts as **Valid**. The stored path is left as it is, so the drive stays portable.
- A stored path that exists outside the collection folder is also searched for. If the book is in the collection folder, the path is corrected; if not, it is listed as **Incorrect**.
- Title folders and files may have a number before or after the title, such as `3 - Silver Lantern` or `4 Copper Bridge`, or a series tag at the end, such as `2 Glass Harbor(Tide Runner 02).m4b`. A tag with no number, such as `(Unabridged)`, is ignored. Listen uses the same rules: see **Listen to a Book**.
- The collection folder itself is not listed as a separate row; set or fix it in Collection Manager.
- Choose a **Collection** the same way as the main window filter: **All Collections** or one name.

## Check book locations

1. Open **Manage → Check Book Locations** (**Alt+M**, then **L**).
2. Choose **Collection** (**Alt+C**): **All Collections** (every book) or one collection. In Collection and Filter, plain Up and Down arrows do nothing (a beep); press **Alt+Down** to open the list, then Enter to choose.
3. Choose **Filter** (**Alt+F**):
   - **All** (default) — missing and incorrect
   - **Missing** — the book cannot be found on disk. The row says why, for example the collection folder is missing or the author folder was not found.
   - **Incorrect** — the stored path is on disk but not under the collection folder, and the book was not found in the collection folder
4. Click **Scan** (**Alt+S**, or Enter when Scan has focus). Scanning runs only when you press Scan. Changing **Filter** after a scan refilters the last results without rescanning; changing **Collection** clears the list until you Scan again.
5. If a scanned collection has no collection folder set, or the folder is missing or has no audiobook files, a warning explains that books cannot be found without it and how to fix it in Collection Manager. Press Enter to close the warning; the scan continues.
6. While scanning, a progress window shows **Missing**, **Corrected**, **Incorrect**, and **Valid** counts plus how many books are done and elapsed time. Escape cancels (with confirm) and keeps results found so far.
7. When the scan ends, paths found in the collection folder are saved. The status bar starts with how many were corrected, for example "12 book paths corrected." Corrected books are not listed.
8. The table lists Author, Title, Error, and Path. The **Error** column shows the status (Missing or Incorrect), and Missing rows include the reason. Blank paths show as `(empty)`. Screen readers hear the title, author, status, and path on the Title cell. The Path cell reads only the path.
9. To fix one book, focus a row (**Alt+L**) and press **Enter** (or double-click). Book Details opens in edit mode. Use **Browse** (**Alt+B**) or type the path, then Save. **Page Up** and **Page Down** move through the listed books, and Save stays available on each one.
10. When you close Book Details after a save, Check Book Locations re-checks only the books you edited and refreshes the list; it does not run a full scan. Export the list with **Export** (**Alt+X**) if needed; the CSV includes the reason for missing books.
11. Press **Escape** to close and return to the main window.

## What happens next

- Corrected and saved paths stay in the database.
- Closing Check Book Locations refreshes the main book list.

## Mouse, shortcuts, and accessibility

- Open **Manage → Check Book Locations**.
- Double-click a row to open Book Details.
- Status bar reports the corrected count and scan counts; press **Alt+/** to re-read it. During Scan, Alt+/ reads the progress window status.

| Shortcut | Action |
|----------|--------|
| Alt+M, L | Open Check Book Locations (Manage menu) |
| Alt+C | Collection |
| Alt+F | Filter |
| Alt+Down | Open the Collection or Filter list |
| Alt+I | Info instructions at top of window |
| Alt+S | Scan |
| Alt+L | Jump to list |
| Enter | Open Book Details for the focused row |
| Page Up / Page Down | Previous or next listed book (in Book Details) |
| Alt+X | Export list to CSV |
| Escape | Cancel scan (with confirm) or close |
| Alt+/ | Re-read status |
| F1 | Shortcuts for this window |
| Shift+F1 | This help topic |

## Common confusion

**Where did some books go after a scan?**
Books found in the collection folder had their path corrected and are not listed, whether their path was blank, gone, or outside the collection folder. They count only as **Corrected**; the status bar says how many.

**What is the difference between Missing and Incorrect?**
**Missing** means AbCS cannot find the book at the stored path or under the collection folder. **Incorrect** means the stored path still exists on disk but points outside the collection folder, and the book was not found in the collection folder.

**Is the collection folder checked?**
Yes. Before scanning, a warning appears if a collection folder is not set, missing, or has no audiobook files, because books cannot be found without it. Missing rows also say so. Fix the folder in Collection Manager, not in this list.

**Does Check Book Locations delete books?**
No. It corrects paths it can find and lists the rest. Delete stays on the main window.

## Related documentation

- [Book Details process](04_book_details.md)
- [Collections process](06_collections.md)
- [Import process](02_import.md)
- [Keyboard shortcuts by window](16_shortcuts.md)
