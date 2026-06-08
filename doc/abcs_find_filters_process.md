# Find and Filters Process

## What this is

These tools help you narrow and organize the main book list without changing your data. You can search for text, limit by collection, filter by read status or plot, and change sort order.

## When to use it

- Looking for a specific author, title, series, or genre.
- Viewing only read or unread books.
- Showing only books that have (or lack) a plot synopsis.
- Sorting the list by year, length, read date, or other columns.

## Before you start

- Filters combine: collection + plot + read + find text can all be active at once.
- During **duplicate mode**, filters are cleared and restored when you exit. See [Duplicate Mode](abcs_duplicate_mode_process.md).

## Steps — Find (search)

1. Open **View → Find**, or press **Ctrl+F**.
2. Choose a **field** to search (**Alt+I**): Author, Title, Series, or Genre. If your focus is on Author, Title, Series, or Genre in the book table, that field is pre-selected. From Year, Time, Read Date, or elsewhere, the last search field is used.
3. Type your search text.
4. Optionally check **Exact match** (**Alt+X**) for a strict comparison. When unchecked, keyword search is used (more flexible).
5. Press **Enter** to run the search. The Find dialog closes and the main list updates.
6. The filter summary shows your search (for example, "Find: Christie").
7. If nothing matches, a message reports no results.

## Steps — Collection filter

1. Open **View → Collections** (**Alt+V**, then **C**).
2. Choose a collection name or **All Collections**.
3. Only books in that collection appear in the list.

## Steps — Plot filter

1. Open **View → Plot** (**Alt+V**, then **P**), or press **Alt+P** to toggle the plot filter.
2. Choose **All**, **With Plot**, or **Without Plot**.
3. Books are filtered by whether they have plot text in comments.

## Steps — Read filter

1. Open **View → Read** (**Alt+V**, then **R**), or press **Alt+R** to toggle the read filter.
2. Choose **All**, **Read**, or **Unread**.
3. The list shows only books matching that read status.

## Steps — Sort

1. Open the **Sort** menu on the menu bar (**Alt+S**).
2. Choose a sort field: **A** Author, **T** Title, **Y** Year, **S** Series, **G** Genre, **M** Time, or **D** Read Date.
3. Use **Alt+1** through **Alt+7** to jump to a column, then click the same column header in the book table to reverse ascending/descending order.
4. The filter summary shows the current sort (for example, "Sort: Title (ascending)").

## Clearing filters

- Press **Escape** on the main window to step through clearing in this order:
  1. Clear row selection (if any books are selected).
  2. Clear the Find search (if active). Focus returns to the book you were on before searching.
  3. Clear read filter (if not All).
  4. Further Escape presses continue clearing filters as applicable.

## What happens next

- The book table shows only rows matching all active filters.
- The status or filter summary area lists active filters and the book count.
- Sort order affects Book Details Next/Previous navigation. See [Update and New Book](abcs_update_new_book_process.md).

## Settings that affect this

- **Exact match** in the Find dialog is remembered for your next search session.

## Shortcuts and accessibility

| Shortcut | Action |
|----------|--------|
| Ctrl+F | Open Find dialog |
| Alt+V, C | View → Collections filter |
| Alt+V, P | View → Plot filter |
| Alt+P | Toggle plot filter |
| Alt+V, R | View → Read filter |
| Alt+R | Toggle read filter |
| Alt+S | Sort menu |
| Alt+1–Alt+7 | Jump to table columns |
| Alt+/ | Re-read filter summary and status |
| Escape | Clear selection, then search, then other filters (step by step) |
| F1 | Help for main window |

Find dialog shortcuts (while open):

| Shortcut | Action |
|----------|--------|
| Alt+I | Find field combo |
| Alt+T | Find text (when Title field selected) |
| Alt+X | Exact match checkbox |
| Alt+/ | Re-read Find dialog status |
| Enter | Run search |

## Verification

Manual QA for this workflow is complete. See [QA verification](qa_verification.md).

## Common confusion

**Find vs filters — what is the difference?**
Find searches text in a specific field. Collection, Plot, and Read filters limit the list by category without typing search text. All can be used together.

**Why did Escape not clear everything at once?**
Escape works in steps: selection first, then search, then other filters. This lets you undo one layer at a time.

**Does sorting remove filters?**
No. Sort only changes the order of books that already match your filters.
