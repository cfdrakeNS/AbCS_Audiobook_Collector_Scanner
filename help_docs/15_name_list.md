# Name List

## What this is

The Name List window manages the **author**, **genre**, and **series** names in your library. You can find names, rename them, and merge two names into one.

## When to use it

- To fix the spelling of an author, series, or genre everywhere it is used.
- To merge two names for the same author, for example "Dorothy Sayers" and "Dorothy L. Sayers".
- To see how many books use each name.

## Before you start

- Open it from the main window by double-clicking an **Author**, **Series**, or **Genre** cell, or by focusing that cell and pressing **Enter**.
- Or open **Manage → Authors**, **Manage → Genre**, or **Manage → Series**.
- A rename changes every book that uses that name.

## Window layout

- **Top row:** **Find** field, and the name field labeled **Author**, **Series**, or **Genre**. The name field is grayed out until you press Edit.
- **Sort** dropdown: Name or Book count.
- **Name list:** columns for the name and **Books** (the number of books that use it).
- **Footer:** status bar, then the **Edit** button. While editing, **Save** replaces Edit.

Tab order: Find, Sort, the name list, the name field (while editing), then Edit or Save.

## Find and sort names

1. Type in **Find** to narrow the list. **Ctrl+F** clears Find and starts a new search.
2. Press **Escape** in Find to clear the text and return to the list.
3. Choose a sort in **Sort** (**Alt+S**). Press **Alt+Down Arrow** to open the list; plain Up and Down Arrow leave the sort as it is.
4. You can also click the name or **Books** column header to sort. Click it again to reverse the order.
5. After sorting, focus moves to the first row and AbCS announces the new order.

## Rename or merge a name

1. Select a row: click it, press **Tab** from Find, or press **Alt+L**.
2. Press **Edit** (**Alt+E**), or double-click the row.
3. Type the new name in the name field.
4. Press **Save** (**Ctrl+S**).
5. If the new name already exists, AbCS asks whether to move this name's books to the existing name. **Yes** moves the books, removes the old name, and reports how many books changed. **No** keeps both names as they were.
6. Press **Escape** while editing to stop. With no changes, you return to the list. With changes, AbCS asks whether to save, keep editing, or discard.
7. Press **Escape** in the list to close the window.

## Clear series or genre on books

To remove the series or genre from some books, use the Update window:

1. Select those books on the main table.
2. Open **Edit → Update** (**Alt+U**).
3. In **Series** or **Genre**, choose **None**.

See [Update](05_update.md).

## Mouse, shortcuts, and accessibility

- Double-click an Author, Series, or Genre cell on the main book table to open the list for that category.
- Click a row, then **Edit**; change the text and click **Save**.
- Right-click a row or press the Menu key and choose **Copy**, or press **Ctrl+C**, to copy the selected name.

| Shortcut | Action |
|----------|--------|
| Alt+E | Edit selected row |
| Alt+L | Jump to list |
| Ctrl+C | Copy selected name |
| Ctrl+F | Clear find and start a new search |
| Ctrl+S | Save (while editing) |
| Alt+S | Sort |
| Alt+Down | Open Sort dropdown (when Sort has focus) |
| Escape | Return to list from Find, cancel edit, or close window |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Name List or Collections — which window?**
Use this window for author, genre, and series **names**. Use **Manage → Collections** for collections. See [Collections](06_collections.md).

**How do I remove the series or genre from a book?**
Use [Update](05_update.md) and choose **None** in Series or Genre. Name List renames or merges names; each book keeps a name.

## Related help

- Main window: [Find and Filters (Main Window)](03_find_filters.md)
- Collections: [Collections](06_collections.md)
- Several books at once: [Update](05_update.md)
- One book: [Book Details](04_book_details.md)
