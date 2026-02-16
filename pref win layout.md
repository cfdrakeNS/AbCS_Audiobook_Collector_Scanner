PREFERENCES WINDOW LAYOUT MAP (editable)
========================================

01 | [WINDOW] Preferences
02 |
03 | [GROUP] Display Settings
04 |   04.1  Theme:                [theme_combo________________________]
05 |   04.2  Preset:               [preset_combo_______________________]
06 |   04.3  Zoom (%):             [zoom_spin]
07 |
08 | [GROUP] Import Settings
09 |   09.1  Directory:            [import_dir_edit___________________] [Browse]
10 |
11 |   09.2  Left block: Formats                    Right block: Scenario
12 |        Formats:                                Scenario:
13 |        [ ] MP3  [ ] M4A                        [import_scenario_combo___________]
14 |        [ ] M4B  [ ] FLAC                       Scenario Description:
15 |        [ ] OGG  [ ] WAV                        [scenario_description_text_______]
16 |        [ ] WMA                                 [_______________________________]
17 |
18 |   09.3  Author Fallback:      [author_fallback_combo______________]
19 |   09.4  Title Fallback:       [title_fallback_combo_______________]
20 |   09.5  Reader Keywords:      [reader_keywords_edit_______________]
21 |
22 |   [GROUP] Author/Title Rules
23 |   23.0                         Severity
24 |   23.1  Author in Title:      [None | Error | Warning]
25 |   23.2  Title in Author:      [None | Error | Warning]
26 |   23.3  Unknown/Various:      [None | Error | Warning]
27 |   23.4  Min Title Length:     [min_title_spin] [None|Error|Warning]
28 |   23.5  Duplicate Match:      [duplicate_match_combo______________]
29 |          options:
30 |            - Title + Author + Collection
31 |            - Title + Author + Year
32 |            - Title + Author + Year + Collection
33 |            - Title + Author + Year (Ignore Collection)
34 |
35 | [FOOTER]
36 |   [status_bar_____________________________________________] [Save] [Cancel]


ALTERNATIVE A - BALANCED (recommended default)
==============================================

01 | [WINDOW] Preferences
02 |
03 | [GROUP] Display Settings
04 |   Theme:       [theme_combo__________]
05 |   Preset:      [preset_combo_________]
06 |   Zoom (%):    [zoom_spin]
07 |
08 | [GROUP] Import Settings
09 |   Directory:   [import_dir_edit____________________] [Browse]
10 |
11 |   Left block: Formats               Right block: Scenario
12 |   Formats:                          Scenario:
13 |   [ ] MP3 [ ] M4A [ ] M4B           [import_scenario_combo________]
14 |   [ ] FLAC [ ] OGG [ ] WAV [ ] WMA  Scenario Description:
15 |                                    [scenario_description_text____]
16 |
17 |   Author Fallback: [author_fallback_combo_____]
18 |   Title Fallback:  [title_fallback_combo______]
19 |   Flip Author:     [ ] Last, First
20 |   Reader Keywords: [reader_keywords_edit______]
21 |
22 |   [GROUP] Author/Title Rules
23 |   Author in Title:      [severity_combo]
24 |   Title in Author:      [severity_combo]
25 |   Unknown/Various:      [severity_combo]
26 |   Min Title Length:     [min_title_spin] [severity_combo]
27 |   Duplicate Match:      [duplicate_match_combo________]
28 |
29 |   [GROUP] Auto-Correction
30 |   Description: [Auto-Correction: applies to Title, Author, Series, Genre & Narrator.]
31 |   [ ] Trim whitespace        [ ] Proper case fields
32 |   [ ] Strip punctuation      [ ] Move leading The in title
33 |   [ ] Remove special chars
34 |
35 | [FOOTER]
36 |   [status_bar_____________________________________________] [Save] [Cancel]


ALTERNATIVE B - 3 COLUMNS (wide screens only)
==============================================

01 | [WINDOW] Preferences (widescreen)
02 |
03 | [ROW 1]
04 |   Col 1: Display             Col 2: Import Core            Col 3: Fallback/Keywords
05 |   Theme: [combo____]         Directory: [edit______][B]    Author FB: [combo___]
06 |   Preset:[combo____]         Scenario:  [combo____]        Title FB:  [combo___]
07 |   Zoom:  [spin]              Formats: [compact checks]     Flip: [ ] Last, First
08 |                              Scenario Desc: [text____]     Keywords: [edit_____]
09 |
10 | [ROW 2]
11 |   Col 1-2: Author/Title Rules (2-column grid, compact controls)
12 |   Col 3:   Auto-Correction (single compact card)
13 |
14 | [FOOTER]
15 |   [status_bar____________________________________] [Save] [Cancel]

Notes:
- Keep each combo fixed to content-fit width; do not stretch combos to column width.
- Best for >= 1400 px width. On smaller widths, switch to Alternative A or C.


ALTERNATIVE C - 2 COLUMNS (best accessibility density)
=======================================================

01 | [WINDOW] Preferences
02 |
03 | [GROUP] Display Settings (full width compact rows)
04 |   Theme: [combo____]   Preset: [combo____]   Zoom: [spin]
05 |
06 | [GROUP] Import Settings (two equal columns)
07 |   LEFT COLUMN                           RIGHT COLUMN
08 |   Directory: [edit__________] [Browse]  Scenario: [combo_____]
09 |   Formats: [compact checks block]       Scenario Desc: [text___]
10 |   Reader Keywords: [edit_______]        Author FB: [combo_____]
11 |                                        Title FB:  [combo_____]
12 |                                        Flip: [ ] Last, First
13 |
14 | [GROUP] Rules + Auto-Correction (stacked, no wide blanks)
15 |   Rules card (compact rows)
16 |   Auto-Correction card directly below rules:
17 |   [ ] Trim whitespace   [ ] Proper case
18 |   [ ] Strip punctuation [ ] Move leading The
19 |   [ ] Remove special chars
20 |
21 | [FOOTER]
22 |   [status_bar_____________________________________________] [Save] [Cancel]

Notes:
- This layout keeps visual grouping strongest for low-vision scanning.
- Minimize horizontal whitespace between Auto-Correction columns (tight gap).
```
