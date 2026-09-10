"""Tests for initial focus on book list import and preferences windows."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QComboBox, QLabel, QScrollArea

from src.ui.book_list_import_window import BookListImportWindow
from src.ui.preferences_window import PreferencesWindow

pandas = pytest.importorskip("pandas")

def test_book_list_import_opens_with_collection_focus(qapp, temp_db, ui_scaler, theme_manager):
    window = BookListImportWindow(temp_db, ui_scaler, theme_manager)
    window.show()
    qapp.processEvents()
    assert isinstance(window.focusWidget(), QComboBox)
    assert window.focusWidget() is window.collection_combo
    window.close()

def test_preferences_tab_descriptions_are_tab_focusable(qapp, ui_scaler, theme_manager):
    window = PreferencesWindow(ui_scaler, theme_manager)
    assert len(window._tab_description_labels) == 4
    for label in window._tab_description_labels.values():
        assert isinstance(label, QLabel)
        assert label.focusPolicy() == Qt.TabFocus
        assert label.objectName() == "preferencesTabDescription"
        assert "palette(base)" in label.styleSheet()
    window.close()

def test_preferences_show_event_focuses_tab_description(qapp, ui_scaler, theme_manager):
    window = PreferencesWindow(ui_scaler, theme_manager)
    window.show()
    qapp.processEvents()
    focused = window.focusWidget()
    assert focused in window._tab_description_labels.values()
    window.close()

def test_preferences_tab_from_blurb_reaches_first_control(qapp, ui_scaler, theme_manager):
    window = PreferencesWindow(ui_scaler, theme_manager)
    window.show()
    qapp.processEvents()

    cases = (
        (PreferencesWindow.TAB_DISPLAY, window.preset_combo),
        (PreferencesWindow.TAB_IMPORT, window.import_dir_edit),
        (PreferencesWindow.TAB_FALLBACK, window.author_fallback_checkbox),
        (PreferencesWindow.TAB_VALIDATION, window.rules_section_text),
    )
    for tab_index, expected in cases:
        window.tab_widget.setCurrentIndex(tab_index)
        window._focus_tab_description(tab_index)
        qapp.processEvents()
        assert window.focusWidget() is window._tab_description_labels[tab_index]
        QTest.keyClick(window, Qt.Key_Tab)
        qapp.processEvents()
        assert window.focusWidget() is expected
        assert not isinstance(window.focusWidget(), QScrollArea)

    window.close()
