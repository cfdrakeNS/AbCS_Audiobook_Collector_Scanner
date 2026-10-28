# Import Preferences

## What this is

This guide explains how **Preferences** shape folder import: import scenarios, fallback rules, auto-correct options, validation, and duplicate matching. Factory values are in [Default preferences](17_default_preferences.md), and the step-by-step workflow is in [Import (Folder Scan)](02_import.md).

Open **Manage → Preferences** from the menu bar. The **Import Settings**, **Fallback & Auto Correct**, and **Validation Rules** tabs control import. See [Preferences](10_preferences.md) for moving around that window.

Press **F1** in Preferences for shortcuts. Press **Alt+/** to re-read the status bar.

## Import scenarios

Choose the scenario that matches how your audiobook folders are organized. The scenario is saved in Preferences and used each time you scan from the Import window. **Mass Standard Import** is the default.

| Scenario | Best for | Folder layout |
|----------|----------|---------------|
| **Mass Standard Import** (default) | Most libraries | Root, then author folders, then title subfolders or files. Series folders may appear under the author |
| **Mass Import - Series From Directory** | Series with files directly in the series folder | Root, then author, then series folder, then audio files |
| **Mass Import - Series From Directory (Nested Books)** | Series with a subfolder for each book | Root, then author, then series folder, then book folder, then audio files. Standalone books sit at author, then book folder |
| **Mass Import - Series From File Name** | Series written in file names | Any layout. The series comes from the first block in parentheses in each file name |
| **Single Author / Book Import** | One book at a time | One author folder, one book or series folder, or one audio file |

### Mass Standard Import (default)

- Takes the author from the folder structure when the tag is missing and author fallback is checked.
- Takes the series from tags, and is careful about guessing series from folder names.
- Use it when each author has a top-level folder, and books are title subfolders or files under the author.

### Mass Import - Series From Directory

- For libraries where **audio files sit directly in the series folder**, with no per-book subfolders.
- Path pattern: `Author/Series/Files`, three levels under the scan root.
- The **series folder name** becomes the series. Each file, or album group, in that folder is one book.
- When the book file name starts with a number, for example `03 The Hound of the Baskervilles.m4b`, that number is stored as the **series number**. When a book has several files, the number is used only if every file starts with the same number. Different numbers such as 01, 02, 03 are treated as track numbers.
- AbCS skips the series and adds a **warning** when the folder path is missing or unclear, the series folder name matches the author name, or the parent folder does not match the book's author tag.
- Author fallback uses the **parent** folder name, at the author level.

**Example:** `Sir Arthur Conan Doyle/Sherlock Holmes/The Hound of the Baskervilles.m4b` gives the series **Sherlock Holmes**, with the author from the tag or the parent folder **Sir Arthur Conan Doyle**. With `Sir Arthur Conan Doyle/Sherlock Holmes/03 - The Hound of the Baskervilles.m4b`, the series number **3** is stored too.

When each book has its own subfolder (`Author/Series/Book/Files`), use **Series From Directory (Nested Books)**. On that layout, this scenario skips the series with a warning.

### Mass Import - Series From Directory (Nested Books)

- For author folders where each series folder has a subfolder for each book (`Author/Series/Book/Files`).
- Standalone books directly under the author (`Author/Book/Files`) are imported with no series.
- The series is the first folder under the author.
- When the title tag is missing, title fallback uses the book subfolder name without its leading number, for example `1- Whose Body` gives **Whose Body**.
- When the book folder name starts with a number, for example `1- Whose Body`, that number is stored as the **series number**. Track file names inside the book folder are not used for the number.
- Extra subfolders under a book, for example `CD-01`, are ignored for the series. The book folder name is still used for title fallback.
- AbCS skips the series and adds a **warning** when the author tag cannot be matched in the folder path, or the path is too short.

**Example:** `Dorothy Sayers/Lord Peter Wimsey/1- Whose Body/01 Whose Body.mp3` gives the series **Lord Peter Wimsey**, series number **1**, title **Whose Body**, and author **Dorothy Sayers**.

**Second example:** `G. K. Chesterton/Father Brown/1 The Innocence of Father Brown/01 The Innocence of Father Brown.m4b` gives the series **Father Brown**, series number **1**, title **The Innocence of Father Brown**, and author **G. K. Chesterton**.

**Standalone example:** `Wilkie Collins/The Moonstone/01 The Moonstone.mp3` gives no series, the title **The Moonstone**, and the author **Wilkie Collins**.

### Mass Import - Series From File Name

- Reads the **first block in parentheses** in the file name, without the extension.
- Uses that block as the series name.
- When the block ends with a number, for example `(Father Brown 1)`, the number is stored as the **series number**. The title is left without a suffix.

**Example:** `01 - The Innocence of Father Brown (Father Brown 1).m4b` gives the series **Father Brown** and series number **1**.

### Single Author / Book Import

- For importing one author folder, one book folder, or one audio file.
- When you pick a single file, only the audio formats checked in Preferences are offered.
- Fallback, auto-correct, and validation rules still apply.

## Fallback and auto correct

The **Fallback & Auto Correct** tab has two groups: fallback and text auto-correct.

### Fallback

| Setting | When it is used | Effect |
|---------|-----------------|--------|
| **Author fallback to folder** | Author tag missing or a placeholder | Uses folder names for the author, depending on the scenario |
| **Title fallback to file** | Title tag missing or a placeholder | Uses the file name without leading track numbers. The nested-books scenario uses the book folder name first |
| **Reader keywords** | Always (a comma-separated list) | Finds the narrator in comment or tag text, for example "narrator" or "read by" |

Placeholder values treated as missing include an empty tag, "unknown", "untitled", and "n/a".

When a fallback checkbox is **unchecked**, a missing author or title stays missing, and validation reports an error such as **Author blank** or **Title blank**.

When a fallback is used, the review list marks the book with **F:** (fallback). A fallback always holds the book for review.

Each Import scan reads the latest saved fallback and auto-correct settings.

### Auto correct

The **Auto Correct** group lists four options. Each option has a **main checkbox** that turns the correction on, and an indented **Skip review** checkbox below it, available when the main option is checked.

| Main option | What it does |
|-------------|--------------|
| **Apply proper case to title and author** | Capitalizes words, for example `the moonstone` becomes `The Moonstone` |
| **Trim extra and leading/trailing whitespace** | Collapses repeated spaces and removes spaces at the start or end |
| **Remove leading punctuation from title and author** | Removes characters other than letters from the start, for example `...The Moonstone` becomes `The Moonstone` |
| **Remove non-printable control characters** | Removes invisible control characters. Accented letters such as é, ñ, and ü are kept |

When the main option is on and **Skip review** is off, a corrected title or author gets a **C:** flag and the book is held for review.

When **Skip review** is on, that correction alone lets the book be added automatically. When the book has another issue, such as a duplicate, a validation warning, a fallback, or a correction without Skip review, it is still held.

When the main option is off, that correction does not run, and its Skip review checkbox is grayed out.

**F:** fallback flags always hold the book, whatever the Skip review settings.

## Validation rules

Each rule can be **None** (off), **Warning**, or **Error**. Warnings and errors hold the book in the **review list**.

| Rule | What it checks |
|------|----------------|
| Author in Title | The author name appears inside the title |
| Title in Author | The title text appears in the author field, for example the author **Anna Sewell Black Beauty** for the book Black Beauty |
| Unknown / Various author | The author is a placeholder such as "Unknown" or "Various" |
| Minimum title length | The title is shorter than the set minimum |
| Minimum / maximum book length | The listening time is too short or too long |
| File structure | The path does not match the expected pattern (default **Author/Title**) |
| Year consistency | The year is before 1800 or in the future |

A book with a warning can be added with **Add Selected**. A book with an error must be fixed first.

## Duplicate matching during import

This is separate from **Duplicate Mode** on the main window, which finds duplicates already in your library.

| Setting | Meaning |
|---------|---------|
| **Duplicate match** | Which fields must match. The default is Title + Author |
| **Fuzzy duplicate** (slider) | How similar the title **and** author text must be (0% turns fuzzy matching off) |

Both the title and the author must meet the fuzzy threshold. At **90%**, the default, only minor typos match. At **0%**, near-exact text is required.

A book that matches one already in your library is held in review with a **Duplicate** flag.

## When settings take effect

- Preferences are saved when you press **Save** (**Ctrl+S**) in Preferences, or when you confirm **Restore Defaults** (**Alt+R**).
- The values Restore Defaults sets are listed in [Default preferences](17_default_preferences.md).

## Related help

- Factory values: [Default preferences](17_default_preferences.md)
- Folder scan: [Import (Folder Scan)](02_import.md)
- All shortcuts: [Keyboard shortcuts by window](16_shortcuts.md)
- Import words: [Glossary](27_glossary.md)
