# Update Process

## What this is

The **Update** window lets you change one or more fields on books you have already selected in the main table. Leave a field blank to keep the existing value for that field. For **Series** and **Genre**, choose **None** in the dropdown to clear that field on every selected book (no series or no genre).

For editing a single book with full fields and navigation, use [Book Details](04_book_details.md) instead.

## When to use it

- You need to change the same field on several selected books at once.
- You want a quick bulk edit without opening each book separately.

## Before you start

- Select one or more books in the main table (**click** a row; **Ctrl+click** to add rows; **Shift+click** for a range; or press **Space** on each row with the keyboard).
- **Update** is not available during duplicate mode.

## Update selected books

1. In the main window, select one or more books (click rows, or use **Space** on each row).
2. Click **Update** on the toolbar, open **Edit → Update**, or press **Alt+U**.
3. The **Update** window opens showing fields you can change.
4. Enter new values only in the fields you want to change. Leave fields blank to keep existing values.
5. To **clear Series or Genre** on all selected books, open the **Series** (**Alt+S**) or **Genre** (**Alt+G**) dropdown and choose **None**. Do not type the word None unless you are adding a literal series or genre with that name.
6. Click **Save** (**Ctrl+S**) to apply your changes.
7. Selection clears and the main list refreshes. Focus returns to the first selected book in list order.

## New Book

New books use the Book Details window. Open **File → New Book** or press **Ctrl+N**. See [Book Details](04_book_details.md).

## What happens next

- Saved changes appear immediately in the main book list.
- If filters hide an updated book, AbCS may clear filters so you are not left with an empty list.

## Mouse, shortcuts, and accessibility

- Click **Update** on the main toolbar or choose **Edit → Update** after selecting books.
- In the Update window, fill only the fields you want to change, then click **Save**.

### Main window

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Book |
| Alt+U | Update selected |
| Ctrl+U | Update selected |
| Ctrl+S | Save (Update window) |
| Space | Select/deselect row |
| Alt+C | Cancel selection |
| Enter | Open Book Details (title column) |

### Update window

| Shortcut | Action |
|----------|--------|
| Shift+F1 | Help for this window |
| F1 | Keyboard shortcuts |
| Alt+/ | Re-read status |
| Alt+S | Series field |
| Alt+G | Genre field |
| Ctrl+S | Save |
| Escape | Close |

## Common confusion

**Update vs Book Details — which should I use?**
Use **Book Details** to work on one book with full fields and navigation. Use **Update** when you want to change the same field on several selected books at once.

**Why did my selection clear after Update?**
This is normal. Update clears selection after a successful save so you can continue browsing.

**How do I clear series or genre on selected books?**
Choose **None** in the **Series** or **Genre** dropdown. A blank dropdown means “do not change this field.” **None** removes the series or genre from each selected book. Collection has no **None** option because every book must belong to a collection.
