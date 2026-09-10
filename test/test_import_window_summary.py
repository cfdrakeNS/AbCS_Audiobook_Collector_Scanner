"""Import window summary, filter, and revalidation tests."""

from __future__ import annotations

import pytest

from helpers.import_window_helpers import (
    apply_suppress_import_confirmations,
    cleanup_window,
)

from src.ui.import_window import ImportWindow


@pytest.fixture(autouse=True)
def suppress_import_confirmations(monkeypatch):
    apply_suppress_import_confirmations(monkeypatch)

def test_import_warning_filter_excludes_fallback_and_corrected(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Warning filter should include pure warnings but exclude fallback/corrected rows."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    warning_index = window.error_filter_combo.findData("warning")
    assert warning_index >= 0
    window.error_filter_combo.setCurrentIndex(warning_index)

    warning_only = {
        "status": "Warning",
        "errors": ["W: year missing"],
    }
    warning_with_fallback = {
        "status": "Warning",
        "errors": ["F: author from folder", "W: year missing"],
    }
    warning_with_corrected = {
        "status": "Warning",
        "errors": ["C: trimmed whitespace", "W: year missing"],
    }

    assert window._matches_error_filter(warning_only) is True
    assert window._matches_error_filter(warning_with_fallback) is False
    assert window._matches_error_filter(warning_with_corrected) is False

    # Cleanup
    cleanup_window(window)

def test_import_summary_uses_errors_warnings_label(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Status summary should display separate Errors and Warnings counts."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    window.update_summary(
        scanned=10, fixed=3, errors=2, warnings=4, duplicates=1, added=5
    )
    status_text = window.status_bar.currentMessage()

    assert "Corrected: 3" in status_text
    assert "Valid:" not in status_text
    assert "Errors: 2" in status_text
    assert "Warnings: 4" in status_text
    assert "Errors/Warnings:" not in status_text
    assert "Issues:" not in status_text

    # Cleanup
    cleanup_window(window)

def test_import_summary_showing_count_on_filter(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Active error filter should show count as Showing on the right."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    window.scanned_items = [
        {"status": "Warning", "errors": ["W: test"], "book": {}},
        {"status": "OK", "errors": [], "book": {}},
    ]

    warning_index = window.error_filter_combo.findData("warning")
    assert warning_index >= 0
    window.error_filter_combo.setCurrentIndex(warning_index)
    window.update_summary(scanned=2, fixed=0, errors=0, warnings=1, duplicates=0, added=0)

    status_text = window.status_bar.currentMessage()
    assert "Filtered:" not in status_text
    assert "Showing:" not in status_text
    assert "Filter: Warning" in status_text
    assert window.showing_status_label.isVisible()
    assert window.showing_status_label.text() == "Showing: 1"
    assert "Showing: 1" in window._default_status_message

    cleanup_window(window)

def test_refresh_summary_updates_after_revalidate(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Editing a review row should refresh Errors/Warnings counts from current status."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    book = {
        "title": "Short",
        "author": "Author One",
        "year": 2020,
        "folder": "/tmp/book-a",
        "errors": ["Title below minimum length (8)"],
    }
    item = {
        "book": book,
        "status": "Warning",
        "errors": list(book["errors"]),
        "is_duplicate": False,
        "error_summary": "",
        "author": book["author"],
        "title": book["title"],
        "year": book["year"],
        "folder": book["folder"],
    }
    window.scanned_items = [item]
    window.scan_outcomes = [
        {
            "book": book,
            "status": "Warning",
            "errors": list(book["errors"]),
            "is_duplicate": False,
            "outcomes": ["warning"],
        }
    ]

    window._refresh_summary_from_items()
    assert window._summary_counts["warnings"] == 1
    assert window._summary_counts["errors"] == 0

    book["title"] = "A Proper Long Title"
    window._revalidate_scanned_item(item)
    window._refresh_summary_from_items()

    assert window._summary_counts["warnings"] == 0
    assert window._summary_counts["errors"] == 0
    assert window._summary_counts["scanned"] == 1
    assert window.scan_outcomes[0]["status"] == "OK"
    assert "warning" not in window.scan_outcomes[0]["outcomes"]

    cleanup_window(window)

def test_revalidate_clears_author_blank_after_edit(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Fixing a missing author in import detail should clear stale Author Blank flags."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    book = {
        "title": "A Good Title Here",
        "author": "",
        "year": 2020,
        "folder": "/tmp/book-missing-author",
        "errors": ["Author Blank"],
    }
    item = {
        "book": book,
        "status": "Error",
        "errors": list(book["errors"]),
        "is_duplicate": False,
        "error_summary": "",
        "author": book["author"],
        "title": book["title"],
        "year": book["year"],
        "folder": book["folder"],
    }
    window.scanned_items = [item]
    window.scan_outcomes = []

    book["author"] = "New Author"
    item["author"] = "New Author"
    window._revalidate_scanned_item(item)

    assert item["status"] == "OK"
    assert book["errors"] == item["errors"]
    assert not any("author blank" in str(err).lower() for err in item["errors"])

    cleanup_window(window)

def test_refresh_summary_drops_discarded_row_from_scanned_total(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Discarding a review row should reduce Scanned and issue counters."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    warning_book = {
        "title": "Short",
        "author": "Warn Author",
        "year": 2020,
        "folder": "/tmp/warn",
        "errors": ["Title below minimum length (8)"],
    }
    ok_book = {
        "title": "Good Title Here",
        "author": "Ok Author",
        "year": 2020,
        "folder": "/tmp/ok",
        "errors": [],
    }
    window.scanned_items = [
        {
            "book": warning_book,
            "status": "Warning",
            "errors": list(warning_book["errors"]),
            "is_duplicate": False,
            "error_summary": "",
            "author": warning_book["author"],
            "title": warning_book["title"],
            "year": None,
            "folder": warning_book["folder"],
        },
        {
            "book": ok_book,
            "status": "OK",
            "errors": [],
            "is_duplicate": False,
            "error_summary": "",
            "author": ok_book["author"],
            "title": ok_book["title"],
            "year": None,
            "folder": ok_book["folder"],
        },
    ]
    window.scan_outcomes = [
        {
            "book": warning_book,
            "status": "Warning",
            "errors": list(warning_book["errors"]),
            "is_duplicate": False,
            "outcomes": ["warning"],
        },
        {
            "book": ok_book,
            "status": "OK",
            "errors": [],
            "is_duplicate": False,
            "outcomes": [],
        },
    ]
    window.table.setRowCount(2)

    window._discard_scanned_item(0)
    assert len(window.scanned_items) == 1
    assert len(window.scan_outcomes) == 1
    assert window._summary_counts["scanned"] == 1
    assert window._summary_counts["warnings"] == 0
    assert window._summary_counts["errors"] == 0

    cleanup_window(window)

def test_import_fixed_counter_counts_fallback_and_autocorrect(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Fixed counter should include fallback+autocorrect without inflating warnings/errors."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    window.scanned_items = []
    window.scan_outcomes = [
        {"status": "Added", "is_duplicate": False, "outcomes": ["autocorrect_used"]}
        for _ in range(6)
    ] + [
        {"status": "Added", "is_duplicate": False, "outcomes": ["fallback_used"]}
        for _ in range(2)
    ]

    window._refresh_summary_from_items()

    assert window._summary_counts["fixed"] == 8
    assert window._summary_counts["errors"] == 0
    assert window._summary_counts["warnings"] == 0

    # Cleanup
    cleanup_window(window)

