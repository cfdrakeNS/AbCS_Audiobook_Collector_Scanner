# Book Details

## What this is

The **Book Details** window lets you view or edit one book at a time. Page Up and Page Down move to the previous or next book in the current main-window list order.

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
- Sort order on the main window sets the Page Up and Page Down order in Book Details.

## Window layout

- Without a screen reader, a panel at the top shows the title, author, and series in larger text. With a screen reader running, that panel is hidden and is not spoken.
- On the left: **Title**, **Author**, **Series**, **Series number**, **Genre**, and **Plot**.
- On the right: the cover picture. It says **Book cover** when the audio file has one, and **No cover** when it shows the stand-in picture.
- Under the picture: **Year**, **Time**, **Listen progress** with a **Clear** button, **Files**, **Format**, and **Bitrate**.
- Below that, one row each: **Narrator**, **Collection**, **Read** date, **Want to read** checkbox, **Size**, **Source**, **Added**, and **Path** with a **Browse** button. **Errors** appears only when the book has a location problem.
- Button row in view mode: **New**, **Edit**, **Delete**, **Fetch Web Info**, and **Listen**.
- Button row in edit mode, and for a new book: **Save** only.
- Status bar at the bottom.

Tab follows the order above and stops on the cover picture.

## View or edit one book

1. In the main window, click the book row you want, or move to it with the keyboard.
2. Double-click the **Title** column, open **View → Open Focused Item**, or press **Enter** when the Title column is focused.
3. Book Details opens in view mode and shows all fields for that book.
4. Press **Edit** (**Alt+E**) to change fields. The button row changes to **Save**.
5. To fix a missing or moved location, use **Browse** (**Alt+B**) beside **Path**, or type the path. If the stored path is gone, Browse starts under the collection folder or the Preferences import folder. Set the collection folder itself in Collections.
6. Press **Save** (**Ctrl+S**) to keep your changes.
7. Press **Escape** when you have changes. AbCS asks what to do. **Yes** saves and closes. **No** keeps Book Details open and returns to the last field you changed. Press **Escape** on that message to discard the changes and close.
8. Press **Page Down** for the next book or **Page Up** for the previous book.
9. With no unsaved changes, press **Escape** to close. The main list refreshes.

## Set or clear a read date

1. Move to **Read** (**Alt+R**), in view or edit mode.
2. Type or pick the date, or clear it.
3. When you leave the field, press Page Up or Page Down, or Save, AbCS asks "Mark this title as read on this date?" or "Clear the read date for this title?".
4. **Yes** saves the read date right away. **No** puts the old date back.

A read date you confirmed with **Yes** stays saved even if you then press **Escape** and discard your other changes.

## Listen and listening progress

1. In view mode, press **Listen** (**Ctrl+L**) to play the book inside AbCS. See [Listen to a book](26_listen_to_a_book.md) for player controls.
2. **Listen** is hidden in edit mode. Save or press **Escape** first.
3. If the Path is blank or gone, Listen looks in the collection folder and saves the path it finds. If the book is still not found, Listen offers Browse.
4. **Listen progress** shows the percent of the book completed. When Time is blank, the percent is estimated from the audio file you stopped in. It is blank when no place is saved.
5. To clear a saved place, press **Clear** beside **Listen progress**. On the main window, **Edit → Clear listening position** clears it for the selection.
6. Setting a read date also clears the listening position and Want to read.

## New Book

1. Open **File → New Book**, or press **Ctrl+N**.
2. Book Details opens with empty fields. The button row shows **Save**.
3. Fill in Title, Author, Collection, and any other fields.
4. Press **Save** (**Ctrl+S**).
5. Close with **Escape**. Focus moves to the new book if it was saved.

## What happens next

- Saved changes appear in the main book list.
- If filters hide the updated book, AbCS clears filters so the book stays in view.

## Mouse, shortcuts, and accessibility

- Click any field after pressing **Edit**; click **Save** when you are done.
- From the main window, double-click a title or use **File → New Book** to open Book Details.

| Shortcut | Action |
|----------|--------|
| Alt+T | Title |
| Alt+A | Author |
| Alt+S | Series |
| Alt+S, then Tab | Series number |
| Alt+G | Genre |
| Alt+P | Plot |
| Alt+Y | Year |
| Alt+M | Time |
| Alt+N | Narrator |
| Alt+C | Collection |
| Alt+R | Read date |
| Alt+K | Want to read |
| Alt+H | Path |
| Alt+B | Browse path (in edit mode; in view mode it says to press Alt+E) |
| Ctrl+N | New book |
| Alt+E | Edit book |
| Ctrl+S | Save book |
| Alt+D | Delete book |
| Alt+W | Get web info |
| Ctrl+L | Listen to audiobook |
| Page Up | Previous book |
| Page Down | Next book |
| Escape | Close |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

Series number is a text box. Type a number such as 3 or 6.5, or leave it blank. Saving stores the series number only; the title stays as typed. The main book table shows "- 03" or "- 6.5" after the title when a series number is set.

With a screen reader running, **Year** and **Read** are typed text fields: a four-digit year, and a date as year-month-day. Leave a field blank for no year or no read date. An invalid year or read date shows a warning, and focus returns to that field. The year warning appears once. Press **Enter** to close it. Saving with an invalid year keeps Book Details open. Without a screen reader, use the calendar for Read, and press **Clear** beside the date to remove a read date. Up or Down on a blank Year starts at this year, and on a blank Read date starts at today.

## Common confusion

**Book Details or Update — which should I use?**
Use **Book Details** for one book with full fields and Page Up and Page Down navigation. Use **Update** to set the Series, Genre, or Collection on several selected books at once.

**How do I delete a book from Book Details?**
In view mode, press the **Delete** button or **Alt+D**. AbCS asks you to confirm.

**Why does Alt+B say to press Alt+E?**
Browse works in edit mode. Press **Alt+E** first, then **Alt+B**.

## Related help

Click a guide name, or press Enter on its line, to open it. You can also open these from All Help Topics.

- Several books at once: [Update](05_update.md)
- Online plot lookup: [Web Metadata Fetch](07_web_metadata.md)
- Playing the book: [Listen to a book](26_listen_to_a_book.md)
