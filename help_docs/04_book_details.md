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

## Steps — view or edit one book

1. In the main window, click the book row you want, or move to it with the keyboard.
2. Double-click the **Title** column, open **View → Open Focused Item**, or press **Enter** when the title column is focused.
3. The **Book Details** window shows all fields for that book. When no screen reader is running, a panel at the top also shows the book title, author, and series in larger text; with JAWS or NVDA running this panel is hidden and never spoken. The picture is on the right. Title, author, series, genre, and plot are on the left. Year, time, listen progress, files, format, and bitrate sit under the picture. The other fields are one row each below that. Tab follows that order and stops on the picture. The picture says Book cover when the audio file has one, and No cover when it shows the stand-in picture.
4. Edit any field and **Save** (**Alt+S**).
5. Click **Preview** or press **Alt+Shift+P** to play the book inside AbCS. The Preview window has **Play/Pause** on the left and Title, Author, Series, and Length on the right. If that file has a picture inside it, the picture shows beside those lines and is skipped when you press Tab. Enter plays or pauses. Escape closes Preview and stops playback. F1 lists Preview shortcuts. Preview is not available while books are selected on the main list. Duplicate mode still allows Preview of the focused book. When the collection has a library root, Preview uses that folder plus the author and title folders from the stored path, so a portable drive can move. For a folder of tracks, AbCS starts the first audio file by file name. Filename order may not match listening order (for example chapter 10 before chapter 2). If the file is gone, status says **Book not found in -** and that path. The same action is on the main window **Edit → Preview** and the **Preview** toolbar button after Find.
6. Click **Next** and **Previous** at the bottom of the window, or use Page Down / Page Up.
7. Press **Escape** to close. The main list refreshes.

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
| Alt+I | Series. Tab moves to Series number |
| Alt+S | Save |
| Alt+N | Next book |
| Alt+P | Previous book |
| Alt+W | Fetch Web Info |
| Alt+Shift+P | Preview inside AbCS |
| Enter | Play or pause (Preview window) |
| Escape | Close Preview and stop playback |
| F1 | Preview keyboard shortcuts |
| Shift+F1 | From Preview: help for the window that opened it |
| Insert | New book (from Book Details) |
| Delete | Delete current book |
| Shift+F1 | Help for this window |
| F1 | Keyboard shortcuts |
| Alt+/ | Re-read status |
| Escape | Close |

Series number is a text box. Type a number such as 3 or 6.5, or leave it blank. Saving stores Series number only. The title is not changed. Opening a book does not copy a number from the title into Series number. The main book table shows ` - 03` or ` - 6.5` after the title when Series number is set.

With a screen reader running, **Year** and **Read** are typed text fields (four-digit year, and date as year-month-day). Leave a field blank for no year or no read date. Invalid values show a warning message. Without a screen reader, use the calendar for Read; click **Clear** beside the date to remove a read date (you will be asked to confirm).

## Common confusion

**Book Details vs Update — which should I use?**
Use **Book Details** for one book with full fields and navigation. Use **Update** when you want to change the same field on several selected books at once.

**Can I delete a book from Book Details?**
Yes. Press **Delete** while in Book Details to remove the current book.
