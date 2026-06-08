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

- Python 3.9 or higher (3.12 recommended for development)
- Windows, macOS, or Linux

## Installation and quick start

See [INSTALL.md](INSTALL.md) for step-by-step setup.

```bash
pip install -r requirements.txt
python src/main.py
```

On first launch, AbCS creates a SQLite database automatically. No manual schema setup is required.

## User documentation

Workflow guides for screen reader users:

- [User guide index](doc/abcs_user_index.md) — collections, import, filters, web metadata, backup, and more
- [Keyboard shortcuts by window](doc/abcs_shortcuts_list.md)
- [Default preferences](doc/abCS_default_preference.md)
- [Import preferences (scenarios and rules)](doc/Import_preferences.md)

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

See [doc/abcs_shortcuts_list.md](doc/abcs_shortcuts_list.md) for every window.

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

If you used the original MS Access prototype:

1. Export your Access data to CSV and use **Import Book List**, or re-import from audio folders.
2. Keyboard shortcuts and workflows are designed to feel familiar.
3. Default zoom is **150%** (adjust in **Manage → Preferences**).
4. Core features from the Access version are included in AbCS.

## Accessibility

- All major controls have accessible names and keyboard shortcuts.
- Status changes are announced for screen readers (`Alt+/` re-reads the current status).
- High contrast themes are available in Preferences.

### Developer documentation

- [PySide6 Accessibility Patterns and Implementation Reference](doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md)
- [PySide6 Screen Reader Accessibility Best Practices](doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md)

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

For support or licensing requests, contact C.F. Drake.

## Credits

Original MS Access version: C.F. Drake  
Python version: C.F. Drake
