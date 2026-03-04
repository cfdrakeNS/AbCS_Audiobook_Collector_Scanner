"""
Preferences Window
Basic preferences for display and import settings.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QComboBox, QSpinBox, QLineEdit, QTextEdit,
    QPushButton, QCheckBox, QFileDialog, QStatusBar, QMessageBox, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QApplication,
    QScrollArea, QWidget, QFrame
)
from PySide6.QtCore import QSettings, Qt, QTimer, QEvent, QPoint
from PySide6.QtGui import QShortcut, QKeySequence, QTextCursor
from shiboken6 import isValid
from datetime import datetime

from accessibility.scaling import UIScaler
from accessibility.style_helpers import build_accessible_message_box_style
from accessibility.theme_manager import ThemeManager
from accessibility.key_filters import is_unmapped_alt_letter
from accessibility.accessible_events import (
    announce_status_message, announce_dialog_opened, announce_dialog_closed
)


class PreferencesWindow(QDialog):
    """
    Preferences dialog for display and import settings.
    """

    ALLOWED_ALT_LETTERS = {
        'A', 'C', 'D', 'F', 'O', 'R', 'S', 'V'
    }

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
        self.settings = QSettings('AbCS', 'AudioBookCollector')

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
        self.setup_shortcuts()
        self.scaler.scale_changed.connect(self.on_scale_changed)

        title = "Preferences"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Application preferences for display and import settings")
        self.resize(994, 560)
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
        display_layout = QHBoxLayout(display_group)
        display_layout.setSpacing(18)
        display_label_width = 72

        theme_label = QLabel("Theme:")
        theme_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        theme_label.setMinimumWidth(display_label_width)
        self.theme_combo = QComboBox()
        self.theme_combo.setAccessibleName("Theme")
        self.theme_combo.setAccessibleDescription(
            "Select application theme")
        theme_label.setBuddy(self.theme_combo)
        display_layout.addWidget(theme_label)
        display_layout.addWidget(self.theme_combo)
        display_layout.addSpacing(62)

        preset_label = QLabel("Preset:")
        preset_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        preset_label.setMinimumWidth(display_label_width)
        self.preset_combo = QComboBox()
        self.preset_combo.setAccessibleName("Font scaling preset")
        self.preset_combo.setAccessibleDescription(
            "Select font scaling preset")
        preset_label.setBuddy(self.preset_combo)
        display_layout.addWidget(preset_label)
        display_layout.addWidget(self.preset_combo)
        display_layout.addStretch(1)

        zoom_label = QLabel("Zoom (%):")
        zoom_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        zoom_label.setMinimumWidth(display_label_width + 10)
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(
            UIScaler.MIN_SCALE, UIScaler.MAX_SCALE)
        self.zoom_spin.setSingleStep(UIScaler.SCALE_STEP)
        self.zoom_spin.setAccessibleName("Zoom level")
        self.zoom_spin.setAccessibleDescription(
            "Set zoom level percentage")
        zoom_label.setBuddy(self.zoom_spin)
        display_layout.addWidget(zoom_label)
        display_layout.addWidget(self.zoom_spin)

        self.content_layout.addWidget(display_group)

        # Detail section: Import settings
        import_group = QGroupBox("Import Settings")
        import_layout = QVBoxLayout(import_group)
        import_layout.setSpacing(11)
        import_label_width = 180

        source_scope_group = QGroupBox("Source and Scope")
        source_scope_layout = QVBoxLayout(source_scope_group)
        source_scope_layout.setSpacing(8)

        options_group = QGroupBox("Options")
        options_layout = QGridLayout(options_group)
        self.options_layout = options_layout
        options_layout.setContentsMargins(8, 8, 8, 8)
        options_layout.setHorizontalSpacing(20)
        options_layout.setVerticalSpacing(8)

        fallback_group = QGroupBox("Fallback and Parsing Behavior")
        fallback_layout = QVBoxLayout(fallback_group)
        fallback_layout.setContentsMargins(8, 8, 8, 8)
        fallback_layout.setSpacing(8)

        fallback_checks_layout = QGridLayout()
        self.fallback_checks_layout = fallback_checks_layout
        fallback_checks_layout.setContentsMargins(0, 0, 0, 0)
        fallback_checks_layout.setHorizontalSpacing(20)
        fallback_checks_layout.setVerticalSpacing(0)

        validation_group = QGroupBox("Validation Rules")
        validation_layout = QVBoxLayout(validation_group)
        validation_layout.setSpacing(8)

        autocorrect_block_group = QGroupBox("Auto-Correction")
        autocorrect_block_layout = QVBoxLayout(autocorrect_block_group)
        autocorrect_block_layout.setSpacing(8)

        dir_layout = QHBoxLayout()
        dir_label = QLabel("Directory:")
        dir_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        dir_label.setMinimumWidth(import_label_width)
        self.import_dir_edit = QLineEdit()
        self.import_dir_edit.setAccessibleName("Default import directory")
        self.import_dir_edit.setAccessibleDescription(
            "Default folder to scan for imports")
        dir_label.setBuddy(self.import_dir_edit)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.import_dir_edit, 1)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setAccessibleName("Browse")
        self.browse_button.setAccessibleDescription(
            "Browse for a default import directory")
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
            checkbox.setAccessibleDescription(
                f"Include {key.upper()} files in scan")
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
            "Select import scenario mode")
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
        self.scenario_description_edit.setAccessibleName(
            "Scenario description")
        self.scenario_description_edit.setAccessibleDescription(
            "Description of selected import scenario")
        self.scenario_description_edit.setMinimumHeight(60)
        scenario_desc_label.setBuddy(self.scenario_description_edit)
        scenario_desc_layout = QHBoxLayout()
        scenario_desc_layout.setContentsMargins(0, 0, 0, 0)
        scenario_desc_layout.setSpacing(8)
        scenario_desc_layout.addWidget(scenario_desc_label)
        scenario_desc_layout.addWidget(self.scenario_description_edit, 1)
        source_scope_layout.addLayout(scenario_desc_layout)

        self.auto_add_clean_books_check = QCheckBox(
            "Review Clean Books Before Adding")
        self.auto_add_clean_books_check.setAccessibleName(
            "Review clean books before adding")
        self.auto_add_clean_books_check.setAccessibleDescription(
            "Keep valid books in Import Window for review and Add Valid when enabled")
        self.flip_author_check = QCheckBox("Flip Author Last, First")
        self.flip_author_check.setAccessibleName("Flip author name")
        self.flip_author_check.setAccessibleDescription(
            "Flip author names to Last, First during import")
        self.autocorrect_proper_case_check = QCheckBox(
            "Apply proper case")
        self.autocorrect_proper_case_check.setAccessibleName(
            "Proper case fields")
        self.autocorrect_move_the_check = QCheckBox(
            "Move leading 'The' to end of title")
        self.autocorrect_move_the_check.setAccessibleName(
            "Move leading The to end of title")
        options_layout.addWidget(self.auto_add_clean_books_check, 0, 0)
        options_layout.addWidget(self.flip_author_check, 0, 1)
        options_layout.addWidget(self.autocorrect_proper_case_check, 1, 0)
        options_layout.addWidget(self.autocorrect_move_the_check, 1, 1)
        options_col0_width = max(
            self.auto_add_clean_books_check.sizeHint().width(),
            self.autocorrect_proper_case_check.sizeHint().width(),
        )
        options_layout.setColumnMinimumWidth(0, options_col0_width)
        self.autocorrect_proper_case_check.setMinimumWidth(options_col0_width)
        options_layout.setColumnStretch(0, 0)
        options_layout.setColumnStretch(1, 0)

        import_layout.addWidget(source_scope_group)
        import_layout.addWidget(options_group)

        self.author_fallback_checkbox = QCheckBox("Author fallback to folder?")
        self.author_fallback_checkbox.setAccessibleName(
            "Author fallback to folder")
        self.author_fallback_checkbox.setAccessibleDescription(
            "If checked, missing author will fallback to folder name")
        self.title_fallback_checkbox = QCheckBox("Title fallback to file?")
        self.title_fallback_checkbox.setAccessibleName(
            "Title fallback to file")
        self.title_fallback_checkbox.setAccessibleDescription(
            "If checked, missing title will fallback to file name")
        fallback_checks_layout.setColumnMinimumWidth(0, options_col0_width)
        self.author_fallback_checkbox.setMinimumWidth(options_col0_width)
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
            "Comma-separated keywords for narrator parsing")
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
        self.rules_section_text.setAccessibleName(
            "Author and title rules description")
        self.rules_section_text.setAccessibleDescription(
            "Read-only description for author and title validation rules")
        self.rules_section_text.setFocusPolicy(Qt.StrongFocus)
        self.rules_section_text.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard)
        self.rules_section_text.setPlainText(
            "Author/Title Rules: configure severity for metadata consistency checks.")
        self._fit_readonly_section_text_height(self.rules_section_text)

        rules_group = QGroupBox("")
        rules_group.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        rules_layout = QGridLayout(rules_group)
        rules_layout.setContentsMargins(2, 4, 2, 4)
        rules_layout.setHorizontalSpacing(6)
        rules_layout.setVerticalSpacing(6)
        rules_layout.setColumnMinimumWidth(0, 140)
        rules_layout.setColumnMinimumWidth(2, 140)
        rules_layout.setColumnStretch(1, 0)
        rules_layout.setColumnStretch(3, 0)
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
        self.rule_author_in_title_severity.setAccessibleName(
            "Author in Title severity")
        self.rule_author_in_title_severity.setAccessibleDescription(
            "Set severity or None for Author in Title rule")
        author_in_title_label.setBuddy(self.rule_author_in_title_severity)
        rules_layout.addWidget(author_in_title_label, 1, 0)
        rules_layout.addWidget(self.rule_author_in_title_severity, 1, 1)

        title_in_author_label = QLabel("Title in Author:")
        title_in_author_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rule_title_in_author_severity = QComboBox()
        self.rule_title_in_author_severity.setAccessibleName(
            "Title in Author severity")
        self.rule_title_in_author_severity.setAccessibleDescription(
            "Set severity or None for Title in Author rule")
        title_in_author_label.setBuddy(self.rule_title_in_author_severity)
        rules_layout.addWidget(title_in_author_label, 1, 2)
        rules_layout.addWidget(self.rule_title_in_author_severity, 1, 3)

        unknown_author_label = QLabel("Unknown/Various:")
        unknown_author_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rule_unknown_author_severity = QComboBox()
        self.rule_unknown_author_severity.setAccessibleName(
            "Unknown or various author severity")
        self.rule_unknown_author_severity.setAccessibleDescription(
            "Set severity or None for unknown or various author rule")
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
        self.rule_min_title_value.setAccessibleName(
            "Minimum title length value")
        self.rule_min_title_severity = QComboBox()
        self.rule_min_title_severity.setAccessibleName(
            "Minimum title length severity")
        self.rule_min_title_severity.setAccessibleDescription(
            "Set severity or None for minimum title length rule")
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
            "Choose whether duplicate checks include collection")
        self.duplicate_match_combo.setSizeAdjustPolicy(
            QComboBox.AdjustToContents)
        self.duplicate_match_combo.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        duplicate_match_label.setBuddy(self.duplicate_match_combo)
        rules_layout.addWidget(duplicate_match_label, 3, 0)
        rules_layout.addWidget(self.duplicate_match_combo, 3, 1)

        duplicate_fuzzy_label = QLabel("Fuzzy Duplicate (%):")
        duplicate_fuzzy_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.duplicate_fuzzy_spin = QSpinBox()
        self.duplicate_fuzzy_spin.setRange(0, 100)
        self.duplicate_fuzzy_spin.setSuffix("%")
        self.duplicate_fuzzy_spin.setSingleStep(5)
        self.duplicate_fuzzy_spin.setAccessibleName(
            "Duplicate fuzzy threshold")
        self.duplicate_fuzzy_spin.setAccessibleDescription(
            "Optional fuzzy duplicate threshold percentage. 0 disables fuzzy duplicate matching")
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
            "Expected file structure pattern")
        self.rule_file_structure_pattern.setAccessibleDescription(
            "Select expected folder structure pattern for imports")
        self.rule_file_structure_severity = QComboBox()
        self.rule_file_structure_severity.setAccessibleName(
            "File structure severity")
        self.rule_file_structure_severity.setAccessibleDescription(
            "Set severity or None for file structure rule")
        file_structure_config_layout.addWidget(
            self.rule_file_structure_pattern)
        file_structure_config_layout.addWidget(
            self.rule_file_structure_severity)
        file_structure_label.setBuddy(self.rule_file_structure_pattern)
        rules_layout.addWidget(file_structure_label, 4, 0)
        rules_layout.addLayout(file_structure_config_layout, 4, 1)

        year_quality_label = QLabel("Year Consistency:")
        year_quality_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        year_quality_layout = QHBoxLayout()
        year_quality_layout.setContentsMargins(0, 0, 0, 0)
        year_quality_layout.setSpacing(6)
        self.rule_year_quality_severity = QComboBox()
        self.rule_year_quality_severity.setAccessibleName(
            "Year range severity")
        self.rule_year_quality_severity.setAccessibleDescription(
            "Set severity or None for year consistency rule (>1800 and <= current year)")
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

        validation_layout.addWidget(rules_group, 0, Qt.AlignLeft)
        validation_layout.addWidget(self.rules_section_text)
        import_layout.addWidget(validation_group)
        import_layout.addSpacing(self.scaler.get_scaled_size(8))

        self.autocorrect_section_text = QTextEdit()
        self.autocorrect_section_text.setReadOnly(True)
        self.autocorrect_section_text.setTabChangesFocus(True)
        self.autocorrect_section_text.setAccessibleName(
            "Auto correction description")
        self.autocorrect_section_text.setAccessibleDescription(
            "Read-only description for auto-correction settings")
        self.autocorrect_section_text.setFocusPolicy(Qt.StrongFocus)
        self.autocorrect_section_text.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard)
        self.autocorrect_section_text.setPlainText(
            "Auto-Correction: applies to Author, Series, Genre, and Narrator. Trim whitespace always applies to Title.")
        self._fit_readonly_section_text_height(self.autocorrect_section_text)
        self._sync_section_label_heights()

        self.autocorrect_group = QGroupBox("")
        self.autocorrect_group.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.autocorrect_layout = QHBoxLayout(self.autocorrect_group)
        self.autocorrect_layout.setContentsMargins(4, 2, 4, 2)
        self.autocorrect_layout.setSpacing(35)

        self.autocorrect_trim_check = QCheckBox("Trim whitespace")
        self.autocorrect_trim_check.setAccessibleName("Trim whitespace")
        self.autocorrect_strip_punct_check = QCheckBox(
            "Strip leading &punctuation")
        self.autocorrect_strip_punct_check.setAccessibleName(
            "Strip leading punctuation")
        self.autocorrect_non_alnum_check = QCheckBox(
            "Remove sp&ecial characters")
        self.autocorrect_non_alnum_check.setAccessibleName(
            "Remove special characters")

        self.autocorrect_trim_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.autocorrect_strip_punct_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.autocorrect_non_alnum_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.autocorrect_proper_case_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.autocorrect_move_the_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.autocorrect_layout.addWidget(self.autocorrect_trim_check)
        self.autocorrect_layout.addWidget(self.autocorrect_strip_punct_check)
        self.autocorrect_layout.addWidget(self.autocorrect_non_alnum_check)
        self.autocorrect_layout.addStretch(1)

        autocorrect_block_layout.addWidget(
            self.autocorrect_group, 0, Qt.AlignLeft)
        autocorrect_block_layout.addWidget(self.autocorrect_section_text)
        import_layout.addWidget(autocorrect_block_group)
        self._sync_autocorrect_group_width()

        self.content_layout.addWidget(import_group)

        # Footer section: Status bar and action buttons
        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.save_button = QPushButton("Sa&ve")
        self.save_button.setAccessibleName("Save")
        self.save_button.setAccessibleDescription(
            "Save preferences and close - Alt+V")
        self.save_button.setDefault(True)
        self.save_button.setAutoDefault(True)
        footer_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("&Cancel")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription(
            "Discard changes and close - Alt+C")
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(True)
        footer_layout.addWidget(self.cancel_button)

        layout.addLayout(footer_layout)

    def _apply_compact_combo_widths(self):
        """Apply content-fit width to all combo boxes in Preferences."""
        # This method is now a no-op because _fit_combo_to_text is missing
        pass

    def _sync_reader_keywords_width(self):
        """Match Reader Keywords field width to Duplicate Match combo width."""
        if not hasattr(self, "reader_keywords_edit") or not hasattr(self, "duplicate_match_combo"):
            return

        target_width = max(
            self.duplicate_match_combo.minimumWidth(),
            self.duplicate_match_combo.sizeHint().width(),
            120,
        )
        self.reader_keywords_edit.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.reader_keywords_edit.setMinimumWidth(target_width)
        self.reader_keywords_edit.setMaximumWidth(target_width)

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
        self.import_dir_edit.setStyleSheet(lineedit_style)
        self.reader_keywords_edit.setStyleSheet(lineedit_style)
        self.rule_min_title_value.setStyleSheet(combo_style)
        self.browse_button.setStyleSheet(button_style)
        self.save_button.setStyleSheet(button_style)
        self.cancel_button.setStyleSheet(button_style)

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
        self.flip_author_check.setStyleSheet(format_checkbox_style)
        self.auto_add_clean_books_check.setStyleSheet(format_checkbox_style)
        self.autocorrect_trim_check.setStyleSheet(format_checkbox_style)
        self.autocorrect_strip_punct_check.setStyleSheet(format_checkbox_style)
        self.autocorrect_non_alnum_check.setStyleSheet(format_checkbox_style)
        self.autocorrect_proper_case_check.setStyleSheet(format_checkbox_style)
        self.autocorrect_move_the_check.setStyleSheet(format_checkbox_style)

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
            self._fit_readonly_section_text_height(
                self.autocorrect_section_text)
        self._sync_section_label_heights()
        self._sync_autocorrect_group_width()
        self.update_scenario_description_height()

    def _sync_autocorrect_group_width(self):
        """Set Auto-Correction frame width so column spacing is visible."""
        if not hasattr(self, "autocorrect_group") or not hasattr(self, "autocorrect_layout"):
            return

        content_width = self.autocorrect_layout.sizeHint().width()
        target_width = content_width + self.scaler.get_scaled_size(24)
        min_width = self.scaler.get_scaled_size(420)
        target_width = max(min_width, target_width)

        self.autocorrect_group.setMinimumWidth(target_width)
        self.autocorrect_group.setMaximumWidth(target_width)

    def _sync_fallback_column_alignment(self):
        """Align fallback checkbox columns with Options checkbox columns."""
        required_attrs = (
            "options_layout",
            "fallback_checks_layout",
            "auto_add_clean_books_check",
            "autocorrect_proper_case_check",
            "author_fallback_checkbox",
        )
        if not all(hasattr(self, attr) for attr in required_attrs):
            return

        options_col0_width = max(
            self.auto_add_clean_books_check.sizeHint().width(),
            self.autocorrect_proper_case_check.sizeHint().width(),
        )
        self.options_layout.setColumnMinimumWidth(0, options_col0_width)
        self.autocorrect_proper_case_check.setMinimumWidth(options_col0_width)
        self.fallback_checks_layout.setColumnMinimumWidth(
            0, options_col0_width)
        self.author_fallback_checkbox.setMinimumWidth(options_col0_width)

        options_spacing = self.options_layout.horizontalSpacing()
        if options_spacing >= 0:
            self.fallback_checks_layout.setHorizontalSpacing(options_spacing)

        QTimer.singleShot(0, self._sync_fallback_visual_alignment)

    def _sync_fallback_visual_alignment(self):
        """Fine-tune fallback checkbox positions to match options row visually."""
        required_attrs = (
            "fallback_checks_layout",
            "autocorrect_proper_case_check",
            "autocorrect_move_the_check",
            "author_fallback_checkbox",
            "title_fallback_checkbox",
        )
        if not all(hasattr(self, attr) for attr in required_attrs):
            return
        if not self.isVisible():
            return

        options_col0_x = self.autocorrect_proper_case_check.mapTo(
            self, QPoint(0, 0)).x()
        fallback_col0_x = self.author_fallback_checkbox.mapTo(
            self, QPoint(0, 0)).x()
        delta_left = options_col0_x - fallback_col0_x

        left, top, right, bottom = self.fallback_checks_layout.getContentsMargins()
        new_left = max(0, left + delta_left)
        self.fallback_checks_layout.setContentsMargins(
            new_left, top, right, bottom)

        options_col1_x = self.autocorrect_move_the_check.mapTo(
            self, QPoint(0, 0)).x()
        fallback_col1_x = self.title_fallback_checkbox.mapTo(
            self, QPoint(0, 0)).x()
        residual_col1 = options_col1_x - (fallback_col1_x + (new_left - left))

        current_spacing = self.fallback_checks_layout.horizontalSpacing()
        if current_spacing < 0:
            current_spacing = 0
        self.fallback_checks_layout.setHorizontalSpacing(
            max(0, current_spacing + residual_col1)
        )

    def _sync_section_label_heights(self):
        """Keep section label boxes the same height for visual consistency."""
        if not hasattr(self, "rules_section_text") or not hasattr(self, "autocorrect_section_text"):
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
            self.scenario_description_edit.document().documentMargin() * 2)
        frame_margin = int(self.scenario_description_edit.frameWidth() * 2)
        extra_padding = self.scaler.get_scaled_size(8)
        target_height = text_rect.height() + document_margin + \
            frame_margin + extra_padding

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
            "flip_author_name": self.flip_author_check.isChecked(),
            "auto_add_clean_books": self.auto_add_clean_books_check.isChecked(),
            "reader_keywords": self.reader_keywords_edit.text().strip(),
            "rule_author_in_title": (
                self.rule_author_in_title_severity.currentData(),
            ),
            "rule_title_in_author": (
                self.rule_title_in_author_severity.currentData(),
            ),
            "rule_unknown_author": (
                self.rule_unknown_author_severity.currentData(),
            ),
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
            "autocorrect": (
                self.autocorrect_trim_check.isChecked(),
                self.autocorrect_strip_punct_check.isChecked(),
                self.autocorrect_non_alnum_check.isChecked(),
                self.autocorrect_proper_case_check.isChecked(),
                self.autocorrect_move_the_check.isChecked(),
            ),
        }

    def _has_unsaved_changes(self) -> bool:
        """Return True when preferences differ from initial dialog state."""
        return self._capture_state() != self._initial_state

    def _confirm_exit_with_changes(self) -> int:
        """Ask whether to save changes before exit. Returns QMessageBox reply."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Unsaved Changes")
        msg.setStyleSheet(
            build_accessible_message_box_style(self.scaler.get_scaled_size(20))
        )
        msg.setText(
            "You have unsaved changes.\n\n"
            "Yes = Save and close\n"
            "No = Continue editing\n"
            "Cancel = Revert and close"
        )
        msg.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        msg.button(QMessageBox.Yes).setText("&Yes - Save")
        msg.button(QMessageBox.No).setText("&No - Continue editing")
        msg.button(QMessageBox.Cancel).setText("Cance&l - Revert and close")
        return msg.exec()

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
        import_dir = self.settings.value(
            "import/default_directory", "", type=str)

        self.import_dir_edit.setText(import_dir)

        for key in self.format_checks:
            default_value = True
            value = self.settings.value(
                f"import/formats/{key}", default_value, type=bool)
            self.format_checks[key].setChecked(value)
        self.settings.setValue("import/include_subfolders", True)

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

        author_fallback_to_folder = self.settings.value(
            "import/fallback/author_to_folder", True, type=bool)
        self.author_fallback_checkbox.setChecked(author_fallback_to_folder)

        title_fallback_to_file = self.settings.value(
            "import/fallback/title_to_file", True, type=bool)
        self.title_fallback_checkbox.setChecked(title_fallback_to_file)

        flip_author = self.settings.value(
            "import/flip_author_name", False, type=bool)
        self.flip_author_check.setChecked(flip_author)

        auto_add_clean_books = self.settings.value(
            "import/auto_add_clean_books", False, type=bool)
        self.auto_add_clean_books_check.setChecked(auto_add_clean_books)

        reader_keywords = self.settings.value(
            "import/reader_keywords",
            "reader, read by, narrator, narrated by",
            type=str)
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
        self.rule_file_structure_pattern.addItem(
            "Author/Title", "author_title")
        self.rule_file_structure_pattern.addItem(
            "Year/Author/Title", "year_author_title")
        self.rule_file_structure_pattern.addItem(
            "Either", "either")

        self.duplicate_match_combo.clear()
        self.duplicate_match_combo.addItem(
            "Title + Author + Collection", "title_author")
        self.duplicate_match_combo.addItem(
            "Title + Author + Year", "title_author_year")
        self.duplicate_match_combo.addItem(
            "Title + Author + Year + Collection", "title_author_year_collection")
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
            0 if duplicate_index < 0 else duplicate_index)

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
        index = self.rule_author_in_title_severity.findData(
            author_in_title_severity)
        self.rule_author_in_title_severity.setCurrentIndex(
            0 if index < 0 else index)

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
        index = self.rule_title_in_author_severity.findData(
            title_in_author_severity)
        self.rule_title_in_author_severity.setCurrentIndex(
            0 if index < 0 else index)

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
        index = self.rule_unknown_author_severity.findData(
            unknown_author_severity)
        self.rule_unknown_author_severity.setCurrentIndex(
            0 if index < 0 else index)

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
            file_structure_severity)
        self.rule_file_structure_severity.setCurrentIndex(
            0 if file_structure_index < 0 else file_structure_index)

        file_structure_pattern = self.settings.value(
            "import/rules/file_structure/pattern",
            "author_title",
            type=str,
        )
        file_structure_pattern_index = self.rule_file_structure_pattern.findData(
            file_structure_pattern)
        self.rule_file_structure_pattern.setCurrentIndex(
            0 if file_structure_pattern_index < 0 else file_structure_pattern_index)

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
            year_quality_severity)
        self.rule_year_quality_severity.setCurrentIndex(
            0 if year_quality_index < 0 else year_quality_index)

        self.autocorrect_trim_check.setChecked(
            self.settings.value(
                "import/autocorrect/trim_whitespace",
                False,
                type=bool,
            )
        )
        self.autocorrect_strip_punct_check.setChecked(
            self.settings.value(
                "import/autocorrect/strip_leading_punctuation",
                False,
                type=bool,
            )
        )
        self.autocorrect_non_alnum_check.setChecked(
            self.settings.value(
                "import/autocorrect/remove_non_alphanumeric",
                False,
                type=bool,
            )
        )
        self.autocorrect_proper_case_check.setChecked(
            self.settings.value(
                "import/autocorrect/proper_case",
                False,
                type=bool,
            )
        )
        self.autocorrect_move_the_check.setChecked(
            self.settings.value(
                "import/autocorrect/move_leading_the_title",
                False,
                type=bool,
            )
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
            self.on_import_scenario_changed)
        self.browse_button.clicked.connect(self.on_browse)

        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.on_cancel)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for the dialog."""
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.section_shortcuts = []
        section_shortcut_map = [
            ("Alt+D", self.focus_display_section),
            ("Alt+S", self.focus_source_scope_section),
            ("Alt+O", self.focus_options_section),
            ("Alt+F", self.focus_fallback_section),
            ("Alt+R", self.focus_validation_section),
            ("Alt+A", self.focus_autocorrect_section),
        ]
        for key_sequence, handler in section_shortcut_map:
            shortcut = QShortcut(QKeySequence(key_sequence), self)
            shortcut.activated.connect(handler)
            self.section_shortcuts.append(shortcut)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

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
        """Focus first control in Source and Scope section."""
        self._focus_section_widget(self.import_dir_edit, "Source and Scope")

    def focus_options_section(self):
        """Focus first control in Options section."""
        self._focus_section_widget(
            self.auto_add_clean_books_check, "Options")

    def focus_fallback_section(self):
        """Focus first control in Fallback and Parsing section."""
        self._focus_section_widget(
            self.author_fallback_checkbox, "Fallback and Parsing Behavior")

    def focus_validation_section(self):
        """Focus first control in Validation Rules section."""
        self._focus_section_widget(
            self.rule_author_in_title_severity, "Validation Rules")

    def focus_autocorrect_section(self):
        """Focus first control in Auto-Correction section."""
        self._focus_section_widget(
            self.autocorrect_trim_check, "Auto-Correction")

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
            ("Alt+S", "Source and Scope section"),
            ("Alt+O", "Options section"),
            ("Alt+F", "Fallback and Parsing Behavior section"),
            ("Alt+R", "Validation Rules section"),
            ("Alt+A", "Auto-Correction section"),
            ("Alt+V", "Save"),
            ("Alt+C", "Cancel"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
            ("Tab/Shift+Tab", "Move between controls in the current section"),
        ]

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
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }"
        )

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

    def on_run_display_audit(self):
        """Show current display diagnostics in screen-reader friendly list format."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Display Audit")
        dlg.setAccessibleName("Display Audit")
        dlg.resize(620, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        rows = self._collect_display_audit_rows()

        table = QTableWidget()
        table.setAccessibleName("Display audit table")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(rows))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }"
            "QTableWidget::item:selected { border: none; outline: none; }"
            "QTableWidget::item:selected:focus { border: none; outline: none; }"
        )

        for row, (area, prop, value) in enumerate(rows):
            item = QTableWidgetItem(f"{area} - {prop} - {value}")
            item.setData(Qt.AccessibleTextRole, f"{area}: {prop}: {value}")
            table.setItem(row, 0, item)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)

        layout.addWidget(table, 1)

        dlg.exec()
        self.set_status("Display audit opened")

    def _collect_display_audit_rows(self):
        """Collect display settings and effective font values for diagnostics."""
        app = QApplication.instance()
        app_font_size = app.font().pointSize() if app else self.font().pointSize()
        rows = [
            ("Global", "Theme", self.theme_manager.get_current_theme_display_name()),
            ("Global", "Scale (%)", self.scaler.current_scale),
            ("Global", "Preset", self.scaler.get_preset_name()),
            ("Global", "Application font (pt)", app_font_size),
            ("Preferences", "Dialog font (pt)", self.font().pointSize()),
            ("Preferences", "Status bar font (pt)",
             self.status_bar.font().pointSize()),
            ("Preferences", "Theme combo font (pt)",
             self.theme_combo.font().pointSize()),
            ("Preferences", "Zoom spin font (pt)",
             self.zoom_spin.font().pointSize()),
            ("Preferences", "Save button font (pt)",
             self.save_button.font().pointSize()),
            ("Import", "Scenario", self.import_scenario_combo.currentText()),
            ("Import", "Formats enabled", sum(
                1 for checkbox in self.format_checks.values() if checkbox.isChecked())),
        ]
        return rows

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
                    0, lambda w=source: (w.setCursorPosition(len(w.text())), w.deselect()) if w is not None and w is not getattr(w, 'deleted', False) else None)
            elif isinstance(source, QTextEdit):
                QTimer.singleShot(
                    0, lambda w=source: self._safe_move_cursor(w))
            elif isinstance(source, QComboBox):
                QTimer.singleShot(
                    0,
                    lambda w=source: self._safe_move_embedded_lineedit_cursor(
                        w),
                )
            elif isinstance(source, QSpinBox):
                QTimer.singleShot(
                    0,
                    lambda w=source: self._safe_move_embedded_lineedit_cursor(
                        w),
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
            f"Scenario selected: {self.import_scenario_combo.currentText()}")

    def on_browse(self):
        """Open folder browser for default import directory."""
        current_dir = self.import_dir_edit.text().strip() or ""
        selected = QFileDialog.getExistingDirectory(
            self, "Select Import Directory", current_dir)
        if selected:
            self.import_dir_edit.setText(selected)
            self.set_status("Import directory selected")

    def on_save(self):
        """Save settings and close dialog."""
        self.settings.setValue(
            "import/default_directory", self.import_dir_edit.text().strip())
        self.settings.setValue("import/include_subfolders", True)

        for key, checkbox in self.format_checks.items():
            self.settings.setValue(
                f"import/formats/{key}", checkbox.isChecked())

        self.settings.setValue(
            "import/scenario/mode", self.import_scenario_combo.currentData())
        self.settings.setValue(
            "import/fallback/author_to_folder", self.author_fallback_checkbox.isChecked())
        self.settings.setValue(
            "import/fallback/title_to_file", self.title_fallback_checkbox.isChecked())
        self.settings.setValue(
            "import/flip_author_name", self.flip_author_check.isChecked())
        self.settings.setValue(
            "import/auto_add_clean_books", self.auto_add_clean_books_check.isChecked())
        self.settings.setValue(
            "import/reader_keywords", self.reader_keywords_edit.text().strip())

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
        self.settings.setValue(
            "import/rules/bitrate_below_minimum/enabled", False)

        self.settings.setValue(
            "import/rules/duplicate/match_mode",
            self.duplicate_match_combo.currentData(),
        )
        self.settings.setValue(
            "import/rules/duplicate/fuzzy_threshold",
            self.duplicate_fuzzy_spin.value(),
        )

        self.settings.setValue(
            "import/autocorrect/trim_whitespace",
            self.autocorrect_trim_check.isChecked(),
        )
        self.settings.setValue(
            "import/autocorrect/strip_leading_punctuation",
            self.autocorrect_strip_punct_check.isChecked(),
        )
        self.settings.setValue(
            "import/autocorrect/remove_non_alphanumeric",
            self.autocorrect_non_alnum_check.isChecked(),
        )
        self.settings.setValue(
            "import/autocorrect/proper_case",
            self.autocorrect_proper_case_check.isChecked(),
        )
        self.settings.setValue(
            "import/autocorrect/move_leading_the_title",
            self.autocorrect_move_the_check.isChecked(),
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
