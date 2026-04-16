"""Accessible About Dialog for AbCS."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QAccessible, QAccessibleEvent
from PySide6.QtCore import Qt, QTimer


class FocusAnnouncingLabel(QLabel):
    def focusInEvent(self, event):
        super().focusInEvent(event)
        acc_event = QAccessibleEvent(self, QAccessible.Event.Focus)
        QAccessible.updateAccessibility(acc_event)


class AboutDialog(QDialog):

    def __init__(self, scaler, parent=None):
        from src.accessibility.icon_helper import get_app_icon

        super().__init__(parent)
        self.setWindowIcon(get_app_icon())

        self.scaler = scaler
        self.setWindowTitle("About AbCS")
        self.setAccessibleName("About AbCS")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(400))
        self.setMinimumHeight(self.scaler.get_scaled_size(520))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(6),  # Tighter top margin
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )

    def get_app_version(self):
        try:
            from src.build_config import APP_VERSION

            return f"v{APP_VERSION}"
        except ImportError:
            try:
                from build_config import APP_VERSION

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
        self.setMinimumHeight(self.scaler.get_scaled_size(520))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(6),  # Tighter top margin
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))  # Tighter spacing

        # --- Graphic and About text in a zero-spacing container ---
        from PySide6.QtWidgets import QWidget, QVBoxLayout as QVBoxLayout2

        content_widget = QWidget(self)
        content_layout = QVBoxLayout2(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        pixmap = QPixmap("Graphics/abcs_app_splash.png")
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
            graphic_label.setPixmap(pixmap)  # Show at native size (500x162)
            graphic_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            graphic_label.setFocusPolicy(Qt.NoFocus)
            graphic_label.setContentsMargins(0, 0, 0, 0)
            graphic_layout.addWidget(graphic_label, alignment=Qt.AlignHCenter)
            graphic_layout.addStretch(1)
            content_layout.addWidget(graphic_container)

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

        # Tabstop 1: the text content
        about_label = FocusAnnouncingLabel(about_text, self)
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        about_label.setTextInteractionFlags(Qt.NoTextInteraction)
        about_label.setFocusPolicy(Qt.TabFocus)
        about_label.setAccessibleName(about_text)
        about_label.setAccessibleDescription(
            "About information. Press Tab to move to Close button."
        )

        font = about_label.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        about_label.setFont(font)
        about_label.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(about_label)

        layout.addWidget(content_widget)

        # Tabstop 2: Close button — styled and right-aligned
        from PySide6.QtWidgets import QHBoxLayout, QWidget

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok_btn = QPushButton("OK", self)
        ok_btn.setAccessibleName("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        from src.accessibility.style_helpers import build_accessible_button_style

        base_height = 20
        scale_pct = (
            self.scaler.current_scale if hasattr(self.scaler, "current_scale") else 150
        )
        scaled_height = int(base_height * (scale_pct / 100.0))
        btn_font = ok_btn.font()
        btn_font.setPointSize(self.scaler.get_scaled_size(12))
        ok_btn.setFont(btn_font)
        ok_btn.setMinimumHeight(max(scaled_height - 4, 14))
        ok_btn.setMaximumHeight(max(scaled_height - 4, 14))
        ok_btn.setStyleSheet(build_accessible_button_style(scaled_height))
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        self.about_label = about_label
        self.ok_btn = ok_btn

        # Start focus on about_label so the screen reader reads the text first
        QTimer.singleShot(100, lambda: about_label.setFocus(Qt.TabFocusReason))
