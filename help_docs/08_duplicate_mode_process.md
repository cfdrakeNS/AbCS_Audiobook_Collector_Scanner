# Duplicate Mode Process

## What this is

Duplicate Mode is a library cleanup tool. It scans all books already in your database, finds groups that match on the same title, author, year, or collection (depending on the rule you choose), and shows only those books so you can review, delete, or export them.

This is **not** the same as duplicate detection during Import. Import uses fuzzy matching to block new books that look similar. Duplicate Mode uses exact key matching on books already stored.

## When to use it

- You suspect the same book was added more than once.
- You want to review and remove duplicate entries after importing from multiple sources.

## Before you start

- You do not need to select books first. The scan covers your entire library.
- The default match type comes from **Preferences → Validation Rules → Duplicate Match**. You can change it in the duplicate check dialog.

## Steps

1. Open **Manage → Duplicate Check** (**Alt+M**, then **D**).
2. A dialog asks which **match type** to use (**Alt+M** to focus the match type combo):
   - Title + Author + Year + Collection
   - Title + Author + Year
   - Title + Author + Collection
   - Title + Author only
3. Click **Start** (**Alt+R**) to run the scan, or **Cancel** (**Alt+L**) to close without changes.
4. **If no duplicates are found:** an information message appears and you stay in the normal book list.
5. **If duplicates are found:**
   - Duplicate mode activates.
   - Your current filters (collection, read, plot, find) are saved and cleared so every duplicate is visible.
   - The book table shows **only** duplicate books.
   - The status area reports how many duplicates were found and which match type was used.
   - Focus moves to the first book in the list.
6. While duplicate mode is active:
   - **Delete** (Alt+D) — select one or more rows and delete them.
   - **Export Duplicates** (Alt+X) — save a CSV with Author, Title, Year, Time, Collection, and Date Added.
   - **Update** and **Fetch Web Info** are disabled.
7. After deleting, the duplicate list refreshes. If no duplicates remain, duplicate mode exits automatically with a completion message.
8. To exit manually, press **Escape**. If rows are selected, Escape clears the selection first; press Escape again to confirm exit.
9. When duplicate mode ends, your previous filters are restored and the full book list returns.

## What happens next

- Deleted books are removed from the database.
- Starting **Import** or **Import Book List** also exits duplicate mode automatically before those windows open.

## Settings that affect this

- **Duplicate Match** in Preferences sets the default match type shown in the duplicate check dialog.
- **Fuzzy Duplicate percent** applies to **Import only**, not to Duplicate Mode. Library duplicate check uses exact matching on the fields in your chosen rule.

## Shortcuts and accessibility

| Alt+M, D | Open Duplicate Check (Manage menu) |

Duplicate Check dialog (steps 1–3):

| Shortcut | Action |
|----------|--------|
| Alt+M | Focus match type combo |
| Alt+R | Start duplicate check |
| Alt+L | Cancel duplicate check |

Main window (while duplicate mode is active):

| Shortcut | Action |
|----------|--------|
| Alt+D | Delete selected |
| Alt+X | Export duplicates to CSV |
| Escape | Clear selection, then confirm exit from duplicate mode |
| F1 | Help for main window |
| Alt+/ | Re-read status |
## Common confusion

**Duplicate Mode vs Import duplicates — what is the difference?**

| | Import duplicates | Duplicate Mode |
|--|-------------------|----------------|
| When | While adding new books | Any time, on existing library |
| Matching | Can use fuzzy percent | Exact key match only |
| Result | Book held in review list | Table filtered to duplicates |

**Why did my filters disappear?**
Duplicate mode clears filters so you can see all duplicate books across collections. Filters return when you exit.

**How do I cancel duplicate mode?**
Press Escape (confirm when asked), or delete all duplicates so mode ends on its own. Starting Import also cancels it.
