"""Clipboard helpers for table Copy (Ctrl+C and right-click)."""

from __future__ import annotations

from PySide6.QtGui import QGuiApplication


def copy_plain_text(text: str | None) -> bool:
    """Put plain text on the system clipboard. Returns True when text was copied."""
    if text is None:
        return False
    value = str(text)
    if value == "":
        return False
    QGuiApplication.clipboard().setText(value)
    return True
