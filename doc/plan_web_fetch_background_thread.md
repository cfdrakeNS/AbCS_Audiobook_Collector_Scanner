# Web Fetch Background Thread + Module Split — Fall Follow-on

**Status:** Planned (deferred; Phases 1–5 of web fetch improvements are done)  
**Created:** September 2026  
**Related:** [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md), [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md), [help_docs/07_web_metadata.md](../help_docs/07_web_metadata.md)

---

## What this is

Finish **Phase 6** of the web metadata fetch improvements (chosen scope: full option — background thread **and** split of `web_book_api.py`).

Phases 1–5 already shipped: fetch budget, cooperative cancel, shared HTTP helper, effective cache, `web_fetch_service`, removal of inert title/author formatting prefs, and related cleanup. Fetch still runs on the **GUI thread**; cancel only applies between requests.

---

## Problem

A single `urlopen` (up to ~10s) can still freeze the UI until that request returns. The wait dialog and Escape/Alt+C cancel work, but the app is not fully responsive during network I/O. The API module remains a large monolith (~2k+ lines), which makes bulk fetch and future source work harder.

---

## Design

### A — Background thread

- Move `WebBookAPI.get_book_metadata` (via [web_fetch_service.py](../src/web/web_fetch_service.py)) onto a `QObject` worker on a `QThread`.
- Progress, cancel, and completion via Qt signals so [WebFetchProgressDialog](../src/ui/web_fetch_progress.py) / `FetchStatusLabel` announcements stay on the GUI thread.
- Keep cooperative `should_cancel` + fetch budget; cancel must be safe across threads (atomic flag or queued slot).
- First production background thread in AbCS — follow Qt thread rules (no UI from the worker).

### B — Split `web_book_api.py`

Suggested modules (names flexible):

| Module | Responsibility |
|--------|----------------|
| `http` / shared helpers | `_http_get_json`, cooldown, budget, User-Agent |
| `matching` | Title/author match scoring |
| `cache` | Persistent / in-memory cache |
| Per-source | Open Library, Google Books, WikiData, Wikipedia |
| `enrich` | Plot and series enrichment |
| Facade | `WebBookAPI` / `get_web_api` public API unchanged for callers |

Do the split **after** or **with** the thread work so imports and patches in tests stay stable.

---

## Accessibility

- Progress announcements must not move to the worker thread.
- Cancel (Escape / Alt+C) remains keyboard-reachable; status announces cancel/complete.
- Focus restore after fetch unchanged (main table / Book Details title).

---

## Tests

- Worker completes and emits cleaned result on the GUI thread.
- Cancel mid-fetch yields `_canceled` without crashing.
- Existing `test_web_book_api_matching.py` / `test_web_fetch_improvements.py` still pass after the module split (patch targets updated as needed).

---

## Estimate

~3–5 days (thread + careful split + a11y/regression).

---

## Out of scope

- Bulk multi-book queue ([plan_bulk_web_metadata.md](plan_bulk_web_metadata.md)) — separate plan; benefits from this work but is not this plan.
- New metadata sources.
