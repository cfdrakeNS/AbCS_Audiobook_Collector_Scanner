"""
Accessibility Event Helpers
Utility functions for emitting accessibility events that screen readers can detect.

This module properly supports screen readers by:
1. Setting accessible names/descriptions on widgets
2. Emitting proper accessibility events when content changes
3. Only emitting events when accessibility is active (QAccessible.isActive())
"""

import time

from PySide6.QtGui import QAccessible, QAccessibleEvent
from PySide6.QtWidgets import QStatusBar, QDialog, QApplication
from PySide6.QtCore import Qt
from src.accessibility.screen_reader import (
    get_screen_reader_focus_delay_ms,
    is_screen_reader_active,
)

# Guard repeated focus-based announcements per status bar.
_LAST_FOCUS_ANNOUNCE: dict[int, tuple[str, float]] = {}
_FOCUS_ANNOUNCE_DEDUP_SECONDS = 0.9
_MIN_STATUS_READ_DELAY_MS = 300


def _accessibility_announcements_enabled() -> bool:
    """True when a screen reader is likely active and should receive speech."""
    return QAccessible.isActive() or is_screen_reader_active()


def _status_bar_focus_delay_ms() -> int:
    """Delay before restoring status-bar focus; JAWS/NVDA need time to speak."""
    detected = get_screen_reader_focus_delay_ms()
    if _accessibility_announcements_enabled() and detected <= 0:
        return _MIN_STATUS_READ_DELAY_MS
    return detected


def configure_status_bar_accessibility(status_bar: QStatusBar) -> None:
    """Initialize status bar for screen readers: no generic name/description noise."""
    try:
        status_bar.setAccessibleName("")
        status_bar.setAccessibleDescription("")
        status_bar.setFocusPolicy(Qt.NoFocus)
    except Exception:
        pass


def prepare_status_bar_for_readback(
    status_bar: QStatusBar, message: str | None = None
) -> str:
    """
    Set accessible metadata so focus-based readback speaks only the status text.

    Returns the resolved message string.
    """
    try:
        resolved = (message or status_bar.currentMessage() or "").strip()
        status_bar.setAccessibleDescription("")
        status_bar.setAccessibleName(resolved)
        return resolved
    except Exception:
        return (message or "").strip()


def read_status_bar_message(
    status_bar: QStatusBar,
    fallback: str = "",
    *,
    announce_text: str | None = None,
    restore_focus: bool = True,
    update_visible: bool = True,
) -> None:
    """
    Alt+/ handler: read current status bar text with no generic SR prefixes.

    Does nothing when no screen reader is active (no popup).

    Args:
        announce_text: When set, spoken text (e.g. main-window filter summary with sort).
            Otherwise uses visible status bar message, then fallback.
        restore_focus: When False, leave focus on the status bar after readback.
        update_visible: When False, speak announce_text without changing visible status text.
    """
    if not _accessibility_announcements_enabled():
        return
    try:
        visible = (status_bar.currentMessage() or "").strip()
        if announce_text is not None:
            text = announce_text.strip() or visible or (fallback or "").strip() or "Ready"
        else:
            text = visible or (fallback or "").strip() or "Ready"
        prepare_status_bar_for_readback(status_bar, text)
        announce_status_message(
            status_bar,
            text,
            move_focus=True,
            force_focus_announce=True,
            restore_focus=restore_focus,
            update_visible=update_visible,
        )
    except Exception:
        pass


def announce_status_message(
    status_bar: QStatusBar,
    message: str,
    move_focus: bool = False,
    force_focus_announce: bool = False,
    restore_focus: bool = True,
    update_visible: bool = True,
) -> None:
    """
    Update status bar message and notify screen readers of the change.

    Uses focus manipulation which works reliably with JAWS.

    Args:
        status_bar: QStatusBar widget to update
        message: Message text to display and announce
        move_focus: If True, briefly move focus to status bar so screen readers read it
        force_focus_announce: If True, bypass duplicate-suppression for focus announcements.
        restore_focus: When False, do not return focus to the prior widget after readback.
        update_visible: When False, announce without changing the visible status bar text.
    """
    try:
        message = message or ""

        # Update the visible status bar message
        if update_visible and status_bar.currentMessage() != message:
            status_bar.showMessage(message)

        # Workaround: Briefly move focus to status bar so screen readers read the message
        # This is more reliable than QAccessibleEvent which can cause crashes
        if move_focus and _accessibility_announcements_enabled():
            prepare_status_bar_for_readback(status_bar, message)
            status_key = id(status_bar)
            now = time.monotonic()
            last_message, last_ts = _LAST_FOCUS_ANNOUNCE.get(status_key, ("", 0.0))
            if (
                not force_focus_announce
                and message == last_message
                and (now - last_ts) < _FOCUS_ANNOUNCE_DEDUP_SECONDS
            ):
                return

            _LAST_FOCUS_ANNOUNCE[status_key] = (message, now)

            # Get the currently focused widget to restore focus later
            app = QApplication.instance()
            if app:
                previous_focus = app.focusWidget()

                # Make status bar focusable temporarily
                status_bar.setFocusPolicy(Qt.StrongFocus)
                status_bar.setFocus(Qt.OtherFocusReason)
                QApplication.processEvents()
                if app.focusWidget() != status_bar:
                    event = QAccessibleEvent(status_bar, QAccessible.Event.NameChanged)
                    QAccessible.updateAccessibility(event)

                # Use a timer to restore focus after screen reader reads the message
                def restore_focus_handler():
                    try:
                        if restore_focus:
                            active_app = QApplication.instance()
                            if (
                                active_app
                                and previous_focus
                                and active_app.focusWidget() == status_bar
                            ):
                                try:
                                    previous_focus.setFocus()
                                except RuntimeError:
                                    pass
                    finally:
                        try:
                            status_bar.setFocusPolicy(Qt.NoFocus)
                        except RuntimeError:
                            pass

                from PySide6.QtCore import QTimer
                delay_ms = _status_bar_focus_delay_ms()
                if delay_ms <= 0:
                    restore_focus_handler()
                else:
                    QTimer.singleShot(delay_ms, restore_focus_handler)

    except Exception:
        # Silently fail - don't let accessibility break the app
        pass


def announce_dialog_opened(dialog: QDialog, title: str = "") -> None:
    """
    Announce that a dialog window has opened.

    Args:
        dialog: QDialog that opened
        title: Optional dialog title/description
    """
    try:
        # Set accessible name if title provided
        if title:
            dialog.setAccessibleName(title)

        # Emit event if accessibility is active
        if QAccessible.isActive():
            event = QAccessibleEvent(dialog, QAccessible.Event.DialogStart)
            QAccessible.updateAccessibility(event)
    except Exception:
        # Silently ignore errors during announcement
        pass


def announce_dialog_closed(dialog: QDialog) -> None:
    """
    Announce that a dialog window has closed.

    Args:
        dialog: QDialog that closed
    """
    try:
        # Emit event if accessibility is active
        if QAccessible.isActive():
            event = QAccessibleEvent(dialog, QAccessible.Event.DialogEnd)
            QAccessible.updateAccessibility(event)
    except Exception:
        # Silently ignore errors during announcement
        pass
