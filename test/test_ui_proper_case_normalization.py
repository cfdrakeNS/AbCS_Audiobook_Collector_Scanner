"""Tests for preference-aware proper-case normalization in UI save helpers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings

from ui.book_details import BookDetailsWindow
from ui.import_detail_window import ImportDetailWindow
from ui.update_window import UpdateWindow


@pytest.fixture
def isolated_qsettings(tmp_path):
    """Use temporary INI-backed QSettings storage for deterministic tests."""
    original_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))

    settings = QSettings("AbCS", "AbCS")
    settings.clear()
    settings.sync()
    try:
        yield settings
    finally:
        settings.clear()
        settings.sync()
        QSettings.setDefaultFormat(original_format)


@pytest.mark.parametrize(
    "window_cls",
    [BookDetailsWindow, ImportDetailWindow, UpdateWindow],
)
def test_normalize_name_field_applies_proper_case_when_enabled(
    isolated_qsettings,
    window_cls,
):
    isolated_qsettings.setValue("import/autocorrect/proper_case", True)
    isolated_qsettings.sync()

    assert window_cls._normalize_name_field("  tHe hOBbiT  ") == "The Hobbit"
    assert window_cls._normalize_name_field(
        "  mary-jane o'connor  ") == "Mary-Jane O'Connor"


@pytest.mark.parametrize(
    "window_cls",
    [BookDetailsWindow, ImportDetailWindow, UpdateWindow],
)
def test_normalize_name_field_preserves_user_case_when_disabled(
    isolated_qsettings,
    window_cls,
):
    isolated_qsettings.setValue("import/autocorrect/proper_case", False)
    isolated_qsettings.sync()

    assert window_cls._normalize_name_field("  tHe hOBbiT  ") == "tHe hOBbiT"
    assert window_cls._normalize_name_field("   ") == ""
