# Book Details cover — Version 3 Phase 17

**Status:** Implemented. Phase 16 help review is still next on the schedule. Phase 14 stays optional and last.  
**Created:** September 2026  
**Related:** [plan_preview_cover.md](plan_preview_cover.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [Plan_covers.md](Plan_covers.md)

Same picture as Preview. Read the art already inside the audio file. Do not download a cover, do not add a database column, and do not save an image file. Web covers and zip backup stay in [Plan_covers.md](Plan_covers.md).

---

## What to build

When Book Details opens a book, show the embedded cover from the same file Preview would play.

- Use [`resolve_preview_file`](../src/core/audio_launcher.py) on the book path (including the collection library root), then [`read_embedded_cover`](../src/core/audio_launcher.py).
- Show the picture at the top of [`src/ui/book_details.py`](../src/ui/book_details.py), beside the form. Do not put it inside the header card. That card is hidden while a screen reader is running, and the picture must stay available.
- Not a tab stop. Accessible name: **Cover**. Focus stays on the first field.
- If there is no embedded art, or no playable file, show no image and do not announce that it is missing.
- Refresh when the open book changes (including Next and Previous) and when the path field changes. A new book with an empty path shows no image.
- A folder of tracks uses the first audio file, the same rule as Preview.

## Help and tests

- One sentence in [`help_docs/04_book_details.md`](../help_docs/04_book_details.md).
- Reuse the cover-byte tests. Add a check that the Book Details image is hidden when there is no art, and that it is not a tab stop.

## Gate

A book whose file has embedded art shows Cover, and Tab does not stop on it. A book with no art opens with no extra announcement. The title field still takes focus.
