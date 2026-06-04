# AbCS Web Fetch Improvement Plan

## Overview

The app uses two modules to retrieve book data from the web.

- **`src/web/web_book_api.py`** — all network calls, matching logic, plot enrichment. No UI.
- **`src/ui/web_metadata.py`** — the window that shows DB vs. web data side by side and lets the user choose which fields to keep.

The split is good. The improvements below keep that design and make both modules more reliable, accurate, and easier to maintain.

---

## Section 1 — web_book_api.py (network and matching)

### 1.1  Silent exception swallowing

**Current behaviour:** Every source (`_fetch_from_open_library`, `_fetch_from_google_books`, `_fetch_from_wikidata`) has a bare `except Exception: pass`. When a fetch fails (timeout, network error, API rate limit 429) no information is preserved. The UI can only tell the user "nothing found" with no clue why.

**Improvement:** Capture the last error per source and surface it as an optional `fetch_errors` list in the returned metadata dict when debugging is needed. At minimum, pass the last exception message up to `get_book_metadata` so `main_window.py` and `book_details.py` can show it in their "No Web Data Found" message box (they already have a `last_error` variable but it only catches exceptions in the outer try block).

### 1.2  Cache is per-process only and always discarded on restart

**Current behaviour:** `_cache` is an in-memory dict with a 5-minute TTL. Every restart throws away cached results, so the same book looked up twice in different sessions hits the network again.

**Improvement options (pick one):**
- Persist the cache to a small JSON file in `data/` (e.g. `web_cache.json`) with per-entry timestamps. Load on startup, save on write. This requires a simple read/write helper and a max-size guard (e.g. 200 entries, evict oldest).
- Use SQLite (already present) with a `web_cache` table: `(cache_key TEXT PRIMARY KEY, result TEXT, fetched_at REAL)`. Queries can expire entries automatically. Cleanest long-term solution.

### 1.3  Network timeouts are inconsistent

**Current behaviour:** Open Library search uses 10 s, work detail uses 6 s, Google uses 6 s, Wikipedia uses 8 s, WikiData uses 6 s. None have retries.

**Improvement:** Centralise timeouts as module-level constants so they are easy to tune. Add a simple retry-once on `urllib.error.URLError` (not on HTTP 429/4xx). Example:

```python
TIMEOUT_SEARCH = 10      # seconds - primary searches
TIMEOUT_DETAIL = 6       # seconds - secondary calls (work description, extract)
TIMEOUT_RETRY_DELAY = 1  # seconds before one retry
```

### 1.4  Title matching is word-bag only (no word-order or length penalty)

**Current behaviour:** `_title_matches` requires 50 % of DB title words to appear in the web title. This allows "Date Night" to match "Date Night Club" (2/2 words, 100 %). The broadened-search pass and `match_author` fix prevent wrong-author results, but a longer web title with the right author still passes.

**Improvement:** Add a soft length penalty. If the web title has significantly more non-stopword words than the DB title, apply a small penalty but do not hard-reject. Example: if `len(web_words) > len(db_words) * 2` reduce the score. This keeps flexibility for subtitles while discouraging unrelated books that happen to contain the right words.

### 1.5  Author matching is last-name only

**Current behaviour:** `_author_matches` checks that the DB last name appears anywhere in the web author string. This is intentionally permissive (handles "Jane Austen" vs "Austen, Jane") but can match coincidental last name overlaps (e.g. "King" matches both Stephen King and Laurie R. King).

**Improvement:** When both DB and web author have more than one word, also check that at least one non-last-name part (first name or initials) overlaps. Fall back to last-name-only if either side has only one word.

### 1.6  `_fetch_plot_from_open_library` is now redundant

**Current behaviour:** `_fetch_plot_from_open_library` does a second loose Open Library search to find a description. Since the unified `_enrich_metadata_plot` now uses `open_library_work_key` from the winning match doc, this method is only ever called if there is no work key (rare).

**Improvement:** Remove `_fetch_plot_from_open_library` or convert it to a private helper called only from `_enrich_metadata_plot` when `open_library_work_key` is absent. Reduces one redundant search call per Google/WikiData win.

### 1.7  WikiData rarely returns plot or rating

**Current behaviour:** WikiData is used for title, author, and series when Open Library and Google both fail. The SPARQL query does not return a description, plot, or rating. `_enrich_metadata_plot` then tries Wikipedia for plot regardless.

**Improvement:** When WikiData wins, try the Wikipedia REST summary endpoint (`https://en.wikipedia.org/api/rest_v1/page/summary/{title}`) using the matched book title. This returns a clean `extract` field in one call with no search step, which is faster and more reliable than the current two-step Wikipedia search + extract flow.

### 1.8  Google Books retry adds an extra network call

**Current behaviour:** `_fetch_from_google_books` now tries `intitle + inauthor` then `intitle` only if the first attempt returns nothing. This means up to two Google calls per book.

**Improvement:** On the second attempt (title only), reduce `maxResults` from 10 to 5. The chance of finding the right book in positions 6–10 when positions 1–5 did not match is very low, and the smaller payload saves bandwidth and parse time.

### 1.9  No distinction between "API unreachable" and "no match found"

**Current behaviour:** Both are treated as `None` return. The user sees "No Web Data Found" for both.

**Improvement:** Return a sentinel `{"_no_match": True}` or raise a custom `WebFetchError(source, reason)` exception so callers can distinguish "network problem" from "clean miss". The UI can then say "Unable to reach Open Library" vs "No data found for this title" which is more useful to the user.

---

## Section 2 — web_metadata.py (the window)

### 2.1  `clean_web_data_for_storage` is called in the window, not in the API

**Current behaviour:** `load_book_data` in `web_metadata.py` instantiates a fresh `WebBookAPI()` just to call `clean_web_data_for_storage`. This creates a throwaway object and mixes storage transformation into the display layer.

**Improvement:** Move `clean_web_data_for_storage` to a module-level function (or a separate `web_data_cleaner.py`) so it can be called without constructing the full API client. The window imports the function directly; no API object needed at display time.

### 2.2  `normalize_db_title` is duplicated

**Current behaviour:** `WebMetadataWindow.normalize_db_title` is a `@staticmethod` inside the window class. `WebBookAPI._move_article_to_beginning` does overlapping work.

**Improvement:** Consolidate into a single `normalize_title` function in a shared utility module (or in `web_book_api.py`). Both classes import and call the same function.

### 2.3  `update_fields_with_web_data` does field comparison and UI visibility in one long method

**Current behaviour:** The method is about 170 lines, handling comparison, normalisation, visibility toggling, and checkbox state for every field in sequence. Adding a new field requires editing this method in several places.

**Improvement:** Extract a `_FieldRow` helper dataclass or named tuple that pairs (db_value, web_value, edit_widget, checkbox_widget, field_name). Iterate a list of rows in a loop. New fields are added by appending to the list, not by editing comparison logic.

### 2.4  Plot is the only field stored to DB as comments; no field for rating

**Current behaviour:** Plot and rating are concatenated into a single string and saved to `book.comments`. Rating disappears from the DB as structured data.

**Improvement:** If the `Book` model or DB schema is ever extended to add a `rating` column, the web metadata window already receives `rating` and `ratings_count` from the API. The window currently discards structured rating data. A future improvement (separate task) would add `rating` to `Book` and the `books` table, and wire it through the window.

### 2.5  Retry / re-fetch button is absent

**Current behaviour:** If the web data fetch in `main_window.py` returns `None`, the window never opens. If data is stale or wrong, the user must close the book and try again.

**Improvement:** Add a **Re-fetch** button (Alt+R or separate from Restore Defaults) inside the web metadata window that calls `get_book_metadata` with `refresh=1` (skip Open Library, try Google then WikiData). This lets the user try an alternative source without leaving the window. Wire it to the existing `WebBookAPI` and call `update_fields_with_web_data` with the new result.

### 2.6  No progress indication during fetch

**Current behaviour:** `main_window.py` and `book_details.py` show a modal "Please wait" dialog while fetching. That dialog is plain text with no progress bar or cancel option. Long-running WikiData SPARQL calls or Wikipedia fetches can block the UI for 15–25 seconds.

**Improvement:** Run the fetch in a `QThread` (or `QThreadPool`) and show a cancellable progress dialog. On cancellation, abort the fetch and report "Fetch cancelled" in the status bar. This is a medium-effort change but significantly improves accessibility and responsiveness.

### 2.7  `set_focus_to_first_differing_field` always focuses title

**Current behaviour:** The method is intended to focus the first field that has a web difference, but it always returns to `title_edit`. Comment says "Always start with title field for accessibility."

**Improvement or confirm:** If this is intentional (title is always the right starting point for screen reader users), the function body and the docstring should match. If not intentional, implement the loop: iterate `field_differences` keys in display order and focus the first matching web edit field. Either decision should be documented.

---

## Section 3 — Architecture (longer-term)

### 3.1  Consider making `WebBookAPI` async

**Current behaviour:** All network calls use the synchronous `urllib.request.urlopen`. The UI works around this with `QThread`. Three sources (Open Library, Google, WikiData) are tried sequentially.

**Improvement (longer term):** Use Python `asyncio` + `aiohttp` and run all three primary sources in parallel. Plot enrichment (Open Library work detail + Wikipedia) could also run concurrently. On fast connections this could reduce Fetch Web Info from ~15 seconds to ~5 seconds. Requires adding `aiohttp` to `requirements.txt` and a small async runner bridge for Qt.

### 3.2  Consider an Open Library ISBN lookup path

**Current behaviour:** ISBN is requested from Open Library and Google but is only stored for display; it is not used for lookup.

**Improvement:** If ISBN is already in the DB (imported from a tag or previous web fetch), try `https://openlibrary.org/isbn/{isbn}.json` first. ISBN lookups are exact and always return the right edition, avoiding all title/author matching complexity. This is low-cost to add as a pre-pass in `get_book_metadata`.

### 3.3  Persist `plot_source` to DB

**Current behaviour:** `plot_source` (`open_library`, `wikipedia`, `google_books`) is set on the metadata dict but discarded before caching and never stored.

**Improvement:** Store it in a `book_metadata_source` column (or as a prefix in `comments`). Useful for debugging which source provided the plot and for deciding whether to re-fetch with a different source on a future Re-fetch.

---

## Priority Summary

| Priority | Item | Effort | Status |
|----------|------|--------|--------|
| High | 1.1 Surface fetch errors to UI | Low | Done June 4, 2026 |
| High | 2.5 Add Re-fetch button (Alt+F) | Medium | Done June 4, 2026 |
| High | 1.6 Restructure redundant OL plot search | Low | Done June 4, 2026 |
| Medium | 1.2 Persistent JSON cache | Medium | Done June 4, 2026 |
| Medium | 2.6 Async fetch with cancel | High | Deferred — requires QThread plumbing |
| Medium | 1.7 Wikipedia REST summary for WikiData wins | Low | Done June 4, 2026 |
| Medium | 2.3 Refactor update_fields_with_web_data | Medium | Deferred — structural, no user impact |
| Low | 1.3 Centralise timeout constants | Low | Done June 4, 2026 |
| Low | 1.4 Title length penalty | Low | Done June 4, 2026 |
| Low | 1.5 First-name overlap in author match | Low | Done June 4, 2026 |
| Low | 1.8 Google retry reduced to maxResults=5 | Low | Done June 4, 2026 |
| Low | 1.9 Unreachable vs no-match distinction | Low | Done June 4, 2026 |
| Low | 2.1 Module-level clean_web_data function | Low | Done June 4, 2026 |
| Low | 2.2 Consolidate normalize_db_title | Low | Done June 4, 2026 |
| Low | 2.4 Rating/plot as structured DB fields | High | Deferred — requires schema migration |
| Low | 2.7 set_focus_to_first_differing_field docstring | Low | Done June 4, 2026 |
| Low | 3.1 Async architecture (aiohttp) | High | Deferred — worthwhile after 2.6 |
| Low | 3.2 ISBN lookup pre-pass | Low | Done June 4, 2026 |
| Low | 3.3 Persist plot_source to DB | Low | Deferred — requires schema migration |

---

*Document created June 4, 2026. Updated June 4, 2026 — 14 of 19 items implemented.*
