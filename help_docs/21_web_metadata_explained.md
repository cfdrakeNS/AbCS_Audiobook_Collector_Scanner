# Web Metadata Explained — Under the Hood

What AbCS does internally after you activate **Fetch Web Info** (Alt+W). This is not a how-to guide — for steps and shortcuts see [Web Metadata](07_web_metadata.md).

**Important:** Fetch Web Info works on **one book at a time**. It does not download audiobook files. It only looks up text information online and, if you approve, updates fields inside AbCS. Your audio files on disk are never touched.

---

## 1. Once Fetch Web Info is activated

### Which book is used

- **Main window:** the book on the **focused table row** (keyboard focus). Multi-select is ignored — only one row counts.
- **Book Details window:** the book currently open in that window.

### Blocked before anything starts


| Condition                                   | Result                                         |
| ------------------------------------------- | ---------------------------------------------- |
| Duplicate Mode is active on the main window | Fetch does not run                             |
| Multiple books selected on the main window  | Fetch does not run (no message)                |
| No valid book focused                       | Status: *No book available for web info fetch* |


### What is sent to the web

The search uses the book's **stored title and author** from your library — not the audio filename or folder path on disk.

Before searching, the app prepares those strings:

- Strips a trailing series number from the title (e.g. `Title - 3` → `Title`)
- Moves trailing articles to the front (`Title, The` → `The Title`)
- Cleans extra punctuation and spacing
- Strips honorifics from author (Sir, Dr., etc.)
- **Year from your library is not sent** — stored years are often wrong and would hurt matching

A **Please wait** progress dialog opens immediately and announces status as each source is tried.

---

## 2. Searching the web — source by source

The app tries online catalogs **in order**, stopping at the first result that passes its matching rules.

### First fetch (Alt+W)


| Order | Source       |
| ----- | ------------ |
| 1     | Open Library |
| 2     | Google Books |
| 3     | WikiData     |


### Re-fetch (Alt+F in the review window)

Skips Open Library and tries:


| Order | Source       |
| ----- | ------------ |
| 1     | Google Books |
| 2     | WikiData     |


### Per source

1. Progress dialog announces which source is being tried.
2. The app sends a search query built from the cleaned title and author.
3. Multiple query variations may be tried (title + author, title only, stripped author, etc.).
4. Up to several hits are scored; the best title match is picked.
5. If the hit passes validation (see section 3), the search stops.
6. If the source fails (network error, no match), the error is recorded and the **next source** is tried.

### Cache

Recent lookups are cached in memory and on disk (`data/web_cache.json`) for about five minutes. A repeat fetch for the same book may return cached results without hitting the network.

---

## 3. Deciding if a web result is a match

A candidate result must pass **title and author checks** before AbCS treats it as the right book.

### Title match

- At least **50%** of meaningful words from your library title must appear in the web title.
- Common words (the, a, of, etc.) are ignored.
- If the web title is much longer than yours, the score is penalized.

### Author match

- Your author's **last name** must appear in the web author string.
- If both names have multiple parts, a first-name or initial must also match.

### If no source passes

The app may try **broader searches**:

1. Same title without author in the query — but still requires author to match your record.
2. Title-only search — only when your author field is empty, looks like a narrator name, or the book appears to be from Librivox (based on path, source, or comments).

If everything fails, you get a **No Web Data Found** message. No review window opens.

---

## 4. Enriching the match — plot and series

Once a match is accepted, the app gathers more detail before showing you anything.

### Plot

Collected from several places, in order of preference:

1. Open Library work description
2. Wikipedia summary
3. Google Books description

Plot text must be at least **80 characters** and must not be just a repeat of the series name. If a good plot is found, the progress dialog may announce it.

### Series

Gathered from:

1. Series number already in your title (if any)
2. Open Library work metadata
3. WikiData
4. Google Books (by ISBN or title/author search)

If a series name is found, progress may announce *Series found…*.

### Final cleanup

Before comparison with your book, web data is cleaned:

- Title, author, genre, plot text normalized
- Unlikely series names dropped (e.g. values that look like genres)
- Plot text that is only a series label removed
- Series number may be re-appended to the display title

---

## 5. Comparing web data with your book

The app compares cleaned web values against what is already stored for your book.

### Fields compared


| Field         | How difference is decided                                     |
| ------------- | ------------------------------------------------------------- |
| Title         | Normalized text compared (articles, case, spacing ignored)    |
| Author        | Scalar text compared                                          |
| Year          | Compared as numbers                                           |
| Series        | Compared as text                                              |
| Series number | Compared when web has a number and a series name exists       |
| Genre         | Compared as text                                              |
| Plot          | Compared against your comments field (plot lives in comments) |


### What is not saved from the web


| Field           | Treatment                                                                                                   |
| --------------- | ----------------------------------------------------------------------------------------------------------- |
| Rating          | Shown for reference only — folded into plot/comments text if you save plot, but not stored as its own field |
| Publisher       | Not offered for save                                                                                        |
| Web source name | Display only                                                                                                |


### Gate before the review window

The review window opens **only if** at least one savable difference exists.


| Outcome                                       | What you see                         |
| --------------------------------------------- | ------------------------------------ |
| Web data found with differences               | **Web Metadata** review window       |
| Web data found but everything already matches | *Already up to date* message         |
| Network errors but no match                   | Message listing which sources failed |
| No match at all                               | *No information found…* message      |


---

## 6. The review window — what you decide

If differences exist, the review window shows **your value** on the left and **web value** on the right for each changed field.

### Auto-fill vs checkbox


| Your library field      | Behavior                                                              |
| ----------------------- | --------------------------------------------------------------------- |
| **Empty**               | Web value will be applied on Save — no checkbox needed                |
| **Already has a value** | Checkbox shown, **checked by default** — uncheck to keep your version |


Plot has no checkbox — if plot differs, it appears in the difference list and is offered on Save.

### Re-fetch (Alt+F)

Runs the search again using the Google Books → WikiData order. Refreshes the right-hand column without closing the window.

### Save or Cancel


| Action             | Result                                                |
| ------------------ | ----------------------------------------------------- |
| **Save** (Alt+S)   | Applies checked fields and auto-fills to the database |
| **Cancel** (Alt+C) | Closes with no changes                                |
| **Escape**         | Asks *Save web data?* — Yes saves, No discards        |


---

## 7. Writing to the library (Save path)

For each field you approved (or that was auto-filled because your field was empty):


| Field  | What happens in the database                                              |
| ------ | ------------------------------------------------------------------------- |
| Title  | Updated on the book record                                                |
| Author | Looked up or created in authors table → book's author link updated        |
| Year   | Parsed to a number; invalid values ignored                                |
| Series | Looked up or created in series table → book's series link updated         |
| Genre  | Looked up or created in genres table → book's genre link updated          |
| Plot   | Written to the book's **comments** field (may include rating prefix text) |


Before writing, the app verifies that author, series, genre, and collection links still exist. Broken links are cleared rather than saved.

**One update** writes all approved fields to the `books` row and commits.

After Save:

- Main book list or Book Details refreshes
- Status announces which fields changed (e.g. *Updated: Plot, Series*)
- Focus returns to a sensible place on the main window

If Save fails, an error is announced and the review window **stays open**.

---

## 8. Once the fetch is complete

### If you saved

Your book record reflects the approved web values. Audio files and folder paths are unchanged.

### If you cancelled or no data was found

Your book record is exactly as it was before Alt+W.

### If you want another book

Repeat Alt+W on the next focused row. There is no batch mode.

---

## What Fetch Web Info does not do


| Assumption                            | Reality                                        |
| ------------------------------------- | ---------------------------------------------- |
| Downloads the audiobook               | No — metadata text only                        |
| Updates the whole library at once     | No — one book per fetch                        |
| Always overwrites your data           | No — you choose fields; Cancel changes nothing |
| Saves star ratings as their own field | No — rating is reference only                  |
| Works offline                         | No — internet required                         |
| Uses your file path for the search    | No — title and author from the library record  |
| Has its own Preferences page          | No — behavior is fixed for all users           |


---

## Why several websites are tried

Different catalogs know different books. Open Library is tried first for mainstream titles. Google Books often has descriptions and ISBN links. WikiData helps with less common works. The first source that passes matching rules drives what you see in the review window.

---

## Related guides

- Step-by-step with shortcuts: [Web Metadata](07_web_metadata.md)
- Edit a book by hand: [Book Details](04_book_details.md)
- Bulk add from audio folders: [Import explained](19_import_explained.md)
- Bulk add from a spreadsheet: [Import Book List explained](20_import_book_list_explained.md)
- Why title matching differs by step: [Web metadata title compare explained](22_web_metadata_title_compare.md)

