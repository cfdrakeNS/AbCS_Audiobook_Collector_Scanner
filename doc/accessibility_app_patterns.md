# Deprecated: moved to consolidated references

This document has been consolidated to reduce duplication.

- Implementation patterns and code-oriented guidance now live in:
  - `PySide6_Accessibility_Patterns_and_Implementation_Reference.md`
- Principles and design rules now live in:
  - `PySide6_Screen_Reader_Accessibility_Best_Practices.md`

Use the two files above as the canonical documentation set.
- `src/ui/web_metadata.py` → Confirmation dialogs before close

### Implementation notes
- Always import from `src.accessibility.style_helpers`
- Use appropriate icons for message type
- Set default button to safest option **only when message is fully announced first**
- Test with both screen reader (Insert+B for "read dialog" command) and screen reader
- Announce popup presence in status bar before showing dialog for extra reliability

---

## 12) Focus Management After Operations Pattern

### Why this is unique to the application
- Predictable focus behavior is critical for screen reader efficiency
- Users need to know where focus will be after each action

### Standard behavior
1. After save operations: return focus to updated/created item
2. After delete operations: return focus to first item in list
3. After cancel operations: return focus to list/table
4. Use `QTimer.singleShot()` for delayed focus when needed
5. Use helper methods like `focus_and_select_row()` and `focus_first_item()`

### Reference implementations
- `src/ui/collection_window.py` → Complete focus management after all operations
- `src/ui/book_details.py` → Focus return after save operations

### Implementation notes
- Test focus behavior with both screen readers
- Use explicit focus setting rather than relying on default behavior
- Consider focus timing when UI updates are asynchronous

---

## 13) Tab Order Explicit Management Pattern

### Why this is unique to the application
- screen reader navigation relies heavily on predictable tab order
- Explicit tab order prevents focus jumping and confusion

### Standard behavior
1. Define tab order explicitly using `setTabOrder(widget1, widget2)`
2. Create tab order dynamically based on visible widgets
3. Handle tab order changes when widgets show/hide
4. Use helper methods like `_apply_tab_order()` for complex layouts

### Reference implementations
- `src/ui/collection_window.py` → Dynamic tab order for editing modes
- `src/ui/import_detail_window.py` → Complex form tab management

### Implementation notes
- Tab order should match visual layout
- Update tab order when widget visibility changes
- Test tab flow with keyboard only

---

## 15) Table Row Number Suppression Pattern

### Why this is unique to the application
- Row numbers are noise for data tables where content is meaningful
- screen reader announces "Row 1, Row 2" which interferes with data comprehension
- We optimize for clean screen reader experience by hiding irrelevant structural information

### Standard behavior
1. Hide vertical headers: `table.verticalHeader().setVisible(False)`
2. Set empty header labels: `table.setVerticalHeaderLabels([])`
3. Apply after table population: `setVerticalHeaderLabels([""] * rowCount)`
4. Add meaningful accessible text to table items using `Qt.AccessibleTextRole`

### Reference implementations
- `src/ui/reading_history_window.py` → General statistics table with meaningful value descriptions
- `src/ui/backup_restore_window.py` → Backup list table in `refresh_backup_list()`
- `src/ui/name_list_window.py` → Name/author lists with empty header labels
- `src/ui/main_window.py` → Book list table with hidden vertical headers

### Implementation notes
- Apply `setVerticalHeaderLabels()` after populating table data
- Use `setData(Qt.AccessibleTextRole, "meaningful text")` for value items
- Test with screen reader to ensure row numbers are not announced
- Pattern applies to all data tables where row numbers provide no functional value

---

## 16) Screen Reader-Optimized Button Enablement Pattern

### Why this is unique to the application
- Screen reader users benefit from consistent button behavior and clear feedback
- Disabled buttons can be confusing when the reason isn't obvious
- We enable buttons but provide meaningful error messages with context

### Standard behavior
1. **Keep buttons enabled** for better accessibility and discoverability
2. **Provide clear error messages** when buttons are clicked without valid prerequisites
3. **Use status announcements** to inform screen reader users what's happening
4. **Maintain consistent focus management** after error dialogs

### Reference implementations
- `src/ui/backup_restore_window.py` → Delete button always enabled, shows "No backup selected" message
- `src/ui/import_window.py` → Browse and action buttons with validation feedback
- `src/ui/book_details_window.py` → Save button with field validation messages

### Implementation notes
- **Delete buttons**: Always enabled, show helpful message when no selection exists
- **Action buttons**: Enable when prerequisites exist, but provide clear error feedback
- **Error messages**: Include specific guidance on what the user needs to do
- **Focus restoration**: Return focus to the relevant field after error dialogs
- **Status announcements**: Use centralized announce_status_message for consistency

### Example error message patterns
```python
# Delete button without selection
"Delete canceled: no backup row selected in Backup List"

# Restore button without file  
"Restore canceled: no backup selected"

# Import without folder
"Scan canceled: no folder selected for import"
```

---

## 18) Global Enter Shortcut Anti-Pattern

### Why this is unique to the application
- Global Return/Enter shortcuts interfere with button accessibility
- Screen reader users rely on Enter to activate focused buttons
- Qt's default button behavior must be preserved for accessibility

### Standard behavior
1. **NEVER use global Return/Enter shortcuts** in windows with buttons
2. **Handle Enter in keyPressEvent** instead for specific widgets (like tables)
3. **Preserve Qt's default button behavior** for Enter key activation
4. **Use setAutoDefault carefully** - it can block Enter key on buttons

### Reference implementations
- `src/ui/import_window.py` → keyPressEvent handles Enter for table, preserves button behavior
- `src/ui/book_details.py` → No global Enter shortcuts, buttons work with Enter
- `src/ui/main_window.py` → No global Enter shortcuts, default Qt behavior

### Implementation notes
- **Bad pattern**: `QShortcut(QKeySequence("Return"), self)` - blocks all Enter keys
- **Good pattern**: Handle Enter in `keyPressEvent` for specific widgets only
- **Button setup**: Avoid `setAutoDefault(False)` unless absolutely necessary
- **Testing**: Verify Enter works on all focused buttons after adding shortcuts

### Example correct implementation
```python
def keyPressEvent(self, event):
    if event.key() in (Qt.Key_Return, Qt.Key_Enter):
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QPushButton):
            # Let Qt handle Enter on buttons (default behavior)
            return super().keyPressEvent(event)
        elif self.table.hasFocus():
            # Handle Enter for specific widget
            self.on_table_action()
            return
    super().keyPressEvent(event)
```

---

## 19) Suggested extraction for future apps

If this pattern set is reused in a new app, extract into shared modules:
- `accessibility/status_contract.py` (set/read/announce helpers)
- `accessibility/combo_noise_guard.py` (event filter mixin)
- `accessibility/alt_key_policy.py` (allowlist filter)
- `accessibility/dialogs.py` (styled modal helpers)
- `accessibility/shortcut_help.py` (standard help dialog builder)
- `accessibility/focus_manager.py` (focus management helpers)
- `accessibility/tab_order.py` (tab order management)

This keeps app behavior consistent while reducing per-window copy/paste drift.

