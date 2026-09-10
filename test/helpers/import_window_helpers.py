"""Shared helpers for Import window UI tests."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from src.ui.import_progress_window import ImportProgressWindow
from src.ui.import_window import ImportWindow


def apply_suppress_import_confirmations(monkeypatch, *, patch_progress_close: bool = True):
    """Patch Import window close/cancel prompts for automated teardown."""
    monkeypatch.setattr(ImportWindow, "_confirm_close_window", lambda self: True)
    monkeypatch.setattr(ImportWindow, "_confirm_cancel_scan", lambda self: True)

    if not patch_progress_close:
        return

    def _progress_close_without_prompt(self, event):
        # Failed asserts tear down via qtbot before cleanup_window; never block.
        self._scan_active = False
        self._cancel_requested = True
        type(self).__bases__[0].closeEvent(self, event)

    monkeypatch.setattr(
        ImportProgressWindow, "closeEvent", _progress_close_without_prompt
    )


@pytest.fixture
def suppress_import_confirmations(monkeypatch):
    """Opt-in fixture; prefer module-local autouse wrappers that call this."""
    apply_suppress_import_confirmations(monkeypatch)



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


def configure_mass_standard_scan(window, *, trim_whitespace: bool | None = None):
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


# Back-compat alias used by moved scan-flow tests
_configure_mass_standard_scan = configure_mass_standard_scan
