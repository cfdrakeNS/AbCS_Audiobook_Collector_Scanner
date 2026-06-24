"""Accessible About Dialog for AbCS."""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from src.accessibility.graphics_paths import resolve_graphics_path
from src.accessibility.dialog_prose import create_dialog_html_text
from src.ui.accessible_dialog import AccessibleDialog


def _get_app_version() -> str:
    try:
        from src.build_config import APP_VERSION

        return f"v{APP_VERSION}"
    except ImportError:
        return "v?.?.?"


class AboutDialog(AccessibleDialog):

    def __init__(self, scaler, parent=None):
        from src.accessibility.icon_helper import get_app_icon
        from src.accessibility.style_helpers import build_accessible_button_style

        super().__init__(parent)
        self.setWindowIcon(get_app_icon())

        self.scaler = scaler
        self.setWindowTitle("About AbCS")
        self.setAccessibleName("About AbCS")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(480))
        self.setMinimumHeight(self.scaler.get_scaled_size(520))
        self.resize(
            self.scaler.get_scaled_size(480),
            self.scaler.get_scaled_size(520),
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(6),
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))

        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        pixmap = QPixmap(resolve_graphics_path("abcs_app_splash.png"))
        if not pixmap.isNull():
            graphic_label = QLabel(self)
            graphic_label.setPixmap(pixmap)
            graphic_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            graphic_label.setFocusPolicy(Qt.NoFocus)
            graphic_label.setContentsMargins(0, 0, 0, 0)
            graphic_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            content_layout.addWidget(graphic_label, alignment=Qt.AlignHCenter)

        version = _get_app_version()
        about_blocks = [
            ("body", f"AbCS - Audio Book Collector Scanner    {version}"),
            (
                "body",
                "A cross-platform audiobook collection manager with full accessibility support.",
            ),
            ("heading", "LICENSE"),
            ("body", "Copyright (c) 2025-2026 C.F. Drake & Contributors"),
            ("body", "Custom non-commercial license."),
            ("body", "Commercial sale/distribution requires written permission."),
            ("heading", "FEATURES"),
            ("item", "Audio Book Management with full metadata."),
            ("item", "ID3 Tag Import from most audio format files."),
            ("item", "Web import and updated metadata."),
            ("item", "Advanced search and filtering."),
            ("item", "Complete keyboard navigation."),
            ("item", "Screen reader support."),
            ("item", "Scalable UI (50%-200%+)."),
            ("item", "High contrast themes."),
            ("heading", "HELP"),
            (
                "body",
                "Built-in guides explain workflows in plain language for every major window.",
            ),
            ("item", "Help menu, Help... — browse topics and jump to sections."),
            ("item", "Shift+F1 — context-sensitive help for the current window."),
            ("item", "F1 — keyboard shortcuts for the current window."),
            ("heading", "ACCESSIBILITY"),
            ("body", "Designed for users with low vision and screen readers."),
            ("body", "All features include keyboard shortcuts."),
        ]

        about_label = create_dialog_html_text(
            self,
            about_blocks,
            "About information",
            "About AbCS. Use arrow keys to read line by line. Press Tab to move to Close button.",
        )
        about_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        font = about_label.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        about_label.setFont(font)
        about_label.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(about_label)

        layout.addWidget(content_widget, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok_btn = QPushButton("OK", self)
        ok_btn.setAccessibleName("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)

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

        QTimer.singleShot(100, lambda: about_label.setFocus(Qt.TabFocusReason))
