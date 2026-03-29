

# Accessibility best-practice rules (PySide6-specific)

These matter more than the toolkit itself.

### ✅ Rule 1: Never rely on visuals alone

If text is important:

* Put it in a `QLabel`
* Or a focusable read-only control

### ✅ Rule 2: Everything must be reachable by keyboard

No mouse-only UI. Ever.

```python
widget.setFocusPolicy(Qt.StrongFocus)

### ✅ Rule 3: Accessible names are NOT optional

```python
widget.setAccessibleName("Search results")
widget.setAccessibleDescription("List of matching items")
```

If you don’t set these, JAWS guesses—and guessing is bad.

### ✅ Rule 4: Status updates must be announced

Never rely solely on `QStatusBar`.

Mirror status messages to:

* A hidden label
* Or a read-only focusable control

### ✅ Rule 5: Errors should move focus

If something fails:

* Move focus to the error text
* Or use a modal dialog

JAWS will not announce background errors reliably.

### ✅ Rule 6: Use standardized message boxes

Always use `exec_styled_message_box(...)` for modal dialogs:

```python
from src.accessibility.style_helpers import exec_styled_message_box

exec_styled_message_box(
    self,
    self.scaler.get_scaled_size(20),
    icon=QMessageBox.Warning,
    title="Error",
    text="Something went wrong",
    buttons=QMessageBox.Ok,
    default_button=QMessageBox.Ok
)
```

This ensures consistent styling and accessibility behavior.

### ✅ Rule 7: Manage focus after operations

After save/delete/cancel operations:

* Return focus to the updated/created item
* Or return focus to the first item in list
* Use `QTimer.singleShot()` for delayed focus when needed
* Test focus behavior with screen readers

### ✅ Rule 8: Define explicit tab order

JAWS navigation relies on predictable tab order:

```python
self.setTabOrder(widget1, widget2)
self.setTabOrder(widget2, widget3)
```

Update tab order when widget visibility changes.

### ✅ Rule 9: Suppress table row numbers

For data tables, row numbers are accessibility noise:

```python
table.verticalHeader().setVisible(False)
table.setVerticalHeaderLabels([""] * table.rowCount())
```

Add meaningful accessible text to table items:
```python
item.setData(Qt.AccessibleTextRole, "42 books")  # Instead of just "42"
```

This prevents JAWS from announcing "Row 1, Row 2" which interferes with data comprehension.

## 5. One underrated resource: NVDA

Even if your users are JAWS users, test with **NVDA**.

Why?

* It’s free
* It exposes accessibility bugs faster
* If NVDA can’t read it, JAWS probably won’t either

## 6. Practical reality check (important)

No Python GUI toolkit gives you *perfect* accessibility out of the box.

Accessibility success comes from:

* Widget choice
* Focus management
* Explicit labels
* Predictable navigation

## 7. Screen Reader-Optimized Button Enablement

**Rule: Keep buttons enabled but provide clear error messages**

Instead of disabling buttons when prerequisites aren't met, keep them enabled and show helpful error messages. This improves discoverability for screen reader users.

```python
# Bad: Button disabled with no explanation
button.setEnabled(False)  # Screen reader may not announce why

# Good: Button enabled with clear feedback
def on_delete_clicked(self):
    if not self._has_selection():
        self.show_error("Select an item to delete first")
        self.set_status("Delete canceled: no item selected")
        return
    # Proceed with delete operation
```

**Benefits:**
- Screen readers can always announce the button
- Users learn what actions are available
- Clear error messages teach the workflow
- Consistent with accessibility-first design

**Reference:** `src/ui/backup_restore_window.py` - Delete button pattern

## 8. Global Enter Shortcut Anti-Pattern (Critical)

**Rule: NEVER use global Return/Enter shortcuts in windows with buttons**

Global Enter shortcuts break accessibility by preventing Enter from activating focused buttons.

**REFERENCE IMPLEMENTATION:** `src/ui/accessible_window_skeleton.py` - Shows correct keyPressEvent pattern without global shortcuts.

```python
# BAD: Blocks Enter on ALL buttons
shortcut = QShortcut(QKeySequence("Return"), self)
shortcut.activated.connect(self.some_action)

# GOOD: Handle Enter only for specific widgets in keyPressEvent
def keyPressEvent(self, event):
    if event.key() in (Qt.Key_Return, Qt.Key_Enter):
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QPushButton):
            # Let Qt handle Enter on buttons (default behavior)
            focused_widget.click()
            event.accept()
            return
        elif self.table.hasFocus():
            self.on_table_action()
            return
    super().keyPressEvent(event)  # Let Qt handle Enter on buttons
```

**Why this matters:**
- Screen reader users rely on Enter to activate focused buttons
- Global shortcuts override Qt's default button behavior
- Creates accessibility barriers that are hard to debug

**Reference:** `src/ui/import_window.py` - Fixed global Enter shortcut conflict
