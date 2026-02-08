# QAccessible Quick Reference for AbCS

## Using Accessibility Event Helpers

### Status Message Announcement
For any status message, use the helper instead of `.showMessage()`:

```python
# ❌ WRONG - JAWS won't hear it
self.status_bar.showMessage("Search completed")

# ✅ CORRECT - JAWS will announce it
from accessibility.accessible_events import announce_status_message
announce_status_message(self.status_bar, "Search completed")
```

### Table Navigation Announcement
When user navigates table:

```python
from accessibility.accessible_events import announce_table_selection

row = self.table.currentRow()
col = self.table.currentColumn()
announce_table_selection(self.table, row, col)
# JAWS hears: "[Column Name]: [Cell Value]"
```

### Table Action Announcement
When bulk selecting/deleting:

```python
from accessibility.accessible_events import announce_table_action

# After selecting books
announce_table_action(self.table, "select", count=5)
# JAWS hears that 5 rows are selected
```

### Form Field Change Announcement
When updating a form field:

```python
from accessibility.accessible_events import announce_form_field

announce_form_field(
    self.title_edit, 
    "Book title", 
    "The Great Gatsby"
)
# JAWS hears: "Book title, current value: The Great Gatsby"
```

### Dialog Lifecycle Announcements
When opening/closing dialogs:

```python
from accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed

# When opening
dialog = BookDetailsWindow(...)
announce_dialog_opened(dialog, "New Book")

# When closing
announce_dialog_closed(dialog)
```

### Focus Change Announcement
When programmatically moving focus:

```python
from accessibility.accessible_events import announce_focus_change

self.search_box.setFocus()
announce_focus_change(self.search_box, "Search books")
# JAWS announces focus moved to search box
```

---

## Setting Up Accessible Widget Metadata

### Window/Dialog Setup
```python
from PySide6.QtGui import QAccessible

window = MyWindow()
window.setAccessibleName("Main Window Title")
window.setAccessibleDescription("Purpose of this window")

# Or for any widget:
widget.setAccessibleName("Button purpose")
widget.setAccessibleDescription("Detailed explanation")
```

### Status Bar Setup (Already Done)
```python
self.status_bar = QStatusBar()
self.status_bar.setAccessibleName("Status")
self.status_bar.setAccessibleDescription("Application status messages")
self.setStatusBar(self.status_bar)
```

### Table Setup (Already Done)
```python
self.table = QTableWidget()
self.table.setAccessibleName("Audio books")
self.table.setAccessibleDescription("List of audiobooks with author, title, year, etc.")
QAccessible.setAccessibleDescription(self.table, "Detailed table description")
```

---

## What NOT to Do

❌ Don't use `.showMessage()` directly on status bar - use `announce_status_message()`
❌ Don't forget to set accessible names on custom dialogs
❌ Don't call accessibility functions before widgets are created
❌ Don't emit events for every keystroke (expensive) - only for meaningful changes

---

## Initialization (Already Done in main.py)

On startup, this is called automatically:

```python
from accessibility.accessible_widgets import register_accessible_widgets

register_accessible_widgets()
# Registers all custom QAccessibleInterface implementations
# Must be called once after creating QApplication, before showing windows
```

---

## Testing with JAWS

1. Start JAWS
2. Run AbCS normally
3. Navigate using Tab, arrow keys
4. Listen for:
   - Status bar: "5 books selected"
   - Table: Row/column announcements
   - Dialogs: Title + description
   - Forms: Field labels and current values

If JAWS isn't hearing something, check:
1. Is `.setAccessibleName()` or `.setAccessibleDescription()` set?
2. Is the event being emitted? (check `announce_*()` call)
3. Is the widget visible and enabled?

---

## Common Patterns

### Announcing Search Results
```python
message = f"Found {count} books matching '{search_text}'"
announce_status_message(self.status_bar, message)
```

### Announcing Bulk Operations
```python
message = f"Deleted {len(selected)} books"
announce_status_message(self.status_bar, message)
announce_table_action(self.table, "delete", count=len(selected))
```

### Announcing Filter Changes
```python
filter_name = self.read_combo.currentText()
announce_status_message(self.status_bar, f"Filtered by: {filter_name}")
```

### Announcing Navigation
```python
book = self.books[row]
announce_status_message(self.status_bar, f"Book: {book.title} by {book.author_name}")
announce_table_selection(self.table, row, 1)  # Column 1 = Title
```

---

## Extending Accessibility to New Windows

When creating a new window (e.g., UpdateWindow, CollectionWindow):

1. Set accessible name/description:
   ```python
   self.setAccessibleName("Update Books")
   self.setAccessibleDescription("Bulk update selected books")
   ```

2. For any form, wrap with metadata:
   ```python
   self.series_combo.setAccessibleName("Series")
   self.genre_combo.setAccessibleName("Genre")
   ```

3. When status changes, announce it:
   ```python
   from accessibility.accessible_events import announce_status_message
   announce_status_message(self.status_bar, "10 books updated")
   ```

4. On success/error, use:
   ```python
   announce_dialog_closed(self)
   ```

---

## File Locations

| File | Purpose | Import |
|---|---|---|
| `src/accessibility/accessible_widgets.py` | QAccessibleInterface implementations | `from accessibility.accessible_widgets import register_accessible_widgets` |
| `src/accessibility/accessible_events.py` | Event helper functions | `from accessibility.accessible_events import announce_status_message, ...` |
| `src/ui/main_window.py` | Uses announce_status_message() | Already integrated |
| `src/ui/book_details.py` | Dialog accessibility setup | Already integrated |
| `src/main.py` | Registers accessibility layer | Already integrated |

---

## Questions?

- **Status bar not announcing?** → Use `announce_status_message()`
- **Table navigation unclear?** → Check table's accessible name/description
- **Dialog not announced?** → Set `setAccessibleName()` and `setAccessibleDescription()`
- **Field changes not heard?** → Call `announce_form_field()` explicitly
