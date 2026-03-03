PREFERENCES WINDOW LAYOUT MAP (current prefs window - editable)
===============================================================

01 | [WINDOW] Preferences
02 |
03 | [GROUP] Display Settings (single row)
04 |   Theme: [theme_combo__________]   Preset: [preset_combo_________]   Zoom (%): [zoom_spin]
05 |
06 | [GROUP] Import Settings
07 |
08 |   [SUBGROUP] Source & Scope
09 |   Directory:   [import_dir_edit____________________] [Browse]
10 |   Formats:     [ ] MP3 [ ] M4A [ ] M4B [ ] FLAC [ ] OGG [ ] WAV [ ] WMA
11 |   Scenario:    [import_scenario_combo________]
12 |   Scenario Description:
13 |                [scenario_description_text________________________]
14 |
15 |   [SUBGROUP] Options (2-column grid)
16 |   [ ] Review Clean Books Before Adding     [ ] Flip Author Last, First
17 |   [ ] Apply proper case                    [ ] Move leading The to end of title
18 |
19 |   [SUBGROUP] Fallback & Parsing Behavior (2-column grid, aligned to Options columns)
20 |   [ ] Author fallback to folder?           [ ] Title fallback to file?
21 |   Reader Keywords: [reader_keywords_edit________________________]
22 |
23 |   [SUBGROUP] Validation Rules
24 |   Author/Title Rules Description (read-only):
25 |     [rules_section_text_________________________________________]
26 |   Author in Title:      [severity_combo]      Title in Author:      [severity_combo]
27 |   Unknown/Various:      [severity_combo]      Min Title Length:     [min_title_spin] [severity_combo]
28 |   Duplicate Match:      [duplicate_match_combo________]  Fuzzy Duplicate (%): [duplicate_fuzzy_spin]
29 |   File Structure:       [pattern_combo____] [severity_combo]  Year Consistency: [severity_combo]
30 |
31 |   [SUBGROUP] Auto-Correction
32 |   [ ] Trim whitespace           [ ] Strip punctuation           [ ] Remove special chars
33 |   Description (read-only):
34 |     [autocorrect_section_text___________________________________]
35 |
36 | [FOOTER]
37 |   [status_bar_____________________________________________] [Save] [Cancel]


NOTES
=====
- Source of truth: src/ui/preferences_window.py
- `Options` and `Fallback & Parsing Behavior` both use 2-column grids.
- Fallback column 1 is anchored to the same left start as `Apply proper case`.
- Fallback column 2 is anchored to the same left start as `Move leading The...`.
