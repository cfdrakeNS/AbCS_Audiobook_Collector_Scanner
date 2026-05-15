read these 2 document to understand the accessible approach used thru the app. 
pySide6_accessible_dialogue and PySide6_Screen_Reader_Accessibility_Best_Practices located in the doc folder. 
Then create a plan to address the following issues. Group down the changes by window for testing.
95. Accessible events – change timing from hard coded 300ms to be based on screen reader; jaws 300ms, nvda 1500ms, orca 800ms. No screen reader 0ms. See screen_reader as it check for a screen reader.

96. import window –
- 1. the import should be applying the format filter prior to scanning the file when it creates the directory list. Improve import time in some cases.  
- 2. check to see why there is hard coded “reader” text. Reader should be found by checking the composer tag then if empty 
look in comments for the words defined in the reader keywords in preferences window.
- 3. Comment are not accumulating. If not the same they should be accumulated. Some books have plot in comments.
97. Statistic window -
- 1. collection that have zero books are not showing
-2. change the table so that the label and the value speak as you arrow up/down

I’ll open the plan file I created and show you the contents in the chat.

# Plan

The plan is saved at:

[C:\Users\cfran\.windsurf\plans\accessibility-import-statistics-fixes-a504df.md](cci:7://file:///C:/Users/cfran/.windsurf/plans/accessibility-import-statistics-fixes-a504df.md:0:0-0:0)

## Contents

```markdown
# Accessibility, Import, and Statistics Fix Plan

This plan addresses accessible event timing, import metadata/scanning behavior, and Statistics window collection/table accessibility while grouping changes by window for testing.

## Cross-App Accessibility Events

- **Files:** [src/accessibility/accessible_events.py](cci:7://file:///c:/projects/abcs/src/accessibility/accessible_events.py:0:0-0:0), [src/accessibility/screen_reader.py](cci:7://file:///c:/projects/abcs/src/accessibility/screen_reader.py:0:0-0:0)
- **Change:** Replace the hard-coded 300 ms status focus-restore delay with a helper that returns delay by detected screen reader.
- **Timing rules:** JAWS 300 ms, NVDA 1500 ms, Orca 800 ms, no screen reader 0 ms.
- **Detection approach:** Extend [screen_reader.py](cci:7://file:///c:/projects/abcs/src/accessibility/screen_reader.py:0:0-0:0) beyond [is_screen_reader_active()](cci:1://file:///c:/projects/abcs/src/accessibility/screen_reader.py:12:0-40:16) so callers can identify the active reader name/type, while preserving existing boolean behavior for compatibility.
- **Accessibility risk:** Keep focus restoration predictable and only use focus movement when accessibility is active and announcement was requested.
- **Testing:** Trigger status announcements with `Alt+/` and operation status updates under JAWS, NVDA, Orca if available, and with no screen reader process running.

## Import Window

- **Files:** [src/ui/import_window.py](cci:7://file:///c:/projects/abcs/src/ui/import_window.py:0:0-0:0), [src/core/tag_reader.py](cci:7://file:///c:/projects/abcs/src/core/tag_reader.py:0:0-0:0), [src/core/import_scanner.py](cci:7://file:///c:/projects/abcs/src/core/import_scanner.py:0:0-0:0), possibly tests if existing coverage is found.
- **Format filter before scanning:** Confirm `allowed_extensions` is loaded from preferences and passed into [BookScanner.scan_folder()](cci:1://file:///c:/projects/abcs/src/core/tag_reader.py:291:4-413:21) before directory walking/tag reads. Tighten the scan path so unsupported files are excluded while building the audio file list, including single-file mode.
- **Reader/narrator extraction:** Remove hard-coded reader keyword logic from [TagReader.extract_narrator()](cci:1://file:///c:/projects/abcs/src/core/tag_reader.py:244:4-279:17) and make reader extraction follow the app preference rule: use composer first, then inspect comments using the configured reader keywords from Preferences.
- **Keyword flow:** Ensure [ImportWindow.load_preferences()](cci:1://file:///c:/projects/abcs/src/ui/import_window.py:561:4-633:29) passes reader keywords into the scan/extraction path, not only into post-scan [ImportScanner.apply_preferences()](cci:1://file:///c:/projects/abcs/src/core/import_scanner.py:78:4-181:17).
- **Comment accumulation:** Fix tag reading so multiple comments from the same file format are preserved where available, and keep unique comments accumulated across files in a book. Avoid dropping plot comments when the first comment is not the only meaningful comment.
- **Data compatibility:** Preserve current fields: imported reader still maps to `Book.reader`, and accumulated comments still map to `Book.comments` through `book['comment']`.
- **Testing:** In Import Window, test folder import with mixed audio/non-audio files, single-item import, composer narrator, comment-based narrator using custom Preferences keywords, and multiple distinct comments/plot text across tracks.

## Preferences Window

- **Files:** [src/ui/preferences_window.py](cci:7://file:///c:/projects/abcs/src/ui/preferences_window.py:0:0-0:0)
- **Change:** No UI redesign expected; verify existing Reader Keywords field remains the source of truth.
- **Behavior to preserve:** Comma-separated reader keywords continue saving to `import/reader_keywords` and restore defaults to `reader, read by, narrator, narrated by`.
- **Testing:** Change Reader Keywords, save Preferences, reopen Import Window, and confirm the updated keywords drive comment-based reader extraction.

## Statistics Window

- **Files:** [src/database/queries.py](cci:7://file:///c:/projects/abcs/src/database/queries.py:0:0-0:0), [src/ui/statistics_dialog.py](cci:7://file:///c:/projects/abcs/src/ui/statistics_dialog.py:0:0-0:0)
- **Zero-book collections:** Update [StatisticsQueries.get_statistics()](cci:1://file:///c:/projects/abcs/src/database/queries.py:637:4-708:20) collection breakdown to match the current `total_collections` definition: include all collections, including zero-book collections; preserve inactive collection suffix labeling.
- **No Collection row:** Keep `No Collection` only when it has books, unless a product decision later says otherwise.
- **Table speech:** Change the Statistics table so arrowing up/down speaks the statistic label and value together. Likely set `Qt.AccessibleTextRole` on both cells to combined text such as `Collection Name: 0`, and use selectable/focusable table behavior rather than `NoSelection`/`NoFocus` conflict.
- **Visual layout:** Keep the two-column visual table unless testing shows a one-column accessible row is more reliable.
- **Testing:** Open Statistics from Main Window and arrow through rows. Confirm rows announce label plus value, zero-book collections are listed, inactive labels remain clear, and row headers do not add noise.

## Suggested Test Grouping

- **Global status/event tests:** Main Window, Import Window, Preferences Window status announcements.
- **Import Window tests:** Scan performance/filter behavior, reader extraction, comment accumulation, add/import results.
- **Preferences Window tests:** Reader Keywords save/load/defaults.
- **Statistics Window tests:** Collection breakdown contents and screen reader row announcements.

## Open Implementation Notes

- [screen_reader.py](cci:7://file:///c:/projects/abcs/src/accessibility/screen_reader.py:0:0-0:0) currently returns only a boolean; implementation should add a reader-name helper without breaking existing callers.
- [TagReader.extract_narrator()](cci:1://file:///c:/projects/abcs/src/core/tag_reader.py:244:4-279:17) currently contains fixed patterns and does not accept preference keywords; implementation should either accept keywords directly or move all comment keyword extraction into [ImportScanner](cci:2://file:///c:/projects/abcs/src/core/import_scanner.py:7:0-399:32) after composer is copied into scanned data.
- [StatisticsQueries.get_statistics()](cci:1://file:///c:/projects/abcs/src/database/queries.py:637:4-708:20) currently filters `WHERE book_count > 0`, which is the direct cause of zero-book collections not showing.
```

## Status

- **Plan displayed:** Yes.
- **Code changes:** None yet.
- **Next step:** Confirm when you want me to start implementation.