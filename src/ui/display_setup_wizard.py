"""First-run display setup wizard."""

from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QPushButton,
    QWidget,
)

from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_accessible_button_style
from src.accessibility.theme_manager import ThemeManager


class DisplaySetupWizard(QDialog):
    """Simple first-run wizard for selecting theme and zoom."""

    SETTINGS_KEY_DONE = "ui/first_run_display_setup_done"

    def __init__(self, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.settings = QSettings("AbCS", "AudioBookCollector")
        self._loading = False

        self.setWindowTitle("Display Setup")
        self.setAccessibleName("Display Setup")
        self.resize(620, 420)

        self._build_ui()
        self._load_values()
        self._connect_signals()
        self.disable_hover_highlight()  # Disable mouse hover effects

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        intro = QLabel(
            "Choose your preferred display settings. You can change these later in Preferences."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        theme_row = QHBoxLayout()
        theme_label = QLabel("&Theme:")
        self.theme_combo = QComboBox()
        theme_label.setBuddy(self.theme_combo)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo, 1)
        layout.addLayout(theme_row)

        preset_row = QHBoxLayout()
        preset_label = QLabel("&Preset:")
        self.preset_combo = QComboBox()
        preset_label.setBuddy(self.preset_combo)
        preset_row.addWidget(preset_label)
        preset_row.addWidget(self.preset_combo, 1)
        layout.addLayout(preset_row)

        zoom_row = QHBoxLayout()
        zoom_label = QLabel("&Zoom (%):")
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(UIScaler.MIN_SCALE, UIScaler.MAX_SCALE)
        self.zoom_spin.setSingleStep(UIScaler.SCALE_STEP)
        zoom_label.setBuddy(self.zoom_spin)
        zoom_row.addWidget(zoom_label)
        zoom_row.addWidget(self.zoom_spin)
        zoom_row.addStretch(1)
        layout.addLayout(zoom_row)

        shortcut_lines = [
            "Keyboard quick help",
            "F1: Show keyboard shortcuts",
            "Alt+/: Read status bar",
            "Ctrl++ / Ctrl+- / Ctrl+0: Zoom in, out, reset",
            "Alt+M: Open menu in main window",
        ]
        self.shortcuts_help = QTableWidget(self)
        self.shortcuts_help.setAccessibleName("Shortcut Help")
        self.shortcuts_help.setAccessibleDescription(
            "Read-only shortcut help. Use arrow keys to read line by line."
        )
        self.shortcuts_help.setColumnCount(1)
        self.shortcuts_help.setHorizontalHeaderLabels([""])
        self.shortcuts_help.setRowCount(len(shortcut_lines))
        self.shortcuts_help.setVerticalHeaderLabels([""] * len(shortcut_lines))
        self.shortcuts_help.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.shortcuts_help.setSelectionMode(QAbstractItemView.SingleSelection)
        self.shortcuts_help.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shortcuts_help.setTabKeyNavigation(False)
        self.shortcuts_help.setAlternatingRowColors(False)
        self.shortcuts_help.setFocusPolicy(Qt.StrongFocus)
        self.shortcuts_help.verticalHeader().setVisible(False)
        self.shortcuts_help.horizontalHeader().setVisible(False)
        self.shortcuts_help.setShowGrid(False)
        self.shortcuts_help.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }"
            "QTableWidget::item:selected {"
            " background-color: transparent;"
            " color: palette(text);"
            "}"
            "QTableWidget::item:focus { outline: none; }"
        )
        for row, line in enumerate(shortcut_lines):
            item = QTableWidgetItem(line)
            item.setData(Qt.AccessibleTextRole, line)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.shortcuts_help.setItem(row, 0, item)
        self.shortcuts_help.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)
        if self.shortcuts_help.rowCount() > 0:
            self.shortcuts_help.setCurrentCell(0, 0)
        layout.addWidget(self.shortcuts_help, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.continue_button = QPushButton("&Continue")
        self.skip_button = QPushButton("S&kip")
        buttons.addWidget(self.continue_button)
        buttons.addWidget(self.skip_button)
        layout.addLayout(buttons)

        button_style = build_accessible_button_style(
            self.scaler.get_scaled_size(20)
        )
        self.continue_button.setStyleSheet(button_style)
        self.skip_button.setStyleSheet(button_style)
        self.setTabOrder(self.shortcuts_help, self.continue_button)
        self.setTabOrder(self.continue_button, self.skip_button)

    def _focus_shortcut_help(self) -> None:
        if self.shortcuts_help.rowCount() > 0:
            self.shortcuts_help.setCurrentCell(0, 0)
        self.shortcuts_help.setFocus(Qt.ActiveWindowFocusReason)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._focus_shortcut_help)
        QTimer.singleShot(150, self._focus_shortcut_help)

    def _load_values(self):
        self._loading = True
        self.theme_combo.clear()
        for display_name, theme_id in self.theme_manager.get_theme_names():
            self.theme_combo.addItem(display_name, theme_id)

        current_theme = self.theme_manager.current_theme_name
        idx = self.theme_combo.findData(current_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        self.preset_combo.clear()
        for name in UIScaler.SCALE_PRESETS.keys():
            self.preset_combo.addItem(name)
        self.preset_combo.addItem("Custom")

        self.zoom_spin.setValue(self.scaler.current_scale)
        self.preset_combo.setCurrentText(self.scaler.get_preset_name())
        self._loading = False

    def _connect_signals(self):
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        self.zoom_spin.valueChanged.connect(self._on_zoom_changed)
        self.continue_button.clicked.connect(self._on_continue)
        self.skip_button.clicked.connect(self._on_skip)

    def _on_theme_changed(self):
        if self._loading:
            return
        theme_id = self.theme_combo.currentData()
        if theme_id:
            self.theme_manager.set_theme(theme_id)

    def _on_preset_changed(self, preset_name: str):
        if self._loading:
            return
        if preset_name in UIScaler.SCALE_PRESETS:
            self.zoom_spin.setValue(UIScaler.SCALE_PRESETS[preset_name])

    def _on_zoom_changed(self, value: int):
        if self._loading:
            return
        self.scaler.set_scale(value)
        preset_name = self.scaler.get_preset_name()
        self._loading = True
        self.preset_combo.setCurrentText(preset_name)
        self._loading = False

    def _mark_done(self):
        self.settings.setValue(self.SETTINGS_KEY_DONE, True)

    def _on_continue(self):
        self._mark_done()
        self.accept()

    def _on_skip(self):
        self._mark_done()
        self.accept()

    def disable_hover_highlight(self):
        """Disable hover highlighting for low-vision comfort."""
        self.setMouseTracking(False)
        self.setAttribute(Qt.WA_Hover, False)
        for child in self.findChildren(QWidget):
            child.setMouseTracking(False)
            child.setAttribute(Qt.WA_Hover, False)

    @classmethod
    def should_show(cls) -> bool:
        settings = QSettings("AbCS", "AudioBookCollector")
        return not settings.value(cls.SETTINGS_KEY_DONE, False, type=bool)
