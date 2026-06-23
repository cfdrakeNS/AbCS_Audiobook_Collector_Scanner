# Web Metadata Explained

Describes **Edit → Fetch Web Info** (Alt+W) in everyday terms. For keyboard shortcuts and step-by-step detail, see [Web Metadata](07_web_metadata.md).

---

## What Fetch Web Info does

Fetch Web Info looks up **one book at a time** on the internet, compares what it finds with what you already have in AbCS, and lets you **choose which details to copy** into your library — plot, series, genre, year, title, or author.

It does **not** download audiobook files. It only fills in **text fields** on the book record you already have.

Think of it as: **you pick a book → AbCS searches online catalogs → you see your version next to the web version → you tick what you want to keep → Save.**

---

## What you need first

- An **internet connection**.
- Exactly **one book** selected in the main window (the highlighted row is the one that will be looked up).
- Fetch Web Info is **not available** while **Duplicate Mode** is active on the main window — exit Duplicate Mode first.

You can also run Fetch Web Info from **Book Details** (Alt+W while viewing one book).

---

## Step by step — what happens when you fetch

### 1. You select a book and start the search

In the main window, move to the book you want to enrich. Then:

- Press **Alt+W**, or
- Click **Search Web** on the toolbar, or
- Use **Edit → Fetch Web Info**.

AbCS uses the book’s **current title and author** stored in your library as the search terms. It does not use the file name on disk.

### 2. A progress window appears

While searching, AbCS shows a **progress dialog** with status text. With a screen reader, listen for announcements as each source is tried.

AbCS searches in order:

1. **Open Library**
2. **Google Books**
3. **WikiData**

It stops when it has enough useful information or has tried all sources. This may take a few seconds depending on your connection.

### 3. One of two outcomes

**A — Differences found**

A **review window** opens. For each field (title, author, plot, year, series, genre, and sometimes rating for reference), you see:

- **Your value** — what AbCS has now.
- **Web value** — what the online source suggests.

Fields that **differ** have a **checkbox**. Tick the fields you want to replace or fill from the web.

Fields that are **empty in your library** may be filled automatically when the web has data — you do not always need to tick every blank field.

**B — Nothing useful found**

A **No Web Data Found** message appears. This can mean:

- No good match for that title and author online.
- Your record already matches what the web returned (nothing to change).
- A **network problem** — try again later.

### 4. You review and decide

In the review window:

- Read or listen to each field before saving.
- Use checkboxes only for changes you **want**.
- **Re-fetch** (Alt+F) runs the search again if you want to try alternate matching.
- **Plot** from the web is stored in your book’s **comments** field (the Plot area in Book Details).

**Rating** may appear for comparison only — AbCS does **not** save rating to the database.

### 5. You Save or Cancel

- **Save** (Alt+S) — applies checked fields (and automatic fills for empty fields) to your book **immediately** in the database.
- **Cancel** (Alt+C) or **Escape** — closes without changing your book.

The main list and Book Details update to show saved changes. Focus returns to a sensible place on the main window.

---

## What Fetch Web Info does *not* do

| Myth | Reality |
|------|---------|
| “It downloads the audiobook.” | No. Only metadata text is updated. |
| “It updates my whole library at once.” | No. One book per search. Repeat for each title. |
| “It always overwrites my data.” | No. You choose fields with checkboxes; Cancel changes nothing. |
| “It saves star ratings.” | No. Rating is shown for information only. |
| “It works offline.” | No. An internet connection is required. |

---

## Why AbCS uses several websites

Different catalogs know different books. AbCS tries **Open Library** first (good for many mainstream titles), then **Google Books**, then **WikiData**, to improve the chance of finding plot and series information. The first strong match drives what you see in the review window.

---

## When to use Fetch Web Info vs other tools

| You want to… | Use… |
|--------------|------|
| Add many books from audio folders | [Import explained](19_import_explained.md) — Ctrl+I |
| Add many books from a spreadsheet | [Import Book List explained](20_import_book_list_explained.md) — Ctrl+Shift+I |
| Fill in plot, series, or genre for one book already in AbCS | **Fetch Web Info** (this guide) — Alt+W |

---

## Tips for better results

1. **Fix title and author first** in Book Details if they are wrong — the web search uses those exact strings.
2. Try **Re-fetch** if the first result looks like the wrong edition.
3. Read the **plot** carefully before saving — web summaries may spoil or describe a different printing.
4. For series books, check that the **series name** matches how you organize your library before saving.
5. Fetch Web Info has **no Preferences settings** — behavior is the same for every user.

---

## Where to go next

- Step-by-step with shortcuts: [Web Metadata](07_web_metadata.md)
- Editing a single book by hand: [Book Details](04_book_details.md)
- Bulk add from files: [Import explained](19_import_explained.md)
