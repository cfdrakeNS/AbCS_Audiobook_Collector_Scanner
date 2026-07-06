"""Regression tests for recent Update/Import window behavior changes."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from src.accessibility.scaling import UIScaler
from src.accessibility.shortcuts import ShortcutManager
from src.accessibility.style_helpers import set_message_box_button_accessibility
from src.accessibility.theme_manager import ThemeManager
from src.ui.import_window import ImportWindow
from src.ui.import_detail_window import ImportDetailWindow
from src.ui.import_progress_window import ImportProgressWindow
from src.ui.update_window import UpdateWindow
from src.database.queries import CollectionQueries
from src.database.models import Collection

@pytest.fixture(autouse=True)
def suppress_import_confirmations(monkeypatch):
    """Avoid modal close/cancel prompts during automated test teardown."""
    monkeypatch.setattr(ImportWindow, "_confirm_close_window", lambda self: True)
    monkeypatch.setattr(ImportWindow, "_confirm_cancel_scan", lambda self: True)


@pytest.fixture
def isolated_qsettings(tmp_path):
    """Use temporary INI-based QSettings to avoid user-profile settings writes."""
    original_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    try:
        yield
    finally:
        QSettings.setDefaultFormat(original_format)


def _prepare_window_for_teardown_close(widget):
    """Skip Import Detail dirty-check prompts during automated teardown."""
    if hasattr(widget, "_clear_dirty"):
        widget._clear_dirty()
    if hasattr(widget, "_closing_via_handler"):
        widget._closing_via_handler = True
    # ImportProgressWindow blocks close while scan is active (modal cancel prompt).
    if hasattr(widget, "_scan_active"):
        widget._scan_active = False


def _close_widget_for_teardown(widget):
    """Close a widget without blocking on unsaved-changes prompts."""
    if not widget:
        return
    _prepare_window_for_teardown_close(widget)
    try:
        widget.setVisible(False)
        if hasattr(widget, "reject"):
            widget.reject()
        elif hasattr(widget, "close"):
            widget.close()
    except Exception:
        pass


def cleanup_window(window):
    """Helper to forcefully cleanup a window and all its children."""
    if not window:
        return

    # Close any visible dialogs/message boxes first
    for widget in QApplication.topLevelWidgets():
        if widget.isVisible() and widget != window:
            _close_widget_for_teardown(widget)

    QApplication.processEvents()

    # Force close progress window if exists
    if hasattr(window, "progress_window") and window.progress_window is not None:
        pw = window.progress_window
        _close_widget_for_teardown(pw)
        window.progress_window = None

    QApplication.processEvents()

    # Close the main window (visible or not — qtbot keeps hidden dialogs in topLevelWidgets)
    _close_widget_for_teardown(window)

    # Process events multiple times
    for _ in range(5):
        QApplication.processEvents()

    # Final sweep: close any lingering top-level dialogs (including hidden prompts)
    for widget in QApplication.topLevelWidgets():
        if not widget:
            continue
        _close_widget_for_teardown(widget)

    QApplication.processEvents()


def _configure_mass_standard_scan(window, *, trim_whitespace: bool | None = None):
    """Use mass-standard import rules so scan tests are not host-settings dependent."""
    if trim_whitespace is not None:
        window.import_scanner.trim_whitespace = trim_whitespace
    window.import_scenario_mode = "mass_standard"
    scanner = window.import_scanner
    window.import_scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder" if window.author_fallback_to_folder else None,
        title_fallback_mode="file" if window.title_fallback_to_file else None,
        reader_keywords=window.reader_keywords,
        trim_whitespace=scanner.trim_whitespace,
        strip_leading_punctuation=scanner.strip_leading_punctuation,
        remove_non_alphanumeric=scanner.remove_non_alphanumeric,
        proper_case_fields=scanner.proper_case_fields,
        proper_case_skip_review=scanner.proper_case_skip_review,
        trim_whitespace_skip_review=scanner.trim_whitespace_skip_review,
        strip_leading_punctuation_skip_review=scanner.strip_leading_punctuation_skip_review,
        remove_non_alphanumeric_skip_review=scanner.remove_non_alphanumeric_skip_review,
    )


def test_update_window_series_and_genre_combo_widths_match(qapp, qtbot, temp_db):
    """Series and Genre combos should keep the same minimum width."""
    scaler = UIScaler(qapp)
    window = UpdateWindow(temp_db, scaler, selected_book_ids=set())
    qtbot.addWidget(window)

    assert window.series_combo.minimumWidth() == window.genre_combo.minimumWidth()
    assert window.series_combo.minimumWidth() > 0

    # Cleanup
    cleanup_window(window)


def test_import_warning_filter_excludes_fallback_and_corrected(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Warning filter should include pure warnings but exclude fallback/corrected rows."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
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


def test_import_scan_reloads_fallback_preferences(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Each scan should pick up current fallback checkbox values from settings."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    settings = QSettings("AbCS", "AudioBookCollector")
    settings.setValue("import/fallback/author_to_folder", True)
    settings.setValue("import/fallback/title_to_file", True)
    window._reload_scan_settings()
    assert window.author_fallback_to_folder is True
    assert window.import_scanner.author_fallback_mode == "folder"
    assert window.import_scanner.title_fallback_mode == "file"

    settings.setValue("import/fallback/author_to_folder", False)
    settings.setValue("import/fallback/title_to_file", False)
    window._reload_scan_settings()
    assert window.author_fallback_to_folder is False
    assert window.title_fallback_to_file is False
    assert window.import_scanner.author_fallback_mode is None
    assert window.import_scanner.title_fallback_mode is None

    cleanup_window(window)


def test_import_summary_uses_errors_warnings_label(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Status summary should display separate Errors and Warnings counts."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
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


def test_import_alt_browse_from_collection_combo(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    """Alt+B should open browse even when collection combo has focus."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    browse_called = {"count": 0}

    def fake_browse():
        browse_called["count"] += 1

    monkeypatch.setattr(window, "on_browse", fake_browse)
    window.collection_combo.setFocus()
    qtbot.keyClick(window.collection_combo, Qt.Key_B, Qt.AltModifier)

    assert browse_called["count"] == 1

    cleanup_window(window)


def test_import_summary_showing_count_on_filter(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Active error filter should show count as Showing on the right."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
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


def test_message_box_button_accessibility_helper(qapp):
    """Dialog buttons should keep mnemonics but expose clear accessible text."""
    msg = QMessageBox()
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    set_message_box_button_accessibility(
        msg,
        {
            QMessageBox.Yes: ("Yes, save", "Save changes"),
            QMessageBox.No: ("No, continue editing", "Return to editing"),
        },
    )

    assert msg.button(QMessageBox.Yes).accessibleName() == "Yes, save"
    assert msg.button(QMessageBox.Yes).accessibleDescription() == "Save changes"
    assert msg.button(QMessageBox.No).accessibleName() == "No, continue editing"
    assert msg.button(QMessageBox.No).accessibleDescription() == "Return to editing"


def test_import_detail_save_discard_shortcuts_are_explicit(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Import Detail Save/Discard should not rely on Qt button mnemonics."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportDetailWindow(
        temp_db,
        scaler,
        theme_manager,
        book_data={"title": "Example", "author": "Author"},
    )
    qtbot.addWidget(window)
    window.time_edit.setText("02:30")
    window._collect_form_data()
    assert window.book_data["time_hours"] == 2
    assert window.book_data["time_minutes"] == 30

    shortcuts = ShortcutManager.IMPORT_DETAIL_WINDOW_SHORTCUTS

    assert window.save_return_button.text() == "Save"
    assert window.skip_button.text() == "Discard"
    assert shortcuts["S"] == ("Save", "save_return_button")
    assert shortcuts["D"] == ("Discard", "skip_button")

    cleanup_window(window)


def test_import_detail_actions_return_focus_to_title(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    """Save, discard, and page navigation should return focus to Title."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportDetailWindow(
        temp_db,
        scaler,
        theme_manager,
        book_data={"title": "Example", "author": "Author"},
    )
    qtbot.addWidget(window)

    focus_requests = []
    monkeypatch.setattr(window, "_focus_title_field", lambda: focus_requests.append(1))

    window.on_save()
    monkeypatch.setattr(window, "_navigate_without_close", lambda target_index: True)
    window.on_prev()
    window.on_next()

    class ParentStub:
        scanned_items = [{"book": {"title": "Next Example", "author": "Author"}}]

        def _discard_scanned_item(self, row):
            return 0

        def set_status(self, message, announce=False):
            pass

    window._owner_widget = ParentStub()
    window.on_skip_discard()

    assert len(focus_requests) == 4

    cleanup_window(window)


def test_refresh_summary_updates_after_revalidate(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Editing a review row should refresh Errors/Warnings counts from current status."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
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


def test_revalidate_clears_author_blank_after_edit(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Fixing a missing author in import detail should clear stale Author Blank flags."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
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


def test_import_detail_new_author_survives_focus_out_and_save(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """A typed author not yet in the database must not revert on focus-out or save."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    import_window = ImportWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(import_window)

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
    import_window.scanned_items = [item]
    import_window.scan_outcomes = []

    detail = ImportDetailWindow(
        temp_db,
        scaler,
        theme_manager,
        book_data=book.copy(),
        errors=list(item["errors"]),
        current_index=0,
        total_count=1,
        parent=import_window,
    )
    qtbot.addWidget(detail)

    detail.author_combo.setEditText("Brand New Author")
    detail.title_edit.setFocus()
    qtbot.wait(10)

    assert detail.author_combo.currentText().strip() == "Brand New Author"

    assert detail.on_save() is True
    assert book["author"] == "Brand New Author"
    assert item["author"] == "Brand New Author"
    assert item["status"] == "OK"
    assert not any("author blank" in str(err).lower() for err in item["errors"])

    cleanup_window(detail)
    cleanup_window(import_window)


def test_refresh_summary_drops_discarded_row_from_scanned_total(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Discarding a review row should reduce Scanned and issue counters."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
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


def test_import_fixed_counter_counts_fallback_and_autocorrect(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Fixed counter should include fallback+autocorrect without inflating warnings/errors."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
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


def test_scan_keeps_fixed_warning_rows_for_manual_add(
    qapp, qtbot, temp_db, isolated_qsettings, tmp_path, monkeypatch
):
    """Fallback/autocorrect rows should stay in review list; clean rows may auto-add."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    # Ensure a selectable collection is active.
    cq = CollectionQueries(temp_db)
    if window.collection_combo.count() == 0:
        collection_id = cq.insert(Collection(name="Default", active=True))
        window._load_collection_options()
        target_index = window.collection_combo.findData(collection_id)
        if target_index >= 0:
            window.collection_combo.setCurrentIndex(target_index)
    elif window.collection_combo.currentData() is None:
        window.collection_combo.setCurrentIndex(1)

    scan_dir = Path(tmp_path)
    scan_dir.mkdir(parents=True, exist_ok=True)
    window.folder_edit.setText(str(scan_dir))
    _configure_mass_standard_scan(window)

    fixed_book = {
        "title": "Fixed Example",
        "author": "Author One",
        "year": 2022,
        "genre": "Fiction",
        "narrator": "",
        "comment": "",
        "folder": str(scan_dir),
        "files": [str(scan_dir / "fixed.mp3")],
        "errors": ["F: Author fallback from folder used"],
        "time_hours": 1,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 1.0,
        "bitrate": 128,
        "format": "MP3",
    }
    clean_book = {
        "title": "Clean Example",
        "author": "Author Two",
        "year": 2021,
        "genre": "Fiction",
        "narrator": "",
        "comment": "",
        "folder": str(scan_dir),
        "files": [str(scan_dir / "clean.mp3")],
        "errors": [],
        "time_hours": 1,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 1.0,
        "bitrate": 128,
        "format": "MP3",
    }

    monkeypatch.setattr(
        window.scanner,
        "scan_folder",
        lambda *args, **kwargs: [fixed_book, clean_book],
    )

    window.on_scan()

    # Wait a bit for the scan to complete and UI updates to process
    qtbot.wait(200)

    # Process any pending Qt events to ensure all UI updates have been processed
    from PySide6.QtWidgets import QApplication

    QApplication.processEvents()

    # Give the progress window time to update
    qtbot.wait(100)

    # Clean row auto-added, fixed row remains for review/manual add.
    assert any(
        (item.get("book", {}).get("title") == "Fixed Example")
        for item in window.scanned_items
    )
    assert not any(
        (item.get("book", {}).get("title") == "Clean Example")
        for item in window.scanned_items
    )
    assert window._summary_counts["fixed"] >= 1

    # Cleanup: use helper to close all windows properly
    cleanup_window(window)


def test_scan_keeps_author_title_corrected_rows_for_manual_add(
    qapp, qtbot, temp_db, isolated_qsettings, tmp_path, monkeypatch
):
    """Author/title corrected rows should stay in review list with C: flags."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    cq = CollectionQueries(temp_db)
    if window.collection_combo.count() == 0:
        collection_id = cq.insert(Collection(name="Default", active=True))
        window._load_collection_options()
        target_index = window.collection_combo.findData(collection_id)
        if target_index >= 0:
            window.collection_combo.setCurrentIndex(target_index)
    elif window.collection_combo.currentData() is None:
        window.collection_combo.setCurrentIndex(1)

    scan_dir = Path(tmp_path)
    scan_dir.mkdir(parents=True, exist_ok=True)
    window.folder_edit.setText(str(scan_dir))
    _configure_mass_standard_scan(window, trim_whitespace=True)

    corrected_book = {
        "title": "  Corrected Example  ",
        "author": "Author One",
        "year": 2022,
        "genre": "Fiction",
        "narrator": "",
        "comment": "",
        "folder": str(scan_dir),
        "files": [str(scan_dir / "corrected.mp3")],
        "errors": [],
        "time_hours": 1,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 1.0,
        "bitrate": 128,
        "format": "MP3",
    }
    clean_book = {
        "title": "Clean Example",
        "author": "Author Two",
        "year": 2021,
        "genre": "Fiction",
        "narrator": "",
        "comment": "",
        "folder": str(scan_dir),
        "files": [str(scan_dir / "clean.mp3")],
        "errors": [],
        "time_hours": 1,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 1.0,
        "bitrate": 128,
        "format": "MP3",
    }

    monkeypatch.setattr(
        window.scanner,
        "scan_folder",
        lambda *args, **kwargs: [corrected_book, clean_book],
    )

    window.on_scan()
    qtbot.wait(200)
    QApplication.processEvents()

    corrected_items = [
        item
        for item in window.scanned_items
        if (item.get("book", {}).get("title") or "").strip() == "Corrected Example"
    ]
    assert len(corrected_items) == 1
    assert corrected_items[0]["error_summary"].startswith("C:")
    assert not any(
        (item.get("book", {}).get("title") or "").strip() == "Clean Example"
        for item in window.scanned_items
    )
    assert window._summary_counts["fixed"] == 1
    assert window._summary_counts["added"] == 1
    assert window._summary_counts["errors"] == 0
    assert window._summary_counts["warnings"] == 0
    status_text = window.status_bar.currentMessage()
    assert "Added: 1" in status_text
    assert "Corrected: 1" in status_text
    assert "Errors: 0" in status_text
    assert "Warnings: 0" in status_text
    assert "Valid:" not in status_text

    cleanup_window(window)


def test_apply_detail_edits_persists_time_fields(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    """Import window should copy edited time fields from detail book_data."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    book = {
        "title": "Time Test Book",
        "author": "Author One",
        "year": 2020,
        "folder": "/tmp/time-test",
        "files": ["/tmp/time-test/part1.mp3"],
        "time_hours": 0,
        "time_minutes": 0,
        "tracks": 2,
        "errors": [],
    }
    window.scanned_items = [
        {
            "book": book,
            "status": "OK",
            "errors": [],
            "is_duplicate": False,
            "error_summary": "",
            "author": book["author"],
            "title": book["title"],
            "year": book["year"],
            "folder": book["folder"],
        }
    ]
    window.table.setRowCount(1)

    class DetailStub:
        book_data = {
            **book,
            "time_hours": 2,
            "time_minutes": 30,
        }

    monkeypatch.setattr(window, "_revalidate_scanned_item", lambda item: None)
    monkeypatch.setattr(window, "_refresh_summary_from_items", lambda: None)
    window._apply_detail_edits(0, DetailStub())

    assert book["time_hours"] == 2
    assert book["time_minutes"] == 30
    assert book["tracks"] == 2

    cleanup_window(window)


def test_build_book_from_scan_uses_scanned_time_and_tracks(
    qapp, qtbot, temp_db, isolated_qsettings
):
    """Books added from scan should keep hours, minutes, and track count."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    cq = CollectionQueries(temp_db)
    if window.collection_combo.count() == 0:
        collection_id = cq.insert(Collection(name="Default", active=True))
        window._load_collection_options()
        idx = window.collection_combo.findData(collection_id)
        if idx >= 0:
            window.collection_combo.setCurrentIndex(idx)
    elif window.collection_combo.currentData() is None and window.collection_combo.count() > 1:
        window.collection_combo.setCurrentIndex(1)

    book = {
        "title": "Scan Length Book",
        "author": "Author Two",
        "year": 2019,
        "folder": "/tmp/scan",
        "files": ["/tmp/scan/a.mp3", "/tmp/scan/b.mp3", "/tmp/scan/c.mp3"],
        "time_hours": 5,
        "time_minutes": 15,
        "tracks": 3,
        "size_mb": 12.5,
        "bitrate": 128,
        "format": "MP3",
        "comment": "",
    }
    saved = window._build_book_from_scan(book)
    assert saved.time_hours == 5
    assert saved.time_minutes == 15
    assert saved.tracks == 3

    cleanup_window(window)


def test_unreadable_length_warning_when_files_have_no_duration(
    qapp, isolated_qsettings
):
    """Zero length with files present should warn about unreadable length, not minimum."""
    from src.core.validator import ImportValidator

    validator = ImportValidator()
    validator.rules_engine.min_book_length_minutes = 60
    book = {
        "title": "No Duration",
        "author": "Author",
        "year": 2020,
        "files": ["/tmp/a.mp3"],
        "time_hours": 0,
        "time_minutes": 0,
        "tracks": 1,
    }
    errors = validator.validate_book(book)
    assert any("Could not read length" in err for err in errors)
    assert not any("below minimum" in err.lower() for err in errors)

    book["time_hours"] = 1
    book["time_minutes"] = 30
    errors = validator.validate_book(book)
    assert not any("Could not read length" in err for err in errors)


def test_import_progress_add_phase_resets_then_increments(qapp, qtbot):
    """Progress bar should reset at add-phase start, then increment as items process."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportProgressWindow(scaler, theme_manager)
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
    assert "Adding 2/4" in window.status_bar.currentMessage()
    assert "Elapsed 00:05" in window.status_bar.currentMessage()

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
    status_text = window.status_bar.currentMessage()
    assert "Adding 3/4" in status_text
    assert "Valid:" not in status_text
    assert "Added: 2" in status_text
    assert "Elapsed 00:08" in status_text

    cleanup_window(window)
