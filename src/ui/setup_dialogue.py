"""Accessible About Dialog for AbCS."""

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

        super().__init__(parent)
        self.setWindowIcon(get_app_icon())

        self.scaler = scaler
        self.setWindowTitle("Welcome to AbCS")
        self.setAccessibleName("Welcome to AbCS")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(400))
        self.setMinimumHeight(self.scaler.get_scaled_size(260))

        layout = QVBoxLayout(self)
        # Calculate reduced top margin: 1/32 of the new window height
        base_height = self.scaler.get_scaled_size(260)
        reduced_top_margin = max(int(base_height // 32), self.scaler.get_scaled_size(2))
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            reduced_top_margin,
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(9),
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
        self.setWindowTitle("Welcome to AbCS")
        self.setAccessibleName("Welcome to AbCS")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(400))
        self.setMinimumHeight(self.scaler.get_scaled_size(173))  # 520 / 3 ≈ 173

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(6),  # Tighter top margin
            self.scaler.get_scaled_size(24),
            self.scaler.get_scaled_size(18),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))  # Tighter spacing

        # --- Graphic and Setup text in a zero-spacing container (like AboutDialog) ---
        pixmap = QPixmap("Graphics/abcs_app_splash.png")
        if not pixmap.isNull():
            from PySide6.QtWidgets import QSizePolicy

            graphic_label = QLabel(self)
            graphic_label.setPixmap(pixmap)
            graphic_label.setAlignment(Qt.AlignHCenter)
            graphic_label.setFocusPolicy(Qt.NoFocus)
            graphic_label.setContentsMargins(0, 0, 0, 0)
            graphic_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            layout.addWidget(graphic_label, alignment=Qt.AlignHCenter)

        setup_text = (
            "No audiobooks found in the database.\n\n"
            "You can:\n"
            "• Import audiobooks from your computer\n"
            "    ctrl+I or from the menu File->Import\n\n"
            "• Manually add a new book\n"
            "    ctrl+N or from the menu File->New Book\n\n"
            "• Import a book list from a spreadsheet\n"
            "    shift+ctrl+I or from the menu File->Import Book List\n\n"
            "Click OK or press Escape to exit."
        )

        # Tabstop 1: the text content
        setup_label = FocusAnnouncingLabel(setup_text, self)
        setup_label.setWordWrap(True)
        setup_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        setup_label.setTextInteractionFlags(Qt.NoTextInteraction)
        setup_label.setFocusPolicy(Qt.TabFocus)
        setup_label.setAccessibleName(setup_text)
        setup_label.setAccessibleDescription(
            "Welcome/setup information. Press Tab to move to Import, Add Book, or Close button."
        )

        font = setup_label.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        setup_label.setFont(font)
        setup_label.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(setup_label)

        from PySide6.QtWidgets import QHBoxLayout, QWidget

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(0)
        btn_row.addStretch(1)  # Push button to the right
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

        self.setup_label = setup_label
        self.ok_btn = ok_btn

        # Start focus on setup_label so the screen reader reads the text first
        QTimer.singleShot(100, lambda: setup_label.setFocus(Qt.TabFocusReason))
