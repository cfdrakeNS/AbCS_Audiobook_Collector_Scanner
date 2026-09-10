"""Import and Book List Import progress-window tests."""

from __future__ import annotations

from helpers.import_window_helpers import cleanup_window

from src.ui.book_list_import_window import BookListImportWindow
from src.ui.import_progress_window import ImportProgressWindow

def test_format_elapsed_mmss():
    assert BookListImportWindow._format_elapsed(65) == "01:05"
    assert BookListImportWindow._format_elapsed(3661) == "01:01:01"

def test_progress_window_activity_and_help_override(ui_scaler, theme_manager):
    from src.ui.help_router import get_help_doc_filename

    window = ImportProgressWindow(ui_scaler, theme_manager)
    window.set_activity_label("import")
    window.help_doc_override = "11_import_book_list.md"
    assert window._activity_label == "import"
    assert get_help_doc_filename(window) == "11_import_book_list.md"
    # Avoid cancel prompt during teardown
    window._scan_active = False
    window.close()

def test_book_list_progress_omits_unused_counters(ui_scaler, theme_manager):
    window = ImportProgressWindow(ui_scaler, theme_manager)
    window.set_activity_label("import")
    window._scan_active = True
    window.update_counters(
        scanned=3,
        added=2,
        fixed=0,
        errors=1,
        warnings=0,
        duplicates=1,
        elapsed_text="00:05",
    )
    msg = window.status_bar.currentMessage()
    assert "Scanned: 3" in msg
    assert "Added: 2" in msg
    assert "Errors: 1" in msg
    assert "Duplicates: 1" in msg
    assert "Corrected:" not in msg
    assert "Warnings:" not in msg
    assert "Press Escape to cancel" in msg
    window._scan_active = False
    window.close()

def test_folder_import_progress_keeps_corrected_warnings(ui_scaler, theme_manager):
    window = ImportProgressWindow(ui_scaler, theme_manager)
    window.set_activity_label("scan")
    window._scan_active = True
    window.update_counters(
        scanned=10,
        added=5,
        fixed=2,
        errors=1,
        warnings=3,
        duplicates=0,
        elapsed_text="00:01",
    )
    msg = window.status_bar.currentMessage()
    assert "Corrected: 2" in msg
    assert "Warnings: 3" in msg
    assert "Press Escape to cancel" in msg
    window._scan_active = False
    window.close()

def test_build_progress_summary_matches_folder_cancel_pattern():
    summary = BookListImportWindow._build_progress_summary(
        BookListImportWindow,
        canceled=True,
        scanned=4,
        added=2,
        errors=1,
        duplicates=1,
        elapsed_text="00:12",
    )
    assert summary.startswith("Import canceled | ")
    assert "Scanned: 4" in summary
    assert "Added: 2" in summary
    assert "Errors: 1" in summary
    assert "Duplicates: 1" in summary
    assert "Elapsed: 00:12" in summary
    assert "Corrected" not in summary

def test_mark_complete_does_not_double_prefix_canceled(ui_scaler, theme_manager):
    window = ImportProgressWindow(ui_scaler, theme_manager)
    window.set_activity_label("import")
    window.mark_complete(
        canceled=True,
        elapsed_text="00:03",
        files_scanned=0,
        books_added=0,
        read_errors=0,
        summary_text=(
            "Import canceled | Scanned: 2 | Added: 1 | Errors: 0 | "
            "Duplicates: 0 | Elapsed: 00:03"
        ),
    )
    msg = window.status_bar.currentMessage()
    assert msg.startswith("Import canceled | ")
    assert not msg.startswith("Cancel Import: Import canceled")
    assert "Esc to close" in msg
    window.close()

def test_book_list_import_blocks_reentry(qapp, monkeypatch):
    """Import button / Alt+I must not start a second run while one is active."""
    win = BookListImportWindow.__new__(BookListImportWindow)
    win._is_importing = True
    statuses = []
    win.set_status = lambda msg, **k: statuses.append(msg)

    BookListImportWindow.import_books(win)
    assert statuses and "already in progress" in statuses[-1].lower()

    win._is_importing = True
    BookListImportWindow.browse_file(win)
    assert any("import is in progress" in s.lower() for s in statuses)

def test_set_import_controls_enabled_toggles_import_button(qapp):
    from unittest.mock import MagicMock

    win = BookListImportWindow.__new__(BookListImportWindow)
    win.import_button = MagicMock()
    win.browse_button = MagicMock()
    win.collection_combo = MagicMock()
    win.file_edit = MagicMock()
    win.load_books_check = MagicMock()
    win.add_read_date_check = MagicMock()
    win.file_has_header_check = MagicMock()
    win.export_button = MagicMock()
    win.field_mappings = {}
    win.import_errors = []
    win._export_was_enabled = False
    win.import_mode = "new"
    win._apply_mode_field_availability = MagicMock()

    BookListImportWindow._set_import_controls_enabled(win, False)
    win.import_button.setEnabled.assert_called_with(False)
    win.browse_button.setEnabled.assert_called_with(False)

    BookListImportWindow._set_import_controls_enabled(win, True)
    win.import_button.setEnabled.assert_called_with(True)
    win._apply_mode_field_availability.assert_called()


def test_import_progress_add_phase_resets_then_increments(qtbot, ui_scaler, theme_manager):
    """Progress bar should reset at add-phase start, then increment as items process."""
    window = ImportProgressWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)

    window.prepare_for_add_phase(4)

    assert window.scan_progress.value() == 0
    assert window.scan_progress.format() == "Adding... 0/4"

    window.update_add_progress(
        processed=2,
        total=4,
        books_added=1,
        elapsed_text="00:05",
    )

    assert window.scan_progress.value() == 50
    assert window.scan_progress.format() == "Adding... 2/4"
    status_mid = window.status_bar.currentMessage()
    assert "Adding 2/4" in status_mid
    assert "Elapsed 00:05" in status_mid

    window.update_add_progress(
        processed=3,
        total=4,
        books_added=2,
        elapsed_text="00:08",
        scanned=10,
        fixed=1,
        errors=2,
        warnings=1,
        duplicates=0,
    )
    # Progress bar keeps Adding N/N; status switches to counter summary when
    # scanned= is supplied (no duplicate "Adding 3/4" prefix).
    assert window.scan_progress.format() == "Adding... 3/4"
    assert window.scan_progress.value() == 75
    status_text = window.status_bar.currentMessage()
    assert "Scanned: 10" in status_text
    assert "Valid:" not in status_text
    assert "Added: 2" in status_text
    assert "Corrected: 1" in status_text
    assert "Errors: 2" in status_text
    assert "Warnings: 1" in status_text
    assert "Elapsed 00:08" in status_text

    window._scan_active = False
    cleanup_window(window)

