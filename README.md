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

## License

[Your chosen license - MIT, GPL, etc.]

## Support

[Your contact/support information]

## Credits

Original MS Access version: [Your name]
Python version: [Your name]
