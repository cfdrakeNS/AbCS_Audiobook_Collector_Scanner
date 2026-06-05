"""Book details accessibility: status readback and idle status text."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.database.connection import DatabaseManager
from src.database.queries import BookQueries
from src.ui.book_details import BookDetailsWindow

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def temp_db(tmp_path):
    data_dir = Path(PROJECT_ROOT) / "data"
    source_db = next((data_dir / name for name in ("abcs.db", "wh abcs.db") if (data_dir / name).exists()), None)
    if source_db is None:
        pytest.skip("No test database available")
    target_db = tmp_path / "abcs_test.db"
    shutil.copy2(source_db, target_db)
    db = DatabaseManager(str(target_db))
    try:
        yield db
    finally:
        db.close()


def test_idle_status_includes_title_and_author(qapp, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    books = BookQueries(temp_db).get_all()
    if not books:
        pytest.skip("No books in test database")

    window = BookDetailsWindow(
        temp_db,
        scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    message = window._idle_status_message()
    assert message.endswith(".")
    assert " by " in message
    assert window.status_bar.currentMessage() == message
    window.close()


def test_status_bar_has_no_sighted_tooltip(qapp, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    books = BookQueries(temp_db).get_all()
    if not books:
        pytest.skip("No books in test database")

    window = BookDetailsWindow(
        temp_db,
        scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.status_bar.toolTip() == ""
    window.close()


def test_page_navigation_focuses_title(qapp, temp_db, monkeypatch):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    books = BookQueries(temp_db).get_all()
    if len(books) < 2:
        pytest.skip("Need at least two books in test database")

    window = BookDetailsWindow(
        temp_db,
        scaler,
        book=books[0],
        books_list=books,
        current_index=0,
        parent=None,
        theme_manager=theme_manager,
    )
    focus_calls = []

    def track_focus(reason=Qt.OtherFocusReason):
        focus_calls.append(reason)

    monkeypatch.setattr(window.title_edit, "setFocus", track_focus)
    monkeypatch.setattr(
        "src.ui.book_details.QTimer.singleShot",
        lambda _ms, fn: fn(),
    )

    window.on_next()
    assert focus_calls
    assert window.title_edit.text() == books[1].title
    window.close()
