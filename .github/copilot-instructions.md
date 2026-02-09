# AbCS - Copilot Instructions

**Project:** Audio Book Collector Scanner - PySide6/SQLite desktop application with full accessibility support for low vision and screen reader users (JAWS, NVDA)

## Overview

AbCS is a migration from MS Access to Python/PySide6. It's **designed for accessibility first**: 14pt+ fonts, high-contrast themes, complete keyboard navigation (Alt+letter, F-keys), and screen reader support. Users can import audiobooks by scanning ID3 tags, manage collections, search/filter, and perform bulk operations.

## Architecture Overview

AbCS follows a **layered architecture** with clear separation of concerns:

- **Database Layer** (`src/database/`) - SQLite connection, queries, data models
- **UI Layer** (`src/ui/`) - PySide6 windows (main_window.py, book_details.py, and planned windows)
- **Core Services** (`src/core/`) - Audio tag reading, import validation
- **Accessibility** (`src/accessibility/`) - Scaling, theming, keyboard shortcuts (critical for JAWS/NVDA)
- **Entry Point** (`src/main.py`) - Initializes Qt app, database, accessibility systems

### Key Data Flow

1. **Import:** Audio files → `tag_reader.py` (extracts metadata via mutagen) → `validator.py` (detects errors) → Database
2. **Browse:** Database → `BookQueries` → MainWindow table (with filtering/sorting)
3. **Edit:** MainWindow or BookDetailsWindow → Database queries → auto-save
4. **Bulk Ops:** Select books (Shift+Click, Ctrl+Click) → Update Window or Delete button
5. **Accessibility:** QSettings → `UIScaler`/`ThemeManager`/`ShortcutManager` → Applied to all windows

## Critical Conventions & Patterns

### Database Access
- Always use query classes from `src/database/queries.py` (e.g., `BookQueries`, `AuthorQueries`)
- Never write raw SQL in UI code - keep SQL in query classes
- Models are dataclasses in `models.py` - represent database table rows as Python objects
- Example: `book = BookQueries(db).get_by_id(123)` returns a `Book` object

### UI Windows & Window Structure Pattern
Every main window follows a consistent **header/detail/footer** layout:

**Header:** Combo boxes and controls for filtering, sorting, searching, navigation
- Examples: Collection filter, Read status filter, Order By, Search box, Menu
- Always include Alt+letter shortcuts for all header controls
- Use F3 for search focus/clear, F8 for opening related windows

**Detail:** Table or continuous list showing records with columns
- Main window: book table with Author, Title, Year, Series, Genre, Time, Tracks, Read, Date-Added columns
- Multi-select: **Shift+Click** for range, **Ctrl+Click** for individual, standard Qt behavior
- Double-click or Enter on Title to open BookDetailsWindow
- F8 or double-click on Author/Series/Genre fields opens management windows

**Footer:** Action buttons (visible based on context)
- Main window: Update, Delete, Cancel buttons (only when items selected)
- BookDetails: New, Save, Delete, Prev, Next, Close buttons
- Always include Alt+letter shortcuts; Alt+C or F4 for Close/Cancel

### Accessibility Requirements (CRITICAL - for JAWS/NVDA users)
- **Fonts:** Use 14pt default, scaling via `self.scaler.scale(14)` - never hardcode pixels
- **Themes:** High contrast required; apply via `self.theme_manager.apply_theme()` - 6 built-in themes
- **Keyboard Navigation:** 
  - ALL controls must have Alt+letter shortcuts (see reference table below)
  - F-keys: F2 (toggle text), F3 (search/clear), F4 (close), F5 (refresh), F6 (cycle focus), F8 (open related), F9 (import), F10 (menu)
  - Status bar echoes messages and selection feedback for screen readers
- **Messages:** Use custom message boxes (14pt font), route all messages to status bar
- **Example Flow:** Alt+S (search) → type query → status bar announces "Book found: Title by Author" → Shift+Click to select range

### Selection & Bulk Operations Pattern
- MainWindow tracks `self.selected_book_ids` (set of IDs) for bulk update/delete
- **Selection method:** Standard multi-select (Shift+Click range, Ctrl+Click individual)
- Update button opens UpdateWindow (mass update Series, Genre, Collection)
- Delete button deletes selected books with confirmation
- Cancel button clears selection and hides action buttons
- Status bar and header display count: "3 selected"

### Import/Audio Scanning Pattern
- `tag_reader.py`: Reads ID3 tags from MP3, M4A, FLAC, OGG, WAV via mutagen library
- Extracts: Title (Album tag), Author (Album Artist or Artist tag), Year, Genre, Time, Bitrate, etc.
- `validator.py`: Detects errors (blank author/title, unknowns, duplicates, read errors, file not found)
- Returns: List of tuples `(book_title, error_type, error_message)` for ImportWindow display
- **NOT YET BUILT:** ImportWindow UI, ImportDetailWindow (editable error view), ImportProgressWindow

### Theme & Scaling as First-Class Features
- `theme_manager.py`: 6 themes (Normal, High Contrast Light/Dark, etc.), custom theme support
- `scaling.py`: 50-300% zoom with presets (Tiny, Small, Normal, Large, Extra Large, Huge, Maximum)
- `shortcuts.py`: Centralized shortcut management with `ShortcutContext` enum
- These aren't "nice-to-have" - they're core to the application's mission for low vision users

## Common Development Workflows

### Running the Application
```bash
python src/main.py
```
On startup: Splash screen shows DB name and statistics (title count, author count, etc.), then MainWindow displays.

### Adding a New UI Window (Template Pattern)
1. Create class in `src/ui/new_window.py` inheriting from `QDialog` or `QMainWindow`
2. Inject `db`, `scaler`, `theme_manager` in `__init__` (required for all windows)
3. Structure as header/detail/footer sections (see MainWindow for example)
4. Register shortcuts in `__init__` using `ShortcutManager.register(ShortcutContext.WINDOW_NAME, ...)`
5. Apply scaling to all fonts: `font.setPointSize(self.scaler.scale(10))`
6. Status bar setup: `self.statusBar().showMessage(message)` (for screen readers)
7. Use custom message boxes (14pt) instead of QMessageBox for dialogs
8. Import and instantiate from parent window (e.g., main_window.py)

### Adding a New Query Type
1. Create method in appropriate query class (`src/database/queries.py`)
2. Use connection context: `with self.db.connection() as cursor: cursor.execute(...)`
3. Return dataclass instances (Book, Author, etc.) from models.py
4. Add error handling for missing data
5. Avoid raw SQL in UI code - keep it in queries.py

### Implementing Keyboard Shortcuts
Use `ShortcutManager` (not direct QShortcut):
```python
from accessibility.shortcuts import get_shortcut_manager, ShortcutContext

mgr = get_shortcut_manager()
mgr.register(ShortcutContext.MAIN_WINDOW, "Alt+S", self.on_search_activated)
mgr.register(ShortcutContext.MAIN_WINDOW, "F3", self.on_search_focus)
```

See `src/accessibility/shortcuts.py` for all defined shortcuts and contexts.

## Keyboard Shortcuts Reference

**F-Keys (Global):**
- F2: Toggle selected/unselected text within field
- F3: Focus search box / Clear search
- F4: Close window / Cancel edit
- F5: Refresh view
- F6: Cycle focus (Shift+F6 reverse) - Header → Detail → Footer → Menu
- F8: Open related window (Author/Series/Genre fields) or View import error details
- F9: Open Import window
- F10: Focus menu

**Alt+Letter Shortcuts (Sample from MainWindow header):**
- Alt+L: Collection filter
- Alt+R: Read filter
- Alt+O: Order by
- Alt+S: Search
- Alt+M: Menu
- Alt+U: Update (bulk)
- Alt+D: Delete (bulk)
- Alt+C: Cancel

**Zoom:**
- Ctrl+Plus: Zoom in
- Ctrl+Minus: Zoom out
- Ctrl+0: Reset zoom to 100%

All Alt+letter shortcuts are context-aware per `ShortcutContext` enum.

## File Organization & Key Files

| File | Purpose | Key Concept |
|------|---------|-------------|
| `src/main.py` | App lifecycle | Initializes Qt, DB, accessibility; shows splash with statistics |
| `src/database/connection.py` | DB connection | SQLite manager - low-level operations |
| `src/database/queries.py` | SQL operations | High-level queries (BookQueries, AuthorQueries, etc.) |
| `src/database/models.py` | Data models | Dataclasses (Book, Author, Series, Genre, Collection) |
| `src/ui/main_window.py` | Main UI | Book list, filters, search, bulk select/update/delete |
| `src/ui/book_details.py` | Book form | Add/edit books, form validation, navigation (Prev/Next) |
| `src/core/tag_reader.py` | Audio import | Extracts ID3 metadata from audio files (MP3, M4A, FLAC, OGG, WAV) |
| `src/core/validator.py` | Import validation | Detects errors: blank author/title, duplicates, read errors, file not found |
| `src/accessibility/scaling.py` | Font scaling | Scales all UI (50-300%) with presets |
| `src/accessibility/theme_manager.py` | Themes | 6 built-in themes, high contrast dark/light |
| `src/accessibility/shortcuts.py` | Keyboard shortcuts | Centralized F-key and Alt+letter shortcuts by context |

## Implementation Status

### ✅ Fully Implemented (Working)
- Database layer (CRUD, queries, transactions)
- Main Window (browse, filter, search, multi-select, bulk delete)
- Book Details Window (add, edit, navigate, auto-save)
- Accessibility framework (scaling, themes, shortcuts)
- Audio tag reader (metadata extraction)
- Validator (error detection)
- Keyboard navigation (all F-keys and Alt+letter shortcuts)

### 🚧 Not Yet Implemented (Framework Ready)
The backend code exists; UI windows need building:
- **Import Window** - UI to scan folders, display import list with error counts, add books to DB
- **Import Detail Window** - Edit individual imports with errors (tag viewer, fix, keep/discard)
- **Import Status Window** - Real-time progress during scan (files scanned, elapsed time, errors found)
- **Update Window** - Bulk update Series, Genre, Collection for selected books
- **Collection Window** - Add/edit collections, set active status
- **Author/Genre/Series Windows** - Edit/correct these references
- **Show Duplicates** - Find books with same Title, Author, Year, Collection
- **Backup/Restore Window** - Backup DB, restore, full reset
- **Preferences Dialog** - Adjust scaling presets, theme, zoom level

Follow the same header/detail/footer pattern as existing windows when building these.

## Testing & Debugging Tips

- **Database:** Check `data/abcs.db` exists; use SQLite viewer to inspect tables
- **Scaling:** Verify fonts scale by setting `UIScaler.DEFAULT_SCALE = 150` and checking MainWindow
- **Themes:** Change via Menu → View Preferences; test with high contrast themes
- **Keyboard:** Use `ShortcutManager.list_shortcuts()` to verify all shortcuts registered for a context
- **Audio import:** `tag_reader.py` includes debug output for ID3 extraction; use `validator.py` to check error detection
- **Screen readers (JAWS/NVDA):** Test status bar messages, focus order (F6), and screen reader announcements
- **Multi-select:** Test Shift+Click (range), Ctrl+Click (individual) on book table
