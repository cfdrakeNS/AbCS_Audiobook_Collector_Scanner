# AbCS User Guide (Draft)

## 2026-03-03 Change Log

- Main Window standardization completed: Collection/Read/Sort moved from header controls into menus.
- Find workflow standardized: `View > Find...` with `Ctrl+F` replaces inline Search in the header.
- Main list duration terminology standardized from `Time` to `Length` in user-facing labels.
- Main Window legacy shortcuts removed: `Alt+C` (Collection), `Alt+R` (Read), `Alt+O` (Order By), `Alt+S` (Search).
- Sort menu behavior updated: first-letter menu activation and status-bar sort wording now cover non-primary sorts (for example Year).
- Regression tests expanded for Main Window menu/shortcut behavior; full test suite passing (33 tests).
- Preferences documentation updated for the reorganized Import Settings layout and section-jump shortcuts (`Alt+D/S/O/F/R/A`) with current footer/help behavior.

## 2026-03-02 Change Log

- Window dismissal behavior simplified: dismiss-only Close buttons were removed from major windows; Escape is now the standard close path.
- Import Window footer updated: `Add Valid` (Alt+V) available in review mode; Cancel (Alt+N) is shown only while scan/add is running.
- Import review mode added in Preferences: `Review Clean Books Before Adding` (Alt+Y) keeps clean rows in Import Window for manual review.
- Import Progress and shortcut help updated for reliable Alt+/ status read flow and post-complete Escape close.
- Name List status read wording updated to announce edit/close actions as `Alt+E Edit, Escape Close`.
- Main Window About dialog updated to a line-by-line table format for more reliable JAWS reading.
- First-run startup guidance and Display Setup shortcut help updated to line-by-line table format for arrow-key reading.
- Status announcement handling standardized in Main Window, Book Details, and Update Window via shared announcer path.
- Book Details Cancel shortcut reliability improved (Alt+L conflict removed).
- Manage menu includes `Preferences Reorg Preview...` for side-by-side validation of the reorganized preferences layout.
- Startup/version updated to AbCS 1.7.2 (build date 2026-03-02).

## 2026-02-25 Change Log

- Import performance baseline updated with local SSD comparison against USB results.
- Import Window shortcuts/docs updated: Export is Alt+X; scan-time cancel is Alt+N; `Add All Valid` removed.
- Import error filter options updated to include Fallback and Corrected.
- Import Progress behavior documented: status phase messages `Scanning x/x` then `Adding x/x`, with Alt+/ status read verification.

## 2026-02-26 Change Log

- Backup/Restore keyboard flow updated: backup list supports arrow navigation with reliable Alt+/ status read.
- Backup/Restore actions updated: Browse shortcut is Alt+O, Delete selected backup is Alt+D (shown only when backup list has focus and a selected row).
- Import summary wording/counts updated: `Fixed` replaces `Valid`; issue count is `Errors/Warnings`.
- Import review behavior updated: only clean items auto-add; fixed/warning/error/duplicate items remain in the review list for manual `Add Selected`.
- Name List status read updated to include books count and actions in row format: `Name - books xx, Alt+E Edit, Alt+C Close`.
- Focus return documented for Main-window-launched dialogs (for example Import, Backup/Restore, Preferences): focus returns to Main list Title cell on close.
- Main Window safety update: `Ctrl+A` is disabled in the book list to prevent accidental large-batch actions.
- Large batch reliability update: bulk delete/update operations now run in safe chunks for large libraries.

## Overview

AbCS (Audio Book Collector Scanner) is an audiobook collection manager with search, filtering, editing, and metadata import.

AbCS is accessibility-first:

- Keyboard access for major actions (Alt+letter, Ctrl shortcuts, F1 help).
- Screen reader support through status announcements and accessible labels.
- Scalable fonts and zoom.
- Theme and readability preferences.

## Global keyboard shortcuts

- Zoom in: Ctrl++
- Zoom out: Ctrl+-
- Reset zoom: Ctrl+0
- Keyboard shortcut help for current window: F1

## Startup behavior

When AbCS starts for the first time, the book list may be empty.

- If the database is empty, a dialog appears with options: Import, Preferences, or Continue.
- The startup guidance is presented in a line-by-line read-only table; use Up/Down arrows to read each line.
- Open Import from File menu (Alt+F, then Import), or press Ctrl+I.
- If books already exist, Main Window opens with the current list.

## Main Window (Book List)

### Menu

- File (Alt+F): New Book, Import, Quit
- View (Alt+V): Open Focused Item (Ctrl+Enter), Find (Ctrl+F), Collections filter menu, Read filter menu, zoom controls
- Sort (Alt+S): Author, Title, Year, Plot, Series, Genre, Length, Tracks, Read, Added
- Manage (Alt+M): Authors, Collections, Genre, Series, Preferences, Preferences Reorg Preview, Backup/Restore, Statistics
- Help (Alt+H): About, Keyboard Shortcuts

### About dialog

- About content is presented in a single-column line-by-line table for screen reader reliability.
- Use Up/Down arrows to read each line.
- Screen-reader detected/not-detected status text is no longer shown.

### Header controls

Header filter controls are no longer shown in Main Window.

- Collection filtering is available in `View > Collections`.
- Read filtering is available in `View > Read`.
- Sorting is available in the top-level `Sort` menu.
- Finding is available in `View > Find...` and with `Ctrl+F`.
- Main Window Escape behavior clears active find/search filter state.

### Book list window detail

Press Alt+B to move focus to the book list table.

Columns are: Author, Title, Year, Plot, Series, Genre, Length, Tracks, Read, Added.

- Open Book Details with Ctrl+Enter or double-click.
- Open focused item with Ctrl+Enter or double-click:
	- Title/other columns: opens Book Details
	- Author column: always Authors manager 
	- Series column: always opens Series manager
	- Genre column: always opens Genre manager
- Selection with keyboard: Shift+Space starts selection, Shift+Up/Down/Page keys extends selection.
- Selection with mouse: Shift+Click range, Ctrl+Click individual.
- Arrow navigation without Shift clears selection.
- Status bar reports selection count and focused record; Alt+/ reads status message aloud.

### Main Window shortcuts

- File menu: Alt+F
- View menu: Alt+V
- Sort menu: Alt+S
- Manage menu: Alt+M
- Help menu: Alt+H
- Focus book list: Alt+B
- Find: Ctrl+F
- Update selected: Alt+U
- Delete selected: Alt+D
- Cancel selection: Alt+L
- Read status bar: Alt+/
- Jump table columns: Alt+1 through Alt+0
- New Book: Ctrl+N
- Import: Ctrl+I
- Open focused item (context-sensitive): Ctrl+Enter
- Ctrl+A: disabled in Main Window book list (safety guard)

## Book Details Window

Open from Main Window by focusing the Title (or another non-manager column) and using Ctrl+Enter or double-click.

### Field focus shortcuts

- Title: Alt+T
- Author: Alt+A
- Year: Alt+Y
- Files: Alt+F
- Series: Alt+I
- Genre: Alt+G
- Reader: Alt+R
- Collection: Alt+K
- Length: Alt+M
- Read date: Alt+E
- Size: Alt+Z
- Bitrate: Alt+B
- Path: Alt+H
- Comments: Alt+O

### Buttons and navigation

- New: Alt+N
- Save: Alt+S
- Delete: Alt+D
- Cancel (when shown): Alt+L
- Close window: Escape
- Previous book: Page Up
- Next book: Page Down
- Read status bar: Alt+/

## Name List Window (Authors / Genre / Series / Collections)

Main Window opens these from the Manage menu, and from table context actions on Author/Series/Genre.

### Header and list

- Find: Alt+F
- Name field: Alt+M
- Active checkbox (Collections only): Alt+A
- Jump to list: Alt+B
- Enter in Find moves focus to the matched list item.

### Actions

- Edit: Alt+E
- Save: Alt+S
- Cancel edit: Alt+L
- Close window: Escape
- Read status bar: Alt+/

### Status read format (Alt+/)

- With a row focused, status reads: `Name - books xx, Alt+E Edit, Escape Close`.

## Update Window

Use this window to apply bulk changes to selected books.

### Shortcuts

- Series: Alt+S
- Genre: Alt+G
- Collection (when shown): Alt+L
- Focus list: Alt+B
- Read status bar: Alt+/
- Close window: Escape

## Backup / Restore Window

Open from Main Window: Manage (Alt+M) -> Backup/Restore.

Use this window to create database backups, restore a selected backup, or perform a full reset.

### Main controls

- Backup List: Alt+L
- Browse for restore file: Alt+O
- Restore file field: Alt+T (read-only)

### Actions

- Backup: Alt+B
- Restore: Alt+R
- Delete selected backup: Alt+D
- Full Reset: Alt+F
- Close window: Escape
- Read status bar: Alt+/
- Keyboard shortcut help: F1

### Notes

- Backup creates a database snapshot in the configured backup folder.
- Restore replaces current data with the selected backup file.
- Delete removes the currently selected backup file from disk.
- Full Reset clears all data and recreates an empty database.
- Delete action is shown only when the backup list has focus and a row is selected.

## Import Window

The Import Window scans a folder, validates metadata, and imports clean books while keeping review items visible for manual action.

If the database is empty at startup, the first-run dialog includes an Import shortcut.

Below the header area, there are five controls left to right:

1. Collection (Alt+C) - target collection for imported books.
2. Folder (Alt+F) - selected scan path (read-only field).
3. Browse (Alt+W) - choose folder to scan.
4. Errors Filter (Alt+E) - All, Warning, Error, Duplicate, Fallback, Corrected.
5. Scan (Alt+S) - starts scan for supported audio files.

Summary/status after scan uses: `Scanned`, `Added`, `Fixed`, `Errors/Warnings`, `Duplicates`, `Elapsed`.

- `Fixed` counts items corrected by auto-correction or fallback.
- `Errors/Warnings` counts unresolved issues requiring review.
- Warning filter shows unresolved warnings; fixed/fallback-corrected rows are tracked as `Fixed`.

### Import list window detail

Press Alt+B to move focus to the import list table.

Columns are: Author, Title, Year, Error Type, File/Folder.

- Ctrl+Enter or double-click opens Import Detail for the current row.
- Keyboard multi-select: Shift+Space starts selection; Shift+Up/Down/Page keys extends range.
- Mouse multi-select: Shift+Click selects a range.
- Arrow keys without Shift clear selection and move current row.
- Alt+1 through Alt+5 jumps focus to Author, Title, Year, Error Type, or File/Folder column.

### Footer actions

- Add Selected: Alt+I
- Add Valid (review mode): Alt+V
- Export list to CSV: Alt+X
- Escape: close window (or cancel if an operation is running)
- Alt+/ reads the status bar message

Import behavior notes:

- Clean rows are auto-added during scan.
- Rows with fixed metadata, warnings, errors, or duplicates remain in the table for review and manual `Add Selected`.

### Import shortcuts summary

- Alt+/, Alt+C, Alt+F, Alt+W, Alt+E, Alt+S, Alt+B
- Alt+1 to Alt+5
- Ctrl+Enter
- Alt+I, Alt+V, Alt+X, Alt+N
- F1

## Import Progress Window

The Import Progress window is shown during scans in compact mode.

- Progress status bar reports phase messages:
	- Scanning phase: `Scanning x/x`
	- Import phase: `Adding x/x`
- Counters shown: Files scanned, Elapsed time, Books added, Read errors.
- Alt+/ reads the current progress status message.
- Cancel scan: Alt+L
- Close (after completion): Escape

Note: progress information fields are display-only and are not part of tab focus.

## Focus return after dialogs

When dialogs launched from Main Window close (for example Import, Backup/Restore, Preferences, Statistics, About, and Keyboard Shortcuts), focus is restored to Main Window with the Title cell focused on the first visible row.

## Preferences Window

The Preferences Window controls display settings and import behavior.

If the database is empty at startup, the first-run dialog includes a Preferences shortcut.

Top to bottom, the window has three areas:

1. Display Settings
2. Import Settings (organized into Source & Scope, Options, Fallback & Parsing Behavior, Validation Rules, Auto-Correction)
3. Footer actions and status bar

### Section navigation shortcuts

Use section shortcuts to jump quickly to the first control in each section:

- Display section: Alt+D
- Source & Scope section: Alt+S
- Options section: Alt+O
- Fallback & Parsing Behavior section: Alt+F
- Validation Rules section: Alt+R
- Auto-Correction section: Alt+A

### Display Settings (top)

- Theme selector
- Preset selector
- Zoom (%)

Tip: use Alt+D to jump to Display, then Tab/Shift+Tab to move between controls.

### Import Settings (middle)

Source & Scope includes:

- Default import directory and Browse
- Enabled formats (MP3, M4A, M4B, FLAC, OGG, WAV, WMA)
- Import scenario selector and read-only scenario description

Options includes:

- Review Clean Books Before Adding
- Flip Author Last, First
- Apply proper case
- Move leading `The` to end of title

Fallback & Parsing Behavior includes:

- Author fallback to folder
- Title fallback to file
- Reader keywords

Validation Rules includes severity/value settings for:

- Author in title
- Title in author
- Unknown author handling
- Minimum title length
- Duplicate matching/fuzzy settings
- File structure and year quality

Import scenario behavior:

- Mass Standard Import: mixed author/book/series folder structures under root.
- Mass Import - Series From Directory: uses book folder as series (Author/Series/Files); ambiguous or mismatched paths skip series with a warning.
- Mass Import - Series From File Name: parses first `( ... )` block in file name as series; trailing number appends ` - NN` to title.
- Single Author / Book Import: supports folder or single-file import; file picker uses enabled format filters.

Auto-correction options include:

- Trim whitespace
- Strip leading punctuation
- Remove special characters

### Footer actions

- Save: Alt+V
- Cancel: Alt+C
- Alt+/ reads current status bar message
- F1 opens keyboard shortcut help
- Tab/Shift+Tab moves between controls in the current section
- Escape triggers Cancel behavior (including unsaved changes prompt)

## Accessibility notes

- Press F1 in any window for the shortcut list.
- Use Alt+/ where supported to re-read status messages.
- For combo boxes, use Alt+Down to open the list where applicable.
- If a command is unavailable, check focus and selection first.
