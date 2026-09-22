"""Dialog for Help → Check for updates."""

from __future__ import annotations

from PySide6.QtCore import Qt, QObject, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from src.core.update_check import UpdateCheckResult, check_for_update, result_message
from src.ui.accessible_dialog import AccessibleDialog


class UpdateCheckWorker(QObject):
    """Runs the GitHub version check off the GUI thread."""

    finished = Signal(object)

    @Slot()
    def run(self) -> None:
        self.finished.emit(check_for_update())


class UpdateCheckDialog(AccessibleDialog):
    """Shows the check result. Open website is the default when an update exists."""

    help_doc_override = "01_overview.md"
    OPEN_PAGE = 1

    def __init__(self, result: UpdateCheckResult, scaler, parent=None):
        from src.accessibility.icon_helper import (
            apply_decorative_action_icon,
            get_app_icon,
        )
        from src.accessibility.style_helpers import build_modern_button_style

        super().__init__(parent)
        self.scaler = scaler
        self.setWindowIcon(get_app_icon())
        self._result = result
        self._message = result_message(result)
        self.browser_opened = False
        update_available = bool(result.ok and result.update_available)

        self.setWindowTitle("Check for updates")
        self.setAccessibleName("Check for updates")
        self.setAccessibleDescription(self._message)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        app = QApplication.instance()
        if app is not None:
            self.setFont(app.font())

        self.setStyleSheet(
            """
            QDialog {
                background-color: palette(window);
                color: palette(window-text);
            }
            QLabel {
                color: palette(window-text);
                background: transparent;
            }
            """
        )

        layout = QVBoxLayout(self)
        margin = scaler.get_scaled_size(12)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(scaler.get_scaled_size(8))
        layout.setSizeConstraint(QLayout.SetFixedSize)

        self._message_label = QLabel(self._message)
        message = self._message_label
        message.setWordWrap(True)
        text_width = max(scaler.get_scaled_size(420), 360)
        message.setFixedWidth(text_width)
        if app is not None:
            message.setFont(app.font())
        wrapped = message.fontMetrics().boundingRect(
            0, 0, text_width, 400, int(Qt.TextWordWrap), self._message
        )
        message.setFixedHeight(max(wrapped.height() + 4, message.fontMetrics().lineSpacing()))
        message.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        message.setFocusPolicy(Qt.TabFocus)
        message.setAccessibleName(self._message)
        message.setAccessibleDescription("Update check result")
        layout.addWidget(message)

        buttons = QHBoxLayout()
        scaled_height = max(scaler.get_scaled_size(20), 18)
        button_style = build_modern_button_style(scaled_height)

        self.open_button = QPushButton("Open website")
        self.open_button.setAccessibleName("Open website")
        self.open_button.setAccessibleDescription(
            f"{self._message} Opens the AbCS test site."
        )
        self.open_button.setStyleSheet(button_style)
        self.open_button.clicked.connect(self._open_page)
        apply_decorative_action_icon(self.open_button, "browse", scaler)

        self.close_button = QPushButton("Close")
        self.close_button.setAccessibleName("Close")
        self.close_button.setAccessibleDescription(self._message)
        self.close_button.setStyleSheet(button_style)
        self.close_button.clicked.connect(self.reject)
        apply_decorative_action_icon(self.close_button, "close", scaler)

        buttons.addStretch(1)
        buttons.addWidget(self.open_button)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

        primary = self.open_button if update_available else self.close_button
        secondary = self.close_button if update_available else self.open_button
        primary.setObjectName("primaryActionButton")
        primary.setDefault(True)
        secondary.setDefault(False)
        # Enter must activate the focused button. A non-auto button loses Enter to Close.
        self.open_button.setAutoDefault(True)
        self.close_button.setAutoDefault(True)
        if app is not None:
            primary.setFont(app.font())
            secondary.setFont(app.font())
        primary.setFocus(Qt.OtherFocusReason)

        from PySide6.QtGui import QKeySequence, QShortcut

        from src.ui.help_router import install_shift_f1_help

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.status_shortcut.activated.connect(self._read_result)
        self._f1_shortcut = QShortcut(QKeySequence("F1"), self)
        self._f1_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self._f1_shortcut.activated.connect(self._show_shortcuts)
        self.context_help_shortcut = install_shift_f1_help(
            self, shortcut_context=Qt.WidgetWithChildrenShortcut
        )

    def _read_result(self) -> None:
        from PySide6.QtGui import QAccessible, QAccessibleEvent

        previous = self.focusWidget()
        self._message_label.setFocus(Qt.OtherFocusReason)
        if QAccessible.isActive():
            QAccessible.updateAccessibility(
                QAccessibleEvent(self._message_label, QAccessible.Event.Focus)
            )
        if previous is not None and previous is not self._message_label:
            previous.setFocus(Qt.OtherFocusReason)

    def _show_shortcuts(self) -> None:
        from src.accessibility.shortcut_helpers import exec_f1_shortcuts_dialog

        exec_f1_shortcuts_dialog(
            self,
            "Keyboard Shortcuts - Check for updates",
            [
                ("Enter", "Activate the focused button"),
                ("Escape", "Close"),
                ("Alt+/", "Read the result"),
                ("F1", "Show keyboard shortcuts"),
                ("Shift+F1", "Open help"),
            ],
        )

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focus = self.focusWidget()
            if isinstance(focus, QPushButton) and focus.isEnabled():
                focus.click()
                return
        super().keyPressEvent(event)

    def _open_page(self) -> None:
        from src.app_urls import ABCS_UPDATE_DOWNLOAD_URL, open_public_url

        self.browser_opened = open_public_url(ABCS_UPDATE_DOWNLOAD_URL)
        self.done(self.OPEN_PAGE)
