"""Verify Title sort appears in the main window filter summary."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.database.connection import DatabaseManager
from src.ui.main_window import MainWindow

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def temp_db(tmp_path):
    data_dir = Path(PROJECT_ROOT) / "data"
    candidates = [data_dir / "abcs.db", data_dir / "wh abcs.db"]
    source_db = next((path for path in candidates if path.exists()), None)
    if source_db is None:
        pytest.skip("No test database available")
    target_db = tmp_path / "abcs_test.db"
    shutil.copy2(source_db, target_db)
    db = DatabaseManager(str(target_db))
    try:
        yield db
    finally:
        db.close()


def test_default_title_sort_shows_on_startup(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    text = window.filter_summary_label.text()
    assert "Sort: Title" in text, text
    assert window._active_sort_key == "Title"

    window.close()


def test_title_sort_shows_in_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.on_order_changed("Author")
    assert "Sort: Author, Year, Title" in window.filter_summary_label.text()

    window.on_order_changed("Title")
    text = window.filter_summary_label.text()
    assert "Sort: Title" in text, text
    assert window._active_sort_key == "Title"

    window.close()


def test_title_sort_after_time_sort_shows_in_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window._sort_actions_by_key["Time"].trigger()
    assert window._active_sort_key == "Time"
    assert "Sort: Time" in window.filter_summary_label.text()

    window.on_order_changed("Title")
    text = window.filter_summary_label.text()
    assert "Sort: Time" not in text, text
    assert "Sort: Title" in text, text
    assert window._active_sort_key == "Title"

    window.close()
