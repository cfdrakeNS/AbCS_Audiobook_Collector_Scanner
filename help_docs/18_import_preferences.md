# Import Preferences

## What this is

This guide explains how **Preferences** shape folder import behavior: import scenarios, fallback rules, auto-correct options, validation, and duplicate matching. It complements [Default preferences](17_default_preferences.md) (factory values) and [Import process](02_import.md) (step-by-step workflow).

Open **Manage → Preferences** (or **View → Preferences**) from the menu bar. Click the **Import Settings**, **Fallback & Auto Correct**, and **Validation Rules** tabs to change import behavior. See [Preferences](10_preferences.md) for mouse and keyboard navigation in that window.

Press **F1** in Preferences for shortcuts. Press **Alt+/** to re-read the status bar.

## Import scenarios

Choose the scenario that matches how your audiobook folders are organized. The scenario is saved in Preferences and applied when you scan from the Import window. **Mass Standard Import** is the default for new installs and after Restore Defaults.

| Scenario | Best for | Folder layout |
|----------|----------|---------------|
| **Mass Standard Import** (default) | Most libraries | Root → author folders → title subfolders or files (series folders may appear under author) |
| **Mass Import - Series From Directory** | Series with files directly in folder | Root → author → **series folder** → audio files (not book subfolders) |
| **Mass Import - Series From Directory (Nested Books)** | Series with per-book subfolders | Root → author → **series folder** → **book folder** → audio files; standalone books at author → book folder |
| **Mass Import - Series From File Name** | Series encoded in file names | Any layout; series parsed from the first `( … )` block in each file name |
| **Single Author / Book Import** | One book at a time | One author folder, one book/series folder, or a single audio file |

### Mass Standard Import (default)

- **Factory default** after Restore Defaults (Alt+R).
- Expects author names in folder structure when tags are missing (with author fallback enabled).
- Does **not** aggressively derive series from folder paths.
- Use when each author has their own top-level folder and books live in title subfolders or as files under the author.

### Mass Import - Series From Directory

- For libraries where **audio files sit directly in the series folder** — not in per-book subfolders.
- Path pattern: `Author/Series/Files` (three levels under the scan root).
- The **series folder name** becomes the series; each file (or album group) in that folder is one book.
- Skips series assignment and adds a **warning** when:
  - The folder path is missing or ambiguous
  - The series folder name matches the author name
  - The parent folder does not match the book's author tag
- Author fallback prefers the **parent** folder name (the author level).

**Example:** `Tolkien/Lord of the Rings/Fellowship.m4b` → series **Lord of the Rings**, author from tag or parent folder **Tolkien**.

**Not for:** `Author/Series/Book/Files` layouts where each book has its own subfolder — use **Series From Directory (Nested Books)** instead. If you use this scenario on nested folders, series assignment is skipped with a warning.

### Mass Import - Series From Directory (Nested Books)

- Best for author folders where series contain per-book subfolders.
- For libraries where each series has its own folder and **each book has a subfolder** under that series (`Author/Series/Book/Files`).
- Standalone books directly under the author (`Author/Book/Files`) are imported **without** a series.
- Series is taken from the first folder under the author; title fallback (when the title tag is missing) uses the book subfolder name and strips leading numbers (for example `1- Rules of Prey` → **Rules of Prey**).
- Extra subfolders under a book (for example `CD-01`) are ignored for series assignment; the book folder name is still used for title fallback.
- Skips series assignment and adds a **warning** when the author tag cannot be matched in the folder path or the path is too shallow.

**Example:** `John Sandford/Lucas Deavenport Series/1- Rules of Prey/01 Rules of Prey.mp3` → series **Lucas Deavenport Series**, title **Rules of Prey**, author **John Sandford**.

**Nested series example:** `Michael R. Stern/Quantum Touch/1 Storm Portal/01 Storm Portal.m4b` → series **Quantum Touch**, title **Storm Portal**, author **Michael R. Stern**.

**Standalone example:** `John Sandford/Dead Watch/01 Dead Watch.mp3` → no series, title **Dead Watch**, author **John Sandford**.

### Mass Import - Series From File Name

- Reads the **first parenthesized block** in the file name (without extension).
- Uses that block as the series name.
- If the block ends with a number (for example `(Mistborn 1)`), the number becomes a **title suffix** (` - 1`).

**Example:** `01 - The Final Empire (Mistborn 1).m4b` → series **Mistborn**, title may gain suffix ** - 1**.

### Single Author / Book Import

- For importing one author folder, one book folder, or one audio file.
- When picking a single file, only enabled audio formats from Preferences are offered.
- Other fallback, auto-correct, and validation rules still apply.

## Fallback and auto correct

The **Fallback & Auto Correct** tab has two groups: fallback parsing and text auto-correct.

### Fallback and parsing

| Setting | When enabled | Effect |
|---------|--------------|--------|
| **Author fallback to folder** | Author tag missing or placeholder | Uses folder names to infer author (scenario-aware) |
| **Title fallback to file** | Title tag missing or placeholder | Uses file name (strips leading track numbers); nested-books scenario prefers the book folder name first |
| **Reader keywords** | Always (comma-separated list) | Detects narrator in comment/tag text (for example `narrator`, `read by`) |

Placeholder values treated as missing include: empty, `unknown`, `untitled`, `n/a`, and similar.

When a fallback is used, the review list flags the book with **F:** (fallback). Fallback always holds the book for review.

### Auto correct

Each option has two checkboxes:

| Column | Meaning |
|--------|---------|
| **Apply** | Run this correction during folder scan |
| **Skip Review** | If this correction is the only reason a book would go to review, still auto-add it |

| Option | What it does |
|--------|--------------|
| **Apply proper case** | Capitalizes words in title and author (for example `the hobbit` → `The Hobbit`) |
| **Trim whitespace** | Collapses extra spaces and trims leading or trailing spaces |
| **Remove leading punctuation** | Strips non-letter characters from the start of title or author |
| **Remove non-printable characters** | Removes control characters only; accented letters such as é, ñ, and ü are **kept** |

When **Apply** is on and **Skip Review** is off, corrected title or author fields get a **C:** flag and the book is held for review.

When **Skip Review** is on for a correction, that correction alone will not block auto-add. If another issue is present (duplicate, validation warning, fallback, or a different correction without Skip Review), the book still goes to review.

**F:** fallback flags always hold for review regardless of Skip Review settings.

## Validation rules

Each rule can be **None** (off), **Warning**, or **Error**. Warnings and errors send books to the **review list** instead of auto-add.

| Rule | What it checks |
|------|----------------|
| Author in Title | Author name appears inside the title field |
| Title in Author | Title text appears in the author field |
| Unknown / Various author | Author is a generic placeholder |
| Minimum title length | Title shorter than the configured minimum |
| Minimum / maximum book length | Listening duration too short or too long |
| File structure | Path does not match the expected pattern (default **Author/Title**) |
| Year consistency | Year before 1800 or in the future |

Severity **Error** is stricter than **Warning** for blocking auto-import.

## Duplicate matching during import

Separate from **Duplicate Mode** on the main window (which finds duplicates already in your library).

| Setting | Meaning |
|---------|---------|
| **Duplicate match** | Which fields must match (for example Title + Author + Year) |
| **Fuzzy duplicate %** | How similar title **and** author text must be (0% = fuzzy off) |

Both title and author must meet the fuzzy threshold. At **90%** (default after Restore Defaults), only minor typos match. At **0%**, near-exact text is required.

Books that match an existing entry are held in review with a **Duplicate** flag — they are not auto-added.

## When settings take effect

- Preferences are saved to disk when you click **Save** (Alt+S) in Preferences.
- If the Import window is already open, close and reopen it, or start a new scan, so the latest scenario and rules load.
- Default values after **Restore Defaults** (Alt+R) are listed in [Default preferences](17_default_preferences.md).

## Related documentation

- [Default preferences](17_default_preferences.md) — factory default values
- [Import process](02_import.md) — folder scan workflow
- [Keyboard shortcuts by window](16_shortcuts.md) — Import and Preferences shortcuts
