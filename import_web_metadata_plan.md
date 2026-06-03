# AbCS improvement plan — web metadata, import data, import counters

**Created:** June 2, 2026  
**Status:** Planned — work not started (except removing dead `valid_books` progress argument)

This document captures the review and recommended fix order for three areas: web fetch for Librivox-heavy libraries, import time/file counts, and import error/warning counters.

---

## Overview

| Area | Problem | Goal |
|------|---------|------|
| **1. Web metadata** | Few Librivox books return web data | Smarter search and optional new sources |
| **2. Import scan** | Time and file count may be wrong or not saved after edit | Correct scan, display, and persist to library |
| **3. Import counters** | Errors/warnings can be wrong after edits | Trustworthy status bar and progress counts |

---

## 1. Web metadata (Librivox books)

### What the app does today

When you request web info, the app searches in order:

1. Open Library  
2. Google Books  
3. WikiData  

It only accepts a result if:

- At least **half** of the words in your title appear in the web title, and  
- The web **author** contains your book’s author **last name**.

If nothing passes those checks, you get **“No web data found”** — even if the APIs returned possible matches.

### Why Librivox books often fail

| Cause | Explanation |
|--------|-------------|
| **Wrong “author” in the database** | Librivox files often tag the **narrator** (reader) as artist, not the **book author** (e.g. Dickens). The app searches using that name, so matches fail. |
| **Strict matching** | A close title with the **wrong** author is rejected on purpose (avoids wrong books). |
| **Old / obscure titles** | Some classics are in Open Library; very old or oddly titled folders may still miss. |
| **No Librivox-specific source** | The app does **not** call Librivox or Internet Archive APIs — only general book databases. |
| **Extra check in Book Details** | Even when the API finds something, Book Details can still show “no data” if it decides the match is not “meaningful” (e.g. no plot and weak title match). |

**Conclusion:** Many failures are **not only** because books are too old — **author/title in the library often do not match how web catalogs list the book.**

### Planned work

#### Phase A — Diagnose (low risk)

- [ ] Add optional logging or debug mode: searched title/author, rejection reason (title vs author).  
- [ ] Manually sample 5–10 Librivox books: compare app **Author** vs **Reader/Narrator** vs Open Library listing.

#### Phase B — Search smarter (medium effort)

- [x] If author looks like narrator (matches reader field, or path/source suggests Librivox), try **title-only** search as fallback.  
- [x] Retry Open Library / Google **without author** when strict pass fails.  
- [x] Increase number of API results evaluated (10 per source).  
- [x] Align Book Details / main window with API: trust results that passed match gates.

**Key files:** `src/web/web_book_api.py`, `src/ui/book_details.py`, `src/ui/web_metadata.py`, `test/test_web_book_api_matching.py`

#### Phase C — New sources (larger effort)

- [ ] Optional Internet Archive or Librivox lookup by title (and Librivox ID from tags/path if present).  
- [ ] Keep **narrator** separate from **author** in web search logic.

#### Phase D — User control

- [ ] Web metadata window: **“Search without author”** and optional **“Show closest matches”** for manual selection.

---

## 2. Import: time and number of files

### How it works today

During folder scan:

- Each audio file is read (tags + length).  
- Files are grouped into one book (usually by **album** tag).  
- **Total length** → `time_hours` / `time_minutes` (sum of durations).  
- **File count** → `tracks` = number of files in that group.

Import detail shows time as `HH:MM` and file count from those fields. On add to library, the database stores `time_hours`, `time_minutes`, and `tracks` from scan data.

### Issues found

| Issue | Impact |
|--------|--------|
| **Time edits may not save to import list** | `_apply_detail_edits` copies only a fixed field list — **not** `time_hours` / `time_minutes`. Edited length can be lost when closing import detail. |
| **Zero length** | Unrecognized format → duration 0 → blank time and possible **“book length below minimum”** warning when files exist. |
| **File count is display-only** | Count comes from scan; wrong count needs tag/folder grouping fix, not manual edit in detail. |
| **Grouping** | Missing/wrong **album** tag can split one book or merge wrong files. |

### Planned work

- [x] Fix `_apply_detail_edits` to copy **time** (`time_hours`, `time_minutes`) from import detail back to `scanned_items`.  
- [x] Tests: assert `tracks`, `time_hours`, `time_minutes` after detail edit and `_build_book_from_scan`.  
- [x] If duration is 0 but files exist: warn **“Could not read length from audio files”** (minimum-length rule skips zero length).  
- [x] Document in preferences Import tab and import detail tooltips: **album** tag grouping guidance.  
- [ ] Optional: re-scan folder from import detail to refresh time/file count.

**Key files:** `src/core/tag_reader.py`, `src/ui/import_window.py`, `src/ui/import_detail_window.py`, `src/ui/import_window.py` (`_build_book_from_scan`)

---

## 3. Import counters (errors / warnings)

### What you see

Status bar style summary, for example:

`Scanned | Added | Corrected | Errors/Warnings | Duplicates | Filtered`

**Errors/Warnings** = error count + warning count (one combined number).

### How counting works after scan

- **Scanned** — all books processed (including auto-added).  
- **Added** — auto-added during scan (clean rows).  
- **Corrected** — fallback or autocorrect used.  
- **Errors** — hard problems (parse/read).  
- **Warnings** — warning-level issues (length, title length, etc.).  
- **Duplicates** — separate; not included in Errors/Warnings.

### Issues found

| Issue | Impact |
|--------|--------|
| **`Valid: 0` during scan** | ~~Progress showed Valid: 0 always~~ — **fixed:** removed unused `valid_books` argument (`d678d31`). Full valid counter still not implemented. |
| **Counts after editing a row** | `_refresh_summary_from_items` uses `scan_outcomes` from original scan. Import detail updates table but **does not update** `scan_outcomes` — counts can stay wrong. |
| **Discard row** | Discarded book may still be counted in Scanned/Errors from `scan_outcomes`. |
| **Read errors vs Errors** | Progress may show `read_errors` separately from Errors/Warnings — easy to misread. |
| **Combined label** | Cannot see error vs warning split without filtering the table. |

### Planned work

- [x] After import detail save or discard, update matching `scan_outcomes` (or rebuild counts from `scanned_items` only).  
- [x] Implement **valid** counter on import window status bar (review-list clean rows).  
- [x] Split status text — `Errors: N | Warnings: N` (import window status bar).  
- [x] Tests: edit away warning → counts update; discard reduces Scanned.  
- [ ] Document: duplicates are not counted under Errors/Warnings (user-facing help).

**Key files:** `src/ui/import_window.py`, `src/ui/import_progress_window.py`, `src/core/validator.py`

---

## Recommended order of work

```
1. Fix import counter sync after edit/discard
2. Fix time fields saving from import detail
3. Web: title-only fallback when author is likely narrator
4. Web: Librivox path + optional Archive source
5. Tests and manual Librivox sample audit
```

| Priority | Item | Why first |
|----------|------|-----------|
| **1** | Counter sync + valid counter | **Done** — ready for manual test |
| **2** | Time/tracks persistence + duration tests | **Done** — ready for manual test |
| **3** | Web search fallback (title-only, narrator detection) | **Done** — ready for manual test |
| **4** | New web sources + UI options | More coverage, more work |
| **5** | Automated tests + Librivox sample set | Prove fixes |

---

## Quick checks (no code)

1. **Web:** On a failed Librivox book, compare **Author** vs **Reader**. If author is the reader’s name, web fetch will usually fail until search logic changes.  
2. **Import:** After scan, open import detail — do time and files look right before add? Blank time → check format and tags.  
3. **Counters:** Note Errors/Warnings after scan, fix one row in detail, save — if numbers do not change, that matches the `scan_outcomes` sync bug.

---

## Related commits

- `3cbcfc3` — Book detail paging/sort, status bar readback, preferences/theme picker  
- `d678d31` — Remove dead `valid_books` from import scan progress (partial counter fix)

---

## Notes for tomorrow

Pick a starting priority (counters, import time/files, or web metadata) or implement **priority 1–2** together. Update this file by checking off items as they are completed.
