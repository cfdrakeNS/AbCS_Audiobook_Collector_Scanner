# Find and Filters Process

## What this is

These tools help you narrow and organize the main book list without changing your data. You can search for text, limit by collection, filter by read status or plot, show recently added books, and change sort order.

## When to use it

- Looking for a specific author, title, series, or genre.
- Viewing only read or unread books.
- Showing only books that have (or lack) a plot synopsis.
- Reviewing books you imported or added recently (default view: last **2 months**).
- Sorting the list by year, length, read date, or other columns.

## Before you start

- Filters combine: collection + plot + read + recently added + find text can all be active at once.
- During **duplicate mode**, filters are cleared and restored when you exit. See [Duplicate Mode](08_duplicate_mode.md).

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

## Steps — Recently added filter

1. Open **View → Recently Added...** (**Alt+V**, then **A**), or activate the **Recently Added Filter** toolbar button to the right of Read Filter.
2. The date field defaults to **2 months ago** from today. Change it if needed (calendar popup on the date field).
3. Press **Enter** to apply. The list shows books added on or after that date.
4. The filter summary shows **Added since:** with the date you chose.

This filter uses **date added** (when the book was imported or created in AbCS), not read date.

## Steps — Sort

1. Open the **Sort** menu on the menu bar (**Alt+S**).
2. Choose a sort field: **A** Author, **T** Title, **Y** Year, **S** Series, **G** Genre, **M** Time, or **D** Read Date.
3. Use **Tab** to move through table cells, or click a column header to sort by that column; click the same header again to reverse ascending/descending order.
4. The filter summary shows the current sort (for example, "Sort: Title (ascending)").

## Clearing filters

Press **Escape** on the main window to remove **one layer** at a time. Escape always uses this **fixed order** — not the order you turned filters on.

Each press clears the first active step below and stops until you press Escape again:

1. **Row selection** — if any books are selected.
2. **Find search** — if active. Focus returns to the book you were on before searching.
3. **Plot filter** — if not All.
4. **Read filter** — if set to Read or Unread (not All).
5. **Recently added filter** — if active.

After step 5, further Escape presses on the main window do **not** clear any more filters.

**Not cleared by Escape**

- **Collection filter** — choose **All Collections** in **View → Collections** to remove it.
- **Sort order** — choose a different sort from the **Sort** menu; sort is not a filter Escape clears.

**Toolbar toggles:** You can also clear Find, Plot, or Read by clicking their toolbar buttons again while highlighted. Recently added clears when you press Escape at step 5, or set a new date from the toolbar or **View → Recently Added...**.

## What happens next

- The book table shows only rows matching all active filters.
- The status or filter summary area lists active filters and the book count.
- Sort order affects Book Details Next/Previous navigation. See [Book Details](04_book_details.md).

## Settings that affect this

- **Exact match** in the Find dialog is remembered for your next search session.

## Mouse, shortcuts, and accessibility

- Use **View** menu items or the main toolbar buttons for **Plot**, **Read**, and **Recently Added** filters — click a highlighted toolbar button again to turn that filter off.
- In the Find dialog, click the field dropdown, type in the search box, and click **OK** or press **Enter**.
- On the Recently Added filter, click the date field to open the calendar popup and pick a date.

| Shortcut | Action |
|----------|--------|
| Ctrl+F | Open Find dialog |
| Alt+V, C | View → Collections filter |
| Alt+V, P | View → Plot filter |
| Alt+P | Toggle plot filter |
| Alt+V, R | View → Read filter |
| Alt+V, A | View → Recently Added filter (toolbar button after Read Filter) |
| Alt+R | Toggle read filter |
| Alt+S | Sort menu |
| Alt+1–Alt+7 | Jump to table columns |
| Alt+/ | Re-read filter summary and status |
| Escape | Clear selection, then Find, Plot, Read, Recently added (fixed order, one step per press) |
| F1 | Help for main window |

Find dialog shortcuts (while open):

| Shortcut | Action |
|----------|--------|
| Alt+I | Find field combo |
| Alt+T | Find text (when Title field selected) |
| Alt+X | Exact match checkbox |
| Alt+/ | Re-read Find dialog status |
| Enter | Run search |

## Common confusion

**Find vs filters — what is the difference?**
Find searches text in a specific field. Collection, Plot, Read, and Recently Added filters limit the list by category without typing search text. All can be used together.

**Recently added vs read date — what is the difference?**
Recently added uses **date added** (when the book entered your collection), not read date. The dialog opens with a default of **2 months ago**; you can pick an earlier or later date. A book you read years ago but imported yesterday appears in recently added, not in read-date history unless you set its read date.

**Why did Escape not clear everything at once?**
Escape removes one layer per press so you can undo a single change without losing all your filters.

**Does Escape clear filters in the order I set them?**
No. Escape always follows the fixed order above (selection, then Find, Plot, Read, recently added). If you set Read and then Plot, Escape still clears Find first if it is active, then Plot, then Read — not Read first because you set it earlier.

**Why is my collection filter still on after Escape?**
Collection and sort are not part of the Escape sequence. Change collection in **View → Collections** or sort in the **Sort** menu.

**Does sorting remove filters?**
No. Sort only changes the order of books that already match your filters.
