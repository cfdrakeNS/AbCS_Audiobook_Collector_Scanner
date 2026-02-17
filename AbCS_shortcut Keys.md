# AbCS Shortcut Keys (by Window)

This list reflects shortcuts currently implemented in code as of 2026-02-17.

## Mnemonic rules

- Use unique **Alt+letter** mnemonics within each window/dialog (no duplicates in the same form).
- Prefer first letter of the control/action when available; otherwise use a memorable consonant.
- Keep action buttons consistent across windows where possible:
	- **Alt+S** Save / Scan / Scenario (context-specific)
	- **Alt+C** Close / Cancel
	- **Alt+I** Import
- Avoid assigning Alt mnemonics to read-only fields unless users need direct focus there.
- Menu bar mnemonics may repeat across different menus (normal Qt behavior).
- After changing any `&` mnemonic in code, update this document in the same change.

## Main Window (`src/ui/main_window.py`)

### Alt shortcuts
- **Alt+C**: Collection filter
- **Alt+R**: Read filter
- **Alt+O**: Order by
- **Alt+S**: Search
- **Alt+B**: Book list focus
- **Alt+U**: Update selected
- **Alt+D**: Delete selected
- **Alt+L**: Cancel selection
- **Alt+/**: Read status bar aloud
- **Alt+1..Alt+0**: Jump to table columns

### Function / navigation shortcuts
- **F1**: Show keyboard shortcuts
- **Escape**: Clear selection/search (window handler)

### Ctrl shortcuts
- **Ctrl+N**: New Book
- **Ctrl+I**: Import
- **Ctrl+Q**: Quit
- **Ctrl+Return**: Open Book Details
- **Ctrl++** and **Ctrl+Num++**: Zoom in
- **Ctrl+-** and **Ctrl+Num+-**: Zoom out
- **Ctrl+0**: Reset zoom

---

## Book Details Window (`src/ui/book_details.py`)

### Alt shortcuts (field focus / buttons)
- **Alt+T**: Title
- **Alt+A**: Author
- **Alt+O**: Comments
- **Alt+Y**: Year
- **Alt+M**: Time
- **Alt+R**: Reader
- **Alt+E**: Read date
- **Alt+I**: Series
- **Alt+G**: Genre
- **Alt+K**: Collection
- **Alt+F**: Files
- **Alt+B**: Bitrate
- **Alt+Z**: Size
- **Alt+H**: Path
- **Alt+N**: New
- **Alt+S**: Save
- **Alt+D**: Delete
- **Alt+L**: Cancel
- **Alt+C**: Close
- **Alt+/**: Read status bar aloud

### Function / navigation shortcuts
- **F1**: Show keyboard shortcuts
- **Page Up**: Previous book
- **Page Down**: Next book
- **Escape**: Close window

### Other shortcuts
- **Ctrl+Return**: New book
- **Delete**: Delete current book

---

## Import Window (`src/ui/import_window.py`)

### Alt shortcuts
- **Alt+C**: Collection field
- **Alt+F**: Folder field
- **Alt+E**: Error filter
- **Alt+W**: Browse
- **Alt+S**: Scan
- **Alt+I**: Import Selected
- **Alt+V**: Import All Valid
- **Alt+L**: Close window (idle)
- **Alt+C**: Cancel scan (while scanning)
- **Alt+B**: Focus import list table
- **Alt+1..Alt+5**: Jump to import table columns
- **Alt+/**: Read status bar aloud

### Function / navigation shortcuts
- **F1**: Show keyboard shortcuts

### Other shortcuts
- **Ctrl+Return** and **Ctrl+Enter**: Open selected item in Import Detail

---

## Import Detail Window (`src/ui/import_detail_window.py`)

### Alt shortcuts (field focus / buttons)
- **Alt+T**: Title
- **Alt+A**: Author
- **Alt+O**: Comments
- **Alt+Y**: Year
- **Alt+M**: Time
- **Alt+R**: Reader
- **Alt+I**: Series
- **Alt+G**: Genre
- **Alt+C**: Collection
- **Alt+F**: Files
- **Alt+B**: Bitrate
- **Alt+Z**: Size
- **Alt+E**: Errors
- **Alt+H**: Path
- **Alt+S**: Save
- **Alt+D**: Discard

### Function / navigation shortcuts
- **F1**: Show keyboard shortcuts/help
- **Page Up**: Previous import item
- **Page Down**: Next import item
- **Escape**: Close/Cancel

### Other shortcuts
- **Alt+/**: Read status bar aloud

---

## Update Window (`src/ui/update_window.py`)

### Alt shortcuts
- **Alt+S**: Series
- **Alt+G**: Genre
- **Alt+L**: Collection
- **Alt+C**: Close
- **Alt+B**: Focus book list
- **Alt+Down**: Open combo dropdown

### Function / navigation shortcuts
- **F1**: Show keyboard shortcuts
- **Escape**: Close window

---

## Preferences Window (`src/ui/preferences_window.py`)

### Alt shortcuts
- **Alt+/**: Read status bar aloud
- **Alt+T**: Theme
- **Alt+P**: Preset
- **Alt+Z**: Zoom (%)
- **Alt+D**: Directory
- **Alt+B**: Browse
- **Alt+O**: Formats
- **Alt+S**: Scenario
- **Alt+R**: Scenario Description
- **Alt+A**: Author Fallback
- **Alt+I**: Title Fallback
- **Alt+F**: Flip Author
- **Alt+K**: Reader Keywords
- **Alt+W**: Trim whitespace
- **Alt+L**: Proper case fields
- **Alt+U**: Audit display
- **Alt+V**: Save
- **Alt+C**: Cancel

### Function / navigation shortcuts
- **F1**: Show keyboard shortcuts

### Import duplicate matching (Preferences setting)
- Duplicate matching mode options:
	- **Exact**: Title + Author + Year + Collection
	- **Ignore Collection**: Title + Author + Year
	- **Ignore Year**: Title + Author + Collection
	- **Title + Author only**
- Fuzzy threshold option:
	- **Fuzzy Duplicate (%)**: `0` disables fuzzy matching; `1-100` enables similarity-based duplicate detection for title and author

### File structure rule (Preferences setting)
- **File Structure pattern** options:
	- **Author/Title**
	- **Year/Author/Title**
	- **Either**
- **Severity** options: `None`, `Error`, `Warning`

---

## Shortcut QA Checklist (Before Commit)

- Run `python test/check_shortcut_mnemonics.py` (or `.venv/Scripts/python.exe test/check_shortcut_mnemonics.py`).
- Verify no duplicate **Alt+letter** mnemonics exist within any single window/dialog.
- Verify **F1** opens shortcut/help content where implemented.
- Verify **Escape** closes the intended dialog/window.
- Verify **Alt+/** reads status bar text in windows that support it.
- Verify this file is updated for any changed `&` labels or added shortcuts.
