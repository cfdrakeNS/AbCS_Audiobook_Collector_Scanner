# Find and Filters (Main Window)

## What this is

The main window lists the books in your library. Find, filters, and sort narrow and order that list without changing your data. You can search for text, limit by collection, filter by read status, plot, want to read, or listening progress, show recently added books, and change the sort order.

## When to use it

- Looking for a specific author, title, series, or genre.
- Viewing only read or unread books.
- Viewing only books that have, or lack, a plot synopsis.
- Viewing only books marked Want to read.
- Viewing only books with listening in progress.
- Reviewing books you imported or added recently (default view: the last **2 months**).
- Sorting the list by year, length, read date, or other columns.

## Before you start

- Filters combine: collection, plot, read, in progress, want to read, recently added, and Find text can all be active at once.
- During **duplicate mode**, filters are cleared, and they come back when you exit. See [Duplicate Mode](08_duplicate_mode.md).

## Window layout

From top to bottom:

- **Menu bar:** File, Edit, View, Sort, Manage, and Help.
- **Toolbar:** Add Book, Find, Listen, Plot Filter, Read Filter, In Progress Filter, Want to Read Filter, Recently Added Filter, Search Web, Statistics, Preferences, and Help. A filter button stays highlighted while its filter is on.
- **Filter summary:** one line that lists the active collection, filters, and sort.
- **Book table:** columns Author, Title, Year, Series, Genre, Time, and Read.
- **Footer buttons:** shown only when they apply. With books selected: **Update**, **Add to want to read**, **Clear want to read**, **Clear listening position**, and **Delete**. With two or more books selected, **Web fetch** also appears. In duplicate mode: **Delete** and **Export Duplicates**.
- **Status bar** at the bottom.

When AbCS opens, focus is on the first title in the book table. **Tab** leaves the table; use the arrow keys to move between cells.

The Title column shows a mark before the title. A circle means the book has a plot. A square means want to read. A triangle means listening is in progress. A screen reader speaks those words after the title, for example "The Moonstone, plot, want to read, in progress".

## Find (search)

1. Open **View → Find**, or press **Ctrl+F**.
2. Choose a **field** to search (**Alt+I**): Author, Title, Series, or Genre. If your focus is on the Author, Title, Series, or Genre column, that field is pre-selected. From any other column, Title is pre-selected.
3. Type your search text.
4. Optionally check **Exact match** (**Alt+X**) for a strict comparison. When unchecked, keyword search is used, which is more flexible.
5. Press **Enter** to run the search. The Find dialog closes and the main list updates.
6. The filter summary shows your search, for example "Find: Doyle".
7. If no book matches, a message says so.

## Collection filter

1. Open **View → Collections** (**Alt+V**, then **C**).
2. Choose a collection name or **All Collections**.
3. Only books in that collection appear in the list.

## Plot filter

1. Open **View → Plot** (**Alt+V**, then **P**), or press **Alt+P** to toggle the plot filter.
2. Choose **All**, **With Plot**, or **Without Plot**.
3. Books are filtered by whether they have plot text in comments.

## Read filter

1. Open **View → Read** (**Alt+V**, then **R**), or press **Alt+R** to toggle the read filter.
2. Choose **All**, **Read**, or **Unread**.
3. The list shows only books with that read status.

## Listening progress filter

1. Open **View → In progress** (**Alt+V**, then **G**), or press the **In Progress Filter** toolbar button.
2. Choose **All** or **In Progress**.
3. The list shows only books that have a saved listening place. The saved places stay when you turn the filter off.

## Want to read filter

1. Open **View → Want to read** (**Alt+V**, then **W**), or press **Alt+T** to toggle the filter.
2. Choose **All** or **Want to Read**.
3. The list shows only books marked want to read. The marks stay when you turn the filter off.

To mark a book, focus it and choose **Edit → Add to want to read**. With books selected, every selected book is marked. The mark is saved immediately. **Edit → Clear want to read** removes the mark from the selection. **Edit → Clear listening position** clears saved listening places for the selection and keeps the read status.

## Recently added filter

1. Open **View → Recently Added...** (**Alt+V**, then **A**), or press the **Recently Added Filter** toolbar button, the last filter button on the toolbar.
2. The date field starts at **2 months ago** from today. Change it if needed; the date field has a calendar popup.
3. Press **Enter** to apply. The list shows books added on or after that date.
4. The filter summary shows **Added since:** with the date you chose.

This filter uses the **date added**: the day the book was imported or created in AbCS.

## Sort

1. Open the **Sort** menu on the menu bar (**Alt+S**).
2. Choose a sort field: **A** Author, **T** Title, **Y** Year, **S** Series, **G** Genre, **M** Time, or **D** Read Date.
3. Or click a column header to sort by that column. Click the same header again to reverse the order.
4. The filter summary shows the current sort, for example "Sort: Title (ascending)".
5. The book that had focus stays the current book. If a filter hides it, focus moves to the first remaining book.

**Series** sorts by series name, series number, year, then title. Books without a series number come after numbered books in that series. A blank year comes before a filled year. The Title column shows ` - 03` or ` - 6.5` after the title when a series number is set. That text is for display; the stored title stays as typed.

## Set a read date

1. Move to the **Read** column of the book.
2. Press **Enter**, or double-click the cell.
3. Choose the date and confirm. Setting a read date also clears the listening position and Want to read for that book.

You can also set the read date in [Book Details](04_book_details.md).

## Select several books

1. Move to the first book you want.
2. Press **Shift+Down Arrow** to select books moving down the list, or **Shift+Up Arrow** to select books moving up.
3. With the mouse, click the first book, then **Shift+click** the last book. **Ctrl+click** adds or removes one book.
4. The status bar says how many books are selected and the title of the book you just added.
5. The footer shows the buttons for selected books. Press **Escape** to clear the selection.

While books are selected, Find, Import, Add Book, Listen, Statistics, Preferences, and the filters are turned off. Press **Escape** to clear the selection and turn them back on.

## Clear filters

Press **Escape** on the main window to remove **one layer** at a time. Escape always uses this fixed order:

1. **Row selection**, if any books are selected.
2. **Find search**, if active. Focus returns to the book you were on before searching.
3. **Plot filter**, if not All.
4. **Read filter**, if set to Read or Unread.
5. **In progress filter**, if it is on.
6. **Want to read filter**, if it is on.
7. **Recently added filter**, if active.

After step 7, Escape has no more filters to clear.

The **collection filter** and the **sort order** stay as they are. To change them, choose **All Collections** in **View → Collections**, or a different sort in the **Sort** menu.

You can also clear Find, Plot, Read, In progress, or Want to read by pressing its highlighted toolbar button again.

## Listen

Use **Edit → Listen**, the **Listen** toolbar button, or **Ctrl+L** to open the **Listen** window for the **focused** book. Clear any selection first. See [Listen to a book](26_listen_to_a_book.md) for player controls and resume behavior.

## Export the filtered list

To save the books currently shown to CSV or JSON, use **File → Export Library** (**Alt+F**, then **X**). The export follows the filters, search, sort, and any selection. See [Export Library](25_export_library.md).

## What happens next

- The book table shows only rows matching all active filters.
- The filter summary lists the active filters and sort.
- Sort order sets the Page Up and Page Down order in [Book Details](04_book_details.md).

## Mouse, shortcuts, and accessibility

- Use the **View** menu or the toolbar filter buttons. Click a highlighted toolbar button again to turn that filter off.
- In the Find dialog, choose the field, type in the search box, and click **OK** or press **Enter**.
- On the Recently Added filter, click the date field to open the calendar popup.
- On the book list, right-click a cell or press the Menu key and choose **Copy**, or press **Ctrl+C**, to copy that cell's text.

| Shortcut | Action |
|----------|--------|
| Alt+L | Jump to list |
| Alt+1 | Jump to Author |
| Alt+2 | Jump to Title |
| Alt+3 | Jump to Year |
| Alt+4 | Jump to Series |
| Alt+5 | Jump to Genre |
| Alt+6 | Jump to Time |
| Alt+7 | Jump to Read Date |
| Enter | Open focused item (Title: Book Details; Author, Series, Genre: name list; Read: set date) |
| Ctrl+F | Find |
| Ctrl+C | Copy focused cell |
| Alt+V, A | View, Recently Added filter |
| Alt+F, X | File, Export Library |
| Alt+M, L | Manage, Check Book Locations |
| Alt+M, T | Manage, Statistics |
| Alt+P | Toggle plot filter |
| Alt+R | Toggle read filter |
| Alt+T | Toggle want to read filter |
| Alt+W | Fetch web info (batch when two or more selected) |
| Ctrl+L | Listen to focused book inside AbCS |
| Ctrl+I | Import |
| Ctrl+Shift+I | Import book list |
| Ctrl+N | New book |
| Shift+Down/Up | Start selection or extend selection |
| Alt+U | Update selected |
| Alt+D | Delete selected (focused book in duplicate mode) |
| Delete | Delete selected (focused book in duplicate mode) |
| Alt+X | Export duplicates (in duplicate mode) |
| Escape | Clear selection, then Find, plot, read, in progress, want to read, and recently added filters one at a time; exit duplicate mode |
| Ctrl+Plus | Zoom in |
| Ctrl+Minus | Zoom out |
| Ctrl+0 | Reset zoom |
| Ctrl+Q | Quit |
| Alt+/ | Re-read filter summary and status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

Find dialog shortcuts:

| Shortcut | Action |
|----------|--------|
| Alt+I | Find field combo |
| Alt+T | Find text (when Title field selected) |
| Alt+X | Exact match checkbox |
| Enter | Run search |
| Alt+/ | Re-read Find dialog status |

## Common confusion

**Find or filters — what is the difference?**
Find searches text in one field. The collection, plot, read, in progress, want to read, and recently added filters limit the list by category. All of them can be used together.

**Recently added or read date — what is the difference?**
Recently added uses the date the book entered AbCS. A book you read years ago but imported yesterday appears in Recently added. Read date is the day you marked the book as read.

**Why did Escape clear only one filter?**
Escape removes one layer per press, so you can undo a single change and keep the rest.

**In what order does Escape clear filters?**
Always the fixed order in Clear filters: selection, Find, Plot, Read, In progress, Want to read, then Recently added. The order you turned them on does not matter.

**Why is my collection filter still on after Escape?**
Escape leaves the collection and sort alone. Change the collection in **View → Collections** and the sort in the **Sort** menu.

**What happens to my place in the list when I sort or filter?**
You stay on the book that had focus. If a filter hides that book, focus moves to the first remaining book.

## Related help

- One book at a time: [Book Details](04_book_details.md)
- Several books at once: [Update](05_update.md)
- Playing a book: [Listen to a book](26_listen_to_a_book.md)
- Saving the list to a file: [Export Library](25_export_library.md)
- Words such as selection, focused book, and filter summary: [Glossary](27_glossary.md)
