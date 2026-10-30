# Web Metadata Fetch

## What this is

Fetch Web Info looks up a book online and compares what it finds with what is stored in AbCS. You then choose which fields to update, such as plot, genre, year, title, or author. Series is edited in Book Details or the Update window.

For a walkthrough of how the search and comparison work, see [Web metadata explained](21_web_metadata_explained.md).

## Quick steps

1. On the main window, move to the book.
2. Press **Alt+W**.
3. Wait while AbCS searches online.
4. In the review window, check the fields you want, or keep the ones already filled in.
5. Press **Save** (**Ctrl+S**).

## When to use it

- A book in your library is missing a plot or other details.
- You want to compare your record with online sources before saving changes.

## Before you start

- You need an **internet connection**.
- For one book, focus its row in the main window, or open it in Book Details.
- For several books, select **two or more** rows.
- Fetch Web Info is turned off while duplicate mode is active.

## Window layout

**Please wait** progress dialog: a status line that names each online source as it is tried.

**Web Metadata** review window:

- One row each for **Title**, **Author**, **Year**, and **Genre**. Each row shows your value and the web value. A checkbox appears when both have a value and they differ.
- **Plot**, with an **Other plots** list when more than one plot was found.
- **Rating**, shown for reference.
- Buttons: **Re-fetch**, **Save**, and **Skip**. Skip appears only during a batch review.
- Status bar at the bottom.

**Batch progress** dialog: shows book N of M while a batch runs.

**Batch summary** window:

- A summary line at the top.
- A books table with columns Title and Issue.
- Buttons: **Apply all** and **Review each**. The second button is named **Review** when only one book has changes.
- Status bar at the bottom.

## Fetch web info for one book

1. In the main window, move to the book you want to look up.
2. Open **Edit → Fetch Web Info**, press the **Search Web** toolbar button, or press **Alt+W**. You can also press **Alt+W** in Book Details.
3. The **Please wait** dialog announces each source as AbCS tries it: Open Library, then Google Books, then WikiData.
4. When differences are found, the **Web Metadata** review window opens with your values beside the web values.
5. When nothing new is found, a **No Web Data Found** message appears. The message says whether the book is already up to date, no match was found, or a source could not be reached.
6. In the review window, check the box for each field you want to take from the web. Fields that are empty in your record are filled in on Save without a checkbox.
7. Jump to fields with **Alt+T** Title, **Alt+A** Author, **Alt+P** Plot, **Alt+Y** Year, **Alt+G** Genre, or **Alt+R** Rating.
8. When more than one plot was found, choose another one in **Other plots**. Press **Alt+Down** to open the list, then **Enter** to choose.
9. To search again with the other sources, press **Re-fetch** (**Alt+F**).
10. Press **Save** (**Ctrl+S**) to apply the checked fields. Or press **Escape**; AbCS asks "Save web data?". **Yes** saves and **No** closes without saving.

Plot text is saved in the book's **comments** field. When the web source has a rating and you save the plot, a rating line such as "Rating: 4.5 (1,234 ratings)" is placed at the top of the plot text.

## Fetch several books

1. Select two or more books on the main window.
2. Press **Alt+W**, the **Search Web** toolbar button, or the **Web fetch** footer button.
3. The batch progress dialog shows book N of M. Press **Escape** to cancel the remaining books.
4. The batch summary opens with focus on the first book in the list. The **Issue** column says what was found for each book:
   - **Plot found** or **Metadata found**: the book has changes to apply.
   - **Plot and metadata up to date.**: the library already matches the web.
   - **No match found**: nothing usable was found.
   - **Match found. No plot was found.**: a match exists, but there is no usable plot in the library or on the web.
5. Press **Apply all** (**Alt+A**) to save every change, or **Review each** (**Alt+R**) to check each book in the review window.
6. During Review each, **Save** or **Skip** (**Alt+K**) moves to the next book. Press **Escape** for the choices **Save**, **Skip this book**, **Stop review**, and **Cancel**. **Stop review** returns to the summary, and the status bar says how many books were left. **Cancel** stays on the current book.
7. Press **Escape** to close the summary. The main list selection clears.

Apply all writes only the fields that differ from what you already store. A short comment such as an author name or "Unabridged" is not counted as a plot.

When Google Books pauses a large batch, the summary line says "Google Books limit hit. Try in N minutes." The rest of the batch uses Open Library and WikiData.

## What happens next

- Saved fields update the book in your database immediately.
- The main book list and Book Details show the changes.
- Focus returns to the book you started from.

## Settings that affect this

Optional: a Google Books API key under **Manage → Preferences**, **Display Settings** tab, **Web Metadata** group. Without a key, Google Books allows fewer searches.

## Mouse, shortcuts, and accessibility

- Click **Search Web** on the main toolbar, or use **Edit → Fetch Web Info**.
- In the review window, click the checkboxes beside the fields you want, then click **Save** or **Re-fetch**.

Web Metadata review window:

| Shortcut | Action |
|----------|--------|
| Alt+W | Fetch Web Info (main window) |
| Alt+T | Title |
| Alt+A | Author |
| Alt+P | Plot |
| Alt+Y | Year |
| Alt+G | Genre |
| Alt+R | Rating |
| Alt+F | Re-fetch web data |
| Ctrl+S | Save |
| Alt+K | Skip this book (review queue) |
| Escape | Close window (asks whether to save) |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

Batch summary window:

| Shortcut | Action |
|----------|--------|
| Alt+L | Books list |
| Alt+A | Apply all |
| Alt+R | Review each |
| Escape | Close |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

Batch progress dialog:

| Shortcut | Action |
|----------|--------|
| Escape | Cancel the remaining queue |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Why does it search several sources?**
Different catalogs know different books. AbCS tries Open Library first, then Google Books, then WikiData, and uses the first good match for your title and author.

**Is the rating saved?**
The rating is shown for reference (**Alt+R**). When you save the plot and the web result has a rating, the rating line is placed at the top of the plot text. You can edit or remove that line in Book Details.

**What do Alt+A and Alt+R say when nothing is left?**
They say "No books with new information." when no book has changes to apply or review.

**Why does a message say "rate limited" or show a countdown?**
Google Books, WikiData, or Wikipedia sometimes limit how many searches AbCS can send. AbCS waits for a cooldown, often about 15 minutes for Google Books, before using that source again. The other sources keep working in the meantime. When they do not know the book and Google Books was only paused, the message is "No information found" instead of a countdown. The countdown appears when another source also could not be reached, and on the batch summary. Wait for the countdown, then press **Alt+W** again.

## Related help

- How the search works: [Web metadata explained](21_web_metadata_explained.md)
- Editing a book by hand: [Book Details](04_book_details.md)
- Setting series on several books: [Update](05_update.md)
