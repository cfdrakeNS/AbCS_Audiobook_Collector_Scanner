"""Verify Title sort appears in the main window filter summary."""

from __future__ import annotations

import pytest

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.ui.main_window import MainWindow


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
