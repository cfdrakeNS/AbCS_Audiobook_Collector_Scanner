# Import Explained — Under the Hood

What AbCS does internally after you press **Import** (Alt+I). This is not a how-to guide — for steps and shortcuts see [Import](02_import.md). For preference settings see [Import preferences](18_import_preferences.md).

**Important:** Import does **not** create, move, copy, or rename folders on your computer. Your audio files stay exactly where they are. AbCS only reads them and stores book information inside the app.

---

## 1. Once Import is activated

The app checks that everything is ready before it starts:

- A **collection** must be selected — import always attaches new books to that collection.
- A **folder** (or single file, in single-item mode) must be chosen and must exist on disk.
- The collection dropdown is **locked** so books from this scan cannot accidentally go to a different collection.
- Any **previous review list** in this window is cleared.
- The **Import** button is disabled and a **progress window** opens.
- Your current **import preferences** are loaded fresh (file types, scenario, fallbacks, validation rules, duplicate settings).

If any check fails, the scan stops and you see a warning — nothing is read and nothing is added.

---

## 2. Walking the folder — finding audio files

The app walks the folder tree you pointed it at. No new folders are created; it only **reads** what is already there.

### Which folders are searched

- Starts at the **top folder** you chose in the Import window.
- If **include subfolders** is on in preferences, every folder below that level is searched too.
- If subfolders are off, only files directly inside the top folder are checked.

### Which files count as audiobooks

Only files whose extension matches a type you turned on in **Preferences → Import Settings → Formats**:

| Format | Extensions |
|--------|------------|
| MP3 | `.mp3` |
| M4A / M4B | `.m4a`, `.m4b` |
| FLAC | `.flac` |
| OGG | `.ogg`, `.oga` |
| WAV | `.wav` |
| WMA | `.wma` |
| AAC | `.aac` |
| Opus | `.opus` |

Files with any other extension are skipped. If every format is turned off, nothing is found.

### How files become one book

As each audio file is found, the app reads its tags and groups files that belong to the same book:

- **Grouping key** — normally the **album** tag (treated as the book title).
- If album is empty, files in the same parent folder are grouped using that **folder name** instead.
- In **single-item** mode, one file = one book; title falls back to the filename if album is empty.

The **folder path** where the files live is remembered — this is stored as the book's location in AbCS, not as a new folder on disk.

### Progress during this phase

- The progress bar shows **files scanned** vs **total files found**.
- Status text shows something like `Scanning 12/48 | Elapsed 00:35`.
- Updates are throttled so the screen reader is not flooded — roughly every 150 milliseconds.
- **Escape** on the progress window asks to cancel; if you confirm, the scan stops and keeps whatever was found so far.

---

## 3. For each file — reading the tags

For every audio file, the app opens it and reads embedded metadata. Your file is not changed.

### Tags read from the file

| What AbCS needs | Where it looks in the file |
|-----------------|---------------------------|
| **Title** | Album tag |
| **Author** | Album Artist tag first; if missing, Artist tag |
| **Year** | Year / date tag (first four digits) |
| **Genre** | Genre tag |
| **Narrator** | Composer tag first; if empty, comment text after keywords like "read by" or "narrated by" |
| **Comments** | Comment tag (reader-only lines are filtered out) |
| **Duration** | Length of the audio |
| **Bitrate** | Quality of the encoding |
| **Format** | File extension (MP3, M4B, FLAC, etc.) |
| **Size** | File size on disk |

Different file types use different tag names internally (MP3 ID3, MP4 atoms, FLAC Vorbis comments, etc.) but the app maps them all to the same book fields above.

### What gets accumulated per book

When several files share the same album (one multi-part audiobook):

- **Total duration** — sum of all part lengths → converted to hours and minutes.
- **Total size** — sum of all file sizes → converted to megabytes.
- **Track count** — number of files in the group.
- **Comments** — merged from all parts, duplicates removed.
- **Read errors** — if a file cannot be opened, a note is added like `part03.mp3: Error reading file`.

The progress bar advances once per file during this phase.

---

## 4. Applying preference rules to each book

After all files are read, the app processes each grouped book through your **import scenario** and **fallback** settings.

### Import scenario (how folder layout is interpreted)

| Scenario | What the app does with folder names |
|----------|-------------------------------------|
| **Mass standard** | Uses tags only; standard fallbacks and corrections apply |
| **Series from directory** | Series name from the book's folder; author from the parent folder |
| **Series from directory (nested)** | Series and title from nested folders after the author segment |
| **Series from filename** | Series from text inside `(…)` in the filename; may append a series number to the title |
| **Single item** | One file or folder treated as one book |

### Fallbacks when tags are weak

If a tag is blank or looks like a placeholder ("unknown", "untitled", "n/a", etc.):

- **Title fallback from file** — uses the filename (strips leading track numbers like `01 `).
- **Title fallback from folder** — uses the folder name (in nested scenario).
- **Author fallback from folder** — walks up the folder path to find an author name.

Each fallback is flagged so you can review it — unless you turned on **skip review** for that type of correction in preferences.

### Auto-corrections (text cleanup)

If enabled in preferences, the app may adjust title or author text:

- Trim extra whitespace
- Remove leading punctuation
- Remove non-printable characters
- Apply proper case (capitalize words)

Each correction is flagged. If **skip review** is on for that correction type, it still applies but may not block auto-add.

### Other preference adjustments

- **Narrator from comment** — if no narrator tag, searches comment for your keyword list (default: "reader", "read by", "narrator", "narrated by").
- **Author equals title** — if author and title are the same string, author is replaced with the parent folder name.

---

## 5. Validation — checking each book

The app runs your enabled **validation rules**. Each rule can be set to **error** (blocks auto-add) or **warning** (held for review) in preferences.

### Rules on by default

| Rule | Severity | What it checks |
|------|----------|----------------|
| Title blank | Error | No title after tags and fallbacks |
| Author blank | Error | No author after tags and fallbacks |
| Author starts with non-letter | Warning | Author does not begin with a letter |
| Author name in title | Warning | Author text appears inside the title |
| Title in author name | Warning | Title text appears inside the author |
| Unknown or Various author | Warning | Author contains "unknown" or "various" |
| Unreadable audio length | Warning | Files exist but total duration is zero |

### Rules off by default (enable in preferences)

| Rule | What it checks |
|------|----------------|
| Minimum title length | Title shorter than configured minimum (default 3 characters) |
| File structure | Folder path does not match expected Author/Title or Year/Author/Title pattern |
| Minimum book length | Total duration below configured minutes |
| Maximum book length | Total duration above configured hours |
| Year out of range | Year is not a number, or falls outside 1801–current year |

Tag read failures from step 3 are treated as **errors** and always block auto-add.

---

## 6. Duplicate check

Before deciding whether to add a book, the app compares it against books **already in your library**.

### What counts as a duplicate

Controlled by **duplicate match mode** in preferences:

| Mode | Match on |
|------|----------|
| Title + Author + Year + Collection | All four must match (default) |
| Title + Author + Year | Same title, author, and year anywhere in the library |
| Title + Author only | Same title and author, year ignored |

### Fuzzy matching

If a **fuzzy threshold** is set (0–100%), near-matches count as duplicates — both title and author must reach that similarity percentage. At 0%, only exact matches count.

A duplicate is **never** auto-added. It always goes to the review table with status **Duplicate**.

Books auto-added earlier in the same scan are also checked — so two identical albums in one folder cannot both slip through.

---

## 7. Auto-add or review?

For each book, the app decides:

### Auto-added immediately (goes straight into the library)

Only when **all** of these are true:

- Not a duplicate
- No read error (unreadable file)
- No validation error
- No validation warning
- No fallback was used (`F:` flag)
- No auto-correction was applied (`C:` flag)

### Held for review (appears in the Import table)

Everything else, with a status label:

| Status | Reason |
|--------|--------|
| **Duplicate** | Already in the library |
| **Error** | Unreadable file, blank title/author, or other hard failure |
| **Warning** | Validation warning, fallback, or correction |

---

## 8. Writing to the library (auto-add path)

When a book passes all checks, the app creates records **inside AbCS only** — still no changes to your disk folders.

For each auto-added book:

1. **Author** — looked up in the database; created if new.
2. **Genre** — looked up or created if the book has a genre.
3. **Series** — looked up or created if the book has a series.
4. **Book record** — written with:
   - Title, author, year, series, genre, collection
   - Narrator, duration (hours + minutes), track count
   - Size, bitrate, file format
   - **Path** — the folder on your computer where the files live (not individual file names)
   - Comments, date added, source = "Import"

Individual audio file paths are **not** stored as separate records — only the folder and how many files were found.

All auto-adds in one scan are saved together in a single database transaction at the end of processing.

---

## 9. Once the scan is complete

- The progress bar reaches **100%**.
- The status bar shows a summary, for example:  
  `Scanned: 48 | Added: 32 | Corrected: 8 | Errors: 2 | Warnings: 4 | Duplicates: 2 | Elapsed: 01:12`
- The **Import** button is re-enabled.
- The collection dropdown stays locked until the review list is empty or you close Import.
- Closing the progress window returns focus to the review table or Import button.

If no audio files were found (or every format is disabled), you still get a summary — nothing is added.

---

## 10. If issues were found — the review table

Books that were not auto-added appear in the **review table** in the Import window.

### What you can do with them

- **Error filter** (Alt+E) — show only duplicates, errors, warnings, fallbacks, or corrections.
- **Enter** on a row — open the detail window to edit title, author, year, and other fields.
- **Add Selected** (Alt+S) — add rows with status OK or Warning to your collection.
- **Export** (Alt+X) — save the review list to a spreadsheet.

Duplicates are never added through Add Selected unless you edit them first so they no longer match.

### How preferences affect review

| Preference | Effect |
|------------|--------|
| Skip review for a correction type | Correction still applies but may allow auto-add |
| Duplicate match mode | Controls which existing books count as duplicates |
| Fuzzy threshold | Controls how close a near-match must be to flag as duplicate |
| Validation rule severity | Error vs warning determines status and whether Add Selected is allowed |

When you close Import (Escape), the main book list refreshes. Any books you added — automatically or through review — appear in the collection you chose.

---

## What Import does not do

| Assumption | Reality |
|------------|---------|
| Creates folders on your computer | No — only reads an existing folder you choose |
| Copies or moves audio files | No — files stay where they are |
| Stores every individual file path | No — stores the folder path and track count |
| Re-imports without duplicate checks | No — duplicates are always flagged |

---

## Related guides

- Step-by-step with shortcuts: [Import](02_import.md)
- Preference detail: [Import preferences](18_import_preferences.md)
- Spreadsheet import (no audio files): [Import Book List explained](20_import_book_list_explained.md)
- Fill in plot/series for books already in AbCS: [Web metadata explained](21_web_metadata_explained.md)
