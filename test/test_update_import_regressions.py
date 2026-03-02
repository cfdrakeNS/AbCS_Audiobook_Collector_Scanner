"""Regression tests for recent Update/Import window behavior changes."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from database.connection import DatabaseManager
from ui.import_window import ImportWindow
from ui.import_progress_window import ImportProgressWindow
from ui.update_window import UpdateWindow
from database.queries import CollectionQueries
from database.models import Collection


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def suppress_import_confirmations(monkeypatch):
    """Avoid modal close/cancel prompts during automated test teardown."""
    monkeypatch.setattr(
        ImportWindow, "_confirm_close_window", lambda self: True)
    monkeypatch.setattr(
        ImportWindow, "_confirm_cancel_scan", lambda self: True)


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


@pytest.fixture
def temp_db(tmp_path):
    """Provide a writable temporary copy of the project database."""
    data_dir = Path(PROJECT_ROOT) / "data"
    candidates = [
        data_dir / "abcs.db",
        data_dir / "wh abcs.db",
    ]
    backup_candidates = sorted(
        data_dir.glob("abcs.db.backup.*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    candidates.extend(backup_candidates)

    source_db = next((path for path in candidates if path.exists()), None)
    if source_db is None:
        raise FileNotFoundError(
            f"No testable database found in {data_dir}. Expected one of: abcs.db, wh abcs.db, or abcs.db.backup.*"
        )

    target_db = tmp_path / "abcs_test.db"
    shutil.copy2(source_db, target_db)

    db = DatabaseManager(str(target_db))
    try:
        yield db
    finally:
        db.close()


def cleanup_window(window):
    """Helper to forcefully cleanup a window and all its children."""
    if not window:
        return

    # Close any visible dialogs/message boxes first
    for widget in QApplication.topLevelWidgets():
        if widget.isVisible() and widget != window:
            try:
                if hasattr(widget, 'reject'):
                    widget.reject()
                elif hasattr(widget, 'close'):
                    widget.close()
                widget.setVisible(False)
            except:
                pass

    QApplication.processEvents()

    # Force close progress window if exists
    if hasattr(window, 'progress_window') and window.progress_window is not None:
        pw = window.progress_window
        try:
            if pw.isVisible():
                pw.setVisible(False)
            pw.reject()
        except:
            pass
        window.progress_window = None

    QApplication.processEvents()

    # Close the main window
    if window and window.isVisible():
        try:
            window.setVisible(False)
            window.reject()
        except:
            pass

    # Process events multiple times
    for _ in range(5):
        QApplication.processEvents()

    # Final sweep: close any lingering top-level dialogs (including hidden prompts)
    for widget in QApplication.topLevelWidgets():
        if not widget:
            continue
        try:
            if hasattr(widget, 'reject'):
                widget.reject()
            elif hasattr(widget, 'close'):
                widget.close()
            widget.setVisible(False)
        except Exception:
            pass

    QApplication.processEvents()


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


def test_import_summary_uses_errors_warnings_label(qapp, qtbot, temp_db, isolated_qsettings):
    """Status summary should display combined Errors/Warnings count label."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.update_summary(scanned=10, fixed=3, errors=2,
                          warnings=4, duplicates=1, added=5)
    status_text = window.status_bar.currentMessage()

    assert "Fixed: 3" in status_text
    assert "Errors/Warnings: 6" in status_text
    assert "Issues:" not in status_text

    # Cleanup
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
    window.scan_outcomes = (
        [
            {"status": "Added", "is_duplicate": False,
                "outcomes": ["autocorrect_used"]}
            for _ in range(6)
        ]
        + [
            {"status": "Added", "is_duplicate": False,
                "outcomes": ["fallback_used"]}
            for _ in range(2)
        ]
    )

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
    assert any((item.get("book", {}).get("title") == "Fixed Example")
               for item in window.scanned_items)
    assert not any((item.get("book", {}).get("title") == "Clean Example")
                   for item in window.scanned_items)
    assert window._summary_counts["fixed"] >= 1

    # Cleanup: use helper to close all windows properly
    cleanup_window(window)


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
    assert window.added_edit.text() == "1"
    assert window.elapsed_edit.text() == "00:05"

    cleanup_window(window)
