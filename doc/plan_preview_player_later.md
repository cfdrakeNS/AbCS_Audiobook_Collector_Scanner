# Preview player — later (after version 3)

**Status:** Deferred after version 3. Do not build with Phase 15.  
**Created:** September 2026  
**Related:** [plan_preview_cover.md](plan_preview_cover.md), [plan_audiobook_preview.md](plan_audiobook_preview.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

Phase 15 shows embedded cover art only. This plan is the rest of the tester’s player requests.

---

## Next and previous

Move to the next or previous audio file in the same folder. Keep the file-name sort. Help keeps the note that chapter 10 can sort before chapter 2.

## Fast-forward and rewind

Seek 30 seconds on the current file. Buttons plus shortcuts. Speak the new position in the status bar.

## Speed

One speed for every book, stored in `QSettings` (same store as zoom). Default 1.0. Changing it in Preview updates that setting. Not a column on the book.

## Resume

New nullable columns on `books`: position in milliseconds, and the file name when the book is a folder. Same in-place upgrade pattern as `series_number` in `src/database/connection.py`.

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
- Help in `help_docs/03_find_filters.md` when this is built.

## Gate (when built)

Next and previous change files. Fast-forward and rewind move 30 seconds and are spoken. Speed survives from one book to the next without a database column. Escape keeps a per-book position. The in-progress filter lists only books that have a saved position.
