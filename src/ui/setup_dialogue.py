"""Accessible Setup Dialog for AbCS."""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from src.accessibility.graphics_paths import resolve_graphics_path
from src.accessibility.read_only_text import create_dialog_html_text
from src.ui.accessible_dialog import AccessibleDialog


class SetupDialog(AccessibleDialog):

    def __init__(self, scaler, parent=None):
        from src.accessibility.icon_helper import get_app_icon
        from src.accessibility.style_helpers import build_accessible_button_style

        super().__init__(parent)
        self.setWindowIcon(get_app_icon())

        self.scaler = scaler
        self.setWindowTitle("Welcome to AbCS")
        self.setAccessibleName("Welcome to AbCS")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(480))
        self.setMinimumHeight(self.scaler.get_scaled_size(200))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(6),
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))

        pixmap = QPixmap(resolve_graphics_path("abcs_app_splash.png"))
        if not pixmap.isNull():
            graphic_label = QLabel(self)
            graphic_label.setPixmap(pixmap)
            graphic_label.setAlignment(Qt.AlignHCenter)
            graphic_label.setFocusPolicy(Qt.NoFocus)
            graphic_label.setContentsMargins(0, 0, 0, 0)
            graphic_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            layout.addWidget(graphic_label, alignment=Qt.AlignHCenter)

        setup_blocks = [
            ("body", "No audiobooks found in the database."),
            ("heading", "You can:"),
            ("item", "Import audiobooks from your computer."),
            ("body", "Ctrl+I or File → Import."),
            ("item", "Manually add a new book."),
            ("body", "Ctrl+N or File → New Book."),
            ("item", "Import a book list from a spreadsheet."),
            ("body", "Shift+Ctrl+I or File → Import Book List."),
            ("heading", "Help"),
            ("body", "Press Shift+F1 in any window for context-sensitive help."),
            ("body", "Use the Help menu for full workflow guides."),
            ("body", "Click OK or press Escape to exit."),
        ]

        setup_label = create_dialog_html_text(
            self,
            setup_blocks,
            "Welcome information",
            "Setup instructions. Use arrow keys to read line by line. Press Tab to move to OK button.",
        )
        setup_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        font = setup_label.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        setup_label.setFont(font)
        setup_label.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(setup_label)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(0)
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

        self.setup_label = setup_label
        self.ok_btn = ok_btn

        QTimer.singleShot(100, lambda: setup_label.setFocus(Qt.TabFocusReason))
