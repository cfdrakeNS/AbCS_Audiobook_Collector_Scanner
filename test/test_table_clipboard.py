"""Tests for table clipboard Copy helper."""

from src.ui.table_clipboard import copy_plain_text


def test_copy_plain_text_rejects_empty(qapp):
    assert copy_plain_text(None) is False
    assert copy_plain_text("") is False


def test_copy_plain_text_sets_clipboard(qapp):
    assert copy_plain_text("Stephen King") is True
    from PySide6.QtGui import QGuiApplication

    assert QGuiApplication.clipboard().text() == "Stephen King"
