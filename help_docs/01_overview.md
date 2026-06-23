# AbCS Help Overview

These guides describe major workflows in AbCS (Audio Book Collector Scanner) in plain language. AbCS is designed for **sighted**, **low vision**, and **blind** users. Each guide explains what to do, what you should see on screen, and what to listen for with a screen reader.

## About these guides

- **Process guides** (02–15) walk through one window or workflow step by step.
- **Explained guides** (19–21) describe import and web fetch in everyday terms without technical detail.
- **Reference guides** (16–18) list shortcuts, factory defaults, and import settings.
- Every workflow guide has a **Mouse, shortcuts, and accessibility** section with both point-and-click and keyboard options.
- Press **Shift+F1** in any window to open help for that window. Press **F1** for keyboard shortcuts only.

## The help system

### Opening help

- **Menu:** Click **Help** on the menu bar, then **Help...**
- **Context help:** Press **Shift+F1** in any window to open the guide for that window
- **Shortcuts only:** Press **F1** in any window for a list of keyboard shortcuts (not the full process guide)

### Help window layout

The help window has two main areas side by side:

1. **Help Navigation** (left) — a list you can scroll with the mouse or arrow keys
2. **Help content** (right) — the full text of the selected guide

At the bottom are a **Close** button and a status bar. Press **Alt+/** to re-read the status message.

### Topics and sections

When help first opens, the navigation list shows **sections** from the current guide (for example, *What this is*, *Steps*, *Common confusion*).

- Click a section name, or select it and press **Enter**, to jump to that heading in the content area.
- Click **All Help Topics** at the top of the list (or select it and press **Enter**) to see every guide in the library.
- Click a topic name, or select it and press **Enter**, to load that guide. The list then shows that guide's sections again.

**Keyboard navigation in the help window:**

| Key | Action |
|-----|--------|
| Alt+L | Move focus to the Help Navigation list |
| Tab | Switch focus between the list and the content area |
| Enter | Open the selected topic or jump to the selected section |
| Arrow keys | Move through list items or read the content line by line |
| Escape | Close help |

### How topics are listed

Help topics are loaded automatically from the `help_docs` folder. Each file uses the name pattern **`nn_topic_name.md`** (two digits, underscore, topic words). In the topic list, the number is hidden and underscores become spaces — for example, `11_import_book_list.md` appears as **import book list**.

Add a new numbered markdown file to that folder and it appears in **All Help Topics** without changing the application.

## Using the mouse in AbCS

These patterns apply across the application:

- **Menus** — click items on the menu bar (File, Edit, View, Manage, Help). Underlined letters show Alt-key shortcuts if you prefer the keyboard.
- **Toolbar** — many main-window actions (Import, Update, Search Web, Statistics, filters) are on the toolbar as well as in menus.
- **Book table** — click a row to select it; **Ctrl+click** to add or remove rows from a selection; **Shift+click** to select a range. Double-click the **Title** column to open Book Details.
- **Column headers** — click a header to sort by that column; click again to reverse ascending/descending order.
- **Buttons** — **Save**, **Cancel**, **Browse**, **Import**, and similar controls work with a normal click.
- **Tabs** — click a tab label to switch sections (Preferences, Reading History, and others).
- **Dropdowns and checkboxes** — open combos and toggle checkboxes with the mouse in any dialog.
- **Status bar** — at the bottom of most windows; shows filter summaries, counts, and operation results.

Low-vision users can increase text size under **Manage → Preferences → Display Settings** (zoom) or with **View → Zoom In** on the main window.

## Keyboard and screen reader tips

- Press **Alt+/** in any major window to re-read the current status message.
- Press **Escape** to cancel or close most dialogs (some ask for confirmation first).
- In the help content area, each sentence is its own paragraph so screen readers can review line by line without repeated wrapped-line noise.

## Process guides

| Guide | What it covers |
|-------|----------------|
| [Import (Folder Scan)](02_import.md) | Scan audiobook folders and import from audio file tags |
| [Find and Filters](03_find_filters.md) | Search, filter, and sort the main book list |
| [Book Details](04_book_details.md) | View or edit one book; add a new book by hand |
| [Update](05_update.md) | Change fields on several selected books at once |
| [Collections](06_collections.md) | Create and manage collections; filter by collection |
| [Web Metadata Fetch](07_web_metadata.md) | Look up plot, series, and other details online |
| [Duplicate Mode](08_duplicate_mode.md) | Find and clean up duplicate books in your library |
| [Backup and Restore](09_backup_restore.md) | Save or restore your database |
| [Preferences](10_preferences.md) | Theme, zoom, import scenarios, and validation rules |
| [Import Book List](11_import_book_list.md) | Import books from a spreadsheet (CSV, Excel, or ODS) |
| [Import Detail](12_import_detail.md) | Review and fix one held import item |
| [Reading History](13_reading_history.md) | Books finished and listening totals by period |
| [Statistics](14_statistics.md) | Library-wide counts and collection breakdown |
| [Name List](15_name_list.md) | View and edit author, series, and genre name lists |

## Explained guides

These explain *what happens behind the scenes* in everyday language. Use them before or alongside the process guides above.

| Guide | What it covers |
|-------|----------------|
| [Import explained](19_import_explained.md) | How folder scan import works (Ctrl+I) |
| [Import Book List explained](20_import_book_list_explained.md) | How spreadsheet import works (Ctrl+Shift+I) |
| [Web metadata explained](21_web_metadata_explained.md) | How Fetch Web Info works (Alt+W) |

## Suggested order for new users

A default collection named **Audio Books** is created when the database is first set up. You can import into it right away; use the Collections guide when you want to rename it or add more collections.

1. **Import** — add books from audio folders. See [02 Import](02_import.md).
2. **Find and Filters** — browse and narrow the book list. See [03 Find and Filters](03_find_filters.md).
3. **Book Details** — fix metadata or add a manual entry. See [04 Book Details](04_book_details.md).
4. **Collections** — organize your library. See [06 Collections](06_collections.md).
5. **Web Metadata Fetch** — enrich a book with online details. See [07 Web Metadata Fetch](07_web_metadata.md).
6. **Duplicate Mode** — find and remove duplicate entries. See [08 Duplicate Mode](08_duplicate_mode.md).
7. **Backup and Restore** — confirm you can save and recover your data. See [09 Backup and Restore](09_backup_restore.md).

**Import Book List** is a separate import path; use it when you have a spreadsheet to import. See [11 Import Book List](11_import_book_list.md).

## Reference

| Document | What it covers |
|----------|----------------|
| [Keyboard shortcuts by window](16_shortcuts.md) | Alt+key and other shortcuts for every AbCS window |
| [Default preferences](17_default_preferences.md) | Factory defaults for display, import, fallback, and validation rules |
| [Import preferences (scenarios)](18_import_preferences.md) | How each import scenario and validation rule behaves |

Import scenario behavior is also summarized in [Import preferences](18_import_preferences.md).
