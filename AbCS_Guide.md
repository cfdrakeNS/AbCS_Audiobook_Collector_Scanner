# AbCS User Guide

## Overview

AbCS (Audio Book Collector Scanner) is a desktop app for collecting, searching, and updating audiobook metadata.

It is designed for both sighted users and screen reader users:

- Full keyboard support across major windows

- F1 shortcut help in key windows

- Status readback with Alt+/

- Scalable text and UI controls

- Theme and readability preferences

## Quick Start

1. Launch AbCS.

2. If your library is empty, choose one of the startup options:

   - Import Books

   - Import List

   - Preferences

   - Continue

3. Import books, then use Main Window search and filters to browse.

4. Press Enter on a book title to open Book Details.

## Global Shortcuts

- Ctrl++: Zoom in

- Ctrl+-: Zoom out

- Ctrl+0: Reset zoom

- F1: Show keyboard shortcuts for the current window

## Startup Behavior

On first launch (or when the library is empty), AbCS shows a startup choices dialog.

Options:

- Import Books: open folder-based import

- Import List: open spreadsheet-based import

- Preferences: open settings before import

- Continue: open Main Window

Keyboard use:

- Tab/Shift+Tab to move between controls

- Enter to activate the focused button

## Main Window (Book List)

### Main Menus

- File: New Book, Import, Import Book List, Quit

- Edit: Delete, Update, Fetch Web Info, Cancel

- View: Open Focused Item, Find, Collections, Read, Reading History, Zoom

- Sort: Author, Title, Year, Series, Genre, Length, Tracks, Read

- Manage: Authors, Collections, Genre, Series, Preferences, Backup/Restore, Statistics

- Help: About, License, Keyboard Shortcuts

### Book List Columns

Visible columns:

- Author

- Title

- Year

- Series

- Genre

- Length

- Tracks

- Read

### Main Window Navigation

- Enter or double-click:

  - Title: open Book Details

  - Author: open Authors manager

  - Series: open Series manager

  - Genre: open Genre manager

  - Read: open Read Date dialog

- Escape:

  - Clear selection first

  - Then clear active search

  - Then clear Read/Unread filter

### Main Window Shortcuts

- Alt+U: Update selected books

- Alt+D: Delete selected books

- Alt+L: Cancel selection

- Alt+/: Read current status message

- Ctrl+F: Find

- Ctrl+I: Import

- Ctrl+Shift+I: Import Book List

- Ctrl+N: New Book

- Alt+1 through Alt+8: Jump to table columns

- Ctrl+A is intentionally disabled in the main table

## Book Details Window

Open from Main Window by pressing Enter on a book title.

### Field Focus Shortcuts

- Alt+T: Title

- Alt+A: Author

- Alt+Y: Year

- Alt+P: Plot/comments

- Alt+I: Series

- Alt+G: Genre

- Alt+R: Reader

- Alt+E: Read date

- Alt+F: Files

- Alt+M: Length

- Alt+B: Bitrate

- Alt+Z: Size

- Alt+H: Path

- Alt+C: Collection

### Actions

- Alt+N: New

- Alt+S: Save

- Alt+D: Delete

- Alt+W: Get Web Info

- Page Up: Previous book

- Page Down: Next book

- Escape: Cancel/Close

- Alt+/: Read status

- F1: Shortcut help

## Web Metadata Window

Open from:

- Main Window -\> Edit -\> Fetch Web Info

- Book Details -\> Alt+W

Purpose:

- Compare current metadata with web results

- Accept selected changes before saving

### Common Actions

- Alt+T / Alt+A / Alt+Y / Alt+I / Alt+G / Alt+P: Focus fields

- Alt+S: Save accepted changes

- Escape: Close without saving

- Alt+/: Read status

- F1: Shortcut help

## Name List Windows (Authors, Series, Genre, Collections)

### Common Actions

- Alt+L: Jump to list

- Alt+M: Name field

- Alt+E: Edit selected row

- Alt+S: Save

- Escape: Cancel/Close

- Alt+/: Read status

- F1: Shortcut help

Collections-only:

- Alt+A: Active checkbox

## Update Window

Use this for bulk updates on selected books.

- Alt+S: Series

- Alt+G: Genre

- Alt+C: Collection (when available)

- Alt+B: Focus selected-books list

- Alt+/: Read status

- Escape: Close

- F1: Shortcut help

## Import Window (Folder Scan)

Use Import Window to scan folders, validate tags, and add books.

### Top Controls

- Alt+C: Collection

- Alt+F: Folder field

- Alt+W: Browse folder

- Alt+E: Error filter

- Ctrl+I: Start scan/import

### List and Actions

- Alt+L: Focus import table

- Alt+1..Alt+5: Jump table columns

- Alt+S: Add selected

- Alt+V: Add valid

- Alt+X: Export list to CSV

- Enter/double-click row: open Import Detail

- Escape: Cancel/Close

- Alt+/: Read status

- F1: Shortcut help

## Import Detail Window

Use this window to review and fix individual import rows.

- Alt+T/A/Y/P/M/R/I/G/C/F/B/Z/E/H: Focus fields

- Alt+S: Save row

- Alt+D: Discard row

- Page Up/Page Down: Previous/Next row

- Escape: Close

- Alt+/: Read status

- F1: Shortcut help

## Import Progress Window

Shown during long scans/imports.

- Escape: Cancel scan (or close when complete)

- Alt+/: Read current progress status

- F1: Shortcut help

## Book List Import Window (Spreadsheet Import)

Use this window to import from spreadsheet files.

### Main Flow

1. Alt+W to browse and select spreadsheet

2. Map spreadsheet columns to fields

3. Choose import options

4. Alt+I to import

### Shortcuts

- Alt+W: Browse file

- Alt+O: Options section

- Alt+H: Instructions

- Alt+T/A/Y/P/S/G/R/E/M/F: Field mappings

- Alt+I: Import books

- Alt+X: Export errors to CSV

- Alt+/: Read status

- F1: Shortcut help

- Escape: Close

## Backup / Restore Window

Open from Manage -\> Backup/Restore.

### Main Controls and Actions

- Alt+L: Backup list

- Alt+W: Browse restore file

- Alt+T: Restore file field

- Alt+B: Create backup

- Alt+R: Restore

- Alt+D: Delete selected backup

- Alt+F: Full reset

- Escape: Close

- Alt+/: Read status

- F1: Shortcut help

## Preferences Window

Use Preferences for display and import behavior settings.

### Section Shortcuts

- Alt+D: Display

- Alt+P: Path and scope

- Alt+O: Options

- Alt+F: Fallback and parsing behavior

- Alt+R: Validation rules

- Alt+A: Auto-correction

- Alt+S: Save

- Escape: Cancel

- Alt+/: Read status

- F1: Shortcut help

## Reading History Window

Open from View -\> Reading History.

- Alt+G: General tab

- Alt+Y: Year tab

- Alt+M: Month tab

- Alt+R: Date range tab

- Alt+B: Focus current table

- Alt+F: From date field

- Alt+S: Search/refresh

- Alt+/: Read status

- F1: Shortcut help

- Escape: Close

## Accessibility Tips

For sighted users:

- Use Ctrl+F to quickly find books

- Use sort menu and filters together for fast browsing

- Use zoom and theme preferences for comfort

For screen reader users:

- Use Alt+/ to replay status announcements

- Use F1 in each window to review available shortcuts

- Use table arrow navigation for line-by-line review in help/about dialogs

## Troubleshooting

- No command response: check focus first, then use F1 in that window.

- Import appears empty after scan: verify active filters and clear with Escape.

- Web info did not update: no matching web data may have been found for the current book.

