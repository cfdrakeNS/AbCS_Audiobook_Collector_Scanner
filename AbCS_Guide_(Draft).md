# AbCS User Guide (Draft)

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

- Open Import from File menu (Alt+F, then Import), or press Ctrl+I.
- If books already exist, Main Window opens with the current list.

## Main Window (Book List)

### Menu

- File (Alt+F): New Book, Import, Quit
- View (Alt+V): Book Details, Authors, Collections, Genre, Series, zoom controls
- Manage (Alt+M): Preferences, Backup/Restore, Statistics
- Help (Alt+H): About, Keyboard Shortcuts

### Header controls

Below the menu bar, left to right:

1. Collection (Alt+C) - choose All Collections or one collection.
2. Read? (Alt+R) - All, Read, or Unread.
3. Order By (Alt+O) - Title, Author, Genre, or Series.
4. Search (Alt+S) - type to search/filter; Enter moves to the first match; Escape clears search.
5. Menu bar access: Alt+F (File), Alt+V (View), Alt+M (Manage), Alt+H (Help).

### Book list window detail

Press Alt+B to move focus to the book list table.

Columns are: Author, Title, Year, Plot, Series, Genre, Time, Tracks, Read, Added.

- Open Book Details with Ctrl+Enter or double-click.
- Selection with keyboard: Shift+Space starts selection, Shift+Up/Down/Page keys extends selection.
- Selection with mouse: Shift+Click range, Ctrl+Click individual.
- Arrow navigation without Shift clears selection.
- Status bar reports selection count and focused record; Alt+/ reads status message aloud.

### Main Window shortcuts

- Collection: Alt+C
- Read filter: Alt+R
- Order By: Alt+O
- Search: Alt+S
- File menu: Alt+F
- View menu: Alt+V
- Manage menu: Alt+M
- Help menu: Alt+H
- Focus book list: Alt+B
- Update selected: Alt+U
- Delete selected: Alt+D
- Cancel selection: Alt+L
- Read status bar: Alt+/
- Jump table columns: Alt+1 through Alt+0
- New Book: Ctrl+N
- Import: Ctrl+I
- Open Book Details: Ctrl+Enter

## Book Details Window

Open from Main Window with Ctrl+Enter or double-click on a book.

### Field focus shortcuts

- Title: Alt+T
- Author: Alt+A
- Year: Alt+Y
- Files: Alt+F
- Series: Alt+I
- Genre: Alt+G
- Reader: Alt+R
- Collection: Alt+K
- Time: Alt+M
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
- Close: Alt+C or Escape
- Previous book: Page Up
- Next book: Page Down
- Read status bar: Alt+/

## Update Window

Use this window to apply bulk changes to selected books.

### Shortcuts

- Series: Alt+S
- Genre: Alt+G
- Collection (when shown): Alt+L
- Focus list: Alt+B
- Close: Alt+C or Escape

## Import Window

The Import Window scans a folder, validates metadata, and adds valid books to the database.

Below the header area, there are five controls left to right:

1. Collection (Alt+C) - target collection for imported books.
2. Folder (Alt+F) - selected scan path (read-only field).
3. Browse (Alt+W) - choose folder to scan.
4. Errors Filter (Alt+E) - All, Valid, Warning, Error, Duplicate.
5. Scan (Alt+S) - starts scan for supported audio files.

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
- Add All Valid: Alt+V
- Close: Alt+L
- Escape: same action as Close (or cancel if an operation is running)
- During scanning, Close changes to Cancel and uses Alt+C
- Alt+/ reads the status bar message

### Import shortcuts summary

- Alt+/, Alt+C, Alt+F, Alt+W, Alt+E, Alt+S, Alt+B
- Alt+1 to Alt+5
- Ctrl+Enter
- Alt+I, Alt+V, Alt+L
- F1

## Preferences Window

The Preferences Window controls display settings and import behavior.

Top to bottom, the window has three areas:

1. Display Settings
2. Import Settings
3. Footer actions and status bar

### Display Settings (top)

- Theme: Alt+T
- Preset: Alt+P
- Zoom (%): Alt+Z

### Import Settings (middle)

- Directory: Alt+D
- Browse: Alt+B
- Formats: Alt+O (focuses first format checkbox)
- Scenario: Alt+S
- Scenario Description: Alt+R (read-only text)
- Author Fallback: Alt+A
- Title Fallback: Alt+I
- Flip Author: Alt+F
- Reader Keywords: Alt+K

Auto-correction options include:

- Trim whitespace: Alt+W
- Strip leading punctuation: Alt+P
- Remove special characters: Alt+E
- Proper case fields: Alt+L
- Move leading 'The' in title: Alt+H

### Footer actions

- Audit Display: Alt+U
- Save: Alt+V
- Cancel: Alt+C
- Alt+/ reads current status bar message
- F1 opens keyboard shortcut help
- Escape triggers Cancel behavior (including unsaved changes prompt)

## Accessibility notes

- Press F1 in any window for the shortcut list.
- Use Alt+/ where supported to re-read status messages.
- For combo boxes, use Alt+Down to open the list where applicable.
- If a command is unavailable, check focus and selection first.
