# Update and New Book Process

## What this is

These workflows let you add or change book information by hand, without scanning files or spreadsheets.

- **New Book** — create a blank record and fill in the details.
- **Update** — change one or more fields on books you have already selected.
- **Book Details** — view or edit a single book, and move to the next or previous book in the list.

Import (folder scan or spreadsheet) fills in books automatically. Use these processes when you need to correct or enter metadata yourself.

## When to use it

- A book is missing a year, series, or plot after import.
- You want to add a book you do not have audio files for.
- You need to change the same field on several books at once (Update).
- You want to browse through books one at a time (Book Details).

## Before you start

- For **Update**, select one or more books in the main table first (Space toggles selection).
- **Update** is not available during duplicate mode.
- For **New Book**, a collection should exist. The new book uses the collection filter shown on the main window when possible.

## Steps — New Book

1. Open **File → New Book**, or press **Ctrl+N**.
2. The **Book Details** window opens with empty fields.
3. Fill in Title, Author, Collection, and any other fields.
4. Click **Save** (Alt+V) or use the save action for this window.
5. Close Book Details with **Escape** or the close action.
6. The main list refreshes and focus moves to the new book if it was saved.

## Steps — Update selected books

1. In the main window, select one or more books using **Space** on each row.
2. Click **Update** (Alt+U) or open **Edit → Update**.
3. The **Update** window opens showing fields you can change.
4. Enter new values only in the fields you want to change. Leave fields blank to keep existing values.
5. Save your changes.
6. Selection clears and the main list refreshes. Focus returns to the first updated row.

## Steps — Book Details (view or edit one book)

1. In the main window, move to the book you want.
2. Open **View → Open Focused Item**, or press **Enter** when the title column is focused.
3. The **Book Details** window shows all fields for that book.
4. Edit any field and **Save** (Alt+V).
5. Use **Next** (Alt+N or Page Down) and **Previous** (Alt+P or Page Up) to move between books in the current list order.
6. Press **Escape** to close. The main list refreshes.

You can also open Book Details from the title column with Enter, and use **Fetch Web Info** (Alt+W) from within Book Details. See [Web Metadata Fetch](abcs_web_metadata_fetch_process.md).

## What happens next

- Saved changes appear immediately in the main book list.
- If filters hide the updated book, AbCS may clear filters so you are not left with an empty list.
- New books appear in the collection you assigned.

## Settings that affect this

None directly. Sort order on the main window affects the order of Next/Previous in Book Details.

## Shortcuts and accessibility

### Main window

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Book |
| Alt+U | Update selected |
| Ctrl+U | Update selected |
| Space | Select/deselect row |
| Alt+C | Cancel selection |
| Enter | Open Book Details (title column) |

### Book Details

| Shortcut | Action |
|----------|--------|
| Alt+T, Alt+A, Alt+Y, etc. | Jump to field |
| Alt+V | Save |
| Alt+N | Next book |
| Alt+P | Previous book |
| Alt+W | Fetch Web Info |
| Insert | New book (from Book Details) |
| Delete | Delete current book |
| F1 | Help |
| Alt+/ | Re-read status |
| Escape | Close |

## Things to test

- [ ] Create a new book with title and author only — confirm it appears in the list.
- [ ] Update a single field on one book — confirm only that field changes.
- [ ] Select multiple books and update one shared field (for example, genre).
- [ ] Open Book Details, edit, save, and confirm main list updates.
- [ ] Navigate Next/Previous in Book Details — confirm order matches main list sort.
- [ ] Cancel Book Details without saving — confirm no changes.
- [ ] Try Update during duplicate mode — confirm it is blocked.
- [ ] After update, confirm focus returns to a sensible row.
- [ ] Press Alt+/ after save operations.

## Common confusion

**Update vs Book Details — which should I use?**
Use **Book Details** to work on one book with full fields and navigation. Use **Update** when you want to change the same field on several selected books at once.

**Why did my selection clear after Update?**
This is normal. Update clears selection after a successful save so you can continue browsing.

**Can I delete a book from Book Details?**
Yes. Press **Delete** while in Book Details to remove the current book.
