"""Accessible About Dialog for AbCS."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QStatusBar,
)
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut
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

        # Graphic
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

        # About text
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

        # --- KEY CHANGE: QLabel in QScrollArea instead of QTextEdit ---
        about_label = QLabel(about_text, self)
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Prevent Qt from promoting this to QAccessibleTextInterface,
        # which is what causes JAWS to treat it as an edit field.
        about_label.setTextInteractionFlags(Qt.NoTextInteraction)

        # Give it keyboard focus so JAWS finds it via Tab
        about_label.setFocusPolicy(Qt.TabFocus)

        # Full text in accessibleName = JAWS reads the whole thing on focus
        about_label.setAccessibleName(about_text)
        about_label.setAccessibleDescription(
            "About dialog information. Press Tab to move to the next control."
        )

        font = about_label.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        about_label.setFont(font)

        # Wrap in a scroll area so long text doesn't blow out the dialog
        scroll = QScrollArea(self)
        scroll.setWidget(about_label)
        scroll.setWidgetResizable(True)
        scroll.setFocusPolicy(Qt.NoFocus)  # Tab goes to label, not scroll area
        scroll.setFrameShape(scroll.NoFrame)
        layout.addWidget(scroll)

        self.about_label = about_label

        # Delay focus slightly so JAWS has settled on the dialog before we hand
        # focus to the label. 0ms is often too fast; 200ms is reliable.
        QTimer.singleShot(200, lambda: about_label.setFocus(Qt.TabFocusReason))

        # Status bar
        self.status_bar = QStatusBar(self)
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.status_bar)
        self.status_bar.showMessage(
            "AbCS About dialog. Press Alt+/ to read this message."
        )

        # Alt+/ shortcut
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
