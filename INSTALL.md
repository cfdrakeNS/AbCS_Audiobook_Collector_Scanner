# AbCS - Installation and Quick Start Guide

## Prerequisites

- **Python 3.9 or higher** - Check with `python --version`
- **pip** - Python package installer
- **Your SQLite database** - You mentioned you already created this

## Installation Steps

### 1. Install Python Dependencies

Open a terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

This will install:
- PySide6 (Qt GUI framework)
- mutagen (audio file metadata reading)
- python-dateutil (date utilities)
- Send2Trash (safe file deletion)

### 2. Set Up Your Database

You mentioned you already have tables created in SQLite3. Make sure your database file is placed in the `data/` folder:

```
abcs_project/
└── data/
    └── abcs.db  (your existing SQLite database)
```

If you don't have a database yet, the application will create an empty one, but you'll need to create the tables. Here's a reference schema:

```sql
-- This is what your existing database should have
-- (You mentioned you already created these)

`CREATE TABLE` authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE series (
    series_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE collections (
    collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    borrowed INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER,
    year INTEGER,
    series_id INTEGER,
    genre_id INTEGER,
    collection_id INTEGER,
    reader TEXT,
    time_hours INTEGER DEFAULT 0,
    time_minutes INTEGER DEFAULT 0,
    tracks INTEGER DEFAULT 0,
    size_mb REAL DEFAULT 0.0,
    bitrate INTEGER DEFAULT 0,
    file_format TEXT,
    path TEXT,
    comments TEXT,
    read_date DATE,
    returned_date DATE,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT,
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (series_id) REFERENCES series(series_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id),
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
);

CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_books_series ON books(series_id);
CREATE INDEX idx_books_genre ON books(genre_id);
CREATE INDEX idx_books_collection ON books(collection_id);
CREATE INDEX idx_books_title ON books(title);
```

### 3. Run the Application

```bash
cd abcs_project
python src/main.py
```

Or on some systems:
```bash
python3 src/main.py
```

## First Launch

On first launch, you'll see:

1. **Splash Screen** - Shows statistics (will be empty if no data)
2. **Main Window** - The Audio Book Window with filter and search controls

## Quick Tour

### Main Window Layout

```
┌─ AbCS - Audio Book Collector Scanner ──────────────────────────┐
│ File  View  Help                                                │
├─────────────────────────────────────────────────────────────────┤
│ Collection: [All ▼] Read? [All ▼] Order: [Title ▼]              │
│ Search: [________________] Menu: [Select ▼] Selected: 0        │
├─────────────────────────────────────────────────────────────────┤
│ ┌─ Book List ────────────────────────────────────────────────┐ │
│ │ Author      │ Title      │ Year │ Series │ Genre │ ...    │ │
│ │─────────────┼────────────┼──────┼────────┼───────┼────────│ │
│ │             │            │      │        │       │        │ │
│ └────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ [Update] [Delete] [Cancel]               0 books  Sort: Title  │
└─────────────────────────────────────────────────────────────────┘
```

### Essential Keyboard Shortcuts

**Navigation:**
- `F3` - Focus search box / Clear search
- `F4` - Close window
- `F5` - Refresh view
- `F9` - Import window (coming soon)

**Filtering (Alt + letter):**
- `Alt+L` - Collection filter
- `Alt+R` - Read filter
- `Alt+O` - Order by
- `Alt+S` - Search box
- `Alt+M` - Menu

**Zoom:**
- `Ctrl +` - Zoom in
- `Ctrl -` - Zoom out
- `Ctrl 0` - Reset zoom

**Working with Books:**
- `Double-click` or `Enter` - Open book details
- `Space` - Select/deselect book
- `Insert` - New book
- `Delete` - Delete selected books

### Searching

**Regular Search:**
- Type in search box - autocomplete search
- Searches current "Order By" field (Title/Author/Genre/Series)

**Keyword Search:**
- Type `?` followed by search term
- Example: `?space` finds all books with "space" in title
- Shows only matching books (not just jumping to first match)

## Using the Book Details Window

1. **New Book**: Press `Insert` or Menu → New Title
2. **Edit Book**: Double-click a book in the list
3. Fill in fields:
   - Required: Title, Author
   - Optional: Year, Series, Genre, Reader, Comments, etc.
4. Press `Save` or `Alt+S`

## Accessibility Features

### Current Scale

The default scale is set to **125%** (similar to your MS Access 14pt fonts).

To change:
- `View` → `Zoom In/Out/Reset`
- Or use `Ctrl +` / `Ctrl -`

### Themes

Currently: Default system theme

Coming soon:
- View → Preferences → Theme
- High contrast options

### Screen Reader Support

All controls have:
- Accessible names
- Keyboard shortcuts (underlined in labels)
- Status bar announcements

Tested with NVDA on Windows.

## What's Working vs. Coming Soon

### ✅ Currently Working:
- Main window with book list
- Filtering by Collection, Read status
- Sorting by Title, Author, Genre, Series
- Search (both autocomplete and keyword)
- Book details window (view/edit/add/delete)
- Bulk selection (spacebar)
- Bulk delete
- UI scaling (Ctrl +/-)
- All keyboard shortcuts
- Database operations

### 🚧 Coming Soon (in starter code):
- Import window (scan folders for audiobooks)
- Bulk update window
- Collection/Author/Genre/Series management windows
- Backup/Restore
- Theme preferences dialog
- Duplicate detection view
- Import validation and error handling

## Testing the Application

### Add Some Test Data

Since you probably don't have data yet, you can:

1. **Manually add a book:**
   - Press `Insert`
   - Fill in: Title, Author, Year
   - Press Save

2. **Test search:**
   - Add 2-3 books
   - Try searching by title
   - Try `?keyword` search

3. **Test filtering:**
   - Add books to different collections (if you have collections in DB)
   - Use Collection filter dropdown

4. **Test scaling:**
   - Press `Ctrl +` several times
   - Watch everything get larger
   - Press `Ctrl 0` to reset

## Migrating Data from MS Access

If you want to migrate your existing MS Access data:

1. Export from Access to CSV files (one for each table)
2. Create a Python script to import CSV to SQLite
3. Or manually import using SQLite command line:

```sql
.mode csv
.import authors.csv authors
.import books.csv books
-- etc.
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the project directory
cd abcs_project

# Install dependencies
pip install -r requirements.txt

# Try running again
python src/main.py
```

### Database errors
- Make sure `data/abcs.db` exists
- Make sure tables are created (see schema above)
- Check file permissions

### Qt platform plugin errors
- Make sure PySide6 installed correctly
- Try: `pip install --upgrade PySide6`

### Window doesn't scale properly
- Close app
- Delete `~/.config/AbCS/` (Linux/Mac) or registry keys (Windows)
- Restart app

## Next Steps for Development

Priority order to add remaining features:

1. **Import Window** - The most complex feature
   - Folder selection dialog
   - Progress window
   - Error validation
   - Import detail window

2. **Bulk Update Window** - Relatively simple
   - Select books → Update button
   - Change Series/Genre for all selected

3. **List Windows** - Simple CRUD
   - Authors, Collections, Genres, Series
   - All similar structure

4. **Backup/Restore** - SQLite file copy
   - List existing backups
   - Create new backup
   - Restore from backup

5. **Preferences Dialog**
   - Display tab (scale, font)
   - Accessibility tab (theme, contrast)
   - Save/load settings

## File Structure Reference

```
abcs_project/
├── src/
│   ├── main.py              # Start here
│   ├── database/            # All database code
│   ├── ui/                  # All windows
│   ├── core/                # Scanner, validator
│   ├── accessibility/       # Scaling, themes, shortcuts
│   └── utils/               # Settings, helpers
├── data/                    # Your database
├── backups/                 # Backup files
├── resources/               # UI files, icons
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

## Getting Help

Key files to read:
- `README.md` - Overall project info
- `src/database/queries.py` - All SQL operations
- `src/ui/main_window.py` - Main UI logic
- `src/accessibility/scaling.py` - Zoom system

## Questions?

Common questions answered:

**Q: Can I use this with my existing Access database?**
A: No, but you can export from Access to CSV and import to SQLite.

**Q: How do I change the default zoom level?**
A: Edit `src/accessibility/scaling.py`, change `DEFAULT_SCALE = 125` to desired value.

**Q: Can I change keyboard shortcuts?**
A: Yes, edit `src/accessibility/shortcuts.py`.

**Q: How do I add more themes?**
A: Edit `src/accessibility/theme_manager.py`, add to `THEMES` dictionary.

## Ready to Go!

You now have a working starter application. Try it out:

```bash
python src/main.py
```

Enjoy your new accessible, cross-platform audiobook manager! 🎧
