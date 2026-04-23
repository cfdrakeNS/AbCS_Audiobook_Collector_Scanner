"""
Preferences Window
Basic preferences for display and import settings.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QStatusBar,
    QMessageBox,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QApplication,
    QScrollArea,
    QWidget,
    QFrame,
)
from PySide6.QtCore import QSettings, Qt, QTimer, QEvent
from PySide6.QtGui import QShortcut, QKeySequence, QTextCursor
from shiboken6 import isValid
from datetime import datetime

from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_accessible_message_box_style
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.accessible_events import (
    announce_status_message,
    announce_dialog_opened,
    announce_dialog_closed,
)


class PreferencesWindow(QDialog):
    """
    Preferences dialog for display and import settings.
    """

    def __init__(self, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())

    def keyPressEvent(self, event):
        # Accessibility: Pressing Enter/Return on Browse button triggers file dialog
        if self.browse_button.hasFocus() and event.key() in (
            Qt.Key_Return,
            Qt.Key_Enter,
        ):
            self.on_browse()
            event.accept()
            return
        super().keyPressEvent(event)

    ALLOWED_ALT_LETTERS = {"A", "C", "D", "F", "O", "R", "S", "V"}

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
            "Uses book folder as series (Author/Series/Files). "
            "If folder path is ambiguous or does not match author, "
            "series is skipped and flagged with a warning."
        ),
        "series_from_filename": (
            "Parses first parenthesized block in file name as series. "
            "If that block ends in a number, title gets suffix: - NN."
        ),
        "single_item": (
            "Import one author folder, one series/book folder, or one file. "
            "Single-file picker uses enabled audio format filters."
        ),
    }

    def __init__(self, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)

        self.scaler = scaler
        self.theme_manager = theme_manager
        self.settings = QSettings("AbCS", "AudioBookCollector")

        self._loading = False
        self._initial_theme = self.theme_manager.current_theme_name
        self._initial_scale = self.scaler.current_scale
        self._initial_state = {}
        self._closing_via_handler = False
        self._default_status_message = "Ready"

        self.setup_ui()
        self.install_alt_key_filters()
        self.apply_control_styles()
        self.load_settings()
        self._initial_state = self._capture_state()
        self.connect_signals()
        self.register_shortcuts()
        self.scaler.scale_changed.connect(self.on_scale_changed)
        self.theme_manager.theme_changed.connect(self.on_application_theme_changed)

        title = "Preferences"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Application preferences for display and import settings"
        )
        self.resize(994, 747)
        QTimer.singleShot(0, self.update_scenario_description_height)

        announce_dialog_opened(self, title)
        self.set_status("Ready")

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        self.scroll_area.setWidget(content_widget)
        layout.addWidget(self.scroll_area, 1)

        # Header section: Display settings
        display_group = QGroupBox("Display Settings")

        # Apply scaled font to group box title
        from PySide6.QtGui import QFont

        display_font = QFont()
        display_font.setPointSize(self.scaler.get_scaled_size(14))
        display_font.setBold(True)
        display_group.setFont(display_font)
        display_layout = QHBoxLayout(display_group)
        display_layout.setSpacing(18)
        display_layout.addSpacing(6)
        display_label_width = 72

        theme_label = QLabel("Theme:")
        theme_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        theme_label.setMinimumWidth(display_label_width)
        self.theme_combo = QComboBox()
        self.theme_combo.setAccessibleName("Theme")
        self.theme_combo.setAccessibleDescription("Select application theme")
        theme_label.setBuddy(self.theme_combo)
        display_layout.addWidget(theme_label)
        display_layout.addWidget(self.theme_combo)

        preset_label = QLabel("Preset:")
        preset_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        preset_label.setMinimumWidth(display_label_width)
        self.preset_combo = QComboBox()
        self.preset_combo.setAccessibleName("Font scaling preset")
        self.preset_combo.setAccessibleDescription("Select font scaling preset")
        preset_label.setBuddy(self.preset_combo)
        display_layout.addWidget(preset_label)
        display_layout.addWidget(self.preset_combo)

        # Reduce spacing between preset and zoom by 1/2 (was 18)
        display_layout.addSpacing(9)

        zoom_label = QLabel("Zoom (%):")
        zoom_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        zoom_label.setMinimumWidth(display_label_width + 10)
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(UIScaler.MIN_SCALE, UIScaler.MAX_SCALE)
        self.zoom_spin.setSingleStep(UIScaler.SCALE_STEP)
        self.zoom_spin.setAccessibleName("Zoom level")
        self.zoom_spin.setAccessibleDescription("Set zoom level percentage")
        zoom_label.setBuddy(self.zoom_spin)
        display_layout.addWidget(zoom_label)
        display_layout.addWidget(self.zoom_spin)

        self.content_layout.addWidget(display_group)

        # Detail section: Import settings
        import_group = QGroupBox("Import Settings")

        import_group.setFont(display_font)
        import_group.setFont(display_font)
        import_layout = QVBoxLayout(import_group)
        import_layout.setSpacing(11)
        import_label_width = 180

        source_scope_group = QGroupBox("Path & Scope")

        source_scope_group.setFont(display_font)
        source_scope_group.setFont(display_font)
        source_scope_layout = QVBoxLayout(source_scope_group)
        source_scope_layout.setSpacing(8)

        fallback_group = QGroupBox("Fallback and Parsing Behavior")

        fallback_group.setFont(display_font)
        fallback_group.setFont(display_font)
        fallback_layout = QVBoxLayout(fallback_group)
        fallback_layout.setContentsMargins(8, 8, 8, 8)
        fallback_layout.setSpacing(8)

        fallback_checks_layout = QGridLayout()
        self.fallback_checks_layout = fallback_checks_layout
        fallback_checks_layout.setContentsMargins(0, 0, 0, 0)
        fallback_checks_layout.setHorizontalSpacing(20)
        fallback_checks_layout.setVerticalSpacing(0)

        validation_group = QGroupBox("Validation Rules")

        validation_group.setFont(display_font)
        validation_group.setFont(display_font)
        validation_layout = QVBoxLayout(validation_group)
        validation_layout.setSpacing(8)

        dir_layout = QHBoxLayout()
        dir_label = QLabel("Directory:")
        dir_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        dir_label.setMinimumWidth(import_label_width)
        self.import_dir_edit = QLineEdit()
        self.import_dir_edit.setAccessibleName("Default import directory")
        self.import_dir_edit.setAccessibleDescription(
            "Default folder to scan for imports"
        )
        dir_label.setBuddy(self.import_dir_edit)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.import_dir_edit, 1)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setAccessibleName("Browse")
        self.browse_button.setAccessibleDescription(
            "Browse for a default import directory"
        )
        self.browse_button.setDefault(False)
        self.browse_button.setAutoDefault(False)
        dir_layout.addWidget(self.browse_button)
        source_scope_layout.addLayout(dir_layout)

        formats_layout = QHBoxLayout()
        formats_layout.setContentsMargins(0, 0, 0, 0)
        formats_layout.setSpacing(8)
        formats_label = QLabel("Formats:")
        formats_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        formats_label.setMinimumWidth(import_label_width)
        formats_layout.addWidget(formats_label)

        self.format_checks = {}
        format_items = [
            ("MP3", "mp3"),
            ("M4A", "m4a"),
            ("M4B", "m4b"),
            ("FLAC", "flac"),
            ("OGG", "ogg"),
            ("WAV", "wav"),
            ("WMA", "wma"),
        ]
        for label, key in format_items:
            checkbox = QCheckBox(label)
            checkbox.setAccessibleName(f"{key.upper()} format")
            checkbox.setAccessibleDescription(f"Include {key.upper()} files in scan")
            self.format_checks[key] = checkbox
            formats_layout.addWidget(checkbox)

        formats_label.setBuddy(self.format_checks["mp3"])
        formats_layout.addStretch(1)
        source_scope_layout.addLayout(formats_layout)

        scenario_layout = QHBoxLayout()
        scenario_layout.setContentsMargins(0, 0, 0, 0)
        scenario_layout.setSpacing(8)

        scenario_label = QLabel("Scenario:")
        scenario_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        scenario_label.setMinimumWidth(import_label_width)
        self.import_scenario_combo = QComboBox()
        self.import_scenario_combo.setAccessibleName("Import scenario")
        self.import_scenario_combo.setAccessibleDescription(
            "Select import scenario mode"
        )
        scenario_label.setBuddy(self.import_scenario_combo)
        scenario_layout.addWidget(scenario_label)
        scenario_layout.addWidget(self.import_scenario_combo)
        scenario_layout.addStretch(1)
        source_scope_layout.addLayout(scenario_layout)

        scenario_desc_label = QLabel("Scenario Description:")
        scenario_desc_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        scenario_desc_label.setMinimumWidth(import_label_width)
        self.scenario_description_edit = QTextEdit()
        self.scenario_description_edit.setReadOnly(True)
        self.scenario_description_edit.setAccessibleName("Scenario description")
        self.scenario_description_edit.setAccessibleDescription(
            "Description of selected import scenario"
        )
        self.scenario_description_edit.setMinimumHeight(60)
        scenario_desc_label.setBuddy(self.scenario_description_edit)
        scenario_desc_layout = QHBoxLayout()
        scenario_desc_layout.setContentsMargins(0, 0, 0, 0)
        scenario_desc_layout.setSpacing(8)
        scenario_desc_layout.addWidget(scenario_desc_label)
        scenario_desc_layout.addWidget(self.scenario_description_edit, 1)
        source_scope_layout.addLayout(scenario_desc_layout)

        import_layout.addWidget(source_scope_group)

        self.author_fallback_checkbox = QCheckBox("Author fallback to folder?")
        self.author_fallback_checkbox.setAccessibleName("Author fallback to folder")
        self.author_fallback_checkbox.setAccessibleDescription(
            "If checked, missing author will fallback to folder name"
        )
        self.title_fallback_checkbox = QCheckBox("Title fallback to file?")
        self.title_fallback_checkbox.setAccessibleName("Title fallback to file")
        self.title_fallback_checkbox.setAccessibleDescription(
            "If checked, missing title will fallback to file name"
        )
        fallback_checks_layout.setColumnMinimumWidth(0, 0)
        self.author_fallback_checkbox.setMinimumWidth(0)
        fallback_checks_layout.addWidget(
            self.author_fallback_checkbox,
            0,
            0,
            alignment=Qt.AlignLeft | Qt.AlignVCenter,
        )
        fallback_checks_layout.addWidget(
            self.title_fallback_checkbox,
            0,
            1,
            alignment=Qt.AlignLeft | Qt.AlignVCenter,
        )
        fallback_checks_layout.setColumnStretch(0, 0)
        fallback_checks_layout.setColumnStretch(1, 0)
        fallback_layout.addLayout(fallback_checks_layout)

        reader_keywords_layout = QHBoxLayout()
        reader_keywords_layout.setContentsMargins(0, 0, 0, 0)
        reader_keywords_layout.setSpacing(8)
        reader_keywords_label = QLabel("Reader Keywords:")
        reader_keywords_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        reader_keywords_label.setMinimumWidth(import_label_width)
        self.reader_keywords_edit = QLineEdit()
        self.reader_keywords_edit.setAccessibleName("Reader keywords")
        self.reader_keywords_edit.setAccessibleDescription(
            "Comma-separated keywords for narrator parsing"
        )
        reader_keywords_label.setBuddy(self.reader_keywords_edit)
        reader_keywords_layout.addWidget(reader_keywords_label)
        self.reader_keywords_edit.setMinimumWidth(320)
        reader_keywords_layout.addWidget(self.reader_keywords_edit)
        reader_keywords_layout.addStretch(1)
        fallback_layout.addLayout(reader_keywords_layout)
        import_layout.addWidget(fallback_group)

        import_layout.addSpacing(self.scaler.get_scaled_size(8))

        self.rules_section_text = QTextEdit()
        self.rules_section_text.setReadOnly(True)
        self.rules_section_text.setTabChangesFocus(True)
        # self.rules_section_text.setAccessibleName(
        #     "Author and title rules description")
        # self.rules_section_text.setAccessibleDescription(
        #     "")
        self.rules_section_text.setFocusPolicy(Qt.StrongFocus)
        self.rules_section_text.setTextInteractionFlags(Qt.TextSelectableByKeyboard)
        self.rules_section_text.setPlainText(
            "Author/Title Rules: configure severity for metadata consistency checks."
        )
        self._fit_readonly_section_text_height(self.rules_section_text)

        rules_group = QGroupBox("")
        rules_group.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        rules_layout = QGridLayout(rules_group)
        rules_layout.setContentsMargins(2, 4, 2, 4)
        rules_layout.setHorizontalSpacing(6)
        rules_layout.setVerticalSpacing(6)
        rules_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        severity_header_left = QLabel("Severity")
        severity_header_left.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rules_layout.addWidget(severity_header_left, 0, 1)

        severity_header_right = QLabel("Severity")
        severity_header_right.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rules_layout.addWidget(severity_header_right, 0, 3)

        author_in_title_label = QLabel("Author in Title:")
        author_in_title_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rule_author_in_title_severity = QComboBox()
        self.rule_author_in_title_severity.setAccessibleName("Author in Title severity")
        self.rule_author_in_title_severity.setAccessibleDescription(
            "Set severity or None for Author in Title rule"
        )
        author_in_title_label.setBuddy(self.rule_author_in_title_severity)
        rules_layout.addWidget(author_in_title_label, 1, 0)
        rules_layout.addWidget(self.rule_author_in_title_severity, 1, 1)

        title_in_author_label = QLabel("Title in Author:")
        title_in_author_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rule_title_in_author_severity = QComboBox()
        self.rule_title_in_author_severity.setAccessibleName("Title in Author severity")
        self.rule_title_in_author_severity.setAccessibleDescription(
            "Set severity or None for Title in Author rule"
        )
        title_in_author_label.setBuddy(self.rule_title_in_author_severity)
        rules_layout.addWidget(title_in_author_label, 1, 2)
        rules_layout.addWidget(self.rule_title_in_author_severity, 1, 3)

        unknown_author_label = QLabel("Unknown/Various:")
        unknown_author_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rule_unknown_author_severity = QComboBox()
        self.rule_unknown_author_severity.setAccessibleName(
            "Unknown or various author severity"
        )
        self.rule_unknown_author_severity.setAccessibleDescription(
            "Set severity or None for unknown or various author rule"
        )
        unknown_author_label.setBuddy(self.rule_unknown_author_severity)
        rules_layout.addWidget(unknown_author_label, 2, 0)
        rules_layout.addWidget(self.rule_unknown_author_severity, 2, 1)

        min_title_label = QLabel("Min Title Length:")
        min_title_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        min_title_config_layout = QHBoxLayout()
        min_title_config_layout.setContentsMargins(0, 0, 0, 0)
        min_title_config_layout.setSpacing(6)
        self.rule_min_title_value = QSpinBox()
        self.rule_min_title_value.setRange(1, 100)
        self.rule_min_title_value.setAccessibleName("Minimum title length value")
        self.rule_min_title_severity = QComboBox()
        self.rule_min_title_severity.setAccessibleName("Minimum title length severity")
        self.rule_min_title_severity.setAccessibleDescription(
            "Set severity or None for minimum title length rule"
        )
        min_title_config_layout.addWidget(self.rule_min_title_value)
        min_title_config_layout.addWidget(self.rule_min_title_severity)
        min_title_label.setBuddy(self.rule_min_title_value)
        rules_layout.addWidget(min_title_label, 2, 2)
        rules_layout.addLayout(min_title_config_layout, 2, 3)

        duplicate_match_label = QLabel("Duplicate Match:")
        duplicate_match_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.duplicate_match_combo = QComboBox()
        self.duplicate_match_combo.setAccessibleName("Duplicate matching mode")
        self.duplicate_match_combo.setAccessibleDescription(
            "Choose whether duplicate checks include collection"
        )
        self.duplicate_match_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.duplicate_match_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        duplicate_match_label.setBuddy(self.duplicate_match_combo)
        rules_layout.addWidget(duplicate_match_label, 3, 0)
        rules_layout.addWidget(self.duplicate_match_combo, 3, 1)

        duplicate_fuzzy_label = QLabel("Fuzzy Duplicate (%):")
        duplicate_fuzzy_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.duplicate_fuzzy_spin = QSpinBox()
        self.duplicate_fuzzy_spin.setRange(0, 100)
        self.duplicate_fuzzy_spin.setSuffix("%")
        self.duplicate_fuzzy_spin.setSingleStep(5)
        self.duplicate_fuzzy_spin.setAccessibleName("Duplicate fuzzy threshold")
        self.duplicate_fuzzy_spin.setAccessibleDescription(
            "Optional fuzzy duplicate threshold percentage. 0 disables fuzzy duplicate matching"
        )
        duplicate_fuzzy_label.setBuddy(self.duplicate_fuzzy_spin)
        rules_layout.addWidget(duplicate_fuzzy_label, 3, 2)
        rules_layout.addWidget(self.duplicate_fuzzy_spin, 3, 3)

        file_structure_label = QLabel("File Structure:")
        file_structure_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        file_structure_config_layout = QHBoxLayout()
        file_structure_config_layout.setContentsMargins(0, 0, 0, 0)
        file_structure_config_layout.setSpacing(6)
        self.rule_file_structure_pattern = QComboBox()
        self.rule_file_structure_pattern.setAccessibleName(
            "Expected file structure pattern"
        )
        self.rule_file_structure_pattern.setAccessibleDescription(
            "Select expected folder structure pattern for imports"
        )
        self.rule_file_structure_severity = QComboBox()
        self.rule_file_structure_severity.setAccessibleName("File structure severity")
        self.rule_file_structure_severity.setAccessibleDescription(
            "Set severity or None for file structure rule"
        )
        file_structure_config_layout.addWidget(self.rule_file_structure_pattern)
        file_structure_config_layout.addWidget(self.rule_file_structure_severity)
        file_structure_label.setBuddy(self.rule_file_structure_pattern)
        rules_layout.addWidget(file_structure_label, 4, 0)
        rules_layout.addLayout(file_structure_config_layout, 4, 1)

        year_quality_label = QLabel("Year Consistency:")
        year_quality_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        year_quality_layout = QHBoxLayout()
        year_quality_layout.setContentsMargins(0, 0, 0, 0)
        year_quality_layout.setSpacing(6)
        self.rule_year_quality_severity = QComboBox()
        self.rule_year_quality_severity.setAccessibleName("Year range severity")
        self.rule_year_quality_severity.setAccessibleDescription(
            "Set severity or None for year consistency rule (>1800 and <= current year)"
        )
        year_quality_layout.addWidget(self.rule_year_quality_severity)
        year_quality_label.setBuddy(self.rule_year_quality_severity)
        rules_layout.addWidget(year_quality_label, 4, 2)
        rules_layout.addLayout(year_quality_layout, 4, 3)

        rule_severity_combos = (
            self.rule_author_in_title_severity,
            self.rule_title_in_author_severity,
            self.rule_unknown_author_severity,
            self.rule_min_title_severity,
            self.rule_file_structure_severity,
            self.rule_year_quality_severity,
        )
        for combo in rule_severity_combos:
            combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        validation_layout.addWidget(self.rules_section_text)
        validation_layout.addWidget(rules_group, 0, Qt.AlignLeft)
        import_layout.addWidget(validation_group)
        import_layout.addSpacing(self.scaler.get_scaled_size(8))

        self.autocorrect_section_text = QTextEdit()
        self.autocorrect_section_text.setReadOnly(True)
        self.autocorrect_section_text.setTabChangesFocus(True)
        self.autocorrect_section_text.setFocusPolicy(Qt.StrongFocus)
        self.autocorrect_section_text.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard
        )
        self.autocorrect_section_text.setPlainText(
            "Auto-Correction: applies to Author, Series, Genre, and Narrator."
        )
        self._fit_readonly_section_text_height(self.autocorrect_section_text)
        self._sync_section_label_heights()

        self.autocorrect_group = QGroupBox("")
        self.autocorrect_group.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred
        )
        self.autocorrect_layout = QHBoxLayout(self.autocorrect_group)
        self.autocorrect_layout.setContentsMargins(4, 2, 4, 2)
        self.autocorrect_layout.setSpacing(35)

        self.autocorrect_layout.addStretch(1)

        self.content_layout.addWidget(import_group)

        # Footer section: Status bar and action buttons
        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.restore_defaults_button = QPushButton("Restore D&efaults")
        self.restore_defaults_button.setAccessibleName("Restore Defaults")
        self.restore_defaults_button.setAccessibleDescription(
            "Reset all preferences to default values - Alt+R"
        )
        self.restore_defaults_button.setDefault(False)
        self.restore_defaults_button.setAutoDefault(False)
        footer_layout.addWidget(self.restore_defaults_button)

        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save")
        self.save_button.setAccessibleDescription("Save preferences and close - Alt+S")
        self.save_button.setDefault(True)
        self.save_button.setAutoDefault(True)
        footer_layout.addWidget(self.save_button)

        layout.addLayout(footer_layout)

    def _apply_compact_combo_widths(self):
        """Apply content-fit width to all combo boxes in Preferences."""
        # This method is now a no-op because _fit_combo_to_text is missing
        pass

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

        button_style = f"""
            QPushButton {{
                padding: 4px 12px;
                min-height: {max(scaled_height - 4, 14)}px;
                max-height: {max(scaled_height - 4, 14)}px;
                border: 1px solid palette(dark);
                border-radius: 3px;
                background-color: palette(button);
            }}
            QPushButton:focus {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: 2px solid palette(dark);
            }}
        """

        self.theme_combo.setStyleSheet(combo_style)
        self.preset_combo.setStyleSheet(combo_style)
        self.zoom_spin.setStyleSheet(combo_style)
        self.import_scenario_combo.setStyleSheet(combo_style)
        format_checkbox_style = f"""
            QCheckBox {{
                min-height: {max(int(scaled_height * 1.2), 22)}px;
                padding-top: 0px;
                padding-bottom: 0px;
                margin-top: 0px;
                margin-bottom: 0px;
            }}
        """
        self.author_fallback_checkbox.setStyleSheet(format_checkbox_style)
        self.title_fallback_checkbox.setStyleSheet(format_checkbox_style)
        self.rule_author_in_title_severity.setStyleSheet(combo_style)
        self.rule_title_in_author_severity.setStyleSheet(combo_style)
        self.rule_unknown_author_severity.setStyleSheet(combo_style)
        self.rule_min_title_severity.setStyleSheet(combo_style)
        self.duplicate_match_combo.setStyleSheet(combo_style)
        self.duplicate_fuzzy_spin.setStyleSheet(combo_style)
        self.rule_file_structure_pattern.setStyleSheet(combo_style)
        self.rule_file_structure_severity.setStyleSheet(combo_style)
        self.rule_year_quality_severity.setStyleSheet(combo_style)
        # Use theme manager styling for text boxes and combo boxes
        self.import_dir_edit.setStyleSheet("")  # Clear local style
        self.reader_keywords_edit.setStyleSheet("")  # Clear local style
        self.rule_min_title_value.setStyleSheet(combo_style)
        self.browse_button.setStyleSheet(button_style)
        self.restore_defaults_button.setStyleSheet(button_style)
        self.save_button.setStyleSheet(button_style)

        format_checkbox_style = f"""
            QCheckBox {{
                min-height: {max(int(scaled_height * 1.2), 22)}px;
                padding-top: 0px;
                padding-bottom: 0px;
                margin-top: 0px;
                margin-bottom: 0px;
            }}
        """
        for checkbox in self.format_checks.values():
            checkbox.setStyleSheet(format_checkbox_style)

        section_text_style = f"""
            QTextEdit {{
                border: 1px solid palette(dark);
                border-radius: 3px;
                padding: 2px 4px;
                background-color: palette(base);
            }}
            QTextEdit:focus {{
                border: 2px solid palette(highlight);
            }}
        """
        if hasattr(self, "rules_section_text"):
            self.rules_section_text.setStyleSheet(section_text_style)
        if hasattr(self, "autocorrect_section_text"):
            self.autocorrect_section_text.setStyleSheet(section_text_style)

    def on_scale_changed(self, value: int):
        """Refresh control styles when zoom changes."""
        self.apply_control_styles()
        self._apply_compact_combo_widths()
        self._sync_fallback_column_alignment()
        if hasattr(self, "rules_section_text"):
            self._fit_readonly_section_text_height(self.rules_section_text)
        if hasattr(self, "autocorrect_section_text"):
            self._fit_readonly_section_text_height(self.autocorrect_section_text)
        self._sync_section_label_heights()
        self._sync_autocorrect_group_width()
        self.update_scenario_description_height()

    def _sync_autocorrect_group_width(self):
        """Set Auto-Correction frame width so column spacing is visible."""
        if not hasattr(self, "autocorrect_group") or not hasattr(
            self, "autocorrect_layout"
        ):
            return

        content_width = self.autocorrect_layout.sizeHint().width()
        target_width = content_width + self.scaler.get_scaled_size(24)
        min_width = self.scaler.get_scaled_size(420)
        target_width = max(min_width, target_width)

        self.autocorrect_group.setMinimumWidth(target_width)
        self.autocorrect_group.setMaximumWidth(target_width)

    def _sync_fallback_column_alignment(self):
        """Align fallback checkbox columns with Options checkbox columns."""
        if not hasattr(self, "fallback_checks_layout") or not hasattr(
            self, "author_fallback_checkbox"
        ):
            return
        self.fallback_checks_layout.setColumnMinimumWidth(0, 0)
        self.author_fallback_checkbox.setMinimumWidth(0)
        self.fallback_checks_layout.setHorizontalSpacing(0)

    def _sync_section_label_heights(self):
        """Keep section label boxes the same height for visual consistency."""
        if not hasattr(self, "rules_section_text") or not hasattr(
            self, "autocorrect_section_text"
        ):
            return

        target_height = self.rules_section_text.height()
        self.autocorrect_section_text.setMinimumHeight(target_height)
        self.autocorrect_section_text.setMaximumHeight(target_height)

    def _fit_readonly_section_text_height(self, widget: QTextEdit):
        """Size a read-only section textbox to just fit its content."""
        text = widget.toPlainText()
        if not text:
            text = " "

        metrics = widget.fontMetrics()
        width = max(widget.viewport().width(), 300)
        rect = metrics.boundingRect(
            0,
            0,
            width,
            200,
            Qt.TextWordWrap,
            text,
        )

        doc_margin = int(widget.document().documentMargin() * 2)
        frame_margin = int(widget.frameWidth() * 2)
        target_height = rect.height() + doc_margin + frame_margin + 8
        widget.setMinimumHeight(target_height)
        widget.setMaximumHeight(target_height)

    def resizeEvent(self, event):
        """Keep scenario description height fitted to current width."""
        super().resizeEvent(event)
        self._sync_fallback_column_alignment()
        self.update_scenario_description_height()

    def update_scenario_description_height(self):
        """Set description height based on current width."""
        if not hasattr(self, "scenario_description_edit"):
            return

        field_width = max(
            self.import_scenario_combo.width(),
            self.scenario_description_edit.viewport().width(),
            260,
        )
        longest_text = max(self.SCENARIO_DESCRIPTIONS.values(), key=len)
        metrics = self.scenario_description_edit.fontMetrics()
        text_rect = metrics.boundingRect(
            0, 0, max(field_width - 8, 120), 2000, Qt.TextWordWrap, longest_text
        )

        document_margin = int(
            self.scenario_description_edit.document().documentMargin() * 2
        )
        frame_margin = int(self.scenario_description_edit.frameWidth() * 2)
        extra_padding = self.scaler.get_scaled_size(8)
        target_height = (
            text_rect.height() + document_margin + frame_margin + extra_padding
        )

        min_height = self.scaler.get_scaled_size(52)
        max_height = self.scaler.get_scaled_size(120)
        target_height = max(min_height, min(target_height, max_height))

        self.scenario_description_edit.setMinimumHeight(target_height)
        self.scenario_description_edit.setMaximumHeight(target_height)

    def _capture_state(self) -> dict:
        """Capture current UI state for unsaved-change detection."""
        return {
            "theme": self.theme_combo.currentData(),
            "scale": self.zoom_spin.value(),
            "import_directory": self.import_dir_edit.text().strip(),
            "formats": tuple(
                self.format_checks[key].isChecked()
                for key in sorted(self.format_checks.keys())
            ),
            "scenario_mode": self.import_scenario_combo.currentData(),
            "author_fallback": self.author_fallback_checkbox.isChecked(),
            "title_fallback": self.title_fallback_checkbox.isChecked(),
            "reader_keywords": self.reader_keywords_edit.text().strip(),
            "rule_author_in_title": (self.rule_author_in_title_severity.currentData(),),
            "rule_title_in_author": (self.rule_title_in_author_severity.currentData(),),
            "rule_unknown_author": (self.rule_unknown_author_severity.currentData(),),
            "rule_min_title": (
                self.rule_min_title_value.value(),
                self.rule_min_title_severity.currentData(),
            ),
            "rule_file_structure": (
                self.rule_file_structure_pattern.currentData(),
                self.rule_file_structure_severity.currentData(),
            ),
            "rule_year_quality": self.rule_year_quality_severity.currentData(),
            "duplicate_match_mode": self.duplicate_match_combo.currentData(),
            "duplicate_fuzzy_threshold": self.duplicate_fuzzy_spin.value(),
            "autocorrect": (),
        }

    def _has_unsaved_changes(self) -> bool:
        """Return True when preferences differ from initial dialog state."""
        return self._capture_state() != self._initial_state

    def _confirm_exit_with_changes(self) -> int:
        """Ask whether to save changes before exit using standardized message box."""
        from src.accessibility.style_helpers import exec_styled_message_box
        from src.accessibility.icon_helper import get_app_icon

        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Unsaved Changes",
            text="You have unsaved changes.\n\n"
            "Yes = Save and close\n"
            "No = Continue editing\n"
            "Cancel = Revert and close",
            buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            default_button=QMessageBox.Yes,
            window_icon=get_app_icon(),
        )
        return reply

    def _discard_and_close(self):
        """Discard transient changes and close dialog."""
        if self.theme_manager.current_theme_name != self._initial_theme:
            self.theme_manager.set_theme(self._initial_theme)
        if self.scaler.current_scale != self._initial_scale:
            self.scaler.set_scale(self._initial_scale)

        self.set_status("Changes discarded")
        self._closing_via_handler = True
        try:
            announce_dialog_closed(self)
            super().reject()
        finally:
            self._closing_via_handler = False

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
        import_dir = self.settings.value("import/default_directory", "", type=str)

        self.import_dir_edit.setText(import_dir)

        for key in self.format_checks:
            default_value = True
            value = self.settings.value(
                f"import/formats/{key}", default_value, type=bool
            )
            self.format_checks[key].setChecked(value)
        self.settings.setValue("import/include_subfolders", True)

        self.import_scenario_combo.clear()
        for value, label in self.IMPORT_SCENARIOS:
            self.import_scenario_combo.addItem(label, value)

        scenario_mode = self.settings.value(
            "import/scenario/mode", "mass_standard", type=str
        )
        scenario_index = self.import_scenario_combo.findData(scenario_mode)
        if scenario_index < 0:
            scenario_index = 0
        self.import_scenario_combo.setCurrentIndex(scenario_index)
        self.update_scenario_description()

        author_fallback_to_folder = self.settings.value(
            "import/fallback/author_to_folder", True, type=bool
        )
        self.author_fallback_checkbox.setChecked(author_fallback_to_folder)

        title_fallback_to_file = self.settings.value(
            "import/fallback/title_to_file", True, type=bool
        )
        self.title_fallback_checkbox.setChecked(title_fallback_to_file)

        reader_keywords = self.settings.value(
            "import/reader_keywords", "reader, read by, narrator, narrated by", type=str
        )
        self.reader_keywords_edit.setText(reader_keywords)

        for combo in (
            self.rule_author_in_title_severity,
            self.rule_title_in_author_severity,
            self.rule_unknown_author_severity,
            self.rule_min_title_severity,
            self.rule_file_structure_severity,
            self.rule_year_quality_severity,
        ):
            combo.clear()
            combo.addItem("None", "none")
            combo.addItem("Error", "error")
            combo.addItem("Warning", "warning")

        self.rule_file_structure_pattern.clear()
        self.rule_file_structure_pattern.addItem("Author/Title", "author_title")
        self.rule_file_structure_pattern.addItem(
            "Year/Author/Title", "year_author_title"
        )
        self.rule_file_structure_pattern.addItem("Either", "either")

        self.duplicate_match_combo.clear()
        self.duplicate_match_combo.addItem(
            "Title + Author + Collection", "title_author"
        )
        self.duplicate_match_combo.addItem("Title + Author + Year", "title_author_year")
        self.duplicate_match_combo.addItem(
            "Title + Author + Year + Collection", "title_author_year_collection"
        )
        duplicate_mode = self.settings.value(
            "import/rules/duplicate/match_mode",
            "title_author_year_collection",
            type=str,
        )
        if duplicate_mode == "with_collection":
            duplicate_mode = "title_author_year_collection"
        elif duplicate_mode == "ignore_collection":
            duplicate_mode = "title_author_year"
        elif duplicate_mode == "title_author_year_ignore_collection":
            duplicate_mode = "title_author_year"
        elif duplicate_mode == "title_author_ignore_collection":
            duplicate_mode = "title_author_year"
        duplicate_index = self.duplicate_match_combo.findData(duplicate_mode)
        self.duplicate_match_combo.setCurrentIndex(
            0 if duplicate_index < 0 else duplicate_index
        )

        self.duplicate_fuzzy_spin.setValue(
            self.settings.value(
                "import/rules/duplicate/fuzzy_threshold",
                0,
                type=int,
            )
        )

        author_in_title_enabled = self.settings.value(
            "import/rules/author_name_in_title/enabled",
            True,
            type=bool,
        )
        author_in_title_severity = self.settings.value(
            "import/rules/author_name_in_title/severity",
            "warning",
            type=str,
        )
        if not author_in_title_enabled:
            author_in_title_severity = "none"
        index = self.rule_author_in_title_severity.findData(author_in_title_severity)
        self.rule_author_in_title_severity.setCurrentIndex(0 if index < 0 else index)

        title_in_author_enabled = self.settings.value(
            "import/rules/title_in_author_name/enabled",
            True,
            type=bool,
        )
        title_in_author_severity = self.settings.value(
            "import/rules/title_in_author_name/severity",
            "warning",
            type=str,
        )
        if not title_in_author_enabled:
            title_in_author_severity = "none"
        index = self.rule_title_in_author_severity.findData(title_in_author_severity)
        self.rule_title_in_author_severity.setCurrentIndex(0 if index < 0 else index)

        unknown_author_enabled = self.settings.value(
            "import/rules/unknown_or_various_author/enabled",
            True,
            type=bool,
        )
        unknown_author_severity = self.settings.value(
            "import/rules/unknown_or_various_author/severity",
            "warning",
            type=str,
        )
        if not unknown_author_enabled:
            unknown_author_severity = "none"
        index = self.rule_unknown_author_severity.findData(unknown_author_severity)
        self.rule_unknown_author_severity.setCurrentIndex(0 if index < 0 else index)

        min_title_enabled = self.settings.value(
            "import/rules/minimum_title_length/enabled",
            False,
            type=bool,
        )
        self.rule_min_title_value.setValue(
            self.settings.value(
                "import/rules/minimum_title_length/value",
                3,
                type=int,
            )
        )
        min_title_severity = self.settings.value(
            "import/rules/minimum_title_length/severity",
            "warning",
            type=str,
        )
        if not min_title_enabled:
            min_title_severity = "none"
        index = self.rule_min_title_severity.findData(min_title_severity)
        self.rule_min_title_severity.setCurrentIndex(0 if index < 0 else index)

        file_structure_enabled = self.settings.value(
            "import/rules/file_structure/enabled",
            False,
            type=bool,
        )
        file_structure_severity = self.settings.value(
            "import/rules/file_structure/severity",
            "warning",
            type=str,
        )
        if not file_structure_enabled:
            file_structure_severity = "none"
        file_structure_index = self.rule_file_structure_severity.findData(
            file_structure_severity
        )
        self.rule_file_structure_severity.setCurrentIndex(
            0 if file_structure_index < 0 else file_structure_index
        )

        file_structure_pattern = self.settings.value(
            "import/rules/file_structure/pattern",
            "author_title",
            type=str,
        )
        file_structure_pattern_index = self.rule_file_structure_pattern.findData(
            file_structure_pattern
        )
        self.rule_file_structure_pattern.setCurrentIndex(
            0 if file_structure_pattern_index < 0 else file_structure_pattern_index
        )

        year_quality_enabled = self.settings.value(
            "import/rules/year_out_of_range/enabled",
            False,
            type=bool,
        )
        year_quality_severity = self.settings.value(
            "import/rules/year_out_of_range/severity",
            "warning",
            type=str,
        )
        if not year_quality_enabled:
            year_quality_severity = "none"
        year_quality_index = self.rule_year_quality_severity.findData(
            year_quality_severity
        )
        self.rule_year_quality_severity.setCurrentIndex(
            0 if year_quality_index < 0 else year_quality_index
        )

        self._apply_compact_combo_widths()
        QTimer.singleShot(0, self._sync_fallback_column_alignment)

        self._loading = False

    def connect_signals(self):
        """Connect signals to handlers."""
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        self.zoom_spin.valueChanged.connect(self.on_zoom_changed)
        self.import_scenario_combo.currentIndexChanged.connect(
            self.on_import_scenario_changed
        )
        self.browse_button.clicked.connect(self.on_browse)
        self.restore_defaults_button.clicked.connect(self.on_restore_defaults)
        self.save_button.clicked.connect(self.on_save)

    def register_shortcuts(self):
        """Register keyboard shortcuts using ShortcutManager (except Alt+/)."""
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext

        mgr = get_shortcut_manager()
        callback_map = {
            "theme_combo": self.focus_display_section,
            "import_dir_edit": self.focus_source_scope_section,
            "browse_button": self.on_browse,
            "author_fallback_checkbox": self.focus_fallback_section,
            "rules_section_text": self.focus_validation_section,
            "autocorrect_section_text": self.focus_autocorrect_section,
            "restore_defaults_button": self.on_restore_defaults,
            "save_button": self.on_save,
        }
        mgr.register_alt_shortcuts(
            self, ShortcutContext.PREFERENCES_WINDOW, callback_map
        )
        # F1 help shortcut remains local
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)
        # Alt+/ remains local for status bar read
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        # Escape key for cancel functionality
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.on_cancel)

    def _focus_section_widget(self, widget, section_name: str):
        """Focus first widget in a section and announce context."""
        if widget is None or not isValid(widget):
            return
        self.scroll_area.ensureWidgetVisible(widget)
        widget.setFocus()
        self.set_status(f"{section_name} section")

    def focus_display_section(self):
        """Focus first control in Display section."""
        self._focus_section_widget(self.theme_combo, "Display")

    def focus_source_scope_section(self):
        """Focus first control in Path & Scope section."""
        self._focus_section_widget(self.import_dir_edit, "Path & Scope")

    def focus_options_section(self):
        """Focus first control in Options section."""

    def focus_fallback_section(self):
        """Focus first control in Fallback and Parsing section."""
        self._focus_section_widget(
            self.author_fallback_checkbox, "Fallback and Parsing Behavior"
        )

    def focus_validation_section(self):
        """Focus first control in Validation Rules section."""
        self._focus_section_widget(self.rules_section_text, "Validation Rules")

    def focus_autocorrect_section(self):
        """Focus first control in Auto-Correction section."""
        self._focus_section_widget(self.autocorrect_section_text, "Auto-Correction")

    def set_status(self, message: str, announce: bool = False):
        """Set status bar message with optional screen reader announcement."""
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def on_read_status_bar(self):
        """Read current status bar message (Alt+/)."""
        status_text = self.status_bar.currentMessage() or self._default_status_message
        self.set_status(status_text, announce=True)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Preferences")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(520, 480)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        shortcuts = [
            ("Alt+D", "Display section"),
            ("Alt+P", "Path & Scope section"),
            ("Alt+B", "Browse for default import directory"),
            ("Alt+F", "Fallback and Parsing Behavior section"),
            ("Alt+V", "Validation Rules section"),
            ("Alt+R", "Restore Defaults"),
            ("Alt+S", "Save"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
            ("Tab/Shift+Tab", "Move between controls in the current section"),
        ]
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
        )

        shortcuts = get_accessible_shortcuts_list(shortcuts)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)

        # Disable hover highlighting for low-vision comfort
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)

        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, desc) in enumerate(shortcuts):
            item = QTableWidgetItem(f"{desc} - {key}")
            item.setData(Qt.AccessibleTextRole, f"{desc}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)
        layout.addWidget(table)
        dlg.exec()

    def install_alt_key_filters(self):
        """Install key filters to block unmapped Alt+letter input."""
        widgets = []
        widgets.extend(self.findChildren(QLineEdit))
        widgets.extend(self.findChildren(QTextEdit))
        widgets.extend(self.findChildren(QComboBox))
        widgets.extend(self.findChildren(QSpinBox))
        for widget in widgets:
            widget.installEventFilter(self)

    def eventFilter(self, source, event):
        """Block Alt+letter input for letters that are not mapped shortcuts."""
        if event.type() == QEvent.Wheel and isinstance(source, (QComboBox, QSpinBox)):
            event.accept()
            return True

        if event.type() == QEvent.KeyPress and isinstance(source, QComboBox):
            key = event.key()
            modifiers = event.modifiers()
            if key in (Qt.Key_Up, Qt.Key_Down):
                if not (modifiers & Qt.AltModifier):
                    QApplication.beep()
                    return True

        if event.type() == QEvent.FocusIn:
            if isinstance(source, QLineEdit):
                QTimer.singleShot(
                    0,
                    lambda w=source: (
                        (w.setCursorPosition(len(w.text())), w.deselect())
                        if w is not None and w is not getattr(w, "deleted", False)
                        else None
                    ),
                )
            elif isinstance(source, QTextEdit):
                QTimer.singleShot(0, lambda w=source: self._safe_move_cursor(w))
            elif isinstance(source, QComboBox):
                QTimer.singleShot(
                    0,
                    lambda w=source: self._safe_move_embedded_lineedit_cursor(w),
                )
            elif isinstance(source, QSpinBox):
                QTimer.singleShot(
                    0,
                    lambda w=source: self._safe_move_embedded_lineedit_cursor(w),
                )

        if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
            event.accept()
            return True

        return super().eventFilter(source, event)

    @staticmethod
    def _safe_move_cursor(widget):
        """Move cursor safely on QTextEdit that may be deleted by the time the timer fires."""
        if widget is None or not isValid(widget):
            return
        try:
            widget.moveCursor(QTextCursor.End)
        except RuntimeError:
            pass

    @staticmethod
    def _safe_move_embedded_lineedit_cursor(widget):
        """Move cursor safely for combo/spin embedded line edits."""
        if widget is None or not isValid(widget):
            return
        try:
            line_edit = widget.lineEdit()
        except RuntimeError:
            return
        if line_edit is None or not isValid(line_edit):
            return
        try:
            line_edit.setCursorPosition(len(line_edit.text()))
            line_edit.deselect()
        except RuntimeError:
            pass

    def on_theme_changed(self):
        """Apply theme change immediately."""
        if self._loading:
            return
        theme_id = self.theme_combo.currentData()
        if theme_id:
            self.theme_manager.set_theme(theme_id)

            parent = self.parent()
            if parent:
                if hasattr(parent, "apply_control_styles"):
                    parent.apply_control_styles()
                if hasattr(parent, "refresh_books"):
                    parent.refresh_books()
                if hasattr(parent, "table") and parent.table:
                    parent.table.viewport().update()

            announce_status_message(self.status_bar, "Theme applied")

    def on_application_theme_changed(self, _theme_name: str):
        """Refresh controls immediately when any window changes the app theme."""
        self.apply_control_styles()

        for widget in [self, *self.findChildren(QWidget)]:
            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)
            # QListView/QAbstractItemView update() overloads can require an argument.
            # Refresh the viewport directly when available.
            if hasattr(widget, "viewport") and callable(getattr(widget, "viewport")):
                try:
                    viewport = widget.viewport()
                    if viewport is not None:
                        viewport.update()
                        continue
                except Exception:
                    pass
            widget.repaint()

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
            self.set_status(f"Zoom set to {value}%")

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
        self.set_status(
            f"Scenario selected: {self.import_scenario_combo.currentText()}"
        )

    def on_browse(self):
        """Open folder browser for default import directory."""
        current_dir = self.import_dir_edit.text().strip() or ""
        selected = QFileDialog.getExistingDirectory(
            self, "Select Import Directory", current_dir
        )
        if selected:
            self.import_dir_edit.setText(selected)
            self.set_status("Import directory selected")

    def on_restore_defaults(self):
        """Restore all settings to default values with confirmation."""
        # Build confirmation message for screen reader accessibility
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Restore Defaults")
        msg_box.setAccessibleName("Restore Defaults Confirmation")
        msg_box.setAccessibleDescription(
            "Warning, this will reset all preferences to their default values. "
            "This action cannot be undone. Are you sure you want to continue?"
        )
        msg_box.setText(
            "Are you sure you want to restore all preferences to their default values?"
        )
        msg_box.setInformativeText(
            "This will reset: Display settings (theme, zoom), Import settings "
            "(directory, formats, scenario, fallback options), and Validation rules. "
            "This action cannot be undone."
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setAccessibleName("Yes, restore defaults")
        msg_box.button(QMessageBox.No).setAccessibleName("No, keep current settings")

        # Apply accessible styling
        msg_box.setStyleSheet(
            build_accessible_message_box_style(self.scaler.current_scale)
        )

        reply = msg_box.exec()

        if reply != QMessageBox.Yes:
            self.set_status("Restore defaults cancelled")
            return

        # Reset all settings to defaults (from AbCS_default_preference.md)
        # Display settings
        # Theme: repopulate combo and select "Default (System)"
        self.theme_combo.clear()
        for display_name, theme_id in self.theme_manager.get_theme_names():
            self.theme_combo.addItem(display_name, theme_id)
        self.theme_manager.set_theme("default")
        index = self.theme_combo.findData("default")
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        else:
            # Fallback: find by display name
            self.theme_combo.setCurrentText("Default (System)")

        self.scaler.set_scale(150)
        self.preset_combo.setCurrentText("Custom")
        self.zoom_spin.setValue(150)

        # Import settings
        self.import_dir_edit.setText("")
        self.settings.setValue("import/default_directory", "")

        # All formats enabled by default
        for key in self.format_checks:
            self.format_checks[key].setChecked(True)
            self.settings.setValue(f"import/formats/{key}", True)

        # Scenario
        self.import_scenario_combo.setCurrentIndex(
            self.import_scenario_combo.findData("mass_standard")
        )
        self.settings.setValue("import/scenario/mode", "mass_standard")

        # Fallback options
        self.author_fallback_checkbox.setChecked(True)
        self.settings.setValue("import/fallback/author_to_folder", True)
        self.title_fallback_checkbox.setChecked(True)
        self.settings.setValue("import/fallback/title_to_file", True)

        # Reader keywords
        default_keywords = "reader, read by, narrator, narrated by"
        self.reader_keywords_edit.setText(default_keywords)
        self.settings.setValue("import/reader_keywords", default_keywords)

        # Validation rules - reset to defaults
        # Author in Title: warning
        self.rule_author_in_title_severity.setCurrentIndex(
            self.rule_author_in_title_severity.findData("warning")
        )
        self.settings.setValue("import/rules/author_name_in_title/enabled", True)
        self.settings.setValue("import/rules/author_name_in_title/severity", "warning")

        # Title in Author: error
        self.rule_title_in_author_severity.setCurrentIndex(
            self.rule_title_in_author_severity.findData("error")
        )
        self.settings.setValue("import/rules/title_in_author_name/enabled", True)
        self.settings.setValue("import/rules/title_in_author_name/severity", "error")

        # Unknown author: error
        self.rule_unknown_author_severity.setCurrentIndex(
            self.rule_unknown_author_severity.findData("error")
        )
        self.settings.setValue("import/rules/unknown_or_various_author/enabled", True)
        self.settings.setValue(
            "import/rules/unknown_or_various_author/severity", "error"
        )

        # Min title length: value 3, severity none (disabled)
        self.rule_min_title_value.setValue(3)
        self.rule_min_title_severity.setCurrentIndex(
            self.rule_min_title_severity.findData("none")
        )
        self.settings.setValue("import/rules/minimum_title_length/enabled", False)
        self.settings.setValue("import/rules/minimum_title_length/value", 3)
        self.settings.setValue("import/rules/minimum_title_length/severity", "warning")

        # File structure: enabled, warning, pattern author_title
        self.rule_file_structure_pattern.setCurrentIndex(
            self.rule_file_structure_pattern.findData("author_title")
        )
        self.rule_file_structure_severity.setCurrentIndex(
            self.rule_file_structure_severity.findData("warning")
        )
        self.settings.setValue("import/rules/file_structure/enabled", True)
        self.settings.setValue("import/rules/file_structure/pattern", "author_title")
        self.settings.setValue("import/rules/file_structure/severity", "warning")

        # Year quality: enabled, warning
        self.rule_year_quality_severity.setCurrentIndex(
            self.rule_year_quality_severity.findData("warning")
        )
        self.settings.setValue("import/rules/year_out_of_range/enabled", True)
        self.settings.setValue("import/rules/year_out_of_range/severity", "warning")

        # Duplicate checking: title + author + year, 90%
        self.duplicate_match_combo.setCurrentIndex(
            self.duplicate_match_combo.findData("title_author_year")
        )
        self.settings.setValue("import/rules/duplicate/match_mode", "title_author_year")

        self.duplicate_fuzzy_spin.setValue(90)
        self.settings.setValue("import/rules/duplicate/fuzzy_threshold", 90)

        # Update descriptions
        self.update_scenario_description()

        # Update initial state tracking so we don't prompt on close
        self._initial_state = self._capture_state()

        self.set_status("All preferences restored to default values")
        announce_status_message(self, "All preferences restored to default values")

    def on_save(self):
        """Save settings and close dialog."""
        self.settings.setValue(
            "import/default_directory", self.import_dir_edit.text().strip()
        )
        self.settings.setValue("import/include_subfolders", True)

        for key, checkbox in self.format_checks.items():
            self.settings.setValue(f"import/formats/{key}", checkbox.isChecked())

        self.settings.setValue(
            "import/scenario/mode", self.import_scenario_combo.currentData()
        )
        self.settings.setValue(
            "import/fallback/author_to_folder",
            self.author_fallback_checkbox.isChecked(),
        )
        self.settings.setValue(
            "import/fallback/title_to_file", self.title_fallback_checkbox.isChecked()
        )
        self.settings.setValue(
            "import/reader_keywords", self.reader_keywords_edit.text().strip()
        )

        author_in_title_choice = self.rule_author_in_title_severity.currentData()
        self.settings.setValue(
            "import/rules/author_name_in_title/enabled",
            author_in_title_choice != "none",
        )
        self.settings.setValue(
            "import/rules/author_name_in_title/severity",
            "warning" if author_in_title_choice == "none" else author_in_title_choice,
        )

        title_in_author_choice = self.rule_title_in_author_severity.currentData()
        self.settings.setValue(
            "import/rules/title_in_author_name/enabled",
            title_in_author_choice != "none",
        )
        self.settings.setValue(
            "import/rules/title_in_author_name/severity",
            "warning" if title_in_author_choice == "none" else title_in_author_choice,
        )

        unknown_author_choice = self.rule_unknown_author_severity.currentData()
        self.settings.setValue(
            "import/rules/unknown_or_various_author/enabled",
            unknown_author_choice != "none",
        )
        self.settings.setValue(
            "import/rules/unknown_or_various_author/severity",
            "warning" if unknown_author_choice == "none" else unknown_author_choice,
        )

        min_title_choice = self.rule_min_title_severity.currentData()
        self.settings.setValue(
            "import/rules/minimum_title_length/enabled",
            min_title_choice != "none",
        )
        self.settings.setValue(
            "import/rules/minimum_title_length/severity",
            "warning" if min_title_choice == "none" else min_title_choice,
        )
        self.settings.setValue(
            "import/rules/minimum_title_length/value",
            self.rule_min_title_value.value(),
        )

        file_structure_choice = self.rule_file_structure_severity.currentData()
        self.settings.setValue(
            "import/rules/file_structure/enabled",
            file_structure_choice != "none",
        )
        self.settings.setValue(
            "import/rules/file_structure/severity",
            "warning" if file_structure_choice == "none" else file_structure_choice,
        )
        self.settings.setValue(
            "import/rules/file_structure/pattern",
            self.rule_file_structure_pattern.currentData(),
        )

        year_quality_choice = self.rule_year_quality_severity.currentData()
        self.settings.setValue(
            "import/rules/year_out_of_range/enabled",
            year_quality_choice != "none",
        )
        self.settings.setValue(
            "import/rules/year_out_of_range/severity",
            "warning" if year_quality_choice == "none" else year_quality_choice,
        )
        self.settings.setValue(
            "import/rules/year_out_of_range/min_year",
            1801,
        )
        self.settings.setValue(
            "import/rules/year_out_of_range/max_year",
            datetime.now().year,
        )

        self.settings.setValue("import/rules/genre_missing/enabled", False)
        self.settings.setValue("import/rules/bitrate_below_minimum/enabled", False)

        self.settings.setValue(
            "import/rules/duplicate/match_mode",
            self.duplicate_match_combo.currentData(),
        )
        self.settings.setValue(
            "import/rules/duplicate/fuzzy_threshold",
            self.duplicate_fuzzy_spin.value(),
        )

        self._initial_state = self._capture_state()
        self.set_status("Preferences saved")
        self.accept()

    def on_cancel(self):
        """Close dialog, prompting to save when changes exist."""
        if self._has_unsaved_changes():
            reply = self._confirm_exit_with_changes()
            if reply == QMessageBox.Yes:
                self.on_save()
                return
            elif reply == QMessageBox.No:
                self.set_status("Continue editing")
                return
            else:
                self._discard_and_close()
                return
        self._discard_and_close()

    def accept(self):
        """Handle dialog accept."""
        announce_dialog_closed(self)
        super().accept()

    def reject(self):
        """Handle dialog reject (window close, Esc, or explicit reject)."""
        if self._closing_via_handler:
            super().reject()
            return
        self.on_cancel()
