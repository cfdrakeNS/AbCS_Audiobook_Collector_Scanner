# Web Metadata Title Compare Explained — Under the Hood

How AbCS decides whether two titles are “the same book” in three different places. This is not a how-to guide — for Fetch Web Info steps see [Web Metadata](07_web_metadata.md); for the full fetch flow see [Web metadata explained](21_web_metadata_explained.md).

**Important:** These three paths answer **different questions**. They do not use identical rules on purpose. A title that matches well online may still show as a difference in the review window — that is normal.

---

## 1. Three paths, three jobs

| Path | When it runs | Question being answered |
|------|--------------|-------------------------|
| **A. Web search** | Open Library, Google Books, WikiData | “Which online result belongs to this book in my library?” |
| **B. Web review window** | After a result is chosen | “Should we offer to change the title field?” |
| **C. Import Book List** | Spreadsheet import (duplicates, read-date lookup) | “Is this spreadsheet row the same book as this library record?” |

Path A and Path B both belong to **Fetch Web Info**, but they compare titles differently. Path C is part of [Import Book List explained](20_import_book_list_explained.md) — it borrows some of the same title cleanup ideas as Path A, then finishes with a stricter exact match.

---

## 2. Path A — picking the right web result

When you press **Fetch Web Info** (Alt+W), AbCS prepares your stored **title and author** before any website is queried.

### Title cleanup before search

1. **Series suffix removed** when it looks like a volume number, for example:
   - `Triptych - 01` → search uses `Triptych`
   - `Title #09`, `Title Book 09`, `Title Volume 09`
   - `Title, 09` — skipped if the number looks like a publication year (1700–2099)
2. **Trailing article moved to the front** — `Sentinel, The` → `The Sentinel`
3. **Extra spaces and odd punctuation cleaned**

The series number may be **put back** on the title later if preferences ask for it; it is **not** sent in the search query.

Author names get light cleanup too (honorifics such as Sir or Dr. removed).

### How a web hit is accepted

For each candidate from a catalog:

1. **Title:** at least **50%** of meaningful words from your prepared title must appear in the web title. Small words (`the`, `a`, `of`, etc.) are ignored. If the web title is much longer than yours, the score is reduced slightly.
2. **Author:** your author’s **last name** must appear in the web author. When both sides have multiple name parts, a first name or initial must match too.

Among hits that pass, the **best** title score wins. The first source in the try order that produces a passing hit stops the search.

### Design intent

- Web catalogs often use longer or slightly different titles than your library.
- Matching is **fuzzy** — not exact string equality.
- Your stored title `Triptych - 01` is compared as `Triptych` against the web.

### Decimal series numbers

Web search strips **whole-number** suffixes (`- 01`, `# 3`). Decimal series such as `Busted - 6.5` are **not** stripped on the web path. Spreadsheet import (Path C) does handle decimals when massaging titles.

---

## 3. Path B — the review window title row

After Path A picks a result, the **Web Metadata** review window compares web values to what is already in your library so it knows which fields to offer for save.

### How the title row is decided

1. **Your library:** the title **as stored** (for example `Triptych - 01`) — series suffix is **not** stripped again.
2. **Web value:** the title returned from the catalog (series number may have been re-appended).
3. Both sides are **normalized** for comparison:
   - Trailing articles moved (`Title, The` → treated like `the title`)
   - Case ignored
   - Spaces removed (punctuation handled as part of that normalization)

Other scalar fields (author, series, genre) use simpler text comparison.

A title appears as a difference when normalized web ≠ normalized current, or when your title field is empty.

### Design intent

- The review UI answers a simple question: “Is the title text different?”
- **No** word-overlap scoring and **no** series-number strip on the library side.
- Predictable field-by-field checkboxes.

### Why Path A and Path B can disagree

| Aspect | Path A (search) | Path B (review) |
|--------|-----------------|-----------------|
| Your title input | Prepared for search (series suffix stripped) | Stored title exactly as in the library |
| Web title input | Raw catalog hit | Fetched metadata title |
| Compare method | Word overlap (about 50%) | Normalized text equality |
| Author | Required to accept a hit | Compared on its own row |

**Example:** Library has `Triptych - 01`. Path A may match web title `Triptych` easily. Path B may still show a title difference because `Triptych - 01` and `Triptych` normalize to different strings. That does **not** mean the fetch picked the wrong book.

---

## 4. Path C — Import Book List matching

When you import from a **spreadsheet**, AbCS compares sheet titles to library titles for:

- **Duplicate detection** (Add Book From List mode)
- **Finding an existing book** (Add Read Date from List mode)

No web APIs are involved.

### Title cleanup (both sides massaged the same way)

Aligned with **Path A search prep**:

1. **Series suffix stripped** — same patterns as web search, **plus** decimal volumes (`6.5`)
2. **Parenthetical series markers** removed when the text looks series-like or contains digits
3. **Trailing articles** moved to the front (`Hobbit, The` → `The Hobbit`)

Then both titles are reduced to a single **compare key**: lowercase, spaces and punctuation removed.

### Compare method

**Exact equality** on that compare key, plus normalized author. Optional **fuzzy duplicate** percentage from Preferences applies in **new-book** mode only (not read-date mode).

### Design intent

- Spreadsheet rows are often plain titles (`Triptych`).
- Library records often carry AbCS series suffixes (`Triptych - 01`).
- Massage **both** sides the same way, then require an exact key match — appropriate for “same book?” in a list, not “closest catalog hit.”

---

## 5. Quick examples

| Stored in library | Spreadsheet / search input | Path A searches as | Path B title diff? | Path C import match? |
|-------------------|----------------------------|--------------------|--------------------|----------------------|
| `Triptych - 01` | `Triptych` | `Triptych` | Often **yes** (suffix vs plain) | **Yes** — keys match |
| `Hobbit, The` | `The Hobbit` | `The Hobbit` | Depends on web title | **Yes** |
| `Still Life (A Three Pines Mystery)` | `Still Life` | Unchanged (paren not stripped on web) | Often **yes** | May **not** match (paren kept unless series-like) |
| `Bury Your Dead (Armand Gamache 6)` | `Bury Your Dead` | Unchanged on web strip | Often **yes** | **Yes** (digit in paren stripped for import) |

---

## 6. What this means for you

### Fetch Web Info

- A good online match does **not** always mean “no title difference” in the review window.
- If you want to keep your series suffix (`- 01`), uncheck the title row on Save.
- If the review window shows a title change you do not want, **Cancel** or uncheck that field — nothing is overwritten until you Save.

### Import Book List

- A row titled `Triptych` can match a library book `Triptych - 01` when updating read dates or checking duplicates.
- That behavior is **separate** from web fetch; fixing spreadsheet matching does not require changing how web search works.

### When titles still do not match

- Web: try **Re-fetch** (Alt+F) or edit the title in [Book Details](04_book_details.md) before fetching again.
- Spreadsheet: confirm author spelling and collection selection; read-date mode requires an exact key match in the chosen collection.

---

## What title compare does not do

| Assumption | Reality |
|------------|---------|
| Web search and review use the same title rules | No — fuzzy pick, then strict field diff |
| Review window strips series numbers before compare | No — uses your stored title as-is |
| Import Book List uses web word-overlap rules | No — exact compare key after shared cleanup |
| File or folder names are used in web title compare | No — library title and author only |

---

## Related guides

- Fetch Web Info steps: [Web Metadata](07_web_metadata.md)
- Full web fetch flow: [Web metadata explained](21_web_metadata_explained.md)
- Spreadsheet import flow: [Import Book List explained](20_import_book_list_explained.md)
- Edit a title by hand: [Book Details](04_book_details.md)
