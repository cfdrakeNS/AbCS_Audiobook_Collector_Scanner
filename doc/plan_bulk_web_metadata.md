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

- Main window when **two or more** books are selected: footer **Web fetch** (same visibility pattern as Update / Delete).
- Shortcut **Alt+B**.
- **Alt+W stays single-book** and still returns early when multi-select is active.

### Progress

Worker thread runs `collect_batch_results` (sync `get_book_metadata` per book, shared cancel `Event`). Dialog: current title, N of M, Escape cancel (no Cancel button). Failures log a row; the queue continues unless canceled.

Google Books 429 / cooldown is unchanged from Phase 1. Large batches can still hit quota; that is expected, not a batch-wiring failure.

### Summary

Modal [`BatchWebFetchSummaryDialog`](../src/ui/batch_web_fetch_summary.py): `raise_()` / `activateWindow()`, focus default **Apply all**.

Status bar shows **counts only** (processed, new information, no match, up to date, errors) plus Apply / Review / Escape — not the highlighted title.

Buttons: **Apply all**, **Review** (one book with changes) or **Review each** (two or more). Escape discards (no Cancel button).

Enter or click a table row: **Save** / **Review** when that book has new information; otherwise an information message with the fetch reason (no match, up to date, error).

### Review each

[`WebMetadataWindow`](../src/ui/web_metadata.py) with `queue_index` / `queue_total` only when **more than one** book is in the queue. A single-book review does not say “1 of 1” and does not show Skip. Save or Skip (Alt+K) advances when there are multiple books.

### Apply all

Uses `compute_field_differences` / `web_data_offers_changes`. Status announce on the main window. Focus back to the table.

---

## Related v3 work (not this phase)

- Leading A/An/The compare: [plan_leading_article_title_compare.md](plan_leading_article_title_compare.md) (Phase 3).
- Selection-mode toolbar/shortcuts: [plan_selection_mode_toolbar.md](plan_selection_mode_toolbar.md) (Phase 4).
- Non-modal fetch jobs (keep using the app): [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) (Phase 5).

---

## Tester gate

Passed.

1. Footer **Web fetch** appears only with two or more selected.
2. Alt+B runs the queue; Alt+W still one book.
3. Progress N of M spoken; Escape stops the rest.
4. Summary announced; Apply all and Review each work; Escape discards.
5. Focus returns to the table.

---

## Tests

`test/test_batch_web_fetch.py`: outcome counts; queue cancel; per-book fetch; Apply all field apply; summary default button.

---

## Accessibility

Follow the master checklist: [Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases).

- Progress: announce on `showEvent`; Escape cancel; GUI-thread bridge.
- Summary: modal `AccessibleDialog` — never Calibre’s NoFocus overlay.
- Footer button: same modern footer style as Update / Delete; accessible name/description; Alt+B.
- Summary buttons: `build_accessible_button_style`; default Apply all.

---

## Out of scope v1

Fully unattended auto-save all fields; parallel HTTP per book; “all visible filtered books” entry (multi-select only); ratings/covers (deferred features).
