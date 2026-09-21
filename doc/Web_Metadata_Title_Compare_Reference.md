# Web Metadata Title Compare — Technical Reference

Read-only reference for how AbCS compares book titles during **web metadata fetch** and how that relates to **book list import**.

**Related user guides:** [07_web_metadata.md](../help_docs/07_web_metadata.md), [21_web_metadata_explained.md](../help_docs/21_web_metadata_explained.md), [22_web_metadata_title_compare.md](../help_docs/22_web_metadata_title_compare.md)  
**Related import logic:** `src/utils/text_utils.py` (`compare_normalize_title`)  
**Web review compare:** `src/utils/text_utils.py` (`web_titles_match`, `web_authors_match`)  
**Web implementation:** `src/web/web_book_api.py`, `src/ui/web_metadata.py`

---

## Overview

AbCS uses **three separate title-compare strategies**, each tuned for a different job:

| Path | When it runs | Question being answered |
|------|----------------|-------------------------|
| **A. Web search / candidate pick** | Open Library, Google Books, WikiData | “Which API result belongs to this DB book?” |
| **B. Web metadata review window** | After a candidate is chosen | “Should we offer to change the title field?” |
| **C. Book list import** | Spreadsheet import (duplicate check, read-date match) | “Is this sheet row the same book as this DB record?” |

Paths A and B both live in the web metadata feature but **do not use the same rules**. Path C reuses the **search prep** ideas from path A (series strip, articles) but finishes with an **exact** compare key, not word overlap.

```mermaid
flowchart TB
    subgraph web [Web metadata fetch]
        DB1[DB title + author]
        Prep[Path A prep: strip series, move article, clean]
        APIs[API search results]
        Word[Path A match: word overlap plus author]
        Pick[Best candidate metadata]
        Review[Path B: review window field diff]
        DB1 --> Prep --> APIs --> Word --> Pick --> Review
    end

    subgraph import [Book list import]
        Sheet[Sheet title + author]
        Prep2[Path C: pre_normalize_title + aggressive strip]
        DB2[DB title massaged the same way]
        Exact[Exact compare key match]
        Sheet --> Prep2
        DB2 --> Prep2
        Prep2 --> Exact
    end
```

---

## Path A — Web search and candidate selection

**Files:** `WebBookAPI.get_book_metadata()`, `_metadata_matches_db()`, `_title_word_match_score()`, `_pick_best_google_match()`, Open Library / WikiData loops.

### DB title preparation (before any API call)

When fetch starts, the **raw DB title** is transformed into `search_title`:

1. **`_strip_series_number`** — removes clearly separated series suffixes, for example:
   - `Triptych - 01`
   - `Title #09`
   - `Title Book 09`
   - `Title Volume 09`
   - `Title, 09` (skipped if the number looks like a publication year, 1700–2099)
2. **`_move_article_to_beginning`** — `Sentinel, The` → `The Sentinel`
3. **`_clean_text_field`** — collapse spaces, trim leading junk, remove odd characters

The extracted `series_number` may be **re-appended** to the fetched title later if preferences request it; it is **not** part of the search query.

Author side (for matching, not detailed here): honorifics stripped, light cleanup via `_apply_author_transformations`.

### How a web candidate is accepted

For each API hit, `_metadata_matches_db()` requires:

1. **Title:** `_title_matches()` — at least **50%** of meaningful DB words (from `search_title`) appear in the web title.  
   - Words are tokenized with `\b\w+\b`; stopwords removed: `the`, `a`, `an`, `and`, `or`, `of`, `in`, `on`, `to`, `for`.  
   - If the web title has more than twice as many meaningful words as the DB side, score is reduced by 0.15 (reduces false positives on very long web titles).
2. **Author (when required):** web author must contain the DB author’s **last name**; if both sides have multiple words, some given-name overlap is also required.

Among candidates that pass, the one with the **highest** `_title_word_match_score` wins.

### Design intent

- Tolerant matching: web catalogs often use longer or slightly different titles.
- `search_title` is the DB title **after** series strip — so `Triptych - 01` in the DB is compared as `Triptych` against the web.
- **Not** exact string equality.

### Integer-only series suffix note

Web `_strip_series_number` uses integer patterns (`\d+`). Decimal series entries such as `Busted - 6.5` are **not** stripped on the web path. Book list import’s `strip_series_number` in `text_utils.py` extends this with decimal support; web code was left unchanged.

---

## Path B — Web metadata review window

**Files:** `WebMetadataWindow._compare_scalar_field()`, `compute_field_differences()`, helpers in `text_utils.py` (`web_titles_match`, `web_authors_match`).

After path A returns metadata, the review window decides which fields differ from the **current DB record** so checkboxes can be shown. Series is not fetched or compared.

### Title comparison (review only)

1. Fold accents; rewrite `&` to `and`.
2. Strip filler tails (`: A Novel`, `(Unabridged)`, etc.) when they are the entire remaining suffix.
3. Apply `pre_normalize_title`, then aggressive punctuation strip. Optional leading A/An/The is **folded for “same work”** (`web_titles_match`) so the fetch is still a match.
4. The review window **still offers the web title** when the stored form differs (library `Second Chance - 05`, web `A Second Chance - 05`) because the catalog wording is treated as the better save. Trailing article *position* (`The Hobbit` = `Hobbit, The`) is not offered. A genuine extra subtitle still differs and is offered.

### Author comparison (review only)

1. Fold accents; strip honorifics and suffixes.
2. Tokenize on non-alphanumerics.
3. Match when sorted tokens are equal (covers `King, Stephen` vs `Stephen King`), or surnames match and given names are initial-compatible pairwise.

Other scalar fields (year, genre) use simple `.lower()` on trimmed strings.

### Design intent

- Offer only meaningful changes; ignore cosmetic punctuation and series-suffix noise.
- Path A remains fuzzy word-overlap for candidate pick; Path B is tolerant exact-key equality for the UI.

### Why path A and path B differ

| Aspect | Path A (search) | Path B (review) |
|--------|------------------|-----------------|
| DB title input | `search_title` after series strip + clean | Raw `book.title` then `web_titles_match` |
| Web title input | Raw candidate from API | Fetched metadata title then `web_titles_match` |
| Compare method | Word overlap ≥ 50% | Cosmetic-tolerant key equality |
| Author | Required for candidate gate | `web_authors_match` on its own row |

---

## Path C — Book list import (for context)

**Files:** `book_list_import_window.py`, `text_utils.compare_normalize_title()`.

Import compares a **spreadsheet title** to **DB titles** for duplicate detection and read-date updates. It does **not** call web APIs.

### Preparation (`pre_normalize_title`)

Aligned with **path A search prep** (implemented in `text_utils.py`, not by calling web code):

1. **`strip_series_number`** — same suffix patterns as web, plus decimals (`6.5`)
2. Trailing **parenthetical** series markers when content looks series-like or contains digits
3. **`_move_article_to_beginning`** equivalent for comma-articles

Then **`normalize_title(aggressive=True)`** removes all spaces and punctuation and lowercases — producing a single **exact** compare key.

### Compare method

**Exact equality** on the compare key, plus author normalization. Optional fuzzy duplicate threshold from Preferences (folder import rules) applies in **add-book** mode only.

### Design intent

- Sheet rows are usually plain titles (`Triptych`); DB often has AbCS series suffixes (`Triptych - 01`).
- Massage **both** sides the same way, then require an exact key match — appropriate for “same book?” in a list, not “closest API hit.”

---

## Quick examples

| DB stored | Sheet / search input | Path A (`search_title`) | Path A match style | Path B title diff? | Path C import key |
|-----------|----------------------|-------------------------|--------------------|--------------------|-------------------|
| `Triptych - 01` | `Triptych` | `Triptych` | Word overlap vs web `Triptych` | No (series suffix ignored) | `triptych` = `triptych` |
| `Hobbit, The` | `The Hobbit` | `The Hobbit` | Word overlap | No if web is `The Hobbit` | `thehobbit` = `thehobbit` |
| `Gone Girl` | `Gone Girl: A Novel` | `Gone Girl` | Word overlap | No (filler tail) | Depends |
| `Gone Girl` | `Gone Girl: A Novel of Suspense` | (search words) | Word overlap | Yes (real subtitle) | Depends |

---

## File map

| Concern | Location |
|---------|----------|
| Series strip (web search prep) | `WebBookAPI._strip_series_number()` |
| Search title pipeline | `WebBookAPI.get_book_metadata()` |
| Word overlap / author gate | `WebBookAPI._title_word_match_score()`, `_metadata_matches_db()`, `_author_matches()` |
| Review title/author compare | `text_utils.web_titles_match()`, `web_authors_match()`, `WebMetadataWindow._compare_scalar_field()` |
| Field diff table | `WebMetadataWindow.compute_field_differences()` |
| Import compare | `text_utils.pre_normalize_title()`, `compare_normalize_title()` |
| Import UI | `ImportValidator.is_duplicate_fast()` (book list + folder), `BookListImportWindow.update_read_dates()` |

---

## Summary

- **Web fetch works in two steps:** fuzzy **pick** (path A) then cosmetic-tolerant **field diff** for the UI (path B).
- **Series is not part of web fetch or the review window**; edit series elsewhere.
- **Book list import** (path C) still uses exact keys after shared prep; it remains separate from web review matching.

---

*Document purpose: developer/agent reference. Last aligned with codebase: September 2026.*
