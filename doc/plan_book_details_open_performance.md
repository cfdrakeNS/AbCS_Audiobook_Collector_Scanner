# Book Details Open Performance

**Status:** Implemented September 29, 2026.
**Related:** [Version 3 release roadmap](plan_enhancements_version3_release.md), [Book Details layout](plan_book_details_layout.md)

## Problem

Book Details became slower to open after the v3 Listen and embedded-cover work. Opening an existing book could synchronously resolve and scan the audiobook folder several times and read embedded cover art several times on the UI thread. Shared folders, unavailable paths, and large multi-track books made the delay more noticeable. Inspection found no evidence that closed dialogs accumulate; main_window.py already calls deleteLater().

## Implemented changes

- Suppress Listen and cover refreshes while book fields are being populated.
- Resolve one playable audiobook source once per path, collection root, and import-directory combination.
- Reuse that source for both Listen availability and embedded-cover loading.
- Use a lightweight source lookup that does not build or metadata-sort the complete playback playlist.
- Cache the decoded cover input for the current source and scale.
- Keep full playlist construction and metadata ordering for actual Listen playback.
- Isolate QSettings in main-window tests so saved user import paths cannot alter test results.

## Tests

- A Book Details regression test requires exactly one source resolution and one cover read during an ordinary open.
- An audio-launcher regression test verifies lightweight source lookup does not invoke playlist metadata sorting.
- The formerly environment-dependent Listen missing-path test now uses isolated settings.
- Targeted result: 30 passed.
- Full-suite result: 679 passed, 1 skipped.

## Follow-up only if testing remains slow

Move embedded-cover extraction to a worker thread and add opt-in timing logs for local, large multi-track, missing, and network-style paths. This is not included now because the repeated synchronous work was reduced to one lightweight lookup and one cached cover read.