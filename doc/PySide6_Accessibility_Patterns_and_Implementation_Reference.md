# PySide6 Accessibility Patterns and Implementation Reference

This document is the code-oriented reference for accessibility patterns that are proven in production-style PySide6 desktop apps.

## Scope

Use this document when implementing or refactoring windows, dialogs, forms, and tables.

## 1. Status announcement pattern

Goal: make status updates reliably available to screen reader users.

Pattern:
- Provide a per-window status API (for example `set_status(...)`).
- Keep a default status message for explicit readback.
- Support `Alt+/` to re-read the current status on demand.
- Announce only meaningful state changes.

Reference files:
- `src/accessibility/accessible_events.py`
- `src/ui/main_window.py`
- `src/ui/import_progress_window.py`
- `src/ui/book_details.py`

## 2. Editable combo anti-noise pattern

Goal: prevent silent value changes and accidental edits.

Pattern:
- Install event filters on editable combos and their line edits.
- Block plain Up/Down keys when they can silently change values.
- Allow explicit dropdown actions with Alt+Down / Alt+Up.
- Use beep or equivalent feedback when blocking key input.

Reference files:
- `src/ui/update_window.py`
- `src/ui/book_details.py`
- `src/ui/preferences_window.py`
- `src/ui/import_detail_window.py`

## 3. Alt-key hygiene pattern

Goal: avoid stray Alt+letter input leaking into text fields.

Pattern:
- Define a per-window allowlist of Alt+letter actions.
- Consume unmapped Alt+letter events in event filters.
- Keep `Alt+/` available in major windows.

Reference files:
- `src/accessibility/key_filters.py`
- `src/ui/main_window.py`
- `src/ui/import_progress_window.py`

## 4. AccessibleDialog window title pattern (JAWS Insert+T)

Goal: ensure screen readers read the **active dialog title**, not the window behind it.

### Problem

Qt's MSAA/UIA bridge exposes `QDialog(parent=X)` as an accessibility **child** of `X`. JAWS Insert+T walks up the tree from the focused control:

`focused_control → … → DialogWindow → MainWindow`

and reads `MainWindow`'s title instead of the dialog's (for example "Book Details").

### Solution: `AccessibleDialog`

All feature dialogs and inline help/popup dialogs inherit from `AccessibleDialog` (`src/ui/accessible_dialog.py`) instead of `QDialog` directly.

Pattern:
- Pass the logical owner as `parent` to `AccessibleDialog.__init__(parent)` — the base class stores it but calls `QDialog.__init__(None)` so the dialog is a **root** in the accessibility tree.
- On Windows, set the Win32 **owner** via `SetWindowLongPtrW(GWL_HWNDPARENT)` so taskbar grouping and z-order still follow the calling window, without creating an accessibility parent chain.
- On `showEvent`, re-fire focus after 300 ms so JAWS registers the new window before Insert+T is used (subclasses that override `showEvent` must call `super().showEvent(event)`).
- Subclasses that override `done()` must call `super().done(r)`.

**Feature window example:**
```python
from src.ui.accessible_dialog import AccessibleDialog

class BookDetailsWindow(AccessibleDialog):
    def __init__(self, db, scaler, ..., parent=None):
        super().__init__(parent)
        self.setWindowTitle("Book Details")
        # ...
```

**Inline F1 / popup example:**
```python
dlg = AccessibleDialog(self)
dlg.setWindowTitle("Keyboard Shortcuts - Book Details")
dlg.exec()
```

### Exception: `ImportProgressWindow`

`ImportProgressWindow` remains a standard `QDialog` with a normal Qt parent (`parent=self` on `ImportWindow`). It is a modeless scan utility that must stay above its owner via Qt z-order and handle Escape/cancel during an active scan. Do **not** migrate it to `AccessibleDialog`.

Modeless utility windows that do use `AccessibleDialog` may set `self._announce_focus_on_show = False` in `__init__` to skip the 300 ms focus refire when repeated `show()` calls would steal focus.

Reference files:
- `src/ui/accessible_dialog.py`
- `src/ui/book_details.py`
- `src/ui/main_window.py` (Find, Duplicate Check, ReadDateDialog, F1 help)
- `src/ui/import_progress_window.py` (intentional `QDialog` exception)

## 5. Modal dialog accessibility pattern

Goal: make warnings/confirmations readable and actionable.

Pattern:
- Use a consistent modal helper where possible.
- Set clear dialog title/text and explicit button labels.
- Set accessible name and description for custom dialogs.
- Return focus to the most relevant control after dialog close.
- Use `AccessibleDialog` for custom modal dialogs (see section 4), not raw `QDialog(parent)`.

Reference files:
- `src/accessibility/style_helpers.py`
- `src/main.py`
- `src/ui/book_list_import_window.py`
- `src/ui/accessible_dialog.py`

## 6. Keyboard shortcut implementation pattern

Goal: prevent conflicts and keep shortcut behavior predictable.

Pattern:
- Keep `F1`, `Escape`, and `Alt+/` as local window shortcuts.
- Register Alt+field shortcuts through centralized shortcut maps.
- Use lambda callbacks for mapped actions when needed.

Reference files:
- `src/accessibility/shortcuts.py`
- `src/ui/import_window.py`
- `src/ui/backup_restore_window.py`

## 7. Accessible help dialog pattern (F1)

Goal: provide a stable and readable shortcut list.

Pattern:
- Use a simple one-column read-only table or list.
- Provide per-row accessible text with explicit key + action wording.
- Include `Alt+/` in each window help list.
- Instantiate help with `AccessibleDialog(self)`, not `QDialog(self)` (see section 4).

Reference files:
- `src/ui/import_detail_window.py`
- `src/ui/main_window.py`
- `src/ui/name_list_window.py`

## 8. Focus safety pattern for editable fields

Goal: reduce accidental full-value overwrite.

Pattern:
- On FocusIn, defer deselect/cursor behavior with `QTimer.singleShot(0, ...)`.
- Deselect auto-selected text in line edits and combo line edits.

Reference files:
- `src/ui/book_details.py`
- `src/ui/import_detail_window.py`
- `src/ui/preferences_window.py`

## 9. Table accessibility pattern

Goal: improve data comprehension in row-based widgets.

Pattern:
- Hide row-number headers when they add no meaning.
- Add semantic text via `Qt.AccessibleTextRole` for key cells.

Reference files:
- `src/ui/reading_history_window.py`
- `src/ui/main_window.py`
- `src/ui/backup_restore_window.py`

## 10. About/Info Dialog Pattern

Goal: Provide a consistent, accessible, and themed approach for About, License, Setup, and other informational dialogs.

Pattern:
- Use external dialog classes (e.g., `AboutDialog`, `LicenseDialog`, `SetupDialog`) instead of inline popups in main windows.
- Inherit from `AccessibleDialog`, not `QDialog` (see section 4).
- Structure dialog with header/content/footer using `QVBoxLayout`.
- **Use `create_accessible_read_only_text()` for body text** — not `QLabel` (see section 11).
- Footer: right-aligned, styled OK/Close button using `build_accessible_button_style()`.
- Apply font scaling with `scaler.get_scaled_size()` for all text and controls.
- Set a **short** accessible name and a helpful accessible description on the text area.
- Ensure dialog is modal and returns focus to main window after closing.
- Test with JAWS/NVDA for screen reader feedback (verify Insert+T reads the dialog title).

Example usage in main window:
```python
from src.ui.about_dialogue import AboutDialog

def on_about(self):
    dlg = AboutDialog(self.scaler, self)
    dlg.exec()
    self.set_status("About dialog opened.")
    self.restore_main_focus_after_modal()
```

Reference files:
- `src/ui/accessible_dialog.py`
- `src/ui/about_dialogue.py`
- `src/ui/license_dialogue.py`
- `src/ui/setup_dialogue.py`
- `src/accessibility/read_only_text.py`
- `src/accessibility/style_helpers.py`

## 11. Read-only navigable text pattern

Goal: let JAWS/NVDA users move through static help or license text line by line with arrow keys.

### Problem

`QLabel` with the full body in `setAccessibleName()` causes the screen reader to dump all text at once. Arrow keys do not move line by line. Empty lines in the source text can also cause JAWS to repeat the previous line.

### Solution: `create_accessible_read_only_text()`

Module: `src/accessibility/read_only_text.py`

Use a read-only `QTextEdit` configured for keyboard review:

```python
from src.accessibility.read_only_text import create_accessible_read_only_text

about_label = create_accessible_read_only_text(
    self,
    about_text,
    "About information",  # short name only — not the full body
    "About AbCS. Use arrow keys to read line by line. Press Tab to move to OK button.",
)
about_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
```

`configure_accessible_read_only_text()` applies these settings:
- `setReadOnly(True)`
- `setTextInteractionFlags(Qt.TextSelectableByKeyboard)` — enables arrow-key line review
- `setFocusPolicy(Qt.StrongFocus)` and `setTabChangesFocus(True)`
- `setMouseTracking(False)` on widget and viewport; `WA_Hover` disabled
- Transparent background / no frame for dialog embedding
- Body text passed through `_collapse_blank_lines()` to remove empty lines that confuse JAWS

### Rules

- **Never** put the full body text in `setAccessibleName()`.
- Use a short accessible name (for example `"License information"`) and a brief description that mentions arrow-key review.
- Decorative graphics (splash image) use `Qt.NoFocus`.
- Set initial focus to the text area with `QTimer.singleShot(100, lambda: text_widget.setFocus(Qt.TabFocusReason))`.

### Where used

- `src/ui/about_dialogue.py`
- `src/ui/license_dialogue.py`
- `src/ui/setup_dialogue.py`

## 12. Plot field line-by-line review pattern

Goal: let screen reader users review plot text line by line in view mode while keeping continuous prose in the database and edit mode.

### Problem

- Read-only `QTextEdit` did not give reliable Up/Down line navigation in JAWS/NVDA.
- Putting the full plot in `setAccessibleName()` made review worse.
- Splitting every sentence into list rows looked like blank lines between items and polluted stored text with extra line breaks.

### Solution: `PlotLineList` + edit `QTextEdit`

Module: `src/accessibility/read_only_text.py`

**View mode (read-only review):** `PlotLineList` — a `QListWidget` subclass with one row per navigable line.

**Edit mode:** standard `QTextEdit` loaded with `set_navigable_plain_text()` (continuous prose, no injected breaks).

**Book Details** stacks both in a `QStackedWidget`:
- View: `plot_review` (`PlotLineList`)
- Edit: `comments_edit` (`QTextEdit`)
- Switch widgets in `_set_fields_read_only()`; sync prose with `format_plot_text_for_navigation()` when returning to view mode.

**Web Metadata** uses `PlotLineList` for the plot field.

### How plot rows are built

`plot_lines_for_review()` loads text into the list:
1. **Item 0:** rating line only (for example `Rating: 3.5 (2 ratings)`), when present.
2. **Items 1+:** plot body split into lines of at most **73 characters**, breaking only at word boundaries (`_wrap_at_words()`).

Storage and edit mode use `format_plot_text_for_navigation()` — normalizes line endings, rejoins legacy sentence-per-line data, and keeps plot body as continuous prose. **Do not** inject sentence line breaks into stored text.

Compare plot text with `plot_text_equivalent()` (ignores line-break and whitespace differences).

### PlotLineList accessibility and visual settings

- `setAccessibleName("Plot")` — short label only; row text comes from `AccessibleTextRole` per item.
- `setAccessibleDescription("")` — avoid duplicate announcements.
- `setSpacing(0)`, `setUniformItemSizes(True)`, zero item padding in stylesheet.
- `_CompactPlotLineDelegate` paints single-line rows at `fontMetrics().height()` so rows stack tightly without visual gaps.
- Selected/focused rows use base background (no highlight bar) so the field does not flash a selection color while reviewing.
- `setMouseTracking(False)`; `WA_Hover` disabled on widget and viewport.

Example:
```python
from src.accessibility.read_only_text import PlotLineList

self.plot_review = PlotLineList()
self.plot_review.setAccessibleName("Plot")
self.plot_review.set_plot_text(self.book.comments or "")
```

### Rules

- Use `PlotLineList.set_plot_text()` to load; do not call `setPlainText()`.
- Keep rating on its own list row (item 0), separate from plot body lines.
- Do not break words when wrapping plot lines for the list.
- Do not put full plot text in `setAccessibleName()`.
- Web metadata save path: `_build_plot_text_for_db()` uses `format_plot_text_for_navigation()`, not sentence splitting.

Reference files:
- `src/accessibility/read_only_text.py`
- `src/ui/book_details.py`
- `src/ui/web_metadata.py`
- `test/test_read_only_text.py`

## 13. Decision policy: defect vs intentional noise reduction

Use this policy in reviews:
- Confirmed defect: required information or action is not reliably accessible.
- Intentional design: reduced announcement noise but required access remains explicit and testable.
- Needs decision: tradeoff is unclear and requires design confirmation before implementation.
