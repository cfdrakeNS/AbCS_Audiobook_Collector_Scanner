from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton, QDateEdit
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QIcon


from PySide6.QtCore import Signal


class AccessibleDateField(QWidget):

    date_changed = Signal()

    def minimum_date(self):
        # Mimic QDateEdit minimumDate for compatibility
        return QDate(1, 1, 1)

    def set_tab_order(self):
        # Call this after the widget is parented in the window
        QWidget.setTabOrder(self.display, self.button)

    class CalendarButton(QToolButton):
        def __init__(self, parent, open_dialog_func):
            super().__init__(parent)
            self.open_dialog_func = open_dialog_func

        def keyPressEvent(self, event):
            if event.key() in (0x01000004, 0x20):  # Qt.Key_Enter/Return or Qt.Key_Space
                self.open_dialog_func()
                event.accept()
            else:
                super().keyPressEvent(event)

    """
    A composite widget: blank QLineEdit for display, QDateEdit popup for input.
    Shows blank for null, and only announces a date if set.
    """

    def update_display(self):
        """Update the display field to show the current date or blank."""
        if self._date:
            self.display.setText(self._date.toString("yyyy-MM-dd"))
        else:
            self.display.setText("")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(150)
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAccessibleName("Date read")
        self.display.setPlaceholderText("")
        self.display.setMinimumWidth(120)
        self.display.setMaximumWidth(180)
        self.display.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.display.setVisible(True)
        self.display.setEnabled(True)
        self.setMinimumWidth(140)
        self.setMaximumWidth(220)
        self.setVisible(True)
        self.setEnabled(True)
        # Only composite widget is focusable
        self.display.setFocusPolicy(Qt.NoFocus)
        self.setFocusPolicy(Qt.StrongFocus)

    def focusInEvent(self, event):
        # When the composite widget gets focus (Tab or Alt+E), show a visual cue and allow Alt+Down
        self.setStyleSheet("border: 2px solid #0078d7;")  # Optional: highlight border
        QWidget.focusInEvent(self, event)

    def focusOutEvent(self, event):
        # Remove visual cue when focus leaves
        self.setStyleSheet("")
        QWidget.focusOutEvent(self, event)
        # Add accessible description with shortcut info
        self.display.setAccessibleDescription(
            "Press Alt+Down to open calendar.")
        self.button = self.CalendarButton(self, self.show_calendar_dialog)
        self.button.setText("…")
        self.button.setAccessibleName("Open calendar")
        self.button.setFocusPolicy(Qt.NoFocus)  # Remove from tab order
        self.setFocusPolicy(Qt.TabFocus)
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.show_calendar_dialog)
        self._date = None
        self.update_display()

        # Force visibility and update to ensure field is always shown
        self.display.setVisible(True)
        self.setVisible(True)
        self.display.update()
        self.update()
        self.repaint()

        # Add keyboard shortcut for calendar (Alt+Down only) -- only if focused in composite widget
        from PySide6.QtGui import QKeySequence, QShortcut
        shortcut = QShortcut(QKeySequence("Alt+Down"), self)
        shortcut.activated.connect(self._on_alt_down)

    def _on_alt_down(self):
        # Only open calendar if the composite widget has focus
        if self.hasFocus():
            self.show_calendar_dialog()

    def show_calendar_dialog(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QCalendarWidget
        dlg = QDialog(self)
        dlg.setWindowTitle("Pick Date Read")
        layout = QVBoxLayout(dlg)
        cal = QCalendarWidget(dlg)
        cal.setGridVisible(True)
        if self._date:
            cal.setSelectedDate(self._date)
        layout.addWidget(cal)
        # Apply accessible styling to calendar
        try:
            font = cal.font()
            font.setPointSize(14)
            cal.setFont(font)
        except Exception:
            pass

        # Accept dialog immediately when a date is activated (Enter or double-click)
        cal.activated.connect(dlg.accept)
        dlg.setLayout(layout)
        cal.setFocus()  # Ensure calendar gets focus for keyboard navigation
        if dlg.exec() == QDialog.Accepted:
            picked = cal.selectedDate()
            self._date = picked
            self.display.setText(picked.toString("yyyy-MM-dd"))
            self.date_changed.emit()
        # else: do not change

    # No longer needed: on_date_changed

    def set_date(self, date):
        if date:
            if isinstance(date, QDate):
                self._date = date
            else:
                self._date = QDate(date.year, date.month, date.day)
            self.display.setText(self._date.toString("yyyy-MM-dd"))
        else:
            self._date = None
            self.display.setText("")
        self.date_changed.emit()

    def date(self):
        return self._date

    def clear(self):
        self.set_date(None)
