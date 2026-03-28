# AbCS User Guide

## Overview

AbCS (Audio Book Collector Scanner) is an audiobook collection manager with search, filtering, editing, and metadata import.

AbCS is accessibility-first:

- Keyboard access for major actions (Alt+letter, Ctrl shortcuts, F1 help)
- Screen reader support through status announcements and accessible labels
- Scalable fonts and zoom
- Theme and readability preferences

## Global keyboard shortcuts

- Zoom in: Ctrl++
- Zoom out: Ctrl+-
- Reset zoom: Ctrl+0
- Keyboard shortcut help for current window: F1

## Startup behavior

When AbCS starts for the first time, the book list may be empty.

- If the database is empty, a standard message box appears with three buttons: Import, Preferences, or Continue
- Use Tab to navigate between the three buttons and press Enter to select
- If books already exist, Main Window opens with the current list

## Main Window (Book List)

### Menu

- File (Alt+F): New Book, Import, Quit
- Edit (Alt+E): Delete, Update, Get Web Info, Cancel
- View (Alt+V): Open Focused Item (Ctrl+Enter), Find (Ctrl+F), Collections filter menu, Read filter menu, Reading History, zoom controls
- Sort (Alt+S): Author, Title, Year, Plot, Series, Genre, Length, Tracks, Read, Added
- Manage (Alt+M): Authors, Collections, Genre, Series, Preferences, Backup/Restore, Statistics
- Help (Alt+H): About, Keyboard Shortcuts

### About dialog

- About content is presented in a single-column line-by-line table for screen reader reliability
- Use Up/Down arrows to read each line

### Header controls

Header filter controls are no longer shown in Main Window.

- Collection filtering is available in `View > Collections`
- Read filtering is available in `View > Read`
- Sorting is available in the top-level `Sort` menu
- Finding is available in `View > Find...` and with `Ctrl+F`
- Main Window Escape behavior clears active find/search filter state

### Book list window detail

Press Alt+L to move focus to the book list table.

Columns are: Author, Title, Year, Plot, Series, Genre, Length, Tracks, Read, Added.

- Open Book Details with Ctrl+Enter or double-click
- Open focused item with Ctrl+Enter or double-click:
	- Title/other columns: opens Book Details
	- Author column: always Authors manager 
	- Series column: always opens Series manager
	- Genre column: always opens Genre manager
- Selection with keyboard: Shift+Space starts selection, Shift+Up/Down/Page keys extends selection
- Selection with mouse: Shift+Click range, Ctrl+Click individual
- Arrow navigation without Shift clears selection
- Status bar reports selection count and focused record; Alt+/ reads status message aloud

### Main Window shortcuts

- File menu: Alt+F
- View menu: Alt+V
- Sort menu: Alt+S
- Manage menu: Alt+M
- Help menu: Alt+H
- Focus book list: Alt+L
- Find: Ctrl+F
- Update selected: Alt+U
- Delete selected: Alt+D
- Cancel selection: Escape
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
- Cancel edit: Escape
- Close window: Escape
- Previous book: Page Up
- Next book: Page Down
- Read status bar: Alt+/
- Get Web Info: Alt+W

## Web Metadata Window

Open from Main Window: Edit (Alt+E) -> Get Web Info, or from Book Details with Alt+W.

Fetches metadata from Google Books & Open Library APIs for the selected book.

### Window layout

The window displays current database values alongside web-fetched values:

| Field | Current Value | Web Value | Accept |
|-------|---------------|-----------|--------|
| Title | [database title] | [web title] | [checkbox] |
| Author | [database author] | [web author] | [checkbox] |
| Year | [database year] | [web year] | [checkbox] |
| Series | [database series] | [web series] | [checkbox] |
| Genre | [database genre] | [web genre] | [checkbox] |
| Plot | [not displayed] | [web plot] | [checkbox] |

- Check the Accept checkbox to replace database value with web value
- Green checkmark (✓) indicates web data differs from database
- Empty database fields show web value by default (no checkbox needed)
- Plot field only shows if web data is available

### Field shortcuts

- Title: Alt+T
- Author: Alt+A  
- Year: Alt+Y
- Series: Alt+I
- Genre: Alt+G
- Plot: Alt+P

### Actions

- Save: Alt+S (accepts checked changes and closes window)
- Close: Escape (discards changes and closes window)
- Read status bar: Alt+/
- Keyboard shortcut help: F1

### Status messages

- "Web data found" when differences exist
- "No web data found" when search returns nothing
- "Updated: [fields]" when changes are saved
- Error messages for network failures

## Name List Window (Authors / Genre / Series / Collections)

Main Window opens these from the Manage menu, and from table context actions on Author/Series/Genre.

### Header and list

- Find: Alt+F
- Name field: Alt+M
- Active checkbox (Collections only): Alt+A
- Jump to list: Alt+L
- Enter in Find moves focus to the matched list item.

### Actions

- Edit: Alt+E
- Save: Alt+S
- Cancel edit: Escape
- Close window: Escape
- Read status bar: Alt+/

### Status read format (Alt+/)

- With a row focused, status reads: `Name - books xx, Alt+E Edit, Escape Close`.

## Update Window

Use this window to apply bulk changes to selected books.

### Shortcuts

- Series: Alt+S
- Genre: Alt+G
- Collection (when shown): Alt+C
- Focus list: Alt+L
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

- Backup creates a database snapshot in the configured backup folder
- Restore replaces current data with the selected backup file
- Delete removes the currently selected backup file from disk
- Full Reset clears all data and recreates an empty database
- Delete action is shown only when the backup list has focus and a row is selected

## Import Window

The Import Window scans a folder, validates metadata, and imports clean books while keeping review items visible for manual action.

If the database is empty at startup, the first-run dialog includes an Import shortcut.

Below the header area, there are five controls left to right:

1. Collection (Alt+C) - target collection for imported books
2. Folder (Alt+F) - selected scan path (read-only field)
3. Browse (Alt+W) - choose folder to scan
4. Errors Filter (Alt+E) - All, Warning, Error, Duplicate, Fallback, Corrected
5. Scan (Alt+S) - starts scan for supported audio files

Summary/status after scan uses: `Scanned`, `Added`, `Fixed`, `Errors/Warnings`, `Duplicates`, `Elapsed`.

- `Fixed` counts items corrected by auto-correction or fallback
- `Errors/Warnings` counts unresolved issues requiring review
- Warning filter shows unresolved warnings; fixed/fallback-corrected rows are tracked as `Fixed`

### Import list window detail

Press Alt+L to move focus to the import list table.

Columns are: Author, Title, Year, Error Type, File/Folder.

- Ctrl+Enter or double-click opens Import Detail for the current row
- Keyboard multi-select: Shift+Space starts selection; Shift+Up/Down/Page keys extends range
- Mouse multi-select: Shift+Click selects a range
- Arrow keys without Shift clear selection and move current row
- Alt+1 through Alt+5 jumps focus to Author, Title, Year, Error Type, or File/Folder column

### Footer actions

- Add Selected: Alt+I
- Add Valid (review mode): Alt+V
- Export list to CSV: Alt+X
- Escape: close window (or cancel if an operation is running)
- Alt+/ reads the status bar message

Import behavior notes:

- Clean rows are auto-added during scan
- Rows with fixed metadata, warnings, errors, or duplicates remain in the table for review and manual `Add Selected`

### Import shortcuts summary

- Alt+/, Alt+C, Alt+F, Alt+W, Alt+E, Alt+S, Alt+L
- Alt+1 to Alt+5
- Ctrl+Enter
- Alt+I, Alt+V, Alt+X
- F1

## Import Progress Window

The Import Progress window is shown during scans in compact mode.

- Progress status bar reports phase messages:
	- Scanning phase: `Scanning x/x`
	- Import phase: `Adding x/x`
- Counters shown: Files scanned, Elapsed time, Books added, Read errors
- Alt+/ reads the current progress status message
- Cancel scan: Escape
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

- Mass Standard Import: mixed author/book/series folder structures under root
- Mass Import - Series From Directory: uses book folder as series (Author/Series/Files); ambiguous or mismatched paths skip series with a warning
- Mass Import - Series From File Name: parses first `( ... )` block in file name as series; trailing number appends ` - NN` to title
- Single Author / Book Import: supports folder or single-file import; file picker uses enabled format filters

Auto-correction options include:

- Trim whitespace
- Strip leading punctuation
- Remove special characters

### Footer actions

- Save: Alt+V
- Cancel: Escape
- Alt+/ reads current status bar message
- F1 opens keyboard shortcut help
- Tab/Shift+Tab moves between controls in the current section
- Escape triggers Cancel behavior (including unsaved changes prompt)

## Accessibility notes

- Press F1 in any window for the shortcut list
- Use Alt+/ where supported to re-read status messages
- For combo boxes, use Alt+Down to open the list where applicable
- If a command is unavailable, check focus and selection first
