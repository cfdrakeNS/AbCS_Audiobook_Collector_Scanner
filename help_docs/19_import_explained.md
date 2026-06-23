# Import Explained

Describes **File → Import** (Ctrl+I) in everyday terms. For keyboard shortcuts and step-by-step detail, see [Import](02_import.md).

---

## What Import does

Import looks at audiobook **files on your computer** and adds **book records** to AbCS. It does **not** move, copy, or rename your audio files. It does **not** create new folders on your hard drive.

What it does create is information **inside AbCS**: each book gets a row in your library with title, author, year, folder path, and other details read from the file (or guessed from folder names, depending on your settings).

Think of it as: **you point AbCS at a folder → AbCS reads what it can → good books land in your collection right away → questionable ones wait in a review list for you.**

---

## What you need first

- At least one **collection** in AbCS (for example *Audio Books*). Import always adds books to the collection you pick.
- A folder on your computer that contains audiobooks (subfolders are included in the scan).
- Optional but helpful: **Preferences → Import Settings** set to match how your folders are organized (author folders, series folders, and so on). See [Import preferences](18_import_preferences.md) when you are ready for detail.

---

## Step by step — what happens when you import

### 1. You open Import

Use **File → Import** or **Ctrl+I**. The Import window opens.

You choose:

- **Collection** — which AbCS collection these books belong to.
- **Folder** — the top folder to scan. Everything inside it (and in subfolders) is searched for audio files.

### 2. You press Import (Alt+I)

When you start the scan:

1. AbCS **checks** that you picked a collection and a valid folder.
2. The **collection** dropdown is locked for the rest of this session so books are not split across collections by mistake.
3. Any **old review list** from a previous scan in this window is cleared.
4. A **progress window** opens. It shows how many files have been checked and how long the scan has run. You can cancel if needed.

### 3. AbCS walks through your folder

The app searches the folder tree for audio files (types you enabled in Preferences — MP3, M4B, FLAC, and so on).

For each file it finds, AbCS:

- Reads **tags** embedded in the file (title, author, year, comments, and similar).
- Looks at **folder and file names** when tags are missing or incomplete (if you turned those fallbacks on in Preferences).
- Applies your **import scenario** — rules for how author, title, and series should be inferred from the path (for example author folder → series folder → book folder).
- Runs **validation** — flags oddities such as “author looks like a title,” very short books, or suspicious years.
- Checks for **duplicates** — books that already exist in AbCS (or are very similar, if fuzzy matching is on).

Your original files stay where they are. AbCS only records the **path** to each file so it knows where the audiobook lives on disk.

### 4. Two paths: automatic add vs review

After the scan, each book is either **added immediately** or **held for review**.

**Added automatically** when AbCS is confident:

- Tags and paths look good.
- No duplicate conflict.
- No validation errors (only minor warnings may still auto-add, depending on settings).

**Held for review** when something needs your eye:

- Possible **duplicate** of a book already in the library.
- **Missing or guessed** author or title (fallback from folder/file name).
- **Text auto-correct** on title or author (for example trimmed whitespace), unless **Skip Review** is enabled for that correction in Preferences.
- **Validation warning or error** (wrong field in wrong place, odd duration, path mismatch, and so on).
- **Unreadable file** or tag problem.

The status bar and summary tell you how many were scanned, auto-added, and left for review.

### 5. The review table (if any books need you)

Books that were not auto-added appear in a **table** in the Import window.

- Use the **error filter** (Alt+E) to show only duplicates, errors, warnings, or corrected items.
- Select a row and press **Enter** to open the **detail window** — edit title, author, year, and other fields; move to the next book; skip; or discard.
- When you are satisfied, select rows and press **Add Selected** (Alt+S) to add them to your collection.

You can **export** the review list to a spreadsheet (Alt+X) if you want to work offline.

### 6. You close Import

Press **Escape** to close. If review items remain, AbCS asks you to confirm — those books are **not** in your library until you add them.

When Import closes, the **main book list** refreshes. New books appear in the collection you chose.

---

## What Import does *not* do

| Myth | Reality |
|------|---------|
| “Import copies my files into AbCS.” | No. Files stay on your drive. AbCS stores metadata and the file path. |
| “Import creates folders on my computer.” | No. You choose an existing folder to scan. |
| “Import reorganizes my disk.” | No. Only the library inside AbCS changes. |
| “I must import the same folder only once.” | You can re-import later; duplicates are flagged so you do not add the same book twice (unless you override). |

---

## How this ties to your collection

A **collection** in AbCS is a label for grouping books in the app (for example *Audiobooks*, *Wish list*). Import does not create a new Windows or Linux folder with that name — it attaches each new book record to the collection you selected.

If the main window was already filtered to one collection when you opened Import, that collection may be pre-selected.

---

## When to use folder Import vs other tools

| You have… | Use… |
|-----------|------|
| Audiobook files in folders | **Import** (this guide) — Ctrl+I |
| A spreadsheet of titles and authors, no audio files | [Import Book List explained](20_import_book_list_explained.md) — Ctrl+Shift+I |
| Books already in AbCS but missing plot or series | [Web metadata explained](21_web_metadata_explained.md) — Alt+W |

---

## Tips for a smooth first import

1. Start with a **small test folder** (one author) before scanning your whole library.
2. Set **Preferences → Import Settings → Import scenario** to match your folder layout.
3. Turn on **author** and **title fallbacks** if many files have weak tags.
4. After the first scan, open the review table and read the **status** column — it explains why a book was held back.
5. Use **Add Selected** only after you have checked duplicates and corrections.

---

## Where to go next

- Step-by-step with shortcuts: [Import](02_import.md)
- Scenario and validation detail: [Import preferences](18_import_preferences.md)
- Collections: [Collections](06_collections.md)
- Cleaning duplicates already in the library: [Duplicate Mode](08_duplicate_mode.md) (different from import-time duplicate checks)
