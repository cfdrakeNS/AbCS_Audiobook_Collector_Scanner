# Book List Import Progress Window — Future Improvement Plan

**Status:** Completed (Sep 2026, AbCS 2.09)  
**Related:** [Import Book List](../help_docs/11_import_book_list.md), [Import Book List explained](../help_docs/20_import_book_list_explained.md), [Import Progress](../src/ui/import_progress_window.py), Phase 1 series-number / Find work (Sep 2026)

Implemented in 2.09: Book List Import reuses `ImportProgressWindow` with live counters, Esc cancel keeping partial results, Esc/Alt+/ forwarding, and Shift+F1 routed to `11_import_book_list.md`. Date-flake fix for reading-history month assertion included.

**Performance (Sep 2026):** Add Books mode now uses the folder-import O(1) duplicate index, throttles `processEvents` to ~150 ms (same as folder import), caches author/series/genre ids for the run, and iterates with `itertuples` instead of `iterrows`.

## Goal

Reuse `ImportProgressWindow` during Book List Import so slow devices and large spreadsheets show live progress, allow cancel, and keep screen-reader status updates useful.

Today Book List Import runs a fully blocking GUI-thread loop over `self.file_data.iterrows()` in [`book_list_import_window.py`](../src/ui/book_list_import_window.py) with:

- No progress bar or per-row status updates
- No mid-import cancel
- No `QApplication.processEvents()` calls

---

## Why it is not a drop-in

1. **No event pumping.** The row loop never calls `processEvents()`, so a progress window would not repaint. Folder import pumps events at multiple points during scan and add.
2. **No cancel flag.** Inserts commit once after the loop finishes. **Decision:** cancel keeps what was already processed and reports `N added, N skipped` (partial results kept).
3. **Application modality.** `BookListImportWindow` is opened via `dialog.exec()` from the main window, same as folder Import. The modeless progress dialog's own Alt+/ and Escape shortcuts are blocked by modality. Rebuild the forwarding pattern from [`import_window.py`](../src/ui/import_window.py) (Esc and Alt+/ forwarded while progress is visible).
4. **Help routing.** [`help_router.py`](../src/ui/help_router.py) maps `ImportProgressWindow` to `02_import.md` (folder import). Book List Import needs a per-invocation override to `11_import_book_list.md` (Shift+F1).

---

## Counters

The progress status line shows Scanned, Added, Corrected, Errors, Warnings, Duplicates.

After Phase 1, Book List Import already tracks **added**, **duplicates**, and **errors** separately. Corrected and Warnings can pass as zero unless that window starts tracking them.

---

## Implementation sketch

1. Show `ImportProgressWindow` (parent = Book List Import window) when import starts; use compact or full mode with current title/author from the row.
2. Add `processEvents()` (throttled) inside both `import_new_books` and `update_read_dates` loops.
3. Poll `progress_window.cancel_requested`; on cancel, break the loop, commit what was already inserted (new-book mode), and report `N added, M duplicates skipped, K errors, remainder skipped`.
4. Forward Esc and Alt+/ from Book List Import to the progress window while it is visible.
5. Override Shift+F1 help topic for the progress window when owned by Book List Import.
6. Update help docs and the messages reference for cancel wording.
7. Fix the date-hardcoded flake in [`test/test_reading_history_accessibility.py`](../test/test_reading_history_accessibility.py) `test_screen_reader_announcements_structure`: it asserts the period message contains `March` / `April` / `May`, which fails outside spring as the window uses a rolling date range. Replace with a month-name pattern check (or freeze the clock) so the full suite stays green year-round. Unrelated to Book List Import progress, but do it in this phase so suite noise does not block the gate.

---

## Test / a11y gate

- Headless: cancel mid-import keeps partial inserts; counters match.
- Manual JAWS/NVDA: progress status updates are readable via Alt+/; Esc cancel confirmation; focus returns to the file field after close.
- Confirm `test_screen_reader_announcements_structure` passes on the current calendar month (item 7).

---

## Relation to other work

- Depends on Phase 1 duplicate counter (already shipped with series-number tiebreaker).
- Independent of folder-import scan optimization ideas (early skip of audio reads for known duplicates).
- Item 7 is suite hygiene discovered during Phase 1; not caused by the series-number / Find changes.
