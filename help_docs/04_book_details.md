# Book Details Process

## What this is

The **Book Details** window lets you view or edit one book at a time. You can move to the next or previous book in the current main-window list order.

Use **New Book** (File → New Book or **Ctrl+N**) to open Book Details with empty fields for a manual entry.

## When to use it

- You want to review or fix metadata for a single book.
- You need to browse books one at a time in list order.
- You want to add a book without audio files (New Book).
- You want to fetch web metadata for the current book.
- You want to play the book inside AbCS without leaving the app.

## Before you start

- For an existing book, focus it in the main table first.
- For **New Book**, a collection should exist. The new book uses the collection filter shown on the main window when possible.
- Sort order on the main window affects Next/Previous order in Book Details.

## View or edit one book

1. In the main window, click the book row you want, or move to it with the keyboard.
2. Double-click the **Title** column, open **View → Open Focused Item**, or press **Enter** when the title column is focused.
3. The **Book Details** window shows all fields for that book. Without a screen reader, a panel at the top shows the title, author, and series in larger text. With JAWS or NVDA, that panel is hidden and never spoken. The picture is on the right. Title, author, series, genre, and plot are on the left. Year, time, listen progress, files, format, and bitrate sit under the picture. Other fields are one row each below that. Tab follows that order and stops on the picture. The picture says Book cover when the audio file has one, and No cover when it shows the stand-in picture.
4. Press **Edit** (**Alt+E**) to edit. To fix a missing or moved location, use **Browse** (**Alt+B**) beside **Path**, or type the path. If the stored path is gone, Browse starts under the collection library root or the Preferences import folder. Browse does not change the collection library root; set that in Collections. **Listen** is hidden while editing. Save (**Ctrl+S**) or press Escape before listening.
5. To play the book inside AbCS, open **Listen** from Book Details or use **Ctrl+L** on the main window. See [Listen to a book](26_listen_to_a_book.md) for player controls and resume behavior. If the Path is blank or gone, Listen looks in the collection library root folder and saves the path it finds. If nothing is found, Listen offers Browse and shows the saved path in **Path**. Book Details **Listen progress** shows stop time and, when Time is set, the percent of the book completed. It does not show the file name. To clear a saved place, use **Clear** beside **Listen progress**, or main window **Edit → Clear listening position** for the selection. Setting a read date also clears listening position and Want to read.
6. Click **Next** and **Previous** at the bottom of the window, or use Page Down / Page Up.
7. Press **Escape** to close. The main list refreshes.

## New Book

1. Open **File → New Book**, or press **Ctrl+N**.
2. Book Details opens with empty fields.
3. Fill in Title, Author, Collection, and any other fields.
4. Click **Save** (**Ctrl+S**).
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
| Alt+S | Series. Tab moves to Series number |
| Alt+N | Narrator |
| Alt+R | Read date |
| Alt+E | Edit |
| Ctrl+S | Save |
| Ctrl+N | New book |
| Alt+D | Delete book |
| Alt+W | Get web info |
| Ctrl+L | Listen inside AbCS |
| Page Up / Page Down | Previous / next book in list order |
| Shift+F1 | Help for this window |
| F1 | Keyboard shortcuts |
| Alt+/ | Re-read status |
| Escape | Close |

Series number is a text box. Type a number such as 3 or 6.5, or leave it blank. Saving stores Series number only. The title is not changed. The main book table shows ` - 03` or ` - 6.5` after the title when Series number is set.

With a screen reader running, **Year** and **Read** are typed text fields (four-digit year, and date as year-month-day). Leave a field blank for no year or no read date. Invalid values show a warning message. Without a screen reader, use the calendar for Read; click **Clear** beside the date to remove a read date (you will be asked to confirm).

## Common confusion

**Book Details vs Update — which should I use?**
Use **Book Details** for one book with full fields and navigation. Use **Update** when you want to change the Series, Genre or Collection on several selected books at once.


**Can I delete a book from Book Details?**
Yes. Press **Delete** while in Book Details to remove the current book.
