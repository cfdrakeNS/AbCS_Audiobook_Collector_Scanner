# Web Fetch Background Thread + Module Split — Version 3 Phase 1

**Status:** Complete — tester accepted Alt+W after the split (September 2026)  
**Created:** September 2026  
**Related:** [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [help_docs/07_web_metadata.md](../help_docs/07_web_metadata.md)

---

## What this is

Version 3 Phase 1 finishes the last web-fetch work: **background thread** and **split of `web_book_api.py`**.

Phases 1–5 already shipped in 2.10: fetch budget, cooperative cancel, shared HTTP helper, effective cache, `web_fetch_service`, removal of inert title/author formatting prefs.

---

## Tester gate

Passed. Alt+W from main and Book Details matches the threaded fetch. Google Books 429 / `web_source_cooldowns.json` is quota cooldown, not a split regression.

---

## Done

### 0 — JAWS spike (tester accepted)

Fake worker drove the real progress dialog, then a completion dialog. Progress spoken; Escape cancel; completion announced.

### A — Background thread (tester accepted)

- `WebBookAPI.get_book_metadata` runs on a `QObject` worker on a `QThread` via [`web_fetch_service.py`](../src/web/web_fetch_service.py).
- `fetch_web_metadata_for_book` still **blocks** with `popup.exec()` and returns `WebFetchResult`.
- Progress and completion use queued signals. GUI-thread `@Slot` bridge installs the wait-dialog event filter (not the worker).
- Cancel uses `threading.Event` plus `_user_canceled` so shutdown does not look like Escape.
- Initial announce is in `showEvent` on [`WebFetchProgressDialog`](../src/ui/web_fetch_progress.py).
- Escape only — no Cancel button, no Alt+C on the wait dialog.

### B — Split `web_book_api.py`

Public API unchanged (`WebBookAPI`, `get_web_api`, re-exported HTTP/matching/cache names).

| Module | Responsibility |
|--------|----------------|
| [`web_http.py`](../src/web/web_http.py) | `_http_get_json`, urlopen, cooldown, budget, User-Agent, `WEB_CACHE_FILE` |
| [`web_matching.py`](../src/web/web_matching.py) | STOPWORDS, honorifics, Orwell tokens |
| [`web_cache.py`](../src/web/web_cache.py) | TTL / cache-size constants |
| [`web_book_api.py`](../src/web/web_book_api.py) | Facade + `WebBookAPI` (per-source fetch and plot enrich stay here) |

Per-source Open Library / Google Books / WikiData / Wikipedia and plot enrich were **not** extracted. That keeps the split small and patch targets stable.

**Test patches:** `src.web.web_http.urllib.request.urlopen` and `src.web.web_http.time.sleep`. `WebBookAPI._fetch_from_*` still patched on the class. Tests that patch `src.web.web_book_api._http_get_json` still work (facade global).

Plot-length fixtures in `test_clean_web_data_for_storage_strips_series_keys` and `test_cache_hit_strips_legacy_series_keys` now use plots of at least `PLOT_MIN_LENGTH` (80).

Web tests: `test_web_api_unit.py`, `test_web_api_fetch.py`, `test_web_api_series.py`, `test_web_fetch_ui.py` — 81 passed.

---

## Accessibility

Follow the master checklist: [Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases).

- Progress dialog: announce on `showEvent`; Escape cancel; status updates on the GUI thread only (QObject bridge).
- Completion dialog: `raise_()` + `activateWindow()` + focus default button; styled via `exec_styled_message_box` or `AccessibleDialog` + `build_accessible_button_style`.
- Do not install event filters or touch widgets from the worker thread.
- Never use Calibre’s non-modal NoFocus overlay for anything the user must answer.

---

## Out of scope

- Bulk multi-book queue ([plan_bulk_web_metadata.md](plan_bulk_web_metadata.md)) — Phase 2.
- Non-modal keep-using-the-app jobs ([plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md)) — skipped for v3.
- Extracting per-source / enrich modules — later follow-on, not required to close Phase 1.
- Parallel sources / merge-quality rework — later follow-on.
- New metadata sources.
