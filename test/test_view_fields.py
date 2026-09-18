"""Tests for view-mode static value labels."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.accessibility.view_fields import create_view_value_label, set_view_value


def test_create_view_value_label_is_focusable_not_editable(qapp):
    label = create_view_value_label("Author")
    set_view_value(label, "John Connelly", "Author")
    assert label.focusPolicy() == Qt.StrongFocus
    assert label.text() == "John Connelly"
    assert label.accessibleName() == "Author"
    assert "John Connelly" in (label.accessibleDescription() or "")
    # QLabel should not report as a line edit
    assert label.metaObject().className() == "QLabel"
