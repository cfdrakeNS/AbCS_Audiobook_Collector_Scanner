# Web Metadata Fetch Process

## What this is

Fetch Web Info looks up a book online and compares what it finds with what is stored in AbCS. You can then choose which fields to update — such as plot, series, genre, year, title, or author.

For an explained walkthrough, see [Web metadata explained](21_web_metadata_explained.md). If a fetch matches but the review window still offers a title change, see [Web metadata title compare explained](22_web_metadata_title_compare.md).

## When to use it

- A book is in your library but is missing a plot, series, or other details.
- You want to compare your local record with online sources before saving changes.

## Before you start

- You need an **internet connection**.
- Select exactly **one book** in the main window (the focused row is used).
- Fetch Web Info is **not available** while duplicate mode is active.

## Steps

1. In the main window, move to the book you want to look up.
2. Open **Edit → Fetch Web Info**, click **Search Web** on the toolbar, or press **Alt+W**.
   - You can also open **Book Details** for a book and press **Alt+W** there.
3. A **progress dialog** appears. Watch the status text, or listen for announcements as AbCS searches online sources in order: Open Library, then Google Books, then WikiData.
4. When the search finishes, one of two things happens:
   - **Differences found** — a review window opens showing your current values side by side with web values.
   - **Nothing useful found** — a "No Web Data Found" message appears. This can mean no match was found, the book is already up to date, or there was a network problem.
5. In the review window, fields that differ have **checkboxes**. Click each box for the fields you want to apply from the web.
   - Jump to fields with **Alt+T** Title, **Alt+A** Author, **Alt+P** Plot, **Alt+Y** Year, **Alt+I** Series, **Alt+G** Genre, or **Alt+R** Rating.
   - Fields that are empty in your local record may be filled in automatically without a checkbox.
6. To search again using alternate sources, click **Re-fetch** or press **Alt+F**.
7. Click **Save** (or press **Alt+S**) to apply checked fields, or click **Cancel** (or press **Alt+C**) to close without saving.
8. Plot text is saved to the book's **comments** field. If the web source includes a rating and you save plot, the rating line (for example `Rating: 4.5 (1,234 ratings)`) may appear at the **top of that plot text**. It is not stored in a separate rating field.

## What happens next

- Saved fields update the book in your database immediately.
- The main book list and Book Details reflect the changes.
- In Book Details, a saved rating prefix may show as the first line of the plot when you review the book.
- Focus returns to a sensible place after the window closes.

## Settings that affect this

None. Fetch Web Info has no settings of its own in Preferences. It uses the book's stored title and author when searching online.

## Mouse, shortcuts, and accessibility

- Click **Search Web** on the main toolbar, or use **Edit → Fetch Web Info**.
- In the review window, click checkboxes beside fields you want to update, then click **Save**, **Re-fetch**, or **Cancel**.

| Shortcut | Action |
|----------|--------|
| Alt+W | Fetch Web Info (main window or Book Details) |
| Alt+T | Title (review window) |
| Alt+A | Author (review window) |
| Alt+P | Plot (review window) |
| Alt+Y | Year (review window) |
| Alt+I | Series (review window) |
| Alt+G | Genre (review window) |
| Alt+R | Rating (review window) |
| Alt+F | Re-fetch (in review window) |
| Alt+S | Save selected fields |
| Alt+C | Cancel |
| F1 | Help for this window |
| Alt+/ | Re-read status |
| Escape | Close window |
## Common confusion

**Why does it search multiple sources?**
AbCS tries Open Library first, then Google Books, then WikiData, to find the best match for your title and author.

**Is the rating saved?**
Not in its own field. The review window shows **Rating** for reference (Alt+R). AbCS does not keep a separate rating column in the database today. If you save **Plot** and the web result includes a rating, that rating line is written at the **top of the plot/comments text** (for example `Rating: 4.5 (1,234 ratings)` followed by the plot). You can edit or remove that line later in Book Details like any other plot text.

**Can I fetch for multiple books at once?**
No. Only the currently focused book in the main window is used. Use Book Details to fetch one book at a time from that view.

**Why does the message say "rate limited" or show a countdown?**
Google Books sometimes limits how many searches AbCS can send in a short time. AbCS automatically retries once, and if it still fails, waits briefly before contacting Google Books again. A message such as *Try again in about 30s or use Re-fetch (Alt+F)* tells you roughly when it will work again. Open Library and WikiData are not affected and are still tried as usual.
