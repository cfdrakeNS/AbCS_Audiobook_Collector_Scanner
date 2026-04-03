# AbCS - Audio Book Collector Scanner

A cross-platform audiobook collection manager with full accessibility support.

## Features

- **Audio Book Management**: Track your audiobook collection with full metadata
- **ID3 Tag Import**: Automatically scan folders and import audiobook details from ID3 tags
- **Advanced Search**: Filter by title, author, genre, series with instant search
- **Collections**: Organize books into multiple collections
- **Accessibility First**: 
  - Complete keyboard navigation (Alt+key shortcuts)
  - Screen reader support (NVDA, JAWS, VoiceOver)
  - Scalable UI (50%-200%+)
  - High contrast themes
- **Bulk Operations**: Select multiple books for update or deletion
- **Backup/Restore**: Protect your data with easy backup management

## Requirements

- Python 3.9 or higher
- Windows, macOS, or Linux

## Installation

1. Clone or extract the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/main.py
   ```

### Tester Build Expiry

- Bundled tester builds expire after 30 days from build date.
- When expired, AbCS blocks startup and prompts the tester to download a newer build.
- Source runs currently use the same build-expiry check.

## Quick Start

1. **First Launch**: The application will create a new database
2. **Import Books**: Press Ctrl+I or use Menu → Import to scan your audiobook folders
3. **Browse & Search**: Use the main window to explore your collection
4. **Customize**: View → Preferences to adjust font size, theme, and accessibility settings

## Keyboard Shortcuts

### Global
- **F1**: Show keyboard shortcuts/help
- **Ctrl/Cmd +**: Zoom In
- **Ctrl/Cmd -**: Zoom Out
- **Ctrl/Cmd 0**: Reset Zoom

### Main Window
- **Alt+L**: Collection filter
- **Alt+R**: Read filter
- **Alt+O**: Order by
- **Alt+S**: Search
- **Alt+M**: Menu
- **Space**: Select/deselect book (for bulk operations)
- **Alt+U**: Update selected
- **Alt+D**: Delete selected
- **Alt+C**: Cancel selection

### Book Details
- **Alt+T**: Title
- **Alt+A**: Author
- **Alt+Y**: Year
- **Alt+I**: Series
- **Alt+G**: Genre
- **Alt+V**: Save
- **Alt+N**: Next book (Page Down)
- **Alt+P**: Previous book (Page Up)
- **Insert**: New book
- **Delete**: Delete current book

## Project Structure

```
abcs_project/
├── src/                    # Source code
│   ├── main.py            # Application entry point
│   ├── database/          # Database layer
│   ├── ui/                # User interface windows
│   ├── core/              # Core functionality (scanner, validator)
│   ├── accessibility/     # Accessibility features
│   └── utils/             # Utilities and settings
├── resources/             # UI files, icons, themes
├── data/                  # Database location
├── backups/              # Backup files
└── tests/                # Unit tests

```

## Database Schema

The application uses SQLite with the following main tables:
- **books**: Audio book records
- **authors**: Author information
- **series**: Book series
- **genres**: Genre classifications
- **collections**: User collections
- **settings**: Application preferences

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
- Follow PEP 8
- Type hints encouraged
- Document accessibility features

## Migrating from MS Access Version

If you're migrating from the MS Access prototype:
1. Export your Access data to CSV (optional migration script coming)
2. The UI will feel familiar - same keyboard shortcuts
3. Default scale is set to ~125% (similar to Access 14pt fonts)
4. All features from Access version are included

## Accessibility Notes

- All controls have Alt+key shortcuts (underlined in UI)
- Status bar announces actions for screen readers
- High contrast themes available
- Minimum touch target size: 44x44 pixels
- Focus indicators clearly visible
- Tab order follows logical flow

## Accessibility Documentation

For implementation and contribution work, use these two canonical docs:

- `PySide6_Accessibility_Patterns_and_Implementation_Reference.md` (code patterns and implementation checklist)
- `PySide6_Screen_Reader_Accessibility_Best_Practices.md` (design principles and review rules)

Legacy accessibility docs are archived under `archive/`.

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
