# Import Process (Folder Scan)

## What this is

Import scans a folder of audiobook files, reads information from the audio file tags (such as title and author), and adds books to your chosen collection. This is the main way to build your library from files on your computer.

## When to use it

- You have audiobook files organized in folders and want to add them to AbCS.
- You are bringing in a batch of new titles after setting up a collection.

## Before you start

- At least one **active collection** must exist. See [Collections](06_collections_process.md).
- Know which folder contains your audiobooks.
- Optional: set up **Preferences** first (View → Preferences, or Manage → Preferences). Import behavior depends heavily on these settings.

## Steps

1. Open **File → Import**, or press **Ctrl+I**.
2. Choose a **Collection** (**Alt+C**). If the main window already shows a specific collection, it may be pre-selected.
3. Choose a **Folder** (Alt+F, then **Browse** with Alt+B). This is the top-level folder to scan. Subfolders are included.
4. Click **Import** (Alt+I) to start the scan.
5. A **progress window** appears while files are read. You can cancel if needed.
6. When the scan finishes, books are handled in two ways:
   - **Added automatically** — books with clean metadata and no problems.
   - **Held for review** — books with duplicates, errors, warnings, fallback guesses, or autocorrects.
7. If any books need review, they appear in a **review table**. Use the **error filter** (Alt+E) to show only certain issue types: All, Corrected, Duplicate, Error, Fallback, or Warning.
8. To work on one book, select a row and press **Enter** to open the **detail window**. There you can edit fields, move to previous/next book, skip, or discard.
9. Select rows you want to add and click **Add Selected** (Alt+S).
10. Optionally click **Export** (Alt+X) to save the review list to a spreadsheet for offline review.
11. Press **Escape** to close Import. If unscanned review items remain, you will be asked to confirm.

## What happens next

- Books added successfully appear in the main book list when Import closes.
- The status bar reports how many books were scanned, auto-added, and left for review.
- If duplicate mode was active on the main window, it exits automatically when Import opens.

## Settings that affect import

Open **View → Preferences** (or **Manage → Preferences**). Import-related settings are on three tabs:

### Import Settings

- **Default directory** — pre-fills the folder field when Import opens.
- **Audio formats** — which file types to scan (MP3, M4A, M4B, FLAC, OGG, WAV, WMA).
- **Import scenario** — how your folders are organized. Choose the scenario in **Preferences → Import Settings** before scanning. The Import window shows the active scenario name in the status bar.

| Scenario | Folder layout | When to use |
|----------|---------------|-------------|
| **Mass Standard Import** | Author → title subfolders or files | **Default.** Most libraries; does not auto-assign series from folders |
| **Series From Directory** | Author → series folder → **audio files** (no book subfolders) | One file (or album) per book directly inside the series folder |
| **Series From Directory (Nested Books)** | Author → series folder → **book folder** → audio files | Each book in its own subfolder under the series; standalone books under author get no series |
| **Series From File Name** | Any layout | Series name is in the file name inside `( … )` |
| **Single Item** | One author, book, or file | Import a single folder or file at a time |

**Choosing between the two series scenarios:**

- **Series From Directory** — files live **directly** in the series folder:
  - `Tolkien/Lord of the Rings/Fellowship.m4b`
  - `Michael R. Stern/Quantum Touch/01 Storm Portal.m4b` *(one m4b per book, no book subfolder)*

- **Series From Directory (Nested Books)** — each book has its **own subfolder** under the series:
  - `Michael R. Stern/Quantum Touch/1 Storm Portal/01 Storm Portal.m4b`
  - `John Sandford/Lucas Deavenport Series/1- Rules of Prey/01 Rules of Prey.mp3`

If you use **Series From Directory** on a nested layout (book subfolders under the series), series assignment is skipped and books are flagged with a **warning**. Switch to **Nested Books** for that layout.

See [Import preferences](18_import_preferences.md) for full scenario details, fallbacks, and validation rules.

### Fallback and Parsing

- **Author fallback to folder** — if the author tag is missing, use the folder name.
- **Title fallback to file** — if the title tag is missing, use the file name.
- **Reader keywords** — words that help detect the narrator in comments (for example, "narrator", "read by").

### Validation Rules

Rules that flag possible problems during import. Each rule can be off, a warning, or an error:

- Author name appears in the title field.
- Title appears in the author field.
- Author is "Unknown" or "Various".
- Title is too short.
- Book is too short or too long (by duration).
- File or folder naming does not match expected patterns.
- Year is out of a reasonable range.

**Duplicate settings (used during import):**

- **Duplicate match** — how strictly AbCS compares a new book to books already in the database (for example, title + author + year).
- **Fuzzy duplicate percent** — how similar title and author text must be to count as a duplicate. Both title and author must pass the threshold. Set to 0 to turn fuzzy matching off.

Changing preferences while the Import window is open may not apply until you close and reopen Import, or start a new scan.

## Shortcuts and accessibility

| Shortcut | Action |
|----------|--------|
| Ctrl+I | Open Import |
| Alt+C | Collection |
| Alt+F | Folder field |
| Alt+B | Browse for folder |
| Alt+I | Start scan |
| Alt+E | Error filter |
| Alt+L | Focus review table |
| Alt+S | Add selected |
| Alt+X | Export review list to CSV |
| Enter | Open detail for selected row |
| F1 | Help for this window |
| Alt+/ | Re-read status |
| Escape | Close (may confirm if review items remain) |
## Common confusion

**Why were some books added and others not?**
Clean books are added immediately. Anything with a duplicate match, validation issue, or fallback guess stays in the review list until you add it manually.

**Is import duplicate detection the same as Duplicate Mode?**
No. Import duplicate detection happens while adding new books and can use fuzzy matching. Duplicate Mode (Manage menu) finds duplicates already in your library using exact key matching. See [Duplicate Mode](08_duplicate_mode_process.md).

**Do I need to set preferences every time?**
No. Preferences are saved and apply to every import until you change them.

**Why does Series From Directory show warnings for my author folder?**
That scenario expects audio files **directly** in the series folder (`Author/Series/file.m4b`), not in per-book subfolders. If each book has its own folder under the series (`Author/Series/Book/file.m4b`), use **Series From Directory (Nested Books)** in Preferences instead.
