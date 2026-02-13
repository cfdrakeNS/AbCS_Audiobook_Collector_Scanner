"""
Preferences Window
Basic preferences for display and import settings.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QSpinBox, QLineEdit, QTextEdit,
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

    IMPORT_SCENARIOS = [
        ("mass_standard", "Mass Standard Import"),
        ("series_from_directory", "Mass Import - Series From Directory"),
        ("series_from_filename", "Mass Import - Series From File Name"),
        ("single_item", "Single Author / Book Import"),
    ]

    SCENARIO_DESCRIPTIONS = {
        "mass_standard": (
            "Root contains author folders. Books may be in title folders, "
            "single files under author, or nested in series folders. "
            "Series extraction from path is conservative."
        ),
        "series_from_directory": (
            "Root contains author folders. Author subfolders are series names. "
            "Books are single files in series folders."
        ),
        "series_from_filename": (
            "Root contains author folders with single-file books. "
            "Series is parsed from file name text in parentheses."
        ),
        "single_item": (
            "Import one author folder, one series/book folder, or one file. "
            "File chooser filters by enabled audio formats."
        ),
    }

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

        scenario_layout = QHBoxLayout()
        scenario_label = QLabel("&Scenario:")
        self.import_scenario_combo = QComboBox()
        self.import_scenario_combo.setAccessibleName("Import scenario")
        self.import_scenario_combo.setAccessibleDescription(
            "Select import scenario mode - Alt+S")
        scenario_label.setBuddy(self.import_scenario_combo)
        scenario_layout.addWidget(scenario_label)
        scenario_layout.addWidget(self.import_scenario_combo, 1)
        import_layout.addLayout(scenario_layout)

        scenario_desc_label = QLabel("Scenario &Description:")
        self.scenario_description_edit = QTextEdit()
        self.scenario_description_edit.setReadOnly(True)
        self.scenario_description_edit.setAccessibleName(
            "Scenario description")
        self.scenario_description_edit.setAccessibleDescription(
            "Description of selected import scenario")
        self.scenario_description_edit.setMinimumHeight(80)
        scenario_desc_label.setBuddy(self.scenario_description_edit)
        import_layout.addWidget(scenario_desc_label)
        import_layout.addWidget(self.scenario_description_edit)

        author_fallback_layout = QHBoxLayout()
        author_fallback_label = QLabel("&Author Fallback:")
        self.author_fallback_combo = QComboBox()
        self.author_fallback_combo.setAccessibleName("Author fallback")
        self.author_fallback_combo.setAccessibleDescription(
            "Choose fallback for missing author tags")
        author_fallback_label.setBuddy(self.author_fallback_combo)
        author_fallback_layout.addWidget(author_fallback_label)
        author_fallback_layout.addWidget(self.author_fallback_combo, 1)
        import_layout.addLayout(author_fallback_layout)

        title_fallback_layout = QHBoxLayout()
        title_fallback_label = QLabel("T&itle Fallback:")
        self.title_fallback_combo = QComboBox()
        self.title_fallback_combo.setAccessibleName("Title fallback")
        self.title_fallback_combo.setAccessibleDescription(
            "Choose fallback for missing title tags")
        title_fallback_label.setBuddy(self.title_fallback_combo)
        title_fallback_layout.addWidget(title_fallback_label)
        title_fallback_layout.addWidget(self.title_fallback_combo, 1)
        import_layout.addLayout(title_fallback_layout)

        reader_keywords_layout = QHBoxLayout()
        reader_keywords_label = QLabel("&Reader Keywords:")
        self.reader_keywords_edit = QLineEdit()
        self.reader_keywords_edit.setAccessibleName("Reader keywords")
        self.reader_keywords_edit.setAccessibleDescription(
            "Comma-separated keywords for narrator parsing")
        reader_keywords_label.setBuddy(self.reader_keywords_edit)
        reader_keywords_layout.addWidget(reader_keywords_label)
        reader_keywords_layout.addWidget(self.reader_keywords_edit, 1)
        import_layout.addLayout(reader_keywords_layout)

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
        self.import_scenario_combo.setStyleSheet(combo_style)
        self.author_fallback_combo.setStyleSheet(combo_style)
        self.title_fallback_combo.setStyleSheet(combo_style)
        self.import_dir_edit.setStyleSheet(lineedit_style)
        self.reader_keywords_edit.setStyleSheet(lineedit_style)

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

        self.import_scenario_combo.clear()
        for value, label in self.IMPORT_SCENARIOS:
            self.import_scenario_combo.addItem(label, value)

        scenario_mode = self.settings.value(
            "import/scenario/mode", "mass_standard", type=str)
        scenario_index = self.import_scenario_combo.findData(scenario_mode)
        if scenario_index < 0:
            scenario_index = 0
        self.import_scenario_combo.setCurrentIndex(scenario_index)
        self.update_scenario_description()

        self.author_fallback_combo.clear()
        self.author_fallback_combo.addItem("None", "none")
        self.author_fallback_combo.addItem("Folder", "folder")
        author_fallback = self.settings.value(
            "import/fallback/author", "folder", type=str)
        author_index = self.author_fallback_combo.findData(author_fallback)
        self.author_fallback_combo.setCurrentIndex(
            author_index if author_index >= 0 else 0)

        self.title_fallback_combo.clear()
        self.title_fallback_combo.addItem("None", "none")
        self.title_fallback_combo.addItem("Folder", "folder")
        self.title_fallback_combo.addItem("File", "file")
        title_fallback = self.settings.value(
            "import/fallback/title", "file", type=str)
        title_index = self.title_fallback_combo.findData(title_fallback)
        self.title_fallback_combo.setCurrentIndex(
            title_index if title_index >= 0 else 0)

        reader_keywords = self.settings.value(
            "import/reader_keywords",
            "reader, read by, narrator, narrated by",
            type=str)
        self.reader_keywords_edit.setText(reader_keywords)

        self._loading = False

    def connect_signals(self):
        """Connect signals to handlers."""
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        self.zoom_spin.valueChanged.connect(self.on_zoom_changed)
        self.import_scenario_combo.currentIndexChanged.connect(
            self.on_import_scenario_changed)
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

    def update_scenario_description(self):
        """Update scenario description text for the selected scenario."""
        scenario_value = self.import_scenario_combo.currentData()
        description = self.SCENARIO_DESCRIPTIONS.get(scenario_value, "")
        self.scenario_description_edit.setPlainText(description)

    def on_import_scenario_changed(self):
        """Handle import scenario selection changes."""
        self.update_scenario_description()
        if self._loading:
            return
        announce_status_message(
            self.status_bar,
            f"Scenario selected: {self.import_scenario_combo.currentText()}")

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

        self.settings.setValue(
            "import/scenario/mode", self.import_scenario_combo.currentData())
        self.settings.setValue(
            "import/fallback/author", self.author_fallback_combo.currentData())
        self.settings.setValue(
            "import/fallback/title", self.title_fallback_combo.currentData())
        self.settings.setValue(
            "import/reader_keywords", self.reader_keywords_edit.text().strip())

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
