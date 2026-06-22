"""Accessible License Dialog for AbCS."""

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

from src.accessibility.read_only_text import create_dialog_html_text
from src.ui.accessible_dialog import AccessibleDialog


class LicenseDialog(AccessibleDialog):
    def __init__(self, scaler, parent=None):
        from src.accessibility.icon_helper import get_app_icon
        from src.accessibility.style_helpers import build_accessible_button_style

        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        self.scaler = scaler
        self.setWindowTitle("AbCS License")
        self.setAccessibleName("AbCS License")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(480))
        self.setMinimumHeight(self.scaler.get_scaled_size(400))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(12),
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))

        license_blocks = [
            ("body", "AbCS - Audio Book Collector Scanner"),
            ("heading", "Custom Non-Commercial License"),
            ("heading", "License Terms"),
            ("body", "Copyright (c) 2025-2026 C.F. Drake & Contributors"),
            (
                "body",
                "Permission is granted, free of charge, to use, copy, and share this "
                "software for personal, educational, testing, and non-commercial use.",
            ),
            ("body", "You may modify this software for your own use."),
            (
                "body",
                "If you redistribute copies or modified versions, this notice and "
                "copyright attribution must remain intact.",
            ),
            (
                "body",
                "Commercial use is prohibited without prior written permission from "
                "the copyright holder.",
            ),
            (
                "body",
                "You may not sell this software, bundle it into paid products, or "
                "distribute it for a fee without explicit written authorization.",
            ),
            (
                "body",
                'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, '
                "express or implied, including but not limited to the warranties of "
                "MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.",
            ),
            (
                "body",
                "In no event shall the authors or copyright holders be liable for any "
                "claim, damages or other liability, whether in an action of contract, "
                "tort or otherwise, arising from, out of or in connection with the "
                "software or the use or other dealings in the software.",
            ),
        ]

        license_label = create_dialog_html_text(
            self,
            license_blocks,
            "License information",
            "AbCS license terms. Use arrow keys to read line by line. Press Tab to move to OK button.",
        )
        license_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        font = license_label.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        license_label.setFont(font)
        license_label.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(license_label)

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

        self.license_label = license_label
        self.ok_btn = ok_btn
        QTimer.singleShot(100, lambda: license_label.setFocus(Qt.TabFocusReason))
