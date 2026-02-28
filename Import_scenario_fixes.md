# Import scenario structure (planned vs implemented)

Updated: Feb 26, 2026  
Purpose: compare requested import-scenario behavior with current implementation.

## Scenario coverage summary

| Scenario | Planned | Implemented status | Notes |
|---|---|---|---|
| 1. Mass Standard Import | Mixed author/book/series folder structure under root | Implemented | Scenario exists as `mass_standard` |
| 2. Series from directory | Series inferred from author subfolder path | Partially implemented | Series extraction works, but depends on detected folder layout |
| 3. Series from filename | Series parsed from bracketed filename text | Partially implemented | Series text parsed; title-number split/append not implemented |
| 4. Single author/book/file import | Allow one author folder, one book folder, or single file | Partially implemented | Scenario option exists, but browse currently selects folder only |

## Current implementation (code-aligned)

### Preferences and scenario definitions
- Four scenario options are present in Preferences and saved in settings.
- Scenario description textbox is implemented and updates on selection.
- Author fallback options: `none`, `folder`.
- Title fallback options: `none`, `folder`, `file`.

### Import processing behavior
- Import window reads scenario and fallback settings and configures `ImportScanner`.
- Reader extraction behavior:
  - Uses Composer first.
  - If Composer is blank, parses Comment using configurable keywords.
- Multi-file comment handling keeps unique comments only.

## Detailed comparison by requirement

### 1) Mass Standard Import
Planned:
- Author folder under root; books may be in title folder, author folder, or series subfolders.

Implemented:
- Works with recursive scan and metadata grouping.
- Fallback author can use folder-derived value.

Gap / difference:
- Planned title fallback chain (`folder if not author folder`, then `file`) is not implemented as a built-in two-step chain.
- Current behavior applies selected title fallback mode (`folder` or `file`) directly.

### 2) Mass Import - Series from directory
Planned:
- Series comes from directory path under author folder.
- Title fallback from filename when missing.

Implemented:
- `series_from_directory` mode exists.
- Series is assigned from parent folder of first file (when different from book folder name).
- Title fallback to filename works when title fallback mode is set to `file`.

Gap / difference:
- Path assumptions can vary depending on folder depth; no extra path validation specific to this mode.

### 3) Mass Import - Series from filename
Planned:
- Parse filename bracket content like `Book Title (Series Name 04)`.
- Append series number to title (example: `Book Title - 04`).

Implemented:
- `series_from_filename` mode exists.
- Series is parsed from first parenthesized text and stored in `series`.

Gap / difference:
- Split of `series name` and `series number` is not implemented.
- Appending series number to title is not implemented.

### 4) Single author / book / file import
Planned:
- Allow selecting a single author folder, series/book folder, or single file.
- File picker should honor enabled format filters.

Implemented:
- Scenario option `single_item` exists in preferences and runtime mode.

Gap / difference:
- Browse flow currently uses folder selection only.
- Single-file selection flow is not currently implemented in Import window.

## Fallback behavior comparison

Planned:
- Author fallback: none or folder.
- Title fallback: none/folder/file with conditional fallback logic by scenario.

Implemented:
- Author fallback `none|folder` is implemented.
- Title fallback `none|folder|file` is implemented.

Gap / difference:
- Scenario-specific fallback rules are not fully branched.
- Priority fallback chains are not fully encoded (mode selection is direct, not chained).

## Additional tag import requirements

### Reader from Composer or Comments
- Status: Implemented.
- Notes: Reader keywords are configurable and comma-separated in Preferences.

### Unique comments across multi-file books
- Status: Implemented.
- Notes: Duplicate comment text for grouped files is filtered out.


## Additional Gap Notes (Feb 28)

- **Series-from-filename:**
  - Edge cases (multiple parentheses, malformed series info) should be handled or flagged in future updates.

- **Single-item mode:**
  - File dialog filters must match all supported audio formats (MP3, M4A, FLAC, OGG, WAV).
  - Accessibility (keyboard navigation, Alt+letter shortcuts) must be preserved in the file picker.

- **Fallback chains:**
  - Fallback logic should be unit-tested for each scenario.
  - Status bar feedback should be provided when a fallback is triggered.

- **Testing:**
  - Accessibility regression checks (keyboard, screen reader feedback) should be included in each scenario's test block.

- **Documentation:**
  - Update user-facing documentation/help to reflect new scenario behaviors and fallback logic once implemented.

## Plan for Tomorrow (Feb 29)

**Goal:**
- Complete Scenario 1 (Mass Standard) end-to-end: implementation, tests, and focused regression.

**Tasks:**
1. Implement chained title fallback in src/core/import_scanner.py for mass_standard scenario.
2. Add/extend tests in test_import_scanner_fallbacks.py for fallback logic and edge cases.
3. Run scenario-specific and accessibility regression tests.
4. Update Import_scenario_fixes.md checklist and user documentation as features are completed.
5. If Scenario 1 is fully green, prepare Scenario 2 test cases (do not implement yet).

**Notes:**
- Stop and fix immediately on first test failure before continuing.
- Record all changes, tests run, and next steps at session end.

## Technical implementation checklist (file-by-file)

### Phase 1: Scenario behavior in core scanner

#### `src/core/import_scanner.py`
- [ ] Add scenario-specific title fallback strategy function:
  - `mass_standard`: try folder (if folder name is not author folder), then file stem.
  - `series_from_directory`: file stem fallback for missing title.
  - `series_from_filename`: file stem fallback for missing title.
  - `single_item`: keep current fallback behavior configurable; no forced fallback.
- [ ] Add helper to derive `series_name` + `series_number` from filename pattern.
- [ ] In `series_from_filename`, parse `(Series Name 04)` into:
  - `series = Series Name`
  - append ` - 04` to title when number exists.
- [ ] Keep existing reader extraction and unique-comment behavior unchanged.
- [ ] Add guarded flags/messages when scenario inference could not be applied cleanly.

### Phase 2: Import window browse flow for single-item

#### `src/ui/import_window.py`
- [ ] Update `on_browse()` behavior by scenario:
  - non-`single_item`: keep folder picker.
  - `single_item`: allow either folder picker or single-file picker.
- [ ] For single-file mode, use enabled format list to build file dialog filter.
- [ ] Normalize selected single file into scanner input path handling.
- [ ] Update status/header line to announce whether source is folder or file.
- [ ] Ensure cancel/progress UX stays unchanged.

### Phase 3: Preferences text/spec alignment

#### `src/ui/preferences_window.py`
- [ ] Refine scenario descriptions to match final implemented behavior exactly.
- [ ] Add one-line note for fallback strategy per scenario in description text.
- [ ] Keep existing setting keys unchanged (`import/scenario/mode`, fallback keys).

### Phase 4: Validation and duplicate logic compatibility

#### `src/core/validator.py` and `src/core/import_rules.py`
- [ ] Confirm new title suffix behavior (` - NN`) does not break duplicate matching expectations.
- [ ] Verify warning/error categorization still treats fallback/correction markers correctly.
- [ ] No rule severity key changes unless required.

### Phase 5: Tests (targeted additions)

#### `test/test_import_scanner_fallbacks.py`
- [ ] Add tests for mass-standard chained title fallback (folder then file).
- [ ] Add tests for series-from-directory fallback behavior.
- [ ] Add tests for series-from-filename parsing into `series` + title suffix.
- [ ] Add tests that single-item mode does not force unwanted fallback.

#### `test/test_import_window_collection_rules.py`
- [ ] Add tests for `single_item` browse behavior (folder path and file path).
- [ ] Add tests that file picker respects enabled import format settings.

#### `test/test_import_rules_preferences.py`
- [ ] Add coverage asserting preferences scenario descriptions and setting persistence remain correct.

### Phase 6: Regression verification

#### Execute focused test subset
- [ ] `test/test_import_scanner_fallbacks.py`
- [ ] `test/test_import_window_collection_rules.py`
- [ ] `test/test_import_rules_preferences.py`
- [ ] Verify no regressions in import detail interactions (`test/test_import_detail_combo_checks.py`).

## Definition of done
- [ ] All four scenarios behave as documented.
- [ ] Single-item mode can import a single audio file directly.
- [ ] Series-from-filename stores clean series text and appends number to title when present.
- [ ] Scenario-specific fallback behavior matches this document.
- [ ] Targeted import tests pass.

**Execution model**
- For each scenario: implement only that slice, run only its tests, fix immediately, then run a small regression subset.
- Do not start next scenario until current one is green.
- Keep the checklist in Import scenario structure.md updated after each pass.

**Plan by scenario**
- **Scenario 1 (Mass Standard)**  
  - Implement chained title fallback behavior for this mode.  
  - Add/extend tests in test_import_scanner_fallbacks.py.  
  - Run scenario test file + quick import regression set.
- **Scenario 2 (Series from directory)**  
  - Tighten series extraction/path assumptions for this mode.  
  - Add targeted tests for directory-derived series and fallback interactions.  
  - Run same focused regression subset.
- **Scenario 3 (Series from filename)**  
  - Implement parse into `series` + optional title suffix from series number.  
  - Add parser edge-case tests (no number, malformed parentheses, multiple parentheses).  
  - Run focused regressions.
- **Scenario 4 (Single item)**  
  - Add single-file browse/import flow in import window while preserving folder mode.  
  - Add UI tests in test_import_window_collection_rules.py.  
  - Run focused regressions.

**Per-step test cadence**
- Primary: scenario-specific tests only.
- Secondary: test_import_rules_preferences.py and test_import_detail_combo_checks.py.
- Stop and fix immediately on first failure before continuing.

## Next session plan (tomorrow / resume plan)

### Session goal
- Complete **Scenario 1 (Mass Standard)** end-to-end (implementation + tests + focused regression) before touching Scenario 2.

### Startup checklist (10-15 min)
- [ ] Open this file and confirm scope = Scenario 1 only.
- [ ] Re-run baseline tests:
  - [ ] `test/test_import_scanner_fallbacks.py`
  - [ ] `test/test_import_rules_preferences.py`
- [ ] Capture baseline failures (if any) before code edits.

### Work block A: Scenario 1 implementation (45-60 min)
- [ ] Implement chained title fallback in `src/core/import_scanner.py` for `mass_standard`:
  - folder fallback when folder is not effectively author folder.
  - then file-stem fallback if title still missing.
- [ ] Keep existing behavior unchanged for other scenario modes in this block.

### Work block B: Scenario 1 tests (30-45 min)
- [ ] Add/update tests in `test/test_import_scanner_fallbacks.py`:
  - [ ] title missing -> folder fallback (valid case)
  - [ ] title missing -> file fallback when folder fallback is not valid
  - [ ] verify no regression to author fallback behavior
- [ ] Run only Scenario 1-related tests until green.

### Work block C: Focused regression (15-25 min)
- [ ] Run:
  - [ ] `test/test_import_scanner_fallbacks.py`
  - [ ] `test/test_import_rules_preferences.py`
  - [ ] `test/test_import_detail_combo_checks.py`
- [ ] If all pass, mark Scenario 1 complete in this document.

### Stop/continue rule
- If Scenario 1 is not fully green, **do not** start Scenario 2.
- If Scenario 1 is fully green and time remains, prepare (but do not implement) Scenario 2 test cases.

### End-of-session handoff notes
- [ ] Record what changed (files + behavior).
- [ ] Record exact tests run and pass/fail status.
- [ ] Record first task for next resume (likely Scenario 2 implementation).

