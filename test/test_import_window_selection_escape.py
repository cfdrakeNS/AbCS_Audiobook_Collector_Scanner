"""Import window: Escape clears a row selection before it closes the window."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTableWidgetItem

from src.ui.import_window import ImportWindow
from helpers.import_window_helpers import (
    apply_suppress_import_confirmations,
    cleanup_window,
)


@pytest.fixture(autouse=True)
def _no_prompts(monkeypatch):
    apply_suppress_import_confirmations(monkeypatch)


def _window_with_rows(temp_db, ui_scaler, theme_manager, count=3):
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    window.table.setRowCount(count)
    for row in range(count):
        window.table.setItem(
            row, window.COL_TITLE, QTableWidgetItem(f"Import Title {row}")
        )
    window.table.setCurrentCell(0, window.COL_TITLE)
    return window


def test_escape_clears_selection_without_closing(
    temp_db, ui_scaler, theme_manager, monkeypatch
):
    window = _window_with_rows(temp_db, ui_scaler, theme_manager)
    statuses = []
    cancels = []
    monkeypatch.setattr(
        window, "set_status", lambda msg, announce=False: statuses.append((msg, announce))
    )
    monkeypatch.setattr(window, "on_cancel", lambda: cancels.append(True))
    try:
        window.selection_anchor_row = 0
        window._select_row_range(0, 1, window.COL_TITLE)
        assert window.selected_rows == {0, 1}

        window.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))
        assert window.selected_rows == set()
        assert window.selection_anchor_row is None
        assert cancels == []
        assert statuses[-1] == ("Selection cleared", True)

        window.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))
        assert cancels == [True]
    finally:
        cleanup_window(window)


def test_finished_scan_keeps_progress_window_open(temp_db, ui_scaler, theme_manager):
    from src.ui.import_progress_window import ImportProgressWindow

    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    window.progress_window = ImportProgressWindow(
        ui_scaler, theme_manager, parent=window
    )
    window.progress_window.show()
    try:
        window._finish_scan_progress(
            canceled=False,
            elapsed_text="00:01",
            files_scanned=2,
            books_added=2,
            read_errors=0,
            summary_text="Scanned: 2 | Added: 2",
        )
        progress = window.progress_window
        assert progress is not None and progress.isVisible()
        assert "Scan complete" in progress.scan_progress.format()
        assert progress.scan_progress.accessibleName() == "Scan complete"
        message = progress.status_bar.currentMessage()
        assert message.startswith("Scan complete. Scanned: 2")
        assert "Esc to close" in message
    finally:
        cleanup_window(window)


def test_selection_announcement_is_title_and_count(
    temp_db, ui_scaler, theme_manager, monkeypatch
):
    window = _window_with_rows(temp_db, ui_scaler, theme_manager)
    statuses = []
    monkeypatch.setattr(
        window, "set_status", lambda msg, announce=False: statuses.append((msg, announce))
    )
    try:
        window.table.setCurrentCell(2, window.COL_TITLE + 1)
        window.selected_rows = {0, 1, 2}
        window.announce_selection()
        assert statuses == [("Import Title 2 - 3 selected", True)]
    finally:
        cleanup_window(window)
