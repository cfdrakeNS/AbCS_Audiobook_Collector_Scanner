# PySide6 About/Info Dialog Pattern for AbCS

## Overview
This document describes the recommended pattern for creating accessible, themed informational dialogs (About, License, etc.) in AbCS using PySide6. This ensures consistency, accessibility, and maintainability for all future info windows.

---

## Key Principles
- **Use external dialog classes** (e.g., `AboutDialog`, `LicenseDialog`) instead of building dialogs inline in the main window.
- **Inherit from `AccessibleDialog`** (`src/ui/accessible_dialog.py`), not `QDialog`, so JAWS Insert+T reads the correct window title (see `PySide6_Accessibility_Patterns_and_Implementation_Reference.md` section 4).
- **Accessibility first:**
  - Font scaling via `self.scaler.get_scaled_size()`
  - High-contrast theming using `build_accessible_button_style()`
  - Keyboard navigation (Tab, Enter, Alt+letter)
  - Accessible names/descriptions for all controls
- **Consistent layout:**
  - Header/content/footer structure
  - Footer: right-aligned, styled OK/Close button

---

## Implementation Steps

### 1. Create a Dialog Class
- Inherit from `AccessibleDialog` (pass `parent` for Win32 ownership; the base class uses `parent=None` internally for the accessibility tree)
- Accept `scaler` and `parent` in `__init__`
- Set window title, accessible name, and modal state
- Use `QVBoxLayout` for main layout
- Add content (e.g., `QLabel` for text)
- Add a right-aligned OK button in a `QHBoxLayout`
- Style the button using `build_accessible_button_style()`

**Example:**
```python
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from src.accessibility.style_helpers import build_accessible_button_style
from src.ui.accessible_dialog import AccessibleDialog

class AboutDialog(AccessibleDialog):
    def __init__(self, scaler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About AbCS")
        self.setAccessibleName("About AbCS")
        self.setModal(True)
        layout = QVBoxLayout(self)
        # ... add content ...
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok_btn = QPushButton("OK", self)
        ok_btn.setAccessibleName("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        scaled_height = int(20 * (scaler.current_scale / 100.0))
        ok_btn.setFont(ok_btn.font())
        ok_btn.setMinimumHeight(max(scaled_height - 4, 14))
        ok_btn.setMaximumHeight(max(scaled_height - 4, 14))
        ok_btn.setStyleSheet(build_accessible_button_style(scaled_height))
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)
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

## Accessibility & Theming Checklist
- Use `scaler.get_scaled_size()` for all font and size settings
- Use `build_accessible_button_style()` for all dialog buttons
- Set accessible names/descriptions for all widgets
- Ensure dialog is modal and focus returns to main window after closing
- Test with JAWS/NVDA: Insert+T should read this dialog's title, not the main window behind it
- Inline popups (F1 help, Find, etc.) also use `AccessibleDialog(self)`, not `QDialog(self)`

---

## See Also
- `src/ui/accessible_dialog.py` (base class for all feature dialogs)
- `src/ui/about_dialogue.py` (reference implementation)
- `src/ui/license_dialogue.py`
- `src/accessibility/style_helpers.py`
- Project accessibility and theming guidelines in `.github/copilot-instructions.md`
