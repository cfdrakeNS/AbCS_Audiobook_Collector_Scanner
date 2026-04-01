# Book List Import Feature Design

## Overview
New feature to import books from spreadsheet files with two modes:
1. **Import Mode** - Add new books with full data
2. **Read Date Mode** - Update read dates for existing books

## Window Architecture

### File: `src/ui/book_list_import_window.py`

#### UI Layout (Following AbCS Standards)
```
┌─────────────────────────────────────────────────────────┐
│ Book List Import - [File: selected_file.xlsx]           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Import Mode: ◉ Import New Books  ○ Update Read Dates   │
│                                                         │
│ Field Mapping Table:                                    │
│ ┌─────────────────────┬─────────────────────────────────┐ │
│ │ Field              │ Spreadsheet Column              │ │
│ ├─────────────────────┼─────────────────────────────────┤ │
│ │ Title *            │ [Column 1 ▼]                    │ │
│ │ Author *           │ [Column 2 ▼]                    │ │
│ │ Year               │ [Column 3 ▼]                    │ │
│ │ Plot               │ [Column 4 ▼]                    │ │
│ │ Series             │ [Column 5 ▼]                    │ │
│ │ Genre              │ [Column 6 ▼]                    │ │
│ │ Reader             │ [Column 7 ▼]                    │ │
│ │ Read Date          │ [Column 8 ▼]                    │ │
│ │ Time               │ [Column 9 ▼]                    │ │
│ │ Tracks             │ [Column 10 ▼]                   │ │
│ └─────────────────────┴─────────────────────────────────┘ │
│                                                         │
│ Collection: "Book List" (auto-created if needed)        │
│                                                         │
│ [Preview] [Import] [Cancel]                             │
│                                                         │
│ Status: Ready                                           │
└─────────────────────────────────────────────────────────┘
```

## Accessibility Standards Compliance

### 1. ALLOWED_ALT_LETTERS
```python
ALLOWED_ALT_LETTERS = "F M T A Y P S G R I H B C V L /"
```
- **F** - File selector
- **M** - Import mode toggle
- **T** - Title field
- **A** - Author field  
- **Y** - Year field
- **P** - Plot field
- **S** - Series field
- **G** - Genre field
- **R** - Reader field
- **I** - Read Date field
- **H** - Time field
- **B** - Tracks field
- **C** - Preview button
- **V** - Import button
- **L** - Cancel (close)
- **/** - Status bar readback

### 2. Status Bar Pattern
- `set_status()` method for announcements
- `Alt+/` for status readback
- Progress announcements during import

### 3. F1 Help Dialog
- Complete keyboard shortcut list
- Import workflow explanation
- Field mapping instructions

### 4. Focus Management
- Tab order: File selector → Mode toggle → Field table → Buttons
- Return focus after operations
- Error field focus on validation failures

### 5. Modal Messaging
- Use `exec_styled_message_box()` for all dialogs
- Validation errors with focus return
- Success/failure announcements

## Technical Implementation

### File Support
- **Excel (.xlsx, .xls)** - Primary format
- **CSV (.csv)** - Secondary format
- File validation and error handling

### Import Modes

#### Mode 1: Import New Books
1. Validate required fields (Title, Author)
2. Check for duplicates (Title + Author)
3. Create new book records
4. Add to "Book List" collection
5. Announce import results

#### Mode 2: Update Read Dates
1. Match existing books by Title + Author
2. Update read date field only
3. Skip unmatched books with log
4. Announce update results

### Field Mapping Logic
```python
FIELD_MAPPINGS = {
    'title': {'required': True, 'label': 'Title *'},
    'author': {'required': True, 'label': 'Author *'},
    'year': {'required': False, 'label': 'Year'},
    'plot': {'required': False, 'label': 'Plot'},
    'series': {'required': False, 'label': 'Series'},
    'genre': {'required': False, 'label': 'Genre'},
    'reader': {'required': False, 'label': 'Reader'},
    'read_date': {'required': False, 'label': 'Read Date'},
    'time_hours': {'required': False, 'label': 'Time'},
    'tracks': {'required': False, 'label': 'Tracks'}
}
```

### Validation Rules
1. **File validation** - Check format, readability
2. **Required fields** - Title and Author must have column mapping
3. **Data validation** - Year format, date format, numeric fields
4. **Duplicate handling** - Configurable skip/update options

### Error Handling
- Missing required fields
- Invalid file format
- Data format errors
- Database constraint violations
- Clear error messages with focus return

## Integration Points

### Menu Integration
- **File → Import Book List** - New menu item
- **Keyboard shortcut** - Alt+I then L (Import → List)

### Database Integration
- Extend `BookQueries` for bulk insert operations
- Add `ReadingQueries` support for read date updates
- Collection management for "Book List"

### File Processing
- Reuse existing file selection patterns
- Excel parsing with openpyxl library
- CSV parsing with standard csv module

## User Workflow

1. **Open Import** - File → Import Book List
2. **Select File** - Browse and select spreadsheet
3. **Choose Mode** - Import New vs Update Read Dates
4. **Map Fields** - Assign spreadsheet columns to book fields
5. **Preview** - Validate mapping and show sample data
6. **Import** - Process file with progress feedback
7. **Results** - Success/failure announcement with statistics

## Accessibility Features

### Screen Reader Support
- Table row number suppression
- Accessible names for all controls
- Progress announcements during import
- Error messages with focus management

### Keyboard Navigation
- Full keyboard access to all features
- Logical tab order
- Shortcut keys for common actions
- Combo box anti-noise patterns

### Visual Accessibility
- High contrast support
- Scalable UI (50%-200%)
- Clear visual indicators
- Consistent with theme system

## Testing Requirements

### Accessibility Testing
- JAWS screen reader testing
- NVDA screen reader testing
- Keyboard-only navigation
- Focus management verification

### Functional Testing
- File format compatibility
- Field mapping accuracy
- Import mode validation
- Error handling verification
- Performance with large files

## Success Metrics
- Import success rate > 95%
- Error message clarity
- Screen reader compatibility
- User workflow efficiency
- Data integrity maintenance

---

**Next Steps:**
1. Review and approve design
2. Create window skeleton from accessible_window_skeleton.py
3. Implement file selection UI
4. Add field mapping table
5. Implement import logic
6. Add accessibility features
7. Test with screen readers
8. Integration testing
