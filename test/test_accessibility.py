"""Pytest coverage for minimal accessibility window behavior."""

import os
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "test"))

try:
    from accessibility_test_window import MinimalTestWindow
except ModuleNotFoundError:
    from src.ui.accessibility_test_window import MinimalTestWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def window(qapp):
    dlg = MinimalTestWindow()
    yield dlg
    dlg.close()


def test_minimal_accessibility_window_constructs(window):
    assert window.windowTitle() == "Accessibility Test Window"
    assert window.accessibleName() == "Accessibility Test Window"
    assert hasattr(window, "status_bar")


def test_minimal_accessibility_shortcuts_are_registered(window):
    assert hasattr(window, "help_shortcut")
    assert hasattr(window, "read_status_shortcut")
    assert hasattr(window, "close_shortcut")


def test_minimal_accessibility_set_status_updates_status_bar(window):
    message = "Ready for accessibility test"
    window.set_status(message, announce=False)
    assert window.status_bar.currentMessage() == message
