# PySide6 About/Info Dialog Pattern for AbCS

## Overview

This document describes the recommended pattern for creating accessible, themed informational dialogs (About, License, Setup, etc.) in AbCS using PySide6. This ensures consistency, accessibility, and maintainability for all future info windows.

---

## Key Principles

- **Use external dialog classes** (e.g., `AboutDialog`, `LicenseDialog`, `SetupDialog`) instead of building dialogs inline in the main window.
- **Inherit from `AccessibleDialog`** (`src/ui/accessible_dialog.py`), not `QDialog`, so JAWS Insert+T reads the correct window title (see `PySide6_Accessibility_Patterns_and_Implementation_Reference.md` section 4).
- **Use read-only navigable text for body content** — not `QLabel` (see below and implementation reference section 11).
- **Accessibility first:**
  - Font scaling via `self.scaler.get_scaled_size()`
  - High-contrast theming using `build_accessible_button_style()`
  - Keyboard navigation (Tab, Enter, arrow keys in text areas)
  - Short accessible names; brief accessible descriptions
- **Consistent layout:**
  - Header/content/footer structure
  - Footer: right-aligned, styled OK/Close button

---

## Read-Only Navigable Body Text

### Why not QLabel?

`QLabel` is poor for long help or license text:
- Putting the full body in `setAccessibleName()` makes the screen reader read everything at once.
- Arrow keys do not move line by line through the content.

### Use `create_accessible_read_only_text()`

From `src/accessibility/read_only_text.py`:

```python
from PySide6.QtWidgets import QSizePolicy
from src.accessibility.read_only_text import create_accessible_read_only_text

about_label = create_accessible_read_only_text(
    self,
    about_text,
    "About information",
    "About AbCS. Use arrow keys to read line by line. Press Tab to move to OK button.",
)
about_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

font = about_label.font()
font.setPointSize(self.scaler.get_scaled_size(12))
about_label.setFont(font)
```

This creates a read-only `QTextEdit` with:
- `TextSelectableByKeyboard` — JAWS/NVDA arrow-key line review
- `StrongFocus` and `TabChangesFocus`
- Mouse tracking and hover disabled (less noise)
- Blank lines collapsed in the source text (avoids JAWS repeating the previous line on empty rows)
- Transparent background when embedded in a dialog

### Rules for body text

- **Short accessible name** — for example `"License information"`, not the full license text.
- **Helpful accessible description** — mention arrow keys and where Tab goes next.
- Splash/graphics labels: `setFocusPolicy(Qt.NoFocus)`.
- Set initial focus to the text area after the dialog opens:
  `QTimer.singleShot(100, lambda: about_label.setFocus(Qt.TabFocusReason))`

---

## Implementation Steps

### 1. Create a Dialog Class

- Inherit from `AccessibleDialog` (pass `parent` for Win32 ownership; the base class uses `parent=None` internally for the accessibility tree)
- Accept `scaler` and `parent` in `__init__`
- Set window title, accessible name, and modal state
- Use `QVBoxLayout` for main layout
- Add content with `create_accessible_read_only_text()` (not `QLabel`)
- Add a right-aligned OK button in a `QHBoxLayout`
- Style the button using `build_accessible_button_style()`

**Example:**
```python
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QTimer
from src.accessibility.read_only_text import create_accessible_read_only_text
from src.accessibility.style_helpers import build_accessible_button_style
from src.ui.accessible_dialog import AccessibleDialog

class AboutDialog(AccessibleDialog):
    def __init__(self, scaler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About AbCS")
        self.setAccessibleName("About AbCS")
        self.setModal(True)
        layout = QVBoxLayout(self)

        about_label = create_accessible_read_only_text(
            self,
            about_text,
            "About information",
            "About AbCS. Use arrow keys to read line by line. Press Tab to move to OK button.",
        )
        about_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(about_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok_btn = QPushButton("OK", self)
        ok_btn.setAccessibleName("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        scaled_height = int(20 * (scaler.current_scale / 100.0))
        ok_btn.setStyleSheet(build_accessible_button_style(scaled_height))
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        QTimer.singleShot(100, lambda: about_label.setFocus(Qt.TabFocusReason))
```

### 2. Use the Dialog in Main Window

- Import the dialog class
- In the main window, create a slot (e.g., `on_about`)
- Instantiate and exec the dialog
- Restore focus after closing

**Example:**
```python
from src.ui.about_dialogue import AboutDialog

def on_about(self):
    dlg = AboutDialog(self.scaler, self)
    dlg.exec()
    self.set_status("About dialog opened.")
    self.restore_main_focus_after_modal()
```

---

## Plot Fields (Related Pattern)

Plot text in Book Details and Web Metadata uses a different control — `PlotLineList` — because list rows give more reliable Up/Down review for long plot text than a read-only `QTextEdit`. See implementation reference section 12.

- View mode: `PlotLineList` (rating on row 0; plot body in 73-character word-wrapped lines)
- Edit mode: `QTextEdit` with continuous prose
- Module: `src/accessibility/read_only_text.py`

---

## Accessibility & Theming Checklist

- Use `create_accessible_read_only_text()` for About, License, Setup body text
- Use `scaler.get_scaled_size()` for all font and size settings
- Use `build_accessible_button_style()` for all dialog buttons
- Set short accessible names and helpful descriptions on text areas
- Ensure dialog is modal and focus returns to main window after closing
- Test with JAWS/NVDA: Insert+T should read this dialog's title, not the main window behind it
- Test arrow Up/Down in the body text area for line-by-line review
- Inline popups (F1 help, Find, etc.) also use `AccessibleDialog(self)`, not `QDialog(self)`

---

## See Also

- `doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md` — sections 10–12
- `src/accessibility/read_only_text.py` — `create_accessible_read_only_text`, `PlotLineList`
- `src/ui/accessible_dialog.py` — base class for all feature dialogs
- `src/ui/about_dialogue.py` — reference implementation
- `src/ui/license_dialogue.py`
- `src/ui/setup_dialogue.py`
- `src/accessibility/style_helpers.py`
- `test/test_read_only_text.py`
