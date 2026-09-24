# Web Metadata Fetch Process

## What this is

Fetch Web Info looks up a book online and compares what it finds with what is stored in AbCS. You can then choose which fields to update — such as plot, genre, year, title, or author. Series is not fetched from the web; edit series in Book Details or the Update window.

For an explained walkthrough, see [Web metadata explained](21_web_metadata_explained.md). If a fetch matches but the review window still offers a title change, see [Web metadata title compare explained](22_web_metadata_title_compare.md).

## When to use it

- A book is in your library but is missing a plot or other details.
- You want to compare your local record with online sources before saving changes.

## Before you start

- You need an **internet connection**.
- For one book, use the focused row in the main window (or Book Details).
- For several books, select **two or more** rows and use **Web fetch**, **Alt+W**, or toolbar **Search Web**.
- Fetch Web Info is **not available** while duplicate mode is active.

## Steps

1. In the main window, move to the book you want to look up.
2. For one book: open **Edit → Fetch Web Info**, click **Search Web** on the toolbar, or press **Alt+W**. You can also press **Alt+W** in **Book Details**.
   - For two or more selected books: **Alt+W**, toolbar **Search Web**, or footer **Web fetch** all start the same batch fetch. Search Web and Web fetch stay available while books are selected. Add Book, Import, Find, Statistics, Preferences, and plot/read/recent-added filters are disabled. Escape cancels the selection. F1 during selection lists only the shortcuts that still work. A progress dialog shows book N of M. Escape cancels the remaining queue. Then a summary opens with focus on the first book in the list. The Issue column says **Plot found** and/or **Metadata found** when a book has changes, matching the stand-alone fetch wording. It offers **Apply all** and **Review** (or **Review each** when more than one book has changes). With a screen reader, the status bar lists **Alt+A Apply all**, **Alt+R Review**, and Escape. **Up to date** means plot and metadata already match the web result. The Issue column says **Plot and metadata up to date.** **No match found** means nothing usable was saved. **Match found. No plot was found.** means a match exists but neither the library nor the web result has a usable plot (short comments such as an author name or “Unabridged” do not count). When Google Books is paused, those rows still say **No match found**. The summary at the top then says **Google Books limit hit. Try in N minutes.** Escape closes the summary. After the summary closes, the main list selection is cleared, the same as after Update. **Alt+L** jumps to the books table. After Review and Save, the summary stays open so you can continue. **F1** lists shortcuts. **Alt+/** re-reads the status bar.
3. A **progress dialog** appears. Watch the status text, or listen for announcements as AbCS searches online sources in order: Open Library, then Google Books, then WikiData.
4. When the search finishes, one of two things happens:
   - **Differences found** — a review window opens showing your current values side by side with web values.
   - **Nothing useful found** — a "No Web Data Found" message appears. This can mean no match was found, the book is already up to date, or there was a network problem.
5. In the review window, fields that differ have **checkboxes**. Click each box for the fields you want to apply from the web.
   - Jump to fields with **Alt+T** Title, **Alt+A** Author, **Alt+P** Plot, **Alt+Y** Year, **Alt+G** Genre, or **Alt+R** Rating.
   - Fields that are empty in your local record may be filled in automatically without a checkbox.
6. To search again using alternate sources, click **Re-fetch** or press **Alt+F**.
7. Click **Save** (or press **Alt+S**) to apply checked fields, or press **Escape** to close. Escape asks *Save web data?* — Yes saves, No discards.
8. Plot text is saved to the book's **comments** field. If the web source includes a rating and you save plot, the rating line (for example `Rating: 4.5 (1,234 ratings)`) may appear at the **top of that plot text**. It is not stored in a separate rating field.

## What happens next

- Saved fields update the book in your database immediately.
- The main book list and Book Details reflect the changes.
- In Book Details, a saved rating prefix may show as the first line of the plot when you review the book.
- Focus returns to a sensible place after the window closes.

## Settings that affect this

Optional: Preferences → Display → Web Metadata → Google Books API key (or environment variable `ABCS_GOOGLE_BOOKS_API_KEY`). Without a key, Google Books uses anonymous per-IP limits. Fetch still uses the book's stored title and author when searching online.

## Mouse, shortcuts, and accessibility

- Click **Search Web** on the main toolbar, or use **Edit → Fetch Web Info**.
- In the progress dialog, press **Escape** to cancel the fetch.
- In the review window, click checkboxes beside fields you want to update, then click **Save** or **Re-fetch**, or press **Escape** to close.

| Shortcut | Action |
|----------|--------|
| Alt+W | Fetch Web Info for the focused book, or batch fetch when two or more books are selected |
| Alt+L | Books list (batch summary) |
| Alt+K | Skip this book (Review each queue) |
| Alt+T | Title (review window) |
| Alt+A | Author (review window) |
| Alt+P | Plot (review window) |
| Alt+Y | Year (review window) |
| Alt+G | Genre (review window) |
| Alt+R | Rating (review window) |
| Alt+F | Re-fetch (in review window) |
| Alt+S | Save selected fields |
| Escape | Close (asks whether to save) |
| F1 | Help for this window |
| Alt+/ | Re-read status |
## Common confusion

**Why does it search multiple sources?**
AbCS tries Open Library first, then Google Books, then WikiData, to find the best match for your title and author.

**Is the rating saved?**
Not in its own field. The review window shows **Rating** for reference (Alt+R). AbCS does not keep a separate rating column in the database today. If you save **Plot** and the web result includes a rating, that rating line is written at the **top of the plot/comments text** (for example `Rating: 4.5 (1,234 ratings)` followed by the plot). You can edit or remove that line later in Book Details like any other plot text.

**Can I fetch for multiple books at once?**
Yes. Select two or more books and use **Web fetch**, toolbar **Search Web**, or **Alt+W**. With no multi-select, Alt+W still fetches only the focused book. While you are selecting books, Find, Import, Add Book, and filters stay off until Escape. Search Web and the footer Web fetch button stay on. Batch Apply all writes only fields that differ from what you already store. Review each opens the same review window, one book at a time; Save or Skip (Alt+K) returns you to the summary (or the next book in that Review pass). Escape on the summary closes it. A larger batch can hit the Google Books limit. Later books in that batch are not sent to Google. The summary at the top says **Google Books limit hit. Try in N minutes.** Open Library and WikiData are still tried.

**Why does the message say "rate limited" or show a countdown?**
Google Books, WikiData, or Wikipedia sometimes limit how many searches AbCS can send. AbCS waits for a cooldown (often about 15 minutes for Google Books) before contacting that source again. The web details window only opens when data is found — there is no Re-fetch button on that error popup. Wait for the cooldown, then press Alt+W again. Other sources continue in their normal order when one source is limited.
