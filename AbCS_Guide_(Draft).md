# AbCS User Guide (Draft)

## Overview

AbCS (Audio Book Collector Scanner) is an audiobook collection manager with search, filtering, editing, and import from audio metadata.

The app is accessibility-first:

- Keyboard access for all major actions (Alt+letter, Ctrl shortcuts, F1 help).
- Screen reader support through status announcements and accessible control labels.
- Scalable fonts and zoom.
- Theme and readability options in Preferences.

## Global keyboard shortcuts

- Ctrl++: Zoom in
- Ctrl+-: Zoom out
- Ctrl+0: Reset zoom
- F1: Show keyboard shortcuts for the current window

## Startup behavior

On first run, if no books are present, AbCS prompts for next steps such as importing or creating a new book.

If books are already in the database, the Main Window opens directly.

## Main Window (Book List)

### Menu

- File (Alt+F): New Book, Import, Quit
- View (Alt+V): Book Details and view options
- Manage (Alt+M): Preferences, backup/restore, and other management options
- Help (Alt+H): About and Keyboard Shortcuts

### Header controls

- Collection filter
- Read filter (All, Read, Unread)
- Order By (changes sort/search behavior)
- Search box

Type in Search to find matching books. Press Enter to move to the first matching row.

### Book table

Use Alt+B to move focus to the book table.

Open details for the selected row with Ctrl+Enter (or double-click).

For multi-select:

- Keyboard: Shift+Arrow extends selection, Ctrl+Space toggles current row.
- Mouse: Shift+Click for range, Ctrl+Click for individual rows.

When rows are selected, action buttons appear in the footer.

### Footer actions

- Update (Alt+U): Open bulk Update Window for selected books.
- Delete (Alt+D): Delete selected books (with confirmation).
- Cancel (Alt+L): Clear current selection.
- Status bar: Announces counts, search results, and selection state.

Screen reader tip: press Alt+/ to read the current status message.

### Main Window shortcuts

- Alt+B: Focus book list
- Alt+U: Update selected
- Alt+D: Delete selected
- Alt+L: Cancel selection
- Alt+/: Read status bar
- Alt+1 through Alt+0: Jump to table columns
- Ctrl+N: New Book
- Ctrl+I: Import
- Ctrl+Enter: Open Book Details

## Book Details Window

Open from Main Window with Ctrl+Enter or double-click on a book row.

### Fields and editing

The window provides editable fields for title, author, comments, year, time, reader, read date, series, genre, collection, file metadata, and path.

Combo boxes are configured to reduce accidental changes: use Alt+Down to open a combo drop-down.

### Buttons

- New (Alt+N)
- Save (Alt+S)
- Delete (Alt+D)
- Cancel (Alt+L, shown while editing)
- Close (Alt+C or Escape)

There are no Prev/Next buttons.

### Book-to-book navigation

Use keyboard navigation:

- Page Up: Previous book
- Page Down: Next book

### Book Details shortcuts

- Alt+/: Read status bar
- Alt+N: New book
- Alt+S: Save
- Alt+D: Delete
- Alt+L: Cancel (when active)
- Alt+C: Close window
- Page Up / Page Down: Previous / Next book
- Alt+T: Title
- Alt+A: Author
- Alt+O: Comments
- Alt+Y: Year
- Alt+M: Time
- Alt+R: Reader
- Alt+E: Read date
- Alt+I: Series
- Alt+G: Genre
- Alt+K: Collection
- Alt+F: Files
- Alt+B: Bitrate
- Alt+Z: Size
- Alt+H: Path

## Update Window

The Update Window applies bulk changes to selected books.

### Header controls

- Series (Alt+S)
- Genre (Alt+G)
- Collection (Alt+L, visible when multiple collections exist)

Select an existing value, type a new value, or choose None (for fields that support clearing).

Changes apply when the selection/input is committed.

### Detail list

Shows selected books with columns such as Title, Year, Series, Genre, and Collection.

### Footer

- Close (Alt+C or Escape)
- Status bar announcements for update actions

### Update Window shortcuts

- Alt+S: Series
- Alt+G: Genre
- Alt+L: Collection
- Alt+B: Focus book list
- Alt+C or Escape: Close
- Alt+Down: Open combo drop-down

## Import Window

The Import Window scans a folder, validates metadata, and adds valid books to the database.

### Header controls

- Collection (required before scan)
- Folder path
- Browse
- Error Filter (All, Valid, Warning, Error, Duplicate)
- Scan

### Import list

The table shows scanned items with Author, Title, Year, Error Type, and File/Folder.

Use filtering to focus on only valid or only problematic items.

Open selected import detail with Ctrl+Enter.

### Footer actions

- Add Selected (Alt+I)
- Add All Valid (Alt+V)
- Close/Cancel (Alt+C)
- Status bar and scan progress indicator

### Import shortcuts

- Alt+/: Read status bar
- Alt+F: Folder field
- Alt+W: Browse
- Alt+O: Error filter
- Alt+L: Import collection
- Alt+S: Scan
- Alt+B: Focus import list
- Ctrl+Enter: Open selected import detail
- Alt+I: Add selected
- Alt+V: Add all valid
- Alt+C: Close window

## Accessibility notes

- Press F1 in any window for the current shortcut list.
- Use Alt+/ where supported to re-read status messages.
- Prefer keyboard combo navigation (Alt+Down) in editable combo fields.
- If a command is unavailable, check focus and current selection first.
