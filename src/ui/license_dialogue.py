"""Accessible License Dialog for AbCS."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer


class LicenseDialog(QDialog):
    def __init__(self, scaler, parent=None):
        super().__init__(parent)
        self.scaler = scaler
        self.setWindowTitle("AbCS License")
        self.setAccessibleName("AbCS License")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(400))
        self.setMinimumHeight(self.scaler.get_scaled_size(400))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(12),
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))

        license_text = (
            "AbCS - Audio Book Collector Scanner\n"
            "Custom Non-Commercial License\n\n"
            "License Terms\n\n"
            "Copyright (c) 2025-2026 C.F. Drake & Contributors\n\n"
            "Permission is granted, free of charge, to use, copy, and share this\n"
            "software for personal, educational, testing, and non-commercial use.\n\n"
            "You may modify this software for your own use.\n"
            "If you redistribute copies or modified versions, this notice and\n"
            "copyright attribution must remain intact.\n\n"
            "Commercial use is prohibited without prior written permission from\n"
            "the copyright holder.\n"
            "You may not sell this software, bundle it into paid products, or\n"
            "distribute it for a fee without explicit written authorization.\n\n"
            'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,\n'
            "express or implied, including but not limited to the warranties of\n"
            "MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\n"
            "In no event shall the authors or copyright holders be liable for any\n"
            "claim, damages or other liability, whether in an action of contract,\n"
            "tort or otherwise, arising from, out of or in connection with the\n"
            "software or the use or other dealings in the software."
        )

        license_label = QLabel(license_text, self)
        license_label.setWordWrap(True)
        license_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        license_label.setTextInteractionFlags(Qt.NoTextInteraction)
        license_label.setFocusPolicy(Qt.TabFocus)
        license_label.setAccessibleName(license_text)
        license_label.setAccessibleDescription(
            "AbCS license information. Press Tab to move to OK button."
        )
        font = license_label.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        license_label.setFont(font)
        license_label.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(license_label)

        from PySide6.QtWidgets import QHBoxLayout
        from src.accessibility.style_helpers import build_accessible_button_style

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
