"""Accessible Setup Dialog for AbCS (empty database) - AboutDialog style."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QAccessible, QAccessibleEvent
from PySide6.QtCore import Qt, QTimer


class FocusAnnouncingLabel(QLabel):
    def focusInEvent(self, event):
        super().focusInEvent(event)
        acc_event = QAccessibleEvent(self, QAccessible.Event.Focus)
        QAccessible.updateAccessibility(acc_event)


class SetupDialog(QDialog):
    def __init__(self, scaler, parent=None):
        from src.accessibility.icon_helper import get_app_icon
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
        from src.accessibility.style_helpers import build_accessible_button_style

        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        self.scaler = scaler
        self.setWindowTitle("Welcome to AbCS")
        self.setAccessibleName("Setup AbCS - No Books Found")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(400))
        self.setMinimumHeight(self.scaler.get_scaled_size(520))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(6),
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))

        # --- Graphic and message in a zero-spacing container ---
        from PySide6.QtWidgets import QWidget, QVBoxLayout as QVBoxLayout2

        content_widget = QWidget(self)
        content_layout = QVBoxLayout2(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        pixmap = QPixmap("data/graphics/abcs_about_win.png")
        if not pixmap.isNull():
            from PySide6.QtWidgets import (
                QVBoxLayout as QVBoxLayout3,
                QWidget as QWidget2,
            )

            graphic_container = QWidget2(self)
            graphic_layout = QVBoxLayout3(graphic_container)
            graphic_layout.setContentsMargins(0, 0, 0, 0)
            graphic_layout.setSpacing(0)
            graphic_layout.addStretch(1)
            graphic_label = QLabel(self)
            graphic_label.setPixmap(pixmap)
            graphic_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            graphic_label.setFocusPolicy(Qt.NoFocus)
            graphic_label.setContentsMargins(0, 0, 0, 0)
            graphic_layout.addWidget(graphic_label, alignment=Qt.AlignHCenter)
            graphic_layout.addStretch(1)
            content_layout.addWidget(graphic_container)

        # Message label (tabstop 1)
        empty_db_text = (
            "No audiobooks found in the database.\n\n"
            "You can:\n"
            "• Import audiobooks from your computer (scan folders)\n"
            "• Manually add a new book\n\n"
            "Use Ctrl+I to import or Alt+M for menu options."
        )
        label = FocusAnnouncingLabel(empty_db_text, self)
        label.setWordWrap(True)
        font = label.font()
        font.setPointSize(self.scaler.get_scaled_size(14))
        label.setFont(font)
        label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        label.setTextInteractionFlags(Qt.NoTextInteraction)
        label.setFocusPolicy(Qt.TabFocus)
        label.setAccessibleName(empty_db_text)
        label.setAccessibleDescription(
            "Welcome/setup information. Press Tab to move to Import, Add Book, or Close button."
        )
        label.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(label)

        layout.addWidget(content_widget)

        # Buttons (Import, Add Book, Close) - tabstop 2+
        from PySide6.QtWidgets import QHBoxLayout

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.import_button = QPushButton("Import (Ctrl+I)", self)
        self.add_button = QPushButton("Add Book (Ctrl+N)", self)
        self.close_button = QPushButton("Close (Alt+C)", self)

        button_style = build_accessible_button_style(self.scaler.get_scaled_size(20))
        for btn in (self.import_button, self.add_button, self.close_button):
            btn.setStyleSheet(button_style)
            btn.setMinimumWidth(self.scaler.get_scaled_size(120))
            btn.setMinimumHeight(self.scaler.get_scaled_size(36))
            font = btn.font()
            font.setPointSize(self.scaler.get_scaled_size(12))
            btn.setFont(font)
            btn_row.addWidget(btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        # Shortcuts
        mgr = get_shortcut_manager()
        callback_map = {
            "import_button": self.import_button.click,
            "add_button": self.add_button.click,
            "close_button": self.close_button.click,
        }
        mgr.register_alt_shortcuts(self, ShortcutContext.SETUP_DIALOG, callback_map)

        self.import_button.clicked.connect(self.accept)
        self.add_button.clicked.connect(self.accept)
        self.close_button.clicked.connect(self.reject)

        self.setTabOrder(self.import_button, self.add_button)
        self.setTabOrder(self.add_button, self.close_button)
        # Start focus on label so JAWS reads the text first
        QTimer.singleShot(100, lambda: label.setFocus(Qt.TabFocusReason))
