"""Accessible About Dialog for AbCS."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QStatusBar
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer


class AboutDialog(QDialog):
    def get_app_version(self):
        try:
            from main import APP_VERSION

            return f"v{APP_VERSION}"
        except ImportError:
            return "v?.?.?"

    def __init__(self, scaler, parent=None):
        super().__init__(parent)
        self.scaler = scaler
        self.setWindowTitle("About AbCS")
        self.setAccessibleName("About AbCS")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(400))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(16)

        # Graphic at the top
        pixmap = QPixmap("data/graphics/abcs_about_win.png")
        if not pixmap.isNull():
            graphic_label = QLabel(self)
            graphic_label.setPixmap(
                pixmap.scaledToWidth(
                    self.scaler.get_scaled_size(220), Qt.SmoothTransformation
                )
            )
            graphic_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            graphic_label.setAccessibleName("AbCS About Graphic")
            layout.addWidget(graphic_label)

        # About text (including version logic)
        version = self.get_app_version()
        about_text = (
            f"AbCS - Audio Book Collector Scanner    {version}\n"
            "A cross-platform audiobook collection manager with full accessibility support.\n\n"
            "LICENSE\n"
            "Copyright (c) 2025-2026 C.F. Drake & Contributors\n"
            "Custom non-commercial license.\n"
            "Commercial sale/distribution requires written permission.\n\n"
            "FEATURES\n"
            "• Audio Book Management with full metadata\n"
            "• ID3 Tag Import from folders\n"
            "• Advanced Search and Filtering\n"
            "• Complete Keyboard Navigation\n"
            "• Screen Reader Support\n"
            "• Scalable UI (50%-200%+)\n"
            "• High Contrast Themes\n\n"
            "ACCESSIBILITY\n"
            "• Designed for users with low vision and screen readers.\n"
            "• All features include keyboard shortcuts.\n"
            "Press F1 or use Help menu for Keyboard Shortcuts."
        )
        about_text_edit = QTextEdit(self)
        about_text_edit.setReadOnly(True)
        about_text_edit.setPlainText(about_text)
        about_text_edit.setAccessibleName("About Text")
        about_text_edit.setAccessibleDescription(
            "Read-only about dialog text. Use arrow keys to read line by line."
        )
        font = about_text_edit.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        about_text_edit.setFont(font)
        layout.addWidget(about_text_edit)
        self.about_text_edit = about_text_edit
        QTimer.singleShot(0, lambda: about_text_edit.setFocus(Qt.TabFocusReason))

        # Accessible status bar
        self.status_bar = QStatusBar(self)
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.status_bar)
        self.status_bar.showMessage(
            "AbCS About dialog. Press Alt+/ to read this message."
        )


"""Accessible About Dialog for AbCS."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap, QKeySequence
from PySide6.QtCore import Qt


# --- Clean, single AboutDialog implementation ---
class AboutDialog(QDialog):
    def get_app_version(self):
        try:
            from main import APP_VERSION

            return f"v{APP_VERSION}"
        except ImportError:
            return "v?.?.?"

    def __init__(self, scaler, parent=None):
        super().__init__(parent)
        from PySide6.QtGui import QKeySequence, QShortcut
        from PySide6.QtWidgets import QStatusBar
        from src.accessibility.accessible_events import announce_status_message

        self.scaler = scaler
        self.setWindowTitle("About AbCS")
        self.setAccessibleName("About AbCS")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(400))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(16)

        # Graphic at the top
        pixmap = QPixmap("data/graphics/abcs_about_win.png")
        if not pixmap.isNull():
            graphic_label = QLabel(self)
            graphic_label.setPixmap(
                pixmap.scaledToWidth(
                    self.scaler.get_scaled_size(220), Qt.SmoothTransformation
                )
            )
            graphic_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            graphic_label.setAccessibleName("AbCS About Graphic")
            layout.addWidget(graphic_label)

        # About text (including version logic)
        version = self.get_app_version()
        about_text = (
            f"AbCS - Audio Book Collector Scanner    {version}\n"
            "A cross-platform audiobook collection manager with full accessibility support.\n\n"
            "LICENSE\n"
            "Copyright (c) 2025-2026 C.F. Drake & Contributors\n"
            "Custom non-commercial license.\n"
            "Commercial sale/distribution requires written permission.\n\n"
            "FEATURES\n"
            "• Audio Book Management with full metadata\n"
            "• ID3 Tag Import from folders\n"
            "• Advanced Search and Filtering\n"
            "• Complete Keyboard Navigation\n"
            "• Screen Reader Support\n"
            "• Scalable UI (50%-200%+)\n"
            "• High Contrast Themes\n\n"
            "ACCESSIBILITY\n"
            "• Designed for users with low vision and screen readers.\n"
            "• All features include keyboard shortcuts.\n"
            "Press F1 or use Help menu for Keyboard Shortcuts."
        )
        from PySide6.QtWidgets import QTextEdit

        about_text_edit = QTextEdit(self)
        about_text_edit.setReadOnly(True)
        about_text_edit.setPlainText(about_text)
        about_text_edit.setAccessibleName("About Text")
        about_text_edit.setAccessibleDescription(
            "Read-only about dialog text. Use arrow keys to read line by line."
        )
        font = about_text_edit.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        about_text_edit.setFont(font)
        layout.addWidget(about_text_edit)
        # Focus the text area by default for JAWS/NVDA
        self.about_text_edit = about_text_edit
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, lambda: about_text_edit.setFocus(Qt.TabFocusReason))

        # Accessible status bar
        self.status_bar = QStatusBar(self)
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.status_bar)
        self.status_bar.showMessage(
            "AbCS About dialog. Press Alt+/ to read this message."
        )

        # Alt+/ shortcut for status bar
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.setContext(Qt.ApplicationShortcut)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

    def set_status(self, message: str, announce: bool = False):
        self.status_bar.showMessage(message)
        if announce:
            from src.accessibility.accessible_events import announce_status_message

            announce_status_message(
                self.status_bar, message, move_focus=True, force_focus_announce=True
            )

    def on_read_status_bar(self):
        message = self.status_bar.currentMessage() or "About dialog."
        from src.accessibility.accessible_events import announce_status_message

        announce_status_message(
            self.status_bar, message, move_focus=True, force_focus_announce=True
        )
