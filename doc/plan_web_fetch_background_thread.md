# Web Fetch Background Thread + Module Split — Version 3 Phase 1

**Status:** Planned — **Version 3 Phase 1**  
**Created:** September 2026  
**Related:** [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [help_docs/07_web_metadata.md](../help_docs/07_web_metadata.md)

---

## What this is

Finish **Phase 6** of the web metadata fetch improvements (background thread **and** split of `web_book_api.py`). This is **version 3 Phase 1**.

Phases 1–5 already shipped: fetch budget, cooperative cancel, shared HTTP helper, effective cache, `web_fetch_service`, removal of inert title/author formatting prefs. Fetch still runs on the **GUI thread**; cancel only applies between requests.

---

## Problem

A single `urlopen` (up to ~10s) can freeze the UI until that request returns. The wait dialog and Escape/Alt+C cancel work, but the app is not fully responsive during network I/O. The API module remains a large monolith (~2.4k lines), which makes bulk fetch harder.

---

## Design

### 0 — Throwaway JAWS spike (before production code)

Fake worker emits progress strings with sleeps, drives the real [`WebFetchProgressDialog`](../src/ui/web_fetch_progress.py), then opens a real completion dialog. Scratch script or harness addition.

Verify with JAWS (NVDA optional):

1. Progress spoken while the worker runs.
2. App accepts Tab/arrows during the fetch (work left the GUI thread).
3. Completion in foreground: result dialog announced with title and default button.
4. Completion after Alt+Tab away and back — if silent, fix with `raise_()` + `activateWindow()` + focus on default button before announce.
5. Cancel (Escape / Alt+C) announced; focus returns to table or title field.

Only proceed when 1–5 pass.

### A — Background thread

- Move `WebBookAPI.get_book_metadata` (via [`web_fetch_service.py`](../src/web/web_fetch_service.py)) onto a `QObject` worker on a `QThread`.
- Keep **`fetch_web_metadata_for_book` blocking**: start worker, `popup.exec()`, return `WebFetchResult` as today. All call sites (Alt+W in main window, Book Details, Web Metadata refresh) use the worker.
- Progress and completion via Qt **queued** signals so announcements stay on the GUI thread.
- Cancel: replace bool `popup.cancel_requested` with a `threading.Event` set from the GUI thread; worker checks the event.
- `QDialog.exec()` does not call Python `show()` — move `announce_dialog_opened()` / initial timer from `show()` into `showEvent`, or call `show()` before `exec()`.
- First production background thread — no UI calls from the worker.

### B — Split `web_book_api.py` (after the thread)

Do the thread first, then the split, so test patch targets move only once.

| Module | Responsibility |
|--------|----------------|
| `http` / shared helpers | `_http_get_json`, cooldown, budget, User-Agent |
| `matching` | Title/author match scoring |
| `cache` | Persistent / in-memory cache |
| Per-source | Open Library, Google Books, WikiData, Wikipedia |
| `enrich` | Plot enrichment |
| Facade | `WebBookAPI` / `get_web_api` public API unchanged |

Update patches that currently target `src.web.web_book_api.urllib.request.urlopen`, `_http_get_json`, `_fetch_from_*`, and `src.web.web_fetch_service.get_web_api`.

---

## Accessibility

- Progress announcements must not move to the worker thread.
- Cancel (Escape / Alt+C) remains keyboard-reachable; status announces cancel/complete.
- Focus restore after fetch unchanged (main table / Book Details title).
- Never use Calibre’s non-modal NoFocus overlay for anything the user must answer.

---

## Tests

- Worker completes and emits cleaned result on the GUI thread.
- Cancel mid-fetch yields `_canceled` without crashing.
- Existing web API / fetch tests still pass after the module split.
- Optional: fix plot-length fixtures in `test_clean_web_data_for_storage_strips_series_keys` and `test_cache_hit_strips_legacy_series_keys` (short plots dropped by `PLOT_MIN_LENGTH` 80).

---

## Estimate

~3–5 days (spike + thread + careful split + a11y/regression).

---

## Out of scope

- Bulk multi-book queue ([plan_bulk_web_metadata.md](plan_bulk_web_metadata.md)) — Phase 2.
- Parallel sources / merge-quality rework — later follow-on.
- New metadata sources.
