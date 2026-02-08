"""
Accessible Widget Wrappers for QAccessible Integration
Provides QAccessibleInterface implementations for custom widgets and standard Qt widgets.
Enables full accessibility support for JAWS and NVDA screen readers.
"""

from PySide6.QtGui import QAccessible, QAccessibleInterface, QAccessibleEvent
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QDialog, QWidget, QStatusBar
from PySide6.QtCore import Qt, QObject
from typing import Optional, List


class AccessibleTable(QAccessibleInterface):
    """
    Provides accessibility support for QTableWidget.
    Exposes table structure, cell contents, and selection state to screen readers.
    """

    def __init__(self, table: QTableWidget):
        """
        Initialize accessible table wrapper.

        Args:
            table: QTableWidget to wrap
        """
        super().__init__()
        self.table = table
        self.object_ref = table

    def isValid(self) -> bool:
        """Check if the wrapped object is still valid."""
        return self.table is not None and not self.table.isHidden()

    def object(self) -> QObject:
        """Return the wrapped widget."""
        return self.table

    def role(self, child: int = 0) -> QAccessible.Role:
        """
        Return the role of the object.

        Args:
            child: Child index (0 = widget itself)

        Returns:
            QAccessible.Role for the object
        """
        return QAccessible.Table

    def text(self, t: QAccessible.Text, child: int = 0) -> str:
        """
        Return text for the object.

        Args:
            t: Type of text (Name, Description, Value, etc.)
            child: Child index

        Returns:
            Localized text string
        """
        if child == 0:
            if t == QAccessible.Name:
                return self.table.accessibleName() or "Table"
            elif t == QAccessible.Description:
                return f"Table with {self.table.rowCount()} rows and {self.table.columnCount()} columns"
            elif t == QAccessible.Value:
                selected = self.table.selectedIndexes()
                if selected:
                    return f"{len(set(idx.row() for idx in selected))} rows selected"
                return "No selection"
        return ""

    def rect(self, child: int = 0) -> tuple:
        """Return screen coordinates of the widget or child."""
        if child == 0:
            geom = self.table.geometry()
            return (geom.x(), geom.y(), geom.width(), geom.height())
        return (0, 0, 0, 0)

    def childCount(self) -> int:
        """Return number of children (none exposed to avoid incomplete child interfaces)."""
        return 0

    def indexOfChild(self, child: 'QAccessibleInterface') -> int:
        """Return the index of a child interface."""
        return -1

    def parent(self) -> Optional['QAccessibleInterface']:
        """Return parent interface."""
        return None

    def child(self, index: int) -> Optional['QAccessibleInterface']:
        """Return child at given index."""
        return None

    def state(self, child: int = 0) -> QAccessible.State:
        """Return the state of the object."""
        if child == 0:
            state = QAccessible.State()
            state.focusable = True
            state.focused = self.table.hasFocus()
            state.enabled = self.table.isEnabled()
            return state
        return QAccessible.State()


class AccessibleStatusBar(QAccessibleInterface):
    """
    Provides accessibility support for QStatusBar.
    Exposes status messages to screen readers as they change.
    """

    def __init__(self, status_bar: QStatusBar):
        """
        Initialize accessible status bar wrapper.

        Args:
            status_bar: QStatusBar to wrap
        """
        super().__init__()
        self.status_bar = status_bar
        self.object_ref = status_bar

    def isValid(self) -> bool:
        """Check if the wrapped object is still valid."""
        return self.status_bar is not None

    def object(self) -> QObject:
        """Return the wrapped widget."""
        return self.status_bar

    def role(self, child: int = 0) -> QAccessible.Role:
        """Return the role - Status Bar is an informational text area."""
        return QAccessible.Statusbar

    def text(self, t: QAccessible.Text, child: int = 0) -> str:
        """
        Return text for the status bar.

        Args:
            t: Type of text (Name, Description, Value, etc.)
            child: Child index

        Returns:
            Current status message or metadata
        """
        if child == 0:
            if t == QAccessible.Name:
                return self.status_bar.accessibleName() or "Status"
            elif t == QAccessible.Description:
                return self.status_bar.accessibleDescription() or "Application status"
            elif t == QAccessible.Value:
                # Get all permanent widgets and their messages
                messages = []
                for i in range(self.status_bar.layout().count()):
                    widget = self.status_bar.layout().itemAt(i).widget()
                    if hasattr(widget, 'text'):
                        text = widget.text()
                        if text:
                            messages.append(text)
                return " ".join(messages) if messages else "Ready"
        return ""

    def rect(self, child: int = 0) -> tuple:
        """Return screen coordinates of the widget."""
        if child == 0:
            geom = self.status_bar.geometry()
            return (geom.x(), geom.y(), geom.width(), geom.height())
        return (0, 0, 0, 0)

    def childCount(self) -> int:
        """Status bar has no children in accessibility tree."""
        return 0

    def indexOfChild(self, child: 'QAccessibleInterface') -> int:
        """Return the index of a child interface."""
        return -1

    def parent(self) -> Optional['QAccessibleInterface']:
        """Return parent interface."""
        return None

    def child(self, index: int) -> Optional['QAccessibleInterface']:
        """Return child at given index."""
        return None

    def state(self, child: int = 0) -> QAccessible.State:
        """Return the state of the object."""
        if child == 0:
            state = QAccessible.State()
            state.enabled = True
            return state
        return QAccessible.State()


class AccessibleFormDialog(QAccessibleInterface):
    """
    Provides accessibility support for form dialogs.
    Exposes form structure and field relationships to screen readers.
    """

    def __init__(self, dialog: QDialog):
        """
        Initialize accessible form dialog wrapper.

        Args:
            dialog: QDialog (form) to wrap
        """
        super().__init__()
        self.dialog = dialog
        self.object_ref = dialog

    def isValid(self) -> bool:
        """Check if the wrapped object is still valid."""
        return self.dialog is not None and not self.dialog.isHidden()

    def object(self) -> QObject:
        """Return the wrapped widget."""
        return self.dialog

    def role(self, child: int = 0) -> QAccessible.Role:
        """Return the role - Dialog is a container."""
        if child == 0:
            return QAccessible.Dialog
        return QAccessible.EditableText

    def text(self, t: QAccessible.Text, child: int = 0) -> str:
        """
        Return text for the dialog or field.

        Args:
            t: Type of text (Name, Description, Value, etc.)
            child: Child index

        Returns:
            Dialog title, description, or field value
        """
        if child == 0:
            if t == QAccessible.Name:
                return self.dialog.windowTitle()
            elif t == QAccessible.Description:
                return self.dialog.accessibleDescription() or "Form dialog"
        return ""

    def rect(self, child: int = 0) -> tuple:
        """Return screen coordinates of the widget."""
        if child == 0:
            geom = self.dialog.geometry()
            return (geom.x(), geom.y(), geom.width(), geom.height())
        return (0, 0, 0, 0)

    def childCount(self) -> int:
        """Return number of form fields."""
        form_layout = None
        for widget in self.dialog.findChildren(QWidget):
            layout = getattr(widget, 'layout', lambda: None)()
            if hasattr(layout, 'rowCount'):
                form_layout = layout
                break
        if form_layout and hasattr(form_layout, 'rowCount'):
            return form_layout.rowCount()
        return 0

    def indexOfChild(self, child: 'QAccessibleInterface') -> int:
        """Return the index of a child interface."""
        return -1

    def parent(self) -> Optional['QAccessibleInterface']:
        """Return parent interface."""
        return None

    def child(self, index: int) -> Optional['QAccessibleInterface']:
        """Return child at given index."""
        return None

    def state(self, child: int = 0) -> QAccessible.State:
        """Return the state of the object."""
        if child == 0:
            state = QAccessible.State()
            state.focusable = True
            state.focused = self.dialog.hasFocus()
            state.enabled = True
            return state
        return QAccessible.State()


def register_accessible_widgets():
    """
    Register all custom accessible widget implementations with Qt.
    Call this once during application startup.
    """
    # Install accessibility factories for our custom widgets
    # These allow Qt to instantiate our QAccessibleInterface implementations
    QAccessible.installFactory(AccessibleTableFactory)
    QAccessible.installFactory(AccessibleStatusBarFactory)
    QAccessible.installFactory(AccessibleFormDialogFactory)


def AccessibleTableFactory(key: str, obj: QObject) -> Optional[QAccessibleInterface]:
    """Factory function for creating AccessibleTable instances."""
    if isinstance(obj, QTableWidget):
        return AccessibleTable(obj)
    return None


def AccessibleStatusBarFactory(key: str, obj: QObject) -> Optional[QAccessibleInterface]:
    """Factory function for creating AccessibleStatusBar instances."""
    if isinstance(obj, QStatusBar):
        return AccessibleStatusBar(obj)
    return None


def AccessibleFormDialogFactory(key: str, obj: QObject) -> Optional[QAccessibleInterface]:
    """Factory function for creating AccessibleFormDialog instances."""
    if isinstance(obj, QDialog):
        return AccessibleFormDialog(obj)
    return None
