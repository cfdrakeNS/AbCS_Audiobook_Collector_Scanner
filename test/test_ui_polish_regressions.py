"""Regression tests for July 19 UI polish changes.

Covers:
- Help window Enter no longer triggering zoom out (auto-default buttons)
- Table polish cell borders (with opt-out for list-style tables)
- Primary buttons: bold only, no standing highlight border
- Theme-derived Mid color visible on dark themes
- Import window gating of Add Selected / Export / error filter
- Book List Import gating of Export Errors
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import (
    build_modern_button_style,
    build_table_polish_style,
)
from src.accessibility.theme_manager import ThemeManager, ThemeName
from src.ui.book_list_import_window import BookListImportWindow
from src.ui.help_window import HelpWindow
from src.ui.import_window import ImportWindow


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


def _close(window):
    """Force-close a window and flush events, mirroring cleanup_window."""
    if hasattr(window, "_clear_dirty"):
        window._clear_dirty()
    if hasattr(window, "_closing_via_handler"):
        window._closing_via_handler = True
    if hasattr(window, "progress_window") and window.progress_window is not None:
        window.progress_window.setVisible(False)
        window.progress_window.close()
        window.progress_window = None
    window.setVisible(False)
    if hasattr(window, "reject"):
        window.reject()
    else:
        window.close()
    # Fully destroy the window so pending singleShot timers and event
    # filters cannot fire against a half-torn-down widget at interpreter
    # exit (observed 0xC0000409 with HelpWindow + ImportWindow otherwise).
    window.deleteLater()
    for _ in range(5):
        QApplication.processEvents()
    QApplication.sendPostedEvents()


def _extract_block(style: str, header: str) -> str:
    """Return the rule body following the first occurrence of header."""
    start = style.index(header)
    open_brace = style.index("{", start)
    close_brace = style.index("}", open_brace)
    return style[open_brace : close_brace + 1]


# --- Help window: Enter must not activate zoom out ---


def test_help_window_buttons_not_auto_default(qapp, isolated_qsettings):
    scaler = UIScaler(qapp)
    window = HelpWindow(scaler)
    try:
        for button in (
            window.zoom_out_button,
            window.zoom_in_button,
            window.close_button,
        ):
            assert button.autoDefault() is False
            assert button.isDefault() is False
    finally:
        _close(window)


# --- Shared table polish: cell borders with opt-out ---


def test_table_polish_default_has_cell_borders():
    style = build_table_polish_style("QTableView")
    item_block = _extract_block(style, "QTableView::item")
    assert "border: 1px solid palette(mid);" in item_block


def test_table_polish_cell_borders_opt_out():
    style = build_table_polish_style("QTableWidget", cell_borders=False)
    item_block = _extract_block(style, "QTableWidget::item")
    assert "border: none;" in item_block
    assert "palette(mid)" not in item_block


# --- Primary buttons: bold only, no standing highlight border ---


def test_primary_button_style_is_bold_without_border():
    style = build_modern_button_style(20)
    primary_block = _extract_block(style, "QPushButton#primaryActionButton")
    assert "font-weight: bold" in primary_block
    assert "border" not in primary_block


# --- Theme Mid role: gridlines visible on dark and light themes ---


@pytest.mark.parametrize(
    "theme_enum",
    [
        ThemeName.DARK,
        ThemeName.HIGH_CONTRAST_DARK,
        ThemeName.OCEANIC_DARK,
        ThemeName.HIGH_CONTRAST_LIGHT,
    ],
)
def test_derived_mid_color_contrasts_with_base(qapp, theme_enum):
    theme = ThemeManager.THEMES[theme_enum]
    palette = theme.apply_to_palette(QPalette())
    mid = ThemeManager._derive_mid_color(palette)
    base = palette.color(QPalette.Base)
    assert abs(mid.lightness() - base.lightness()) >= 40


# --- Import window: gate Add Selected, Export, and error filter ---


def test_import_window_action_buttons_gated(qapp, temp_db, isolated_qsettings):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportWindow(temp_db, scaler, theme_manager)
    try:
        # Fresh window: nothing scanned yet
        assert not window.import_selected_button.isEnabled()
        assert not window.export_button.isEnabled()
        assert not window.error_filter_combo.isEnabled()

        # Scan produced only clean rows: buttons enable, filter stays off
        window.scanned_items = [{"status": "OK", "errors": [], "book": {}}]
        window._update_action_buttons_enabled()
        assert window.import_selected_button.isEnabled()
        assert window.export_button.isEnabled()
        assert not window.error_filter_combo.isEnabled()

        # Scan produced an issue: filter enables
        window.scanned_items = [
            {"status": "Warning", "errors": ["W: year missing"], "book": {}}
        ]
        window._update_action_buttons_enabled()
        assert window.error_filter_combo.isEnabled()

        # Filter set to Warning, then issues disappear: reset to All + disable
        warning_index = window.error_filter_combo.findData("warning")
        assert warning_index >= 0
        window.error_filter_combo.setCurrentIndex(warning_index)
        window.scanned_items = []
        window._update_action_buttons_enabled()
        assert not window.error_filter_combo.isEnabled()
        assert window.error_filter_combo.currentData() == "all"
        assert not window.import_selected_button.isEnabled()
        assert not window.export_button.isEnabled()
    finally:
        _close(window)


# --- Book List Import: Export Errors gated on errors existing ---


def test_book_list_import_export_errors_starts_disabled(
    qapp, temp_db, isolated_qsettings
):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = BookListImportWindow(temp_db, scaler, theme_manager)
    try:
        assert not window.export_button.isEnabled()
        assert window.import_button.isEnabled()
    finally:
        _close(window)
