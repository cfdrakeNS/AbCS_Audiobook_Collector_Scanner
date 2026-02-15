"""First-run display setup wizard."""

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QPushButton,
)

from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager


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

        shortcuts_help = QTextEdit()
        shortcuts_help.setReadOnly(True)
        shortcuts_help.setAccessibleName("Shortcut Help")
        shortcuts_help.setPlainText(
            "Keyboard quick help:\n"
            "- F1: Show keyboard shortcuts\n"
            "- Alt+/: Read status bar\n"
            "- Ctrl++ / Ctrl+- / Ctrl+0: Zoom in/out/reset\n"
            "- Alt+M: Open menu in main window"
        )
        layout.addWidget(shortcuts_help, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.continue_button = QPushButton("&Continue")
        self.skip_button = QPushButton("S&kip")
        buttons.addWidget(self.continue_button)
        buttons.addWidget(self.skip_button)
        layout.addLayout(buttons)

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

    @classmethod
    def should_show(cls) -> bool:
        settings = QSettings("AbCS", "AudioBookCollector")
        return not settings.value(cls.SETTINGS_KEY_DONE, False, type=bool)
