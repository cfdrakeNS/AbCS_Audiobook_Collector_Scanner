# Name List Process

## What this is

The Name List window manages **authors**, **genres**, and **series** names in your library database. You can find names in the list, rename entries, and merge duplicates when you save a name that already exists.

## When to use it

- Open from the main window by double-clicking an **Author**, **Series**, or **Genre** cell, or by focusing a cell and pressing **Enter**.
- Or open **Manage → Authors**, **Manage → Genre**, or **Manage → Series**.

## Before you start

- Changes may affect how books are grouped or filtered in the main list.
- Click **Save** when the **Save** button is visible and your edits are ready.

## Manage names

1. Open the name list from the main book table (double-click a name cell, or focus a cell and press **Enter**), or from the Manage menu.
2. Use **Sort** (dropdown above the list) or click the **Name** or **Books** column header to sort by name or book count. Click the same header again to reverse the order.
3. Click a row in the list, press **Tab** from **Find** onto the list, or press **Alt+L** to move focus to the list.
4. Click **Edit**, double-click a row, or press **Alt+E** to edit the selected entry.
5. Type in the name field and click **Save** (**Ctrl+S** when Save is available).
6. If the author, series, or genre name already exists, AbCS asks whether to move this name’s books to the existing name. **No** leaves both names unchanged. **Yes** moves the books, removes the edited name, and reports how many books changed.
7. Press **Escape** while editing. If nothing changed, you return to the locked list. If you changed the name, choose whether to save, keep editing, or discard and return to the list. When the list is locked, **Escape** closes the window. In **Find**, **Escape** clears the text if needed and returns to the list instead of closing.

## Clear series or genre on books

This window does **not** remove series or genre from individual books.

To clear **Series** or **Genre** on one or more **books** (so the book has no series or no genre):

1. Select those books on the main table.
2. Open **Edit → Update** (**Alt+U**).
3. Open the **Series** or **Genre** dropdown and choose **None** (blank means leave that field unchanged on each book).
4. Click **Save**.

See [Update](05_update.md) for bulk edits.

## Mouse, shortcuts, and accessibility

- Double-click an Author, Series, or Genre cell on the main book table to open the list for that category.
- Click a row, then **Edit**; change the text and click **Save**.
- Right-click a row (or press the Menu key) and choose **Copy**, or press **Ctrl+C**, to copy the selected name.

| Shortcut | Action |
|----------|--------|
| Shift+F1 | Open this help document |
| F1 | Show keyboard shortcuts for this window |
| Alt+L | Focus name list |
| Ctrl+C | Copy selected name |
| Alt+M | Edit name field |
| Alt+E | Edit selected row |
| Ctrl+F | Clear find and start a new search |
| Ctrl+S | Save (when editing) |
| Alt+/ | Re-read the status bar |
| Escape | In Find, return to the list. Otherwise cancel edit or close window |

## Common confusion

**Name list vs Collections — which window?**
Use this window for author, genre, and series **names**. Use **Manage → Collections** and [Collections](06_collections.md) for virtual libraries (Active, collection folder on disk, and so on).

**How do I remove series or genre from a book?**
Use [Update](05_update.md) and set **Series** or **Genre** to **None**. Renaming or deleting a name in this window does not automatically clear that field on every book unless you merge names as described above.

## Related guides

- [Find and Filters](03_find_filters.md) — main book list search and filters
- [Collections](06_collections.md) — collection management (separate window)
- [Update](05_update.md) — bulk changes including **None** to clear series or genre
- [Book Details](04_book_details.md) — edit one book at a time
