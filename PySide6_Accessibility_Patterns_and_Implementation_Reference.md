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

## 4. Modal dialog accessibility pattern

Goal: make warnings/confirmations readable and actionable.

Pattern:
- Use a consistent modal helper where possible.
- Set clear dialog title/text and explicit button labels.
- Set accessible name and description for custom dialogs.
- Return focus to the most relevant control after dialog close.

Reference files:
- `src/accessibility/style_helpers.py`
- `src/main.py`
- `src/ui/book_list_import_window.py`

## 5. Keyboard shortcut implementation pattern

Goal: prevent conflicts and keep shortcut behavior predictable.

Pattern:
- Keep `F1`, `Escape`, and `Alt+/` as local window shortcuts.
- Register Alt+field shortcuts through centralized shortcut maps.
- Use lambda callbacks for mapped actions when needed.

Reference files:
- `src/accessibility/shortcuts.py`
- `src/ui/import_window.py`
- `src/ui/backup_restore_window.py`

## 6. Accessible help dialog pattern (F1)

Goal: provide a stable and readable shortcut list.

Pattern:
- Use a simple one-column read-only table or list.
- Provide per-row accessible text with explicit key + action wording.
- Include `Alt+/` in each window help list.

Reference files:
- `src/ui/import_detail_window.py`
- `src/ui/main_window.py`
- `src/ui/name_list_window.py`

## 7. Focus safety pattern for editable fields

Goal: reduce accidental full-value overwrite.

Pattern:
- On FocusIn, defer deselect/cursor behavior with `QTimer.singleShot(0, ...)`.
- Deselect auto-selected text in line edits and combo line edits.

Reference files:
- `src/ui/book_details.py`
- `src/ui/import_detail_window.py`
- `src/ui/preferences_window.py`

## 8. Table accessibility pattern

Goal: improve data comprehension in row-based widgets.

Pattern:
- Hide row-number headers when they add no meaning.
- Add semantic text via `Qt.AccessibleTextRole` for key cells.

Reference files:
- `src/ui/reading_history_window.py`
- `src/ui/main_window.py`
- `src/ui/backup_restore_window.py`

## 9. Reuse checklist

When building a new window:
- Add status API + `Alt+/` readback.
- Add F1 shortcut help surface.
- Enforce Alt-key allowlist in event filters.
- Apply combo anti-noise rules where editable combos exist.
- Ensure modal validation errors return focus to the invalid field.
- Set accessible names/descriptions for key controls.
- Verify explicit tab order.
- Avoid global Enter/Return shortcuts that override button activation.

## 10. Decision policy: defect vs intentional noise reduction

Use this policy in reviews:
- Confirmed defect: required information or action is not reliably accessible.
- Intentional design: reduced announcement noise but required access remains explicit and testable.
- Needs decision: tradeoff is unclear and requires design confirmation before implementation.
