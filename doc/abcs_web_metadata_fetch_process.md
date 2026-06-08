# Web Metadata Fetch Process

## What this is

Fetch Web Info looks up a book online and compares what it finds with what is stored in AbCS. You can then choose which fields to update — such as plot, series, genre, year, title, or author.

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
3. A **progress dialog** appears. Listen for announcements as AbCS searches online sources in order: Open Library, then Google Books, then WikiData.
4. When the search finishes, one of two things happens:
   - **Differences found** — a review window opens showing your current values side by side with web values.
   - **Nothing useful found** — a "No Web Data Found" message appears. This can mean no match was found, the book is already up to date, or there was a network problem.
5. In the review window, fields that differ have **checkboxes**. Check the fields you want to apply.
   - Jump to fields with **Alt+T** Title, **Alt+A** Author, **Alt+P** Plot, **Alt+Y** Year, **Alt+I** Series, **Alt+G** Genre, or **Alt+R** Rating.
   - Fields that are empty in your local record may be filled in automatically without a checkbox.
6. To search again using alternate sources, press **Re-fetch** (Alt+F).
7. Click **Save** (Alt+S) to apply checked fields, or **Cancel** (**Alt+C**) to close without saving.
8. Plot text is saved to the book's comments field.

## What happens next

- Saved fields update the book in your database immediately.
- The main book list and Book Details reflect the changes.
- Focus returns to a sensible place after the window closes.

## Settings that affect this

A few preference options influence how AbCS searches online:

- **Move leading "The" in title** — may adjust the title before searching.
- **Flip author name** — may swap "Last, First" to "First Last" before searching.

These are in Preferences and affect search matching, not which sources are used.

## Shortcuts and accessibility

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

## Verification

Manual QA for this workflow is complete. See [QA verification](qa_verification.md).

## Common confusion

**Why does it search multiple sources?**
AbCS tries Open Library first, then Google Books, then WikiData, to find the best match for your title and author.

**Is the rating saved?**
No. Rating may appear in the review window for information only. It is not stored in the database.

**Can I fetch for multiple books at once?**
No. Only the currently focused book in the main window is used. Use Book Details to fetch one book at a time from that view.
