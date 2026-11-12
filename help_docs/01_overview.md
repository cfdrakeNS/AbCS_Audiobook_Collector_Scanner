# AbCS Help Overview

These guides describe the main tasks in AbCS (Audio Book Collector Scanner) in plain language. AbCS is designed for **sighted**, **low vision**, and **blind** users. Each guide explains what to do, what you see on screen, and what to listen for with a screen reader.

## About these guides

- **Process guides** walk through one window or task step by step.
- **Explained guides** describe import and web fetch in everyday terms.
- **Reference guides** list shortcuts, factory defaults, import settings, and the words AbCS uses.
- Each window guide has a **Window layout** section that describes the window from top to bottom.
- Each window guide has a **Mouse, shortcuts, and accessibility** section with point-and-click and keyboard options.
- Press **Shift+F1** in any window to open help for that window. Press **F1** for that window's keyboard shortcuts.

## Using Help

Open Help with **Help → Help...**, or press **Shift+F1** in any window. The list on the left shows the sections of the open guide. Select **All Help Topics** at the top of that list and press **Enter** to see every guide. Press **Ctrl+F** to search help.

Guide names under Related help open that guide. Click the name, or press **Enter** on its line. Other guide names in the text are not links. Open those from **All Help Topics**.

For the Help window layout, search, Help zoom, and its shortcuts, choose **using help** from All Help Topics.

## Check for updates

**Help → Check for updates** compares this copy of AbCS with the latest release. When a newer version is listed, **Open website** opens the AbCS website; the check installs nothing. **Manage → Preferences** has **Automatically check for updates**, off by default. When it is on, the same check runs after startup, and a message appears only when a newer version is available.

## Using the mouse in AbCS

These patterns apply across the application:

- **Menus** — click items on the menu bar: File, Edit, View, Sort, Manage, and Help. Underlined letters show the Alt-key shortcuts.
- **Toolbar** — many main-window actions are on the toolbar as well as in menus: Add Book, Find, Listen, the filters, Search Web, Statistics, Preferences, and Help.
- **Book table** — click a row to select it; **Ctrl+click** to add or remove rows from a selection; **Shift+click** to select a range. Double-click the **Title** column to open Book Details.
- **Column headers** — click a header to sort by that column; click again to reverse the order.
- **Buttons** — **Save**, **Browse**, **Import**, and similar controls work with a normal click.
- **Tabs** — click a tab label to switch sections, for example in Preferences and Reading History.
- **Dropdowns and checkboxes** — open combos and toggle checkboxes with the mouse in any window.
- **Status bar** — at the bottom of most windows; it shows counts and the result of each action.

Low vision users can increase text size under **Manage → Preferences → Display Settings**, or with **View → Zoom In** on the main window.

## Keyboard and screen reader tips

- Press **Alt+/** in any major window to re-read the current status message.
- Press **Escape** to cancel or close most windows. Some ask for confirmation first.
- In an AbCS message, **Escape** works like **Cancel**, or like **No** when there is no Cancel.
- Most AbCS messages and small windows are standard dialog boxes. Your screen reader's usual commands for reading a dialog and its title work in them.
- In a combo box you can type in, plain **Up** or **Down** may beep. Press **Alt+Down** to open the choices.
- In the help content area, each sentence is its own paragraph, so a screen reader can read it line by line.

## Process guides

| Guide | What it covers |
|-------|----------------|
| [Import (Folder Scan)](02_import.md) | Scan audiobook folders and import from audio file tags |
| [Find and Filters (Main Window)](03_find_filters.md) | The main window: search, filter, and sort the book list |
| [Book Details](04_book_details.md) | View or edit one book, or add a new book by hand |
| [Listen to a book](26_listen_to_a_book.md) | Play an audiobook inside AbCS and control playback |
| [Web Metadata Fetch](07_web_metadata.md) | Look up plot and other details online |
| [Name List](15_name_list.md) | Rename and merge author, series, and genre names |
| [Collections](06_collections.md) | Create and manage collections; filter by collection |
| [Duplicate Mode](08_duplicate_mode.md) | Find and clean up duplicate books in your library |
| [Backup and Restore](09_backup_restore.md) | Save or restore your database |
| [Update](05_update.md) | Set the series, genre, or collection on several books at once |
| [Preferences](10_preferences.md) | Theme, zoom, import scenarios, and validation rules |
| [Import Book List (Spreadsheet)](11_import_book_list.md) | Import books from a spreadsheet: CSV, Excel, or ODS |
| [Import Detail](12_import_detail.md) | Review and fix one held import book |
| [Reading History](13_reading_history.md) | Books finished and listening totals by period |
| [Statistics](14_statistics.md) | Library-wide counts and collection breakdown |
| [Check Book Locations](24_check_book_locations.md) | Find and fix books whose stored path is blank, missing, or outside the collection folder |
| [Export Library](25_export_library.md) | Save the books shown in the main list to a CSV or JSON file |

## Explained guides

These explain what happens during import and web fetch, in everyday language. Use them before or alongside the process guides.

| Guide | What it covers |
|-------|----------------|
| [Import explained](19_import_explained.md) | How folder scan import works (Ctrl+I) |
| [Import Book List explained](20_import_book_list_explained.md) | How spreadsheet import works (Ctrl+Shift+I) |
| [Web metadata explained](21_web_metadata_explained.md) | How Fetch Web Info works (Alt+W) |

## Suggested order for new users

A default collection named **Audiobooks** is created when the database is first set up. You can import into it right away, and use Collections later to rename it or add more.

1. **Import** — add books from audio folders, then review any held books in [Import Detail](12_import_detail.md). See [Import (Folder Scan)](02_import.md).
2. **Find and Filters** — browse and narrow the book list. See [Find and Filters (Main Window)](03_find_filters.md).
3. **Book Details** — fix book information or add a book by hand. See [Book Details](04_book_details.md).
4. **Listen to a book** — play a book and learn how your place is saved. See [Listen to a book](26_listen_to_a_book.md).
5. **Collections** — separate libraries for drives, shares, or lists. See [Collections](06_collections.md).
6. **Web Metadata Fetch** — add online details to a book. See [Web Metadata Fetch](07_web_metadata.md).
7. **Duplicate Mode** — find and remove duplicate books. See [Duplicate Mode](08_duplicate_mode.md).
8. **Backup and Restore** — make sure you can save and recover your data. See [Backup and Restore](09_backup_restore.md).

**Import Book List** is a separate import path for when you have a spreadsheet. See [Import Book List (Spreadsheet)](11_import_book_list.md).

## Reference

| Document | What it covers |
|----------|----------------|
| [Using Help](29_using_help.md) | The Help window: topics, sections, search, Help zoom, and its shortcuts |
| [Keyboard shortcuts by window](16_shortcuts.md) | Alt+key and other shortcuts for every AbCS window |
| [Default preferences](17_default_preferences.md) | Factory defaults for display, import, fallback, and validation rules |
| [Import preferences](18_import_preferences.md) | How each import scenario and validation rule behaves |
| [Glossary](27_glossary.md) | The words AbCS uses, such as collection, collection folder, and held for review |
| [What's New in Version 3](28_whats_new.md) | What version 3 adds for finding, organizing, listening, and maintaining the library |
