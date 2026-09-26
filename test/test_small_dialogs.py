"""Smoke tests for small accessible dialogs."""

from __future__ import annotations

from src.database.models import Statistics
from src.ui.about_dialogue import AboutDialog
from src.ui.accessible_dialog import AccessibleDialog
from src.ui.license_dialogue import LicenseDialog
from src.ui.setup_dialogue import SetupDialog
from src.ui.statistics_dialog import StatisticsDialog


def _close_after_focus_timer(qtbot, dialog, wait_ms: int = 150) -> None:
    """Let constructor focus timers fire while the widget is still alive."""
    qtbot.wait(wait_ms)
    dialog.close()


def test_about_dialog_accessible_name(ui_scaler, qtbot):
    dialog = AboutDialog(ui_scaler)
    qtbot.addWidget(dialog)
    assert dialog.windowTitle() == "About AbCS"
    assert dialog.accessibleName() == "About AbCS"
    _close_after_focus_timer(qtbot, dialog)


def test_license_dialog_accessible_name(ui_scaler, qtbot):
    dialog = LicenseDialog(ui_scaler)
    qtbot.addWidget(dialog)
    assert dialog.windowTitle() == "AbCS License"
    assert dialog.accessibleName() == "AbCS License"
    _close_after_focus_timer(qtbot, dialog)


def test_setup_dialog_accessible_name(ui_scaler, qtbot):
    dialog = SetupDialog(ui_scaler)
    qtbot.addWidget(dialog)
    assert dialog.windowTitle() == "Welcome to AbCS"
    assert dialog.accessibleName() == "Welcome to AbCS"
    _close_after_focus_timer(qtbot, dialog)


def test_statistics_dialog_accessible_name(ui_scaler, qtbot):
    stats = Statistics(
        total_books=3,
        total_authors=2,
        total_series=1,
        total_genres=1,
        total_collections=1,
        books_read=1,
        books_unread=2,
        books_want_to_read=1,
        books_in_progress=1,
        total_time_hours=10,
        total_hours_read=4,
        collection_breakdown=[("Main", 3)],
    )
    dialog = StatisticsDialog(stats, ui_scaler)
    qtbot.addWidget(dialog)
    assert dialog.windowTitle() == "Library Statistics"
    assert dialog.accessibleName() == "Library Statistics Dialog"
    labels = [
        dialog.table.item(row, 0).text() for row in range(dialog.table.rowCount())
    ]
    assert "Books Want to Read" in labels
    assert "Books In Progress" in labels
    want_row = labels.index("Books Want to Read")
    progress_row = labels.index("Books In Progress")
    assert dialog.table.item(want_row, 1).text() == "1"
    assert dialog.table.item(progress_row, 1).text() == "1"
    _close_after_focus_timer(qtbot, dialog)


def test_accessible_dialog_base_constructible(qtbot):
    dialog = AccessibleDialog()
    qtbot.addWidget(dialog)
    dialog.setWindowTitle("Accessible Base")
    dialog.setAccessibleName("Accessible Base")
    assert dialog.accessibleName() == "Accessible Base"
    dialog.close()
