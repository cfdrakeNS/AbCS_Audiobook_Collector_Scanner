# AbCS Accessibility Implementation Notes (Code-Backed)

This document summarizes accessibility patterns already implemented in AbCS, with copy/paste snippets you can share.

## 1) Customized status bar handling (screen reader friendly)

### Why we did this
- Default `showMessage()` updates are not always reliably spoken by JAWS/NVDA.
- We needed a repeatable way to announce status changes, including an explicit "read status now" shortcut.

### Pattern
- Central helper updates visible status text and accessible metadata.
- Optional focus hop to status bar (`move_focus=True`) improves JAWS reliability.
- Every major window wraps this in `set_status(...)`.
- `Alt+/` re-reads current status.

### Code snippet: shared announcer
Source: `src/accessibility/accessible_events.py`

```python
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible


def announce_status_message(status_bar, message: str, move_focus: bool = False) -> None:
    status_bar.showMessage(message)
    status_bar.setAccessibleName(message)
    status_bar.setAccessibleDescription(message)

    if move_focus and QAccessible.isActive():
        app = QApplication.instance()
        previous_focus = app.focusWidget() if app else None

        status_bar.setFocusPolicy(Qt.StrongFocus)
        status_bar.setFocus()

        def restore_focus():
            active_app = QApplication.instance()
            if active_app and previous_focus and active_app.focusWidget() == status_bar:
                try:
                    previous_focus.setFocus()
                except RuntimeError:
                    pass
            try:
                status_bar.setFocusPolicy(Qt.NoFocus)
            except RuntimeError:
                pass

        from PySide6.QtCore import QTimer
        QTimer.singleShot(300, restore_focus)
```

### Code snippet: window-level API + Alt+/ reader
Source: `src/ui/main_window.py`, `src/ui/book_details.py`, `src/ui/import_window.py`

```python
def set_status(self, message: str, timeout_ms: int = 0, announce: bool = True):
    announce_status_message(self.status_bar, message, move_focus=announce)


def on_read_status_bar(self):
    if QAccessible.isActive():
        self.set_status(self.get_default_status(), timeout_ms=0, announce=True)
```

## 2) Locking Up/Down arrows in editable combos

### Why we did this
- In editable `QComboBox`, plain Up/Down can silently change values.
- Screen readers may not announce these changes consistently.
- This can corrupt form values without clear feedback.

### Pattern
- Install `eventFilter` on combos (and often their inner `lineEdit()`).
- Block plain Up/Down; only allow with `Alt` (dropdown navigation intent).
- Beep when blocked to provide immediate non-visual feedback.

### Code snippet
Source: `src/ui/book_details.py`, `src/ui/update_window.py`, `src/ui/preferences_window.py`

```python
if event.type() == QEvent.KeyPress and isinstance(source, QComboBox):
    key = event.key()
    modifiers = event.modifiers()

    if key in (Qt.Key_Up, Qt.Key_Down):
        if not (modifiers & Qt.AltModifier):
            QApplication.beep()
            return True  # consume event
```

### Related hardening: block unmapped Alt+letters
Source: `src/accessibility/key_filters.py` and window `eventFilter(...)` usage

```python
def is_unmapped_alt_letter(event, allowed_letters):
    if event.type() != QEvent.KeyPress:
        return False
    if event.modifiers() != Qt.AltModifier:
        return False
    key = event.key()
    if not (Qt.Key_A <= key <= Qt.Key_Z):
        return False
    return chr(key) not in set(allowed_letters)
```

## 3) Using tables for shortcut help lists

### Why we did this
- A structured table is easier for screen readers than free-form text blocks.
- Rows can be read line-by-line and selected predictably.

### Pattern
- Build a one-column read-only `QTableWidget`.
- Hide headers/grid for visual simplicity.
- Set `Qt.AccessibleTextRole` per row so SR output is explicit.

### Code snippet
Source: `src/ui/book_details.py` (same pattern in import/backup/collection windows)

```python
table = QTableWidget()
table.setAccessibleName("Shortcuts list")
table.setColumnCount(1)
table.setHorizontalHeaderLabels([""])
table.setRowCount(len(shortcuts))
table.setVerticalHeaderLabels([""] * len(shortcuts))
table.setSelectionBehavior(QAbstractItemView.SelectRows)
table.setSelectionMode(QAbstractItemView.SingleSelection)
table.setEditTriggers(QAbstractItemView.NoEditTriggers)
table.setTabKeyNavigation(False)
table.setAlternatingRowColors(True)
table.verticalHeader().setVisible(False)
table.horizontalHeader().setVisible(False)
table.setShowGrid(False)

for row, (key, description) in enumerate(shortcuts):
    item = QTableWidgetItem(f"{description} - {key}")
    item.setData(Qt.AccessibleTextRole, f"{description}: {key}")
    table.setItem(row, 0, item)
```

## 4) Focus safety: prevent auto-select overwrite on focus-in

### Why we did this
- Qt often auto-selects full text in line edits/combo line edits on focus.
- Blind/low-vision users can accidentally overwrite entire values with one key press.

### Pattern
- On `FocusIn`, defer to next event loop tick and deselect text / move cursor to end.

### Code snippet
Source: `src/ui/book_details.py`, `src/ui/import_detail_window.py`, `src/ui/preferences_window.py`

```python
if event.type() == QEvent.FocusIn:
    if isinstance(source, QLineEdit):
        QTimer.singleShot(0, lambda w=source: w.deselect())
    elif isinstance(source, QComboBox) and source.lineEdit():
        QTimer.singleShot(0, lambda w=source: w.lineEdit().deselect())
    elif isinstance(source, QTextEdit):
        QTimer.singleShot(0, lambda w=source: w.moveCursor(QTextCursor.End))
```

## 5) Accessibility-first naming/description on controls

### Why we did this
- Screen readers need meaningful names/descriptions, not only visible labels.

### Pattern
- Set `accessibleName`/`accessibleDescription` on windows, fields, tables, status bars, and key actions.

### Code examples
Sources: `src/ui/book_details.py`, `src/ui/import_window.py`, `src/ui/collection_window.py`

```python
self.setAccessibleName("Book Details")
self.title_edit.setAccessibleName("Book title")
self.table.setAccessibleName("Import list")
self.status_bar.setAccessibleDescription("Import progress status")
```

## 6) Scaled UI and reusable accessible styles

### Why we did this
- Larger text and touch targets are core requirements, not optional.
- Style consistency across dialogs/buttons improves predictability.

### Pattern
- Global scaler (`UIScaler`) applies app font size + stylesheet updates.
- Shared style helper returns high-contrast focus/pressed states.

### Style snippet: global scaling stylesheet
Source: `src/accessibility/scaling.py`

```python
stylesheet = f"""
    * {{ font-size: {scaled_size}pt; }}

    QComboBox:focus, QLineEdit:focus {{
        border: 2px solid palette(highlight);
        background-color: palette(base);
    }}

    QPushButton, QComboBox, QCheckBox {{
        min-height: {int(44 * self._current_scale / 100)}px;
        padding: {int(6 * self._current_scale / 100)}px;
    }}

    QStatusBar {{
        font-size: {int(scaled_size * 0.9)}pt;
    }}
"""
```

### Style snippet: shared button focus treatment
Source: `src/accessibility/style_helpers.py`

```python
def build_accessible_button_style(scaled_height: int, selector: str = "QPushButton") -> str:
    return f"""
        {selector} {{
            padding: 4px 12px;
            border: 1px solid palette(dark);
            border-radius: 3px;
            background-color: palette(button);
            outline: none;
        }}
        {selector}:focus {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
            border: 2px solid palette(dark);
            outline: none;
        }}
    """
```

## 7) Theme system with high-contrast presets

### Why we did this
- Users need persistent, selectable themes with strong contrast options.

### Pattern
- Theme palettes are defined in `ThemeManager` and applied globally.
- Includes dedicated high-contrast dark/light plus multiple comfort presets.

### Snippet
Source: `src/accessibility/theme_manager.py`

```python
ThemeName.HIGH_CONTRAST_DARK: Theme("High Contrast Dark", {
    'window': '#000000',
    'window_text': '#FFFFFF',
    'base': '#000000',
    'text': '#FFFFFF',
    'highlight': '#FFFF00',
    'highlight_text': '#000000',
})
```

## 8) Centralized keyboard mapping model

### Why we did this
- Shortcut drift across windows breaks learnability and screen reader training.

### Pattern
- Maintain context-specific shortcut maps in one place and register by context.

### Snippet
Source: `src/accessibility/shortcuts.py`

```python
class ShortcutContext(Enum):
    MAIN_WINDOW = "main_window"
    BOOK_DETAILS = "book_details"

BOOK_DETAILS_SHORTCUTS = {
    'T': ('Title', 'title_edit'),
    'A': ('Author', 'author_combo'),
    'S': ('Save', 'save_button'),
    'L': ('Cancel', 'cancel_button'),
}
```

## 9) App startup accessibility initialization

### Why we did this
- Accessibility must be enabled as early as possible for reliable UIA tree behavior.

### Snippet
Source: `src/main.py`

```python
from PySide6.QtGui import QAccessible
QAccessible.setActive(True)
QAccessible.setRootObject(self.qt_app)
```

## Quick checklist to reuse this in another app

- Add a shared `announce_status_message(...)` helper and use it in every window.
- Add `Alt+/` for "read status" in each primary screen.
- Install event filters for editable combos and block plain Up/Down.
- Use read-only table dialogs for shortcut help; include `AccessibleTextRole` per row.
- Set `accessibleName`/`accessibleDescription` on every interactive control.
- Apply global scaler + shared button/messagebox styles.
- Keep all shortcut maps centralized by window context.
- Enable `QAccessible` at app startup.
