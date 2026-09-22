# Bulk Web Metadata Fetch — Version 3 Phase 2

**Status:** Complete — **tester accepted**  
**Created:** June 2026  
**Updated:** September 2026  
**Related:** [Web Metadata](../help_docs/07_web_metadata.md), [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

Queue **web metadata fetch** for multiple selected books with progress, cancel, an accessible summary dialog, and Apply all / Review each — not one-at-a-time only.

Depends on **Phase 1** (background worker; tester accepted Alt+W after the API split). Does **not** wait on ratings or covers; v3 applies fields AbCS already stores (title, author, plot, year, genre, comments).

---

## Done

### Entry point

- Main window when **two or more** books are selected: footer **Web fetch**, toolbar **Search Web**, or **Alt+W** (same batch).
- One selected book, or no selection: **Alt+W** and Search Web fetch that book only.
- Main window has **no Alt+B** for batch fetch.

### Progress

Worker thread runs `collect_batch_results` (sync `get_book_metadata` per book, shared cancel `Event`). Dialog: current title, N of M, Escape cancel (no Cancel button). The window opens about one third wider than the first build and stays that width; long titles wrap. The progress bar is thicker and uses the highlight color. Failures log a row; the queue continues unless canceled.

Each book may call Google at most twice. That cap starts over on the next book. There is no wait between books. A real Google Books 429 starts the usual cooldown (about 15 minutes). Later books in that batch, and any batch while the pause is on, are not sent to Google. Open Library and WikiData are still tried. One 429 per pause is expected on a larger batch; it is not a wiring failure.

### Summary

Modal [`BatchWebFetchSummaryDialog`](../src/ui/batch_web_fetch_summary.py): `raise_()` / `activateWindow()`, focus on the first list row. Apply all and Review are **not** default buttons, so Enter in the list does not run them.

Issue column (spoken in full): **Plot found**, **Metadata found**, **Plot and metadata up to date.**, **No match found**, or **Match found. No plot was found.** A Google-only miss uses **No match found**, not a Google error in the cell. Title and Issue both stretch when the window is widened. The dialog starts wide enough that the Issue text is not cut off.

When Google Books was not searched because of the limit, the summary at the top adds **Google Books limit hit. Try in N minutes.** The number is the time left on the pause.

With a screen reader, the status bar is **Alt+A Apply all**, **Alt+R Review** (or Review each), and Escape. Without a screen reader, the status bar is the count line. Arrowing the list does not re-read the status bar.

Buttons: **Apply all**, **Review** (one book with changes) or **Review each** (two or more). Escape closes the summary (no Cancel button). There is no per-row Save/Review prompt.

### Review each

[`WebMetadataWindow`](../src/ui/web_metadata.py) with `queue_index` / `queue_total` only when **more than one** book is in the queue. A single-book review does not say “1 of 1” and does not show Skip. The summary is **hidden** during review. Save or Skip (Alt+K) returns to the summary (and advances when there are multiple books) without re-speaking the queue status. Web metadata F1 does not list Series or Series #.

### Apply all

Uses `compute_field_differences` / `web_data_offers_changes`. Status announce on the main window. Focus back to the table.

---

## Related v3 work (not this phase)

- Leading A/An/The compare: [plan_leading_article_title_compare.md](plan_leading_article_title_compare.md) (Phase 3).
- Selection-mode toolbar/shortcuts: [plan_selection_mode_toolbar.md](plan_selection_mode_toolbar.md) (Phase 4).
- Non-modal fetch jobs: [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md). Skipped for v3. Progress stays modal.

---

## Tester gate

Passed.

1. Footer **Web fetch** appears only with two or more selected. Search Web stays enabled.
2. Alt+W, Search Web, and Web fetch run the same queue when two or more are selected. One book stays a single fetch. No main-window Alt+B.
3. Progress N of M spoken; Escape stops the rest.
4. Summary: Issue column uses the short plot, metadata, no-match, and no-plot wording. A Google limit is only on the top summary (**Google Books limit hit. Try in N minutes.**). Enter does nothing. Apply all and Review work. Save/Skip return to the summary.
5. Escape closes the summary. Focus returns to the table.

---

## Tests

`test/test_batch_web_fetch.py`: outcome counts; queue cancel; per-book fetch; Apply all field apply; Issue labels; Enter does not apply; Review keeps the summary open and hides it during review. Main-window registry does **not** include Alt+B. Full suite: `python -m pytest test/`.

---

## Accessibility

Follow the master checklist: [Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases).

- Progress: announce on `showEvent`; Escape cancel; GUI-thread bridge.
- Summary: modal `AccessibleDialog` — never Calibre’s NoFocus overlay.
- Footer button: same modern footer style as Update / Delete; accessible name/description; Alt+W.
- Summary buttons: `build_accessible_button_style`; not auto-default, so Enter in the list does not activate them.

---

## Out of scope v1

Fully unattended auto-save all fields; parallel HTTP per book; “all visible filtered books” entry (multi-select only); ratings/covers (deferred features).
