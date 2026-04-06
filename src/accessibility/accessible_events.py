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

# Guard repeated focus-based announcements per status bar.
_LAST_FOCUS_ANNOUNCE: dict[int, tuple[str, float]] = {}
_FOCUS_ANNOUNCE_DEDUP_SECONDS = 0.9


def announce_status_message(
    status_bar: QStatusBar,
    message: str,
    _announcement_widget=None,
    move_focus: bool = False,
    force_focus_announce: bool = False,
) -> None:
    """
    Update status bar message and notify screen readers of the change.

    Uses a dedicated announcement widget which screen readers read more reliably.

    Args:
        status_bar: QStatusBar widget to update
        message: Message text to display and announce
        announcement_widget: Optional hidden label for announcements (created if not provided)
        move_focus: If True, briefly move focus to status bar so screen readers read it (workaround for event crashes)
        force_focus_announce: If True, bypass duplicate-suppression for focus announcements.
    """
    try:
        message = message or ""

        # Update the visible status bar message
        if status_bar.currentMessage() != message:
            status_bar.showMessage(message)

        # Workaround: Briefly move focus to status bar so screen readers read the message
        # This is more reliable than QAccessibleEvent which can cause crashes
        if move_focus and QAccessible.isActive():
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
                status_bar.setFocus()

                # Use a timer to restore focus after screen reader reads the message
                def restore_focus():
                    try:
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

                # Restore focus after 300ms (time for screen reader to read)
                from PySide6.QtCore import QTimer

                QTimer.singleShot(300, restore_focus)

        # TEMPORARILY DISABLED - QAccessibleEvent may be causing crashes
        # if announcement_widget is not None:
        #     # Change the accessible text - screen reader will announce this
        #     announcement_widget.setAccessibleName(message)
        #     announcement_widget.setAccessibleDescription(message)
        #     announcement_widget.setText(message)

        #     # Update accessibility to notify screen readers
        #     if QAccessible.isActive():
        #         try:
        #             event = QAccessibleEvent(
        #                 announcement_widget, QAccessible.Event.ValueChanged)
        #             QAccessible.updateAccessibility(event)
        #         except Exception:
        #             pass
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
