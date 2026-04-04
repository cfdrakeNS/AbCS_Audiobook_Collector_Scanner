"""
Accessibility Event Helpers
Utility functions for emitting accessibility events that screen readers can detect.

This module properly supports screen readers by:
1. Setting accessible names/descriptions on widgets
2. Emitting proper accessibility events when content changes
3. Only emitting events when accessibility is active (QAccessible.isActive())
"""

from PySide6.QtGui import QAccessible, QAccessibleEvent
from PySide6.QtWidgets import QWidget, QTableWidget, QStatusBar, QDialog, QApplication, QLabel
from PySide6.QtCore import Qt


# Global announcement widget for screen readers
_announcement_widget = None


def get_announcement_widget(parent=None):
    """
    Get or create a hidden label widget that screen readers use for announcements.

    Screen readers can reliably read this widget when its accessible name/description changes.
    This is more reliable than QAccessibleAnnouncementEvent.

    Args:
        parent: Parent widget to attach to

    Returns:
        QLabel widget for announcements
    """
    global _announcement_widget

    if _announcement_widget is None and parent is not None:
        _announcement_widget = QLabel(parent)
        _announcement_widget.setObjectName("AccessibilityAnnouncement")
        _announcement_widget.setAccessibleName("Announcement")
        _announcement_widget.setVisible(False)
        _announcement_widget.setStyleSheet(
            "color: transparent; background: transparent;")

    return _announcement_widget


def check_accessibility_support() -> dict:
    """
    Diagnostic function to verify accessibility is properly set up.

    Returns:
        Dictionary with accessibility status and diagnostics
    """
    results = {
        'isActive': QAccessible.isActive(),
        'has_app': False,
        'app_has_interface': False,
        'app_role': None,
        'app_name': None,
    }

    app = QApplication.instance()
    if app:
        results['has_app'] = True
        iface = QAccessible.queryAccessibleInterface(app)
        if iface:
            results['app_has_interface'] = True
            results['app_role'] = str(iface.role())
            results['app_name'] = iface.text(QAccessible.Text.Name)

    return results


def announce_status_message(status_bar: QStatusBar, message: str, announcement_widget=None, move_focus: bool = False) -> None:
    """
    Update status bar message and notify screen readers of the change.

    Uses a dedicated announcement widget which screen readers read more reliably.

    Args:
        status_bar: QStatusBar widget to update
        message: Message text to display and announce
        announcement_widget: Optional hidden label for announcements (created if not provided)
        move_focus: If True, briefly move focus to status bar so screen readers read it (workaround for event crashes)
    """
    try:
        # Update the visible status bar message
        status_bar.showMessage(message)

        # Set accessible name for when user navigates to status bar
        status_bar.setAccessibleName(message)
        status_bar.setAccessibleDescription(message)

        # Workaround: Briefly move focus to status bar so screen readers read the message
        # This is more reliable than QAccessibleEvent which can cause crashes
        if move_focus and QAccessible.isActive():
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
                        if active_app and previous_focus and active_app.focusWidget() == status_bar:
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


def announce_table_selection(table: QTableWidget, row: int, col: int, message: str = "") -> None:
    """
    Announce table cell or row selection to screen readers.

    Args:
        table: QTableWidget being navigated
        row: Row index of selected cell
        col: Column index of selected cell
        message: Optional additional message to append
    """
    try:
        # Build cell reference with header and value
        header_text = table.horizontalHeaderItem(
            col).text() if col < table.columnCount() else "Column"
        cell_item = table.item(row, col)
        cell_value = cell_item.text() if cell_item else "blank"

        # Set accessible description with selection info
        selection_info = f"Row {row}, {header_text}: {cell_value}"
        if message:
            selection_info += f". {message}"
        table.setAccessibleDescription(selection_info)

        # Emit event if accessibility is active
        if QAccessible.isActive():
            event = QAccessibleEvent(table, QAccessible.Event.Selection)
            QAccessible.updateAccessibility(event)
    except Exception:
        # Silently ignore errors during announcement
        pass


def announce_table_action(table: QTableWidget, action_type: str, count: int = 0) -> None:
    """
    Announce table actions (selection, deletion, etc.) to screen readers.

    Args:
        table: QTableWidget being modified
        action_type: Type of action ('select', 'delete', 'add', etc.)
        count: Number of items affected
    """
    try:
        # Set accessible description with action info
        action_desc = f"{action_type.capitalize()} action"
        if count > 0:
            action_desc += f": {count} item(s)"
        table.setAccessibleDescription(action_desc)

        # Emit event if accessibility is active
        if QAccessible.isActive():
            event = QAccessibleEvent(table, QAccessible.Event.Selection)
            QAccessible.updateAccessibility(event)
    except Exception:
        # Silently ignore errors during announcement
        pass


def announce_form_field(field: QWidget, field_name: str, field_value: str) -> None:
    """
    Announce form field change to screen readers.

    Args:
        field: Form field widget (QLineEdit, QComboBox, etc.)
        field_name: Readable name of the field
        field_value: Current value of the field
    """
    try:
        # Set accessible name and description
        field.setAccessibleName(field_name)
        field.setAccessibleDescription(f"Current value: {field_value}")

        # Emit event if accessibility is active
        if QAccessible.isActive():
            event = QAccessibleEvent(field, QAccessible.Event.ValueChanged)
            QAccessible.updateAccessibility(event)
    except Exception:
        # Silently ignore errors during announcement
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


def announce_focus_change(widget: QWidget, widget_name: str = "") -> None:
    """
    Announce focus change to screen readers.

    Args:
        widget: Widget that received focus
        widget_name: Optional readable name of widget
    """
    try:
        # Set accessible name if provided
        if widget_name:
            widget.setAccessibleName(widget_name)

        # Emit event if accessibility is active
        if QAccessible.isActive():
            event = QAccessibleEvent(widget, QAccessible.Event.Focus)
            QAccessible.updateAccessibility(event)
    except Exception:
        # Silently ignore errors during announcement
        pass
