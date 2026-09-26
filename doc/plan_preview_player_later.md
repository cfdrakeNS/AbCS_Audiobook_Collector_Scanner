# Preview player — Version 3 Phase 21

**Status:** Implemented — Version 3 Phase 21. Resume uses the Phase 19 listening-position and file-name columns. Do not add a second progress store. Help review is last.  
**Created:** September 2026  
**Related:** [plan_preview_cover.md](plan_preview_cover.md), [plan_audiobook_preview.md](plan_audiobook_preview.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

Phase 15 shows embedded cover art only. This plan is the rest of the tester’s player requests.

---

## Next and previous

Move to the next or previous audio file in the same folder. Order by the track number stored in the file, not by file name. A value such as `4/24` uses 4. When a disc number is present, sort by disc, then track. Files with no track number come last, ordered by file name. The file Preview starts on uses this same order. No new database column. Help no longer says chapter 10 can sort before chapter 2.

## Fast-forward and rewind

Seek 30 seconds on the current file. Buttons plus shortcuts. Speak the new position in the status bar.

## Speed

One speed for every book, stored in `QSettings` (same store as zoom). Default 1.0. Changing it in Preview updates that setting. Not a column on the book.

## Resume

Phase 19 columns on `books`: `listen_position_ms`, and `listen_file_name` when the book is a folder. Do not add another pair.

- Escape closes Preview and keeps the position.
- Reaching the end of the last file clears it.
- Opening Preview seeks to the saved spot.

## In progress

A book is in progress when a resume position is saved.

- Main window filter, same pattern as Read: **View** menu and a toolbar control.
- Choices: **All** and **In progress**.
- Name it in the filter summary.
- Add it to the Escape clear order after the Read filter.
- Clearing the filter does not delete saved positions.
- Help in `help_docs/03_find_filters.md`.

## Gate (when built)

Next and previous follow track number, then disc number when it is present. Fast-forward and rewind move 30 seconds and are spoken. Speed survives from one book to the next without a database column. Escape keeps a per-book position. The in-progress filter lists only books that have a saved position.

### Implementation

| Area | Location |
|------|----------|
| Track/disc playlist | [`src/core/audio_launcher.py`](../src/core/audio_launcher.py) |
| Transport, speed, resume | [`src/ui/preview_window.py`](../src/ui/preview_window.py) |
| Save position | `BookQueries.update_listen_progress` in [`src/database/queries.py`](../src/database/queries.py) |
| In progress filter | [`SearchFilter.in_progress_filter`](../src/database/models.py), main window View + toolbar |
| Help | [`help_docs/04_book_details.md`](../help_docs/04_book_details.md), [`help_docs/03_find_filters.md`](../help_docs/03_find_filters.md), [`help_docs/16_shortcuts.md`](../help_docs/16_shortcuts.md) |
