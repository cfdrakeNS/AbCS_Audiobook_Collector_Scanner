# AbCS - Audio Book Collector Scanner

A cross-platform audiobook collection manager with full accessibility support (JAWS, NVDA, and other screen readers).

## Features

- **Audio book management** — track your collection with full metadata
- **ID3 tag import** — scan folders and import from audio file tags
- **Book list import** — import from CSV, Excel, or ODS spreadsheets
- **Advanced search** — filter by title, author, genre, series, plot, and read status
- **Collections** — organize books into multiple collections
- **Bulk update and delete** — change or remove many books at once
- **Duplicate mode** — find and clean up duplicate entries
- **Backup and restore** — protect your database
- **Web metadata** — fetch plot, series, and related fields from Open Library, Google Books, and WikiData
- **Reading history and statistics** — track what you have listened to
- **Accessibility first**
  - Complete keyboard navigation (Alt+key shortcuts)
  - Screen reader support (NVDA, JAWS, Narrator, Orca)
  - Scalable UI (50%–200%+)
  - High contrast themes

## Requirements

- Python 3.10 or higher (3.14 recommended for development)
- Windows, macOS, or Linux

## Installation and quick start

See [INSTALL.md](INSTALL.md) for step-by-step setup.

```bash
pip install -r requirements.txt
python src/main.py
```

On first launch, AbCS creates a SQLite database automatically. No manual schema setup is required.

**Note for Windows Users:** As this is a new, free and source-available project, Windows SmartScreen may display a warning during installation. To bypass this, click **'More info'** on the blue popup window, and then click **'Run anyway.'** This is a standard security check for independent software.

## User documentation

AbCS includes in-app help for sighted, low vision, and blind users. Guides live in the [`help_docs/`](help_docs/) folder as markdown files.

### Using help in the app

- **Help → Help...** — opens the help window (overview by default)
- **Shift+F1** — context-sensitive help for the current window
- **F1** — keyboard shortcuts for the current window (not the full process guide)
- **Alt+/** — re-read the status message

The help window has a **Help Navigation** list on the left and the document on the right. Choose **All Help Topics** to browse every guide, or pick a section heading to jump within the current guide. Use **Tab** to move between the list and content.

Start here: [User guide overview](help_docs/01_overview.md)

Reference guides:

- [Keyboard shortcuts by window](help_docs/16_shortcuts.md)
- [Default preferences](help_docs/17_default_preferences.md)
- [Import preferences (scenarios and rules)](help_docs/18_import_preferences.md)

### Adding or changing help topics (dynamic topics)

Topic names in the help window are **not** hard-coded. At runtime, AbCS scans `help_docs/` for markdown files matching:

```text
nn_topic_name.md
```

- `nn` — two-digit sort order (for example `02`, `11`)
- `topic_name` — lowercase words separated by underscores

The navigation list shows the filename **without** the number, with underscores replaced by spaces. Example: `11_import_book_list.md` appears as **import book list**.

To add a guide:

1. Create `help_docs/19_my_new_topic.md` (use the next free number).
2. Start the file with an `#` heading (used as the window title).
3. Use `##` and `###` headings for sections (they appear in the section list after the topic is opened).
4. Link to other guides with `[label](02_import.md)` — use the filename only.

No code change is required for the topic to appear in **All Help Topics**.

Full authoring rules (naming, allowed markdown, accessibility): [doc/help_docs_authoring.md](doc/help_docs_authoring.md).

**Shift+F1** context help is separate: each window maps to a specific file in [`src/ui/help_router.py`](src/ui/help_router.py) (`WINDOW_HELP_MAP`). Update that map when a new window needs its own default help doc.

Implementation details:

| Module | Role |
|--------|------|
| [`src/accessibility/help_paths.py`](src/accessibility/help_paths.py) | Discovers topics, resolves paths (dev and installed builds) |
| [`src/ui/help_window.py`](src/ui/help_window.py) | Help viewer UI, markdown → HTML, navigation list |
| [`src/ui/help_router.py`](src/ui/help_router.py) | Shift+F1 routing and `show_help_doc()` entry point |

Tests: [`test/test_help_router.py`](test/test_help_router.py)

Press **F1** in any window for that window's shortcuts. Press **Alt+/** to re-read the status message.

## Keyboard shortcuts (summary)

### Global

- **F1** — show keyboard shortcuts / help
- **Alt+/** — re-read status bar
- **Ctrl/Cmd +** — zoom in
- **Ctrl/Cmd -** — zoom out
- **Ctrl/Cmd 0** — reset zoom

### Main window

- **Ctrl+I** — import (folder scan)
- **Alt+L** — collection filter
- **Alt+R** — read filter
- **Alt+O** — order by
- **Alt+S** — search
- **Alt+M** — menu
- **Space** — select/deselect book (bulk operations)
- **Alt+U** — update selected
- **Alt+D** — delete selected

See [help_docs/16_shortcuts.md](help_docs/16_shortcuts.md) for every window.

## Project structure

```
AbCS/
├── src/              # Application source
│   ├── main.py       # Entry point
│   ├── database/     # SQLite layer
│   ├── ui/           # Windows and dialogs
│   ├── core/         # Import scanner, validator, tag reader
│   ├── accessibility/
│   ├── web/          # Web metadata APIs
│   └── utils/
├── doc/              # User and developer documentation
├── help_docs/        # In-app help topics (nn_topic_name.md; loaded dynamically)
├── test/             # Automated tests (pytest)
├── data/             # Development database (created at runtime)
├── Graphics/         # Icons and splash images
├── backups/          # Database backups
└── releases/         # Built installers (when present)
```

## Development

### Running tests

```bash
python -m pytest test/
```

See [TESTING.md](TESTING.md) for CI-style runs, headless Qt, and useful pytest switches.

### Code style

- Follow PEP 8
- Type hints encouraged
- Document accessibility features in code and user-facing strings

### Building installers

- **Windows:** `build_installer.bat` (PyInstaller + Inno Setup)
- **Linux:** [linux_build.md](linux_build.md)

## Migrating from the MS Access version

If you used the original MS Access prototype, export your data to CSV and use **Import Book List**, or re-import from audio folders. There is no automated migration tool. Keyboard shortcuts and workflows are designed to feel familiar; default zoom is **150%** (adjust in **Manage → Preferences**).

## Accessibility

- All major controls have accessible names and keyboard shortcuts.
- Status changes are announced for screen readers (`Alt+/` re-reads the current status).
- High contrast themes are available in Preferences.

### Developer documentation

- [PySide6 Accessibility Patterns and Implementation Reference](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md)
- [PySide6 Screen Reader Accessibility Best Practices](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md)
- Runnable sample app: [pyside6-accessible-ui-reference](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference) — clone the repo, `pip install -r requirements.txt`, then `python main.py`

Legacy accessibility demos and completed bug-fix logs are in the local `archive/` folder (`archive/accessible_pySIde6_demo/`, `archive/AbCS_Bug_Final_fixes.md`). See [doc/qa_verification.md](doc/qa_verification.md).

## Tester build expiry

Bundled tester builds expire 30 days after the build date. When expired, AbCS blocks startup and prompts you to download a newer build. Source runs use the same expiry check when `TRIAL_BUILD_DATE` is set in `src/build_config.py`.

## License

Copyright (c) 2025-2026 C.F. Drake & Contributors.

AbCS is provided under a custom non-commercial license:

- You may use, copy, and share this software for personal, educational, testing, and other non-commercial use.
- You may modify this software for your own use.
- If you redistribute copies or modified versions, this copyright and license notice must remain intact.
- Commercial use is prohibited without prior written permission from the copyright holder.
- You may not sell this software, bundle it into paid products, or distribute it for a fee without explicit written authorization.
- The software is provided "as is", without warranty of any kind.

## Support

For support or licensing requests, contact [auroraaccessibility@gmail.com](mailto:auroraaccessibility@gmail.com).

## Credits

Original MS Access version: C.F. Drake  
Python version: C.F. Drake
