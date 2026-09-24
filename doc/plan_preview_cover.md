# Preview cover — Version 3 Phase 15

**Status:** Implemented. Tester build 2.18 did not show a cover until this change. Phase 16 help review is next.  
**Created:** September 2026  
**Related:** [plan_audiobook_preview.md](plan_audiobook_preview.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [Plan_covers.md](Plan_covers.md)

This is the picture already stored inside the audio file. It is not [Plan_covers.md](Plan_covers.md) (download a cover during web save, show it on Book Details and Import Detail, zip backup). That plan stays deferred after v3.

---

## What to build

When Preview plays a file that has embedded cover art, show that picture in the Preview window.

- Read the art with mutagen from the file [`resolve_preview_file`](../src/core/audio_launcher.py) returns. Mutagen is already used by [`src/core/tag_reader.py`](../src/core/tag_reader.py).
- No new database column. Do not save a copy of the image.
- Show the image beside the existing title block in [`src/ui/preview_window.py`](../src/ui/preview_window.py).
- Focus stays on **Play/Pause**. The image is not a tab stop. Accessible name: **Cover**.
- If the file has no embedded art, show no image and do not announce that it is missing.
- v3 still plays only the first file in a folder, so the cover is that file’s art.

## Help and tests

- One sentence in the Preview step of [`help_docs/04_book_details.md`](../help_docs/04_book_details.md).
- A unit test covers art bytes returned, and no art.

## Gate

A file with embedded art shows a cover that is not in the tab order. A file without art opens Preview with no extra announcement. Play/Pause still has focus.
