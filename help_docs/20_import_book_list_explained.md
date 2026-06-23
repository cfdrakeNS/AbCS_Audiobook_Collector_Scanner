# Import Book List Explained

Describes **File → Import Book List** (Ctrl+Shift+I) in everyday terms. For keyboard shortcuts and step-by-step detail, see [Import Book List](11_import_book_list.md).

---

## What Import Book List does

Import Book List reads a **spreadsheet** on your computer (CSV, Excel, or ODS) and turns each row into book information in AbCS — or updates **read dates** on books you already have.

It does **not** read audio file tags. It does **not** attach audio files to the books it creates. You are importing **text from a table**, not scanning folders.

Think of it as: **you open a list you already made elsewhere → you tell AbCS which column is title and which is author → AbCS adds new rows to your collection or updates dates on matching books.**

---

## What you need first

- At least one **collection** in AbCS.
- A spreadsheet file ready on your computer (`.csv`, `.xlsx`, `.xls`, or `.ods`).
- For **new books**: each row needs at least a **title** and **author** (in columns you will map).
- For **read-date updates**: the books must **already exist** in the collection you pick, with matching title and author.

---

## Step by step — what happens when you import a list

### 1. You open Import Book List

Use **File → Import Book List** or **Ctrl+Shift+I**.

You choose:

- **Collection** — where new books go, or which collection to match for read-date updates.

### 2. You pick your spreadsheet (Browse, Alt+B)

AbCS opens the file and reads it like a table:

- It counts **rows** and **columns**.
- The status bar tells you what it found (for example “50 rows, 6 columns”).
- Your spreadsheet file on disk is **not changed**.

If the first row contains column headings (Title, Author, Date Read, and so on), leave **My file Has Header** checked. If the first row is already data, uncheck it.

### 3. You choose what kind of import (Options, Alt+O)

Two modes:

| Mode | What AbCS does |
|------|----------------|
| **Add Book From List** (default) | Creates **new** book records from each row. |
| **Add Read Date from List** | Finds **existing** books by title + author in the selected collection and updates their **read date** only. No new books are created. |

### 4. You map columns (Field Mapping)

Your spreadsheet might have columns in any order. AbCS shows a **mapping table**: for each book field (Title, Author, Year, Series, and so on), you pick which spreadsheet column holds that data (Column A, B, C, …).

- **New books mode:** Title and Author mappings are **required**. Other fields are optional.
- **Read-date mode:** Title, Author, and Read Date are **required**. Other mappings are turned off.

Nothing is written to your library yet — you are only telling AbCS how to read the file.

### 5. You press Import (Alt+I)

AbCS shows a **Confirm Import** dialog summarizing:

- How many rows it will process.
- Which mode you chose.
- How columns are mapped.

Click **Yes** to continue or **No** to go back and fix mapping.

### 6. AbCS processes each row

For each row in the spreadsheet, AbCS:

**Add Book From List mode:**

- Reads the mapped title and author (and any optional fields you mapped).
- Skips rows with a **missing** title or author.
- Checks for **duplicates** — a book with the same title/author (and year, if your duplicate settings include year) already in that collection.
- Adds good rows as **new book records** in the collection. No audio file path is attached unless your spreadsheet included folder information and you mapped it.

**Add Read Date from List mode:**

- Looks up an existing book in the collection by **title and author**.
- If found, updates its **read date** from the mapped column.
- Skips rows where no matching book exists or the date is invalid.

When finished, an **Import Complete** message shows how many rows succeeded and how many failed.

### 7. Errors (if any)

Failed rows are **not** added. Common reasons:

- Missing title or author.
- Duplicate already in the collection.
- Read-date mode: no matching book, or bad date format.

Click **Export Errors** (Alt+X) to save a CSV file listing the problem rows so you can fix the spreadsheet and try again.

### 8. You close when done

The window **stays open** so you can import another file without reopening the menu. Press **Escape** when finished.

The **main book list** refreshes when you close the window. New or updated books appear in the collection you chose.

---

## What Import Book List does *not* do

| Myth | Reality |
|------|---------|
| “It imports my audiobook files.” | No. Use [Import explained](19_import_explained.md) (Ctrl+I) for audio files. |
| “It updates every field on existing books.” | In read-date mode, only the **read date** changes. In add mode, it only **creates** new books. |
| “It uses my folder import scenario settings.” | No. Spreadsheet import ignores import scenarios and tag fallbacks. Only **duplicate** settings are shared with folder Import. |
| “It changes my spreadsheet.” | No. AbCS only reads the file. |

---

## How duplicates work

Import Book List uses the same **duplicate match** and **fuzzy duplicate percent** settings as folder Import (**Preferences → Validation Rules**). If a row looks like a book you already have, it is skipped and listed in the error export.

See [Import](02_import.md) for a short explanation of those settings.

---

## When to use Import Book List vs other tools

| You have… | Use… |
|-----------|------|
| Audiobook files in folders | [Import explained](19_import_explained.md) — Ctrl+I |
| A spreadsheet or export from another app | **Import Book List** (this guide) — Ctrl+Shift+I |
| Books in AbCS missing plot or series | [Web metadata explained](21_web_metadata_explained.md) — Alt+W |

---

## Tips for a smooth import

1. **Test with a small file** (5–10 rows) before importing hundreds of titles.
2. Open the spreadsheet in Excel or LibreOffice first and confirm column letters match what you expect in the mapping dropdowns.
3. Keep **title and author spelling consistent** with books already in AbCS if you plan to use read-date mode later.
4. After errors, fix the spreadsheet and import again — successfully added rows will be flagged as duplicates if you re-import the same list.
5. Import Book List is ideal for **wish lists**, **exports from Goodreads**, or **migrating from a spreadsheet** before you attach audio files with folder Import.

---

## Where to go next

- Step-by-step with shortcuts: [Import Book List](11_import_book_list.md)
- Scanning audio files: [Import explained](19_import_explained.md)
- Duplicate settings: [Import preferences](18_import_preferences.md)
