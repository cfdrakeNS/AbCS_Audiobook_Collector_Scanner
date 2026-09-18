"""View-mode display fields that avoid JAWS edit / read-only noise.

Spike-backed approach: focusable QLabel reporting as a static value.
Use in view stacks; keep real edit widgets in edit mode.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


def create_view_value_label(accessible_name: str, parent=None) -> QLabel:
    """Return a focusable label for view-mode field values.

    Screen readers should announce the accessible name and text without
    saying ``edit`` or ``read only``.
    """
    label = QLabel(parent)
    label.setTextInteractionFlags(Qt.TextSelectableByKeyboard)
    label.setFocusPolicy(Qt.StrongFocus)
    label.setAccessibleName(accessible_name)
    label.setWordWrap(False)
    return label


def set_view_value(label: QLabel, value: str, accessible_name: str | None = None) -> None:
    text = value if value is not None else ""
    label.setText(text)
    name = accessible_name or label.accessibleName() or "Value"
    label.setAccessibleName(name)
    label.setAccessibleDescription(text if text else "Blank")
