# Changes for Testing — July 19, 2026

Plain-language summary of today's bug fixes and changes.

## Bug fixes

1. Help window: pressing Enter while reading help text no longer shrinks the text (zoom out). Enter on the section list still jumps to that section. Ctrl+Minus and Ctrl+Plus still zoom.

2. Table grid lines were missing: the boxes around each cell are back in the Main window book list, Import review list, and Reading History tables. These were lost in a June change.

3. Dark themes: grid lines and borders were almost invisible on dark themes. They are now clearly visible on every theme, dark and light.

4. Book Details: the "Sorted by" line at the top was never showing, even without a screen reader running. It now appears whenever no screen reader is running.

## Changes

5. Name List, Collections, and Backup/Restore windows: removed the boxes around each cell in their lists. They are simple lists, and the full grid looked cluttered.

6. Book Details header card (new): when no screen reader is running, the top of Book Details shows a panel with the book title in large bold text, plus author and series below it. With JAWS or NVDA running it is hidden and never spoken. Note: the app checks for a screen reader when the window opens, so start or exit the screen reader before opening Book Details.

7. Button highlights: buttons no longer have a permanent colored border (previously Import and Book List Import each showed two "lit up" buttons). Now only the button with keyboard focus lights up. Important buttons still use bold text.

8. Import window: Add Selected and Export are disabled (grayed out) until a scan finds books. The error filter is disabled until the scan results include at least one issue. Tab skips disabled controls, so a fresh Import window goes straight from Scan to the table.

9. Book List Import window: Export Errors is disabled until an import finishes with errors to export.

## Suggested checks

- Help: open Help (F1), arrow through the text, press Enter — text size must not change.
- Main, Import, Reading History: cell boxes visible; try one dark theme and one light theme.
- Name List, Collections, Backup/Restore: lists show no cell boxes.
- Book Details without JAWS/NVDA: header panel and "Sorted by" line visible. With JAWS/NVDA: both hidden, nothing extra spoken.
- Import: before scanning, confirm Add Selected, Export, and the error filter are grayed out; after a scan with results they enable.
- Buttons: in any window, only the focused button is highlighted.
