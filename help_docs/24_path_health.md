# Check Books Path Process

## What this is

**Check Books Path** scans one collection and lists books whose stored **Path** is blank, missing on disk, or not under the collection library root (**Incorrect**). It does not change paths by itself — press **Enter** on a row to open Book Details and use **Browse** or type a new path.

## When to use it

- Listen or import fails because a folder moved.
- You want a list of books with broken or off-root paths before a cleanup.
- Export a CSV of problem paths for reference.

## Before you start

- Each row checks that book’s stored **Path** (file or folder).
- The collection **library root** is used only to decide **Incorrect** (path on disk but not under the root). The root folder itself is not listed as a separate result; set or fix it in Collection Manager.
- Choose a **Collection** the same way as the main window filter: **All Collections** or one name. If the main window has a collection filter, Check Books Path starts with that collection; if main is All Collections, this window starts on All Collections.

## Check book paths

1. Open **Manage → Check Books Path** (**Alt+M**, then **H**).
2. Choose **Collection** (**Alt+C**): **All Collections** (every book) or one collection. If the main window filter is All Collections, this window opens on All Collections; if a specific collection is filtered, that collection is selected.
3. Choose **Filter** (**Alt+F**):
   - **All** (default) — both missing and incorrect (invalid stored paths only; OK paths are omitted)
   - **Missing** — blank path, or not playable even after the same remap Listen uses
   - **Incorrect** — still playable (stored path remapped under the library root or import folder), or on disk but not under the library root
4. Click **Scan** (**Alt+S**). Scanning runs only when you press Scan. Changing **Filter** after a scan refilters the last results without rescanning; changing **Collection** clears the list until you Scan again.
5. While scanning, a progress window shows **Missing**, **Incorrect**, and **Valid** counts plus how many books are done and elapsed time. Escape cancels (with confirm) and keeps rows found so far for the current filter. Status updates are not spoken on every book — only start, cancel, and finish.
6. The table lists Author, Title, and Path. Blank paths show as `(empty)`. The status bar says how many are missing or incorrect in plain language, including Valid when useful.
7. Focus a row (**Alt+L**) and press **Enter** (or double-click) to open Book Details in edit mode. Use **Browse** (**Alt+B**) or type the path, then Save.
8. After you save a fix, Check Books Path rescans. Export the list with **Export** (**Alt+X**) if needed.
9. Press **Escape** to close and return to the main window.

## What happens next

- Fixed paths stay in the database after Save in Book Details.
- Closing Check Books Path refreshes the main book list.

## Mouse, shortcuts, and accessibility

- Open **Manage → Check Books Path**.
- Double-click a row to open Book Details.
- Status bar reports scan counts; press **Alt+/** to re-read it. During Scan, Alt+/ reads the progress window status (Missing / Incorrect / Valid).

| Shortcut | Action |
|----------|--------|
| Alt+M, H | Open Check Books Path (Manage menu) |
| Alt+C | Collection |
| Alt+F | Filter |
| Alt+S | Scan |
| Alt+L | Jump to list |
| Enter | Open Book Details for the focused row |
| Alt+X | Export list to CSV |
| Escape | Cancel scan (with confirm) or close |
| Alt+/ | Re-read status |
| F1 | Shortcuts for this window |
| Shift+F1 | This help topic |

## Common confusion

**What is the difference between a blank path and Missing?**
Both are **Missing** in the filter and status bar: either the Path field is blank, or Listen cannot find the book after remapping under the collection library root or Preferences import folder. Blank paths show as `(empty)` in the Path column.

**Why can I listen to a book that Check Books Path lists?**
If the stored path is stale but Listen remaps it under the library root, that book is **Incorrect**, not **Missing**. Use Browse in Book Details to save the real path. **Missing** means Listen would also fail.

**Is the collection library root checked?**
Only as a reference for remapping (same as Listen) and for **Incorrect**. Book paths are checked one by one. A missing or wrong collection root is fixed in Collection Manager, not in this list.

**Why is a path Incorrect when the file still plays?**
Listen may remap under the collection library root or Preferences import folder. Check Books Path reports problems with the **stored** path. **Incorrect** means the book is still playable that way, or the stored path exists but is not under the collection library root. Fix the stored path with Browse so it matches the real library location.

**Does Check Books Path delete books?**
No. It only lists problems. Delete stays on the main window.

## Related documentation

- [Book Details process](04_book_details.md)
- [Collections process](06_collections.md)
- [Import process](02_import.md)
- [Keyboard shortcuts by window](16_shortcuts.md)
