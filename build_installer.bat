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
        # @@ cfd start
        self.auto_add_clean_books_check = QCheckBox("Review Clean Books Before Adding")
        self.auto_add_clean_books_check.setAccessibleName(
            "Review clean books before adding"
        )
        self.auto_add_clean_books_check.setAccessibleDescription(
            "Keep valid books in Import Window for review and Add Valid when enabled"
        )
        self.flip_author_check = QCheckBox("Flip Author Name Last, First")
        self.flip_author_check.setAccessibleName("Flip author name Last, First")
        self.flip_author_check.setAccessibleDescription(
            "Flip author names to Last, First during import"
        )
        self.autocorrect_proper_case_check = QCheckBox("Apply proper case")
        self.autocorrect_proper_case_check.setAccessibleName(
            "Apply proper case to fields"
        )
        self.autocorrect_move_the_check = QCheckBox(
            "Move leading 'The', 'A', 'An' to end of title"
        )
        self.autocorrect_move_the_check.setAccessibleName(
            "Move leading 'The', 'A', 'An' to end of title"
        )
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
        # @@ to here
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
        # @@ cfd start
        self.autocorrect_section_text = QTextEdit()
        self.autocorrect_section_text.setReadOnly(True)
        self.autocorrect_section_text.setTabChangesFocus(True)
        self.autocorrect_section_text.setFocusPolicy(Qt.StrongFocus)
        self.autocorrect_section_text.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard
        )
        self.autocorrect_section_text.setPlainText(
            "Auto-Correction: applies to Author, Series, Genre, and Narrator. Trim whitespace always applies to Title."
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

        self.autocorrect_trim_check = QCheckBox("Trim whitespace")
        self.autocorrect_trim_check.setAccessibleName("Trim whitespace")
        self.autocorrect_strip_punct_check = QCheckBox("Strip leading punctuation")
        self.autocorrect_strip_punct_check.setAccessibleName(
            "Strip leading punctuation"
        )
        self.autocorrect_non_alnum_check = QCheckBox("Remove special characters")
        self.autocorrect_non_alnum_check.setAccessibleName("Remove special characters")

        self.autocorrect_trim_check.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.autocorrect_strip_punct_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )
        self.autocorrect_non_alnum_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )
        self.autocorrect_proper_case_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )
        self.autocorrect_move_the_check.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )

        self.autocorrect_layout.addWidget(self.autocorrect_trim_check)
        self.autocorrect_layout.addWidget(self.autocorrect_strip_punct_check)
        self.autocorrect_layout.addWidget(self.autocorrect_non_alnum_check)
        self.autocorrect_layout.addStretch(1)
        autocorrect_block_layout.addWidget(self.autocorrect_section_text)
        autocorrect_block_layout.addWidget(self.autocorrect_group, 0, Qt.AlignLeft)
        import_layout.addWidget(autocorrect_block_group)
        self._sync_autocorrect_group_width()

        self.content_layout.addWidget(import_group)

