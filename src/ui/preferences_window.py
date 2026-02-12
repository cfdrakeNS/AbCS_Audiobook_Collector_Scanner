"""
Preferences Window
Basic preferences for display and import settings.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QSpinBox, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QStatusBar
)
from PySide6.QtCore import QSettings
from PySide6.QtGui import QShortcut, QKeySequence

from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from accessibility.accessible_events import (
    announce_status_message, announce_dialog_opened, announce_dialog_closed
)


class PreferencesWindow(QDialog):
    """
    Preferences dialog for display and import settings.
    """

    def __init__(self, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)

        self.scaler = scaler
        self.theme_manager = theme_manager
        self.settings = QSettings('AbCS', 'AudioBookCollector')

        self._loading = False
        self._initial_theme = self.theme_manager.current_theme_name
        self._initial_scale = self.scaler.current_scale

        self.setup_ui()
        self.apply_control_styles()
        self.load_settings()
        self.connect_signals()
        self.setup_shortcuts()
        self.scaler.scale_changed.connect(self.on_scale_changed)

        title = "Preferences"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Application preferences for display and import settings")
        self.resize(700, 520)

        announce_dialog_opened(self, title)
        announce_status_message(self.status_bar, "Ready")

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header section: Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout(display_group)
        display_layout.setSpacing(10)

        theme_layout = QHBoxLayout()
        theme_label = QLabel("&Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.setAccessibleName("Theme")
        self.theme_combo.setAccessibleDescription(
            "Select application theme - Alt+T")
        theme_label.setBuddy(self.theme_combo)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo, 1)
        display_layout.addLayout(theme_layout)

        preset_layout = QHBoxLayout()
        preset_label = QLabel("&Preset:")
        self.preset_combo = QComboBox()
        self.preset_combo.setAccessibleName("Font scaling preset")
        self.preset_combo.setAccessibleDescription(
            "Select font scaling preset - Alt+P")
        preset_label.setBuddy(self.preset_combo)
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo, 1)
        display_layout.addLayout(preset_layout)

        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("&Zoom (%):")
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(
            UIScaler.MIN_SCALE, UIScaler.MAX_SCALE)
        self.zoom_spin.setSingleStep(UIScaler.SCALE_STEP)
        self.zoom_spin.setAccessibleName("Zoom level")
        self.zoom_spin.setAccessibleDescription(
            "Set zoom level percentage - Alt+Z")
        zoom_label.setBuddy(self.zoom_spin)
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_spin)
        display_layout.addLayout(zoom_layout)

        layout.addWidget(display_group)

        # Detail section: Import settings
        import_group = QGroupBox("Import Settings")
        import_layout = QVBoxLayout(import_group)
        import_layout.setSpacing(10)

        dir_layout = QHBoxLayout()
        dir_label = QLabel("&Directory:")
        self.import_dir_edit = QLineEdit()
        self.import_dir_edit.setAccessibleName("Default import directory")
        self.import_dir_edit.setAccessibleDescription(
            "Default folder to scan for imports - Alt+D")
        dir_label.setBuddy(self.import_dir_edit)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.import_dir_edit, 1)

        self.browse_button = QPushButton("&Browse")
        self.browse_button.setAccessibleName("Browse")
        self.browse_button.setAccessibleDescription(
            "Browse for a default import directory - Alt+B")
        dir_layout.addWidget(self.browse_button)
        import_layout.addLayout(dir_layout)

        formats_layout = QHBoxLayout()
        formats_label = QLabel("F&ormats:")
        formats_layout.addWidget(formats_label)

        self.format_checks = {}
        for label, key in [
            ("MP3", "mp3"),
            ("M4A", "m4a"),
            ("M4B", "m4b"),
            ("FLAC", "flac"),
            ("OGG", "ogg"),
            ("WAV", "wav"),
            ("WMA", "wma"),
        ]:
            checkbox = QCheckBox(label)
            checkbox.setAccessibleName(f"{key.upper()} format")
            checkbox.setAccessibleDescription(
                f"Include {key.upper()} files in scan")
            self.format_checks[key] = checkbox
            formats_layout.addWidget(checkbox)

        formats_label.setBuddy(self.format_checks["mp3"])
        import_layout.addLayout(formats_layout)

        self.subfolders_check = QCheckBox("Include S&ubfolders")
        self.subfolders_check.setAccessibleName("Include subfolders")
        self.subfolders_check.setAccessibleDescription(
            "Include subfolders when scanning - Alt+U")
        import_layout.addWidget(self.subfolders_check)

        layout.addWidget(import_group)

        # Footer section: Status bar and action buttons
        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.save_button = QPushButton("Sa&ve")
        self.save_button.setAccessibleName("Save")
        self.save_button.setAccessibleDescription(
            "Save preferences and close - Alt+V")
        self.save_button.setDefault(False)
        self.save_button.setAutoDefault(False)
        footer_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("&Cancel")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription(
            "Discard changes and close - Alt+C or F4")
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        footer_layout.addWidget(self.cancel_button)

        layout.addLayout(footer_layout)

    def apply_control_styles(self):
        """Apply uniform control heights to inputs."""
        base_height = 20
        scale_pct = self.scaler.current_scale
        scaled_height = int(base_height * (scale_pct / 100.0))

        combo_style = f"""
            QComboBox {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QComboBox:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(base);
            }}
        """

        lineedit_style = f"""
            QLineEdit {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QLineEdit:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(base);
            }}
        """

        self.theme_combo.setStyleSheet(combo_style)
        self.preset_combo.setStyleSheet(combo_style)
        self.zoom_spin.setStyleSheet(combo_style)
        self.import_dir_edit.setStyleSheet(lineedit_style)

    def on_scale_changed(self, value: int):
        """Refresh control styles when zoom changes."""
        self.apply_control_styles()

    def load_settings(self):
        """Load settings from QSettings into the UI."""
        self._loading = True

        # Theme options
        self.theme_combo.clear()
        for display_name, theme_id in self.theme_manager.get_theme_names():
            self.theme_combo.addItem(display_name, theme_id)
        current_theme = self.theme_manager.current_theme_name
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        # Scale presets
        self.preset_combo.clear()
        for name in UIScaler.SCALE_PRESETS.keys():
            self.preset_combo.addItem(name)
        self.preset_combo.addItem("Custom")

        preset_name = self.scaler.get_preset_name()
        if preset_name not in UIScaler.SCALE_PRESETS:
            preset_name = "Custom"
        self.preset_combo.setCurrentText(preset_name)

        # Zoom level
        self.zoom_spin.setValue(self.scaler.current_scale)

        # Import settings
        import_dir = self.settings.value(
            "import/default_directory", "", type=str)
        include_subfolders = self.settings.value(
            "import/include_subfolders", True, type=bool)

        self.import_dir_edit.setText(import_dir)
        self.subfolders_check.setChecked(include_subfolders)

        for key in self.format_checks:
            default_value = True
            value = self.settings.value(
                f"import/formats/{key}", default_value, type=bool)
            self.format_checks[key].setChecked(value)

        self._loading = False

    def connect_signals(self):
        """Connect signals to handlers."""
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        self.zoom_spin.valueChanged.connect(self.on_zoom_changed)
        self.browse_button.clicked.connect(self.on_browse)

        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.on_cancel)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for the dialog."""
        close_shortcut = QShortcut(QKeySequence("F4"), self)
        close_shortcut.activated.connect(self.on_cancel)

    def on_theme_changed(self):
        """Apply theme change immediately."""
        if self._loading:
            return
        theme_id = self.theme_combo.currentData()
        if theme_id:
            self.theme_manager.set_theme(theme_id)
            announce_status_message(
                self.status_bar, "Theme applied")

    def on_preset_changed(self, preset_name: str):
        """Update zoom value to match preset."""
        if self._loading:
            return
        if preset_name in UIScaler.SCALE_PRESETS:
            value = UIScaler.SCALE_PRESETS[preset_name]
            if self.zoom_spin.value() != value:
                self.zoom_spin.setValue(value)

    def on_zoom_changed(self, value: int):
        """Apply zoom change immediately and update preset selection."""
        if self._loading:
            return
        if value != self.scaler.current_scale:
            self.scaler.set_scale(value)
            announce_status_message(
                self.status_bar, f"Zoom set to {value}%")

        preset_name = "Custom"
        for name, preset_value in UIScaler.SCALE_PRESETS.items():
            if preset_value == value:
                preset_name = name
                break

        if self.preset_combo.currentText() != preset_name:
            self._loading = True
            self.preset_combo.setCurrentText(preset_name)
            self._loading = False

    def on_browse(self):
        """Open folder browser for default import directory."""
        current_dir = self.import_dir_edit.text().strip() or ""
        selected = QFileDialog.getExistingDirectory(
            self, "Select Import Directory", current_dir)
        if selected:
            self.import_dir_edit.setText(selected)
            announce_status_message(
                self.status_bar, "Import directory selected")

    def on_save(self):
        """Save settings and close dialog."""
        self.settings.setValue(
            "import/default_directory", self.import_dir_edit.text().strip())
        self.settings.setValue(
            "import/include_subfolders", self.subfolders_check.isChecked())

        for key, checkbox in self.format_checks.items():
            self.settings.setValue(
                f"import/formats/{key}", checkbox.isChecked())

        announce_status_message(self.status_bar, "Preferences saved")
        self.accept()

    def on_cancel(self):
        """Discard changes and close dialog."""
        if self.theme_manager.current_theme_name != self._initial_theme:
            self.theme_manager.set_theme(self._initial_theme)
        if self.scaler.current_scale != self._initial_scale:
            self.scaler.set_scale(self._initial_scale)

        announce_status_message(self.status_bar, "Changes discarded")
        self.reject()

    def accept(self):
        """Handle dialog accept."""
        announce_dialog_closed(self)
        super().accept()

    def reject(self):
        """Handle dialog reject."""
        announce_dialog_closed(self)
        super().reject()
