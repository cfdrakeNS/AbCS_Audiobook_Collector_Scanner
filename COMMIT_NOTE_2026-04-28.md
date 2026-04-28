Commit Note - 2026-04-28

Summary:
- Fixed cross-collection duplicate detection for scanner import when preference is set to "Title + Author + Year".
- Corrected logic so duplicate index for this mode uses all existing books, not just books in the target collection.
- Included earlier series-handling fix for title normalization and import matching.
- Removed temporary debug output from validator settings reload.

Details:
- `src/ui/import_window.py`: conditional loading of all books for `title_author_year` duplicate matching mode.
- `src/core/validator.py`: removed debug print added during troubleshooting.
- `src/utils/text_utils.py` / import flow: series normalization fix applied earlier to ensure consistent title matching.

Testing:
- Verified settings reload still reports correct mode in debug run.
- Confirmed no syntax errors with `py -m py_compile src/ui/import_window.py src/core/validator.py`.
