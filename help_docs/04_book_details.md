# Book Details Process

## What this is

The **Book Details** window lets you view or edit one book at a time. You can move to the next or previous book in the current main-window list order.

Use **New Book** (File → New Book or **Ctrl+N**) to open Book Details with empty fields for a manual entry.

## When to use it

- You want to review or fix metadata for a single book.
- You need to browse books one at a time in list order.
- You want to add a book without audio files (New Book).
- You want to fetch web metadata for the current book.

## Before you start

- For an existing book, focus it in the main table first.
- For **New Book**, a collection should exist. The new book uses the collection filter shown on the main window when possible.
- Sort order on the main window affects Next/Previous order in Book Details.

## Steps — view or edit one book

1. In the main window, click the book row you want, or move to it with the keyboard.
2. Double-click the **Title** column, open **View → Open Focused Item**, or press **Enter** when the title column is focused.
3. The **Book Details** window shows all fields for that book.
4. Edit any field and **Save** (**Alt+S**).
5. Click **Next** and **Previous** at the bottom of the window, or use **Alt+N** / **Alt+P** (or Page Down / Page Up).
6. Press **Escape** to close. The main list refreshes.

## Steps — New Book

1. Open **File → New Book**, or press **Ctrl+N**.
2. Book Details opens with empty fields.
3. Fill in Title, Author, Collection, and any other fields.
4. Click **Save** (**Alt+S**).
5. Close with **Escape**. Focus moves to the new book if it was saved.

## What happens next

- Saved changes appear in the main book list.
- If filters hide the updated book, AbCS may clear filters so you are not left with an empty list.

## Related help

- Bulk changes on several selected books: see [Update](05_update.md).
- Online plot and series lookup: see [Web Metadata Fetch](07_web_metadata.md).

## Mouse, shortcuts, and accessibility

- Click any field to edit it; click **Save** when you are done.
- Use **Next** / **Previous** buttons to move through books in the current main-list order.
- From the main window, double-click a title or use **File → New Book** to open an empty Book Details form.

| Shortcut | Action |
|----------|--------|
| Alt+T, Alt+A, Alt+Y, etc. | Jump to field |
| Alt+S | Save |
| Alt+N | Next book |
| Alt+P | Previous book |
| Alt+W | Fetch Web Info |
| Insert | New book (from Book Details) |
| Delete | Delete current book |
| Shift+F1 | Help for this window |
| F1 | Keyboard shortcuts |
| Alt+/ | Re-read status |
| Escape | Close |

## Common confusion

**Book Details vs Update — which should I use?**
Use **Book Details** for one book with full fields and navigation. Use **Update** when you want to change the same field on several selected books at once.

**Can I delete a book from Book Details?**
Yes. Press **Delete** while in Book Details to remove the current book.
