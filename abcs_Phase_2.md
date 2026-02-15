# AbCS Phase 2 - Import Process & Preferences

**Start Date:** February 10, 2026  
**Approach:** Incremental development following MS Access import pattern

---

## Overview

Phase 2 implements the import process and preferences system. The preferences window will be built with basic settings first, then expanded as import validation rules are developed.

**Reviewed:** February 15, 2026 (codebase status sync)

---

## Build Order

### 1. Basic Preferences Window
Initial settings to establish the framework:

**Display Settings:**
- Theme selection (6 built-in: Normal, High Contrast Light/Dark, etc.)
- Font scaling presets (Tiny, Small, Normal, Large, Extra Large, Huge, Maximum)
- Zoom level (50-300%)

**Import Settings (Initial):**
- Default import directory (folder browser)
- File formats to scan (checkboxes: MP3, M4A, FLAC, OGG, WAV)
- Import scenario mode (dropdown with 4 modes)
- Scenario description panel (read-only text updated by mode selection)
- Author fallback combo (None, Folder)
- Title fallback combo (None, Folder, File)
- Reader keyword list (comma-separated text; default: `reader, read by, narrator, narrated by`)

**Storage:**
- Use QSettings for persistence (already in accessibility framework)

### 2. Import Window
Main import interface (mirrors MS Access version):

**Header:**
- Import collection selector (Alt+L) - first header control
- Folder path display with Browse button (Alt+B)
- File format filter display
- Import scenario mode display (from preferences)
- Scan button (Alt+S) - disabled until a collection is selected

**Detail:**
- Table showing scanned files with columns:
  - File/Folder
  - Author (from tags)
  - Title (from tags)
  - Error Type (if any)
- Multi-select support for bulk actions
  - Double-click or Ctrl+Enter to open Import Detail Window

**Footer:**
- Import Selected (Alt+I) - Add selected books to database
- Import All Valid (Alt+V) - Import all non-error items
- Cancel (Alt+C)

**Status Bar:**
- Summary: "Scanned: 150 | Valid: 142 | Errors: 5 | Duplicates: 3"
- Screen reader announcements

### Import Scenario Modes (Phase 2 Baseline)

1. **Mass Standard Import**
   - Root contains author folders.
   - Books may be:
     - in book-title subfolders under author,
     - single files directly under author,
     - or inside series folders under author (series folder may include subfolders or single files).
   - Series extraction from directory should be conservative due to mixed structure.
   - Fallback when tags missing:
     - Author: author folder name
     - Title: prefer non-author folder name, otherwise file name without extension

2. **Mass Import - Series From Directory**
   - Root contains author folders.
   - Author subfolders are series folders.
   - Books are single files inside series folders.
   - Series is derived from folder path.
   - Fallback when tags missing:
     - Author: author folder name
     - Title: file name without extension

3. **Mass Import - Series From File Name**
   - Root contains author folders with single-file books.
   - Series is parsed from file name where series appears in parentheses, e.g. `Harm'S Way (Cold Justice 04) Book Title`.
   - Parsed pattern target: `Series Name + Series Number`.
   - Title normalization rule: append parsed series number to title as `Title - NN`.
   - Fallback when tags missing:
     - Author: author folder name
     - Title: file name without extension

4. **Single Author / Book Import**
   - Supports importing one author folder, one series/book folder, or one file.
   - File chooser should filter file types by selected import preferences.
   - Folder-based fallback is optional and may not always apply (path context can be incomplete).

### 3. Import Detail Window
Edit individual import items (especially errors):

**Header:**
- File path (read-only)
- Error type and message

**Detail:**
- Editable fields: Author, Title, Year, Series, Genre
- Original tag values displayed for reference
- Audio file preview info (duration, bitrate, format)

**Footer:**
- Save & Return (Alt+S)
- Skip/Discard (Alt+K)
- Previous/Next navigation (Alt+P / Alt+N)

### 4. Import Progress Window
Real-time feedback during folder scan:

**Display:**
- Progress bar (files scanned / total files)
- Current file being processed
- Elapsed time
- Running counts: Valid, Errors, Duplicates
- Cancel button to abort scan

---

## Preferences Expansion (As Import Develops)

Import validation rules will be added to Preferences as they're implemented:

### Scenario & Fallback Controls (Early Phase 2)

- [x] Import scenario dropdown with the 4 modes above
- [x] Description text box that explains selected scenario behavior
- [x] Author fallback combo: None, Folder
- [x] Title fallback combo: None, Folder, File
- [x] Persist all scenario/fallback settings in QSettings

### Planned Rule Categories:

**Author/Title Rules:**
- [x] Flag if author name appears in title (enabled + severity in Preferences)
- [x] Flag if title appears in author (enabled + severity in Preferences)
- [x] Flag if author contains "Various" or "Unknown" (enabled + severity in Preferences)
- [x] Minimum title length (enabled + configurable threshold + severity)

**Duplicate Detection:**
- [x] Match criteria: Title + Author + Year + Collection
- [x] Match criteria: Title + Author + Year (ignore Collection)
- [x] Match criteria: Title + Author + Collection (ignore Year)
- [x] Match criteria: Title + Author only
- [x] Fuzzy matching threshold (optional)

**File Structure Rules:**
- [x] Expected folder structure (Author/Title, Year/Author/Title, etc.)
- [x] Extract metadata from folder names if tags missing

**Tag Quality Rules:**
- [x] Year out-of-range rule (configurable min/max + severity)
- [x] Missing genre rule (enabled + severity)
- [x] Minimum bitrate rule (threshold + severity)

**Tag Enrichment Rules:**
- [x] Reader extraction: first from Composer tag
- [x] If Composer missing, parse Comments using configurable reader keywords
- [x] Reader keywords configurable in preferences as comma-separated values
- [x] Comments aggregation for multi-file books keeps only unique comment values

**Auto-Correction:**
- [x] Trim whitespace
- [x] Remove non-alphanumeric characters
- [x] Remove leading punctuation characters
- [x] Field case conversion to Proper Case
- [x] Move leading "The" in author to trailing ", The"

Each rule can be:
- Enabled/Disabled
- Severity: Error (blocks import) or Warning (allows import with flag)

---

## Technical Notes

### Integration Points:
- `src/core/tag_reader.py` - Existing audio metadata extraction
- `src/core/validator.py` - Existing error detection (extend with preference rules)
- `src/core/import_scanner.py` (new) - Directory traversal and scenario-specific extraction
- `src/accessibility/` - Scaling, themes, shortcuts (already built)
- `src/database/queries.py` - Duplicate checking queries

### Compatibility Notes:
- Legacy duplicate mode values are still supported and mapped on load:
  - `with_collection` -> `title_author_year_collection`
  - `ignore_collection` -> `title_author_year_ignore_collection`
  - `title_author_ignore_collection` -> `title_author_year`

### Phase 2 Files (Created / Planned):
- [x] `src/ui/preferences_window.py` - Preferences dialog
- [x] `src/ui/import_window.py` - Main import interface
- [x] `src/ui/import_detail_window.py` - Edit individual imports
- [ ] `src/ui/import_progress_window.py` - Separate scan progress window (deferred; inline progress used in Import Window for accessibility)
- [x] `src/core/import_scanner.py` - Scenario-aware path parser and fallback resolver
- [x] `src/core/import_rules.py` - Rule engine for validation with QSettings-driven rule enable/severity/value

### Settings Storage:
```python
# QSettings keys for import preferences
"import/default_directory"
"import/formats/mp3"
"import/formats/m4a"
"import/formats/flac"
"import/formats/ogg"
"import/formats/wav"
"import/scenario/mode"
"import/fallback/author"
"import/fallback/title"
"import/reader_keywords"
"import/rules/..."  # Added as rules are implemented
```

---

## Accessibility Requirements (All Windows)

- 14pt minimum fonts, scaled via UIScaler
- All controls have Alt+letter shortcuts
- Status bar with screen reader announcements (QAccessible focus trick)
- High contrast theme support
- Complete keyboard navigation

---

## Implementation Tracking

| Component | Status | Notes |
|-----------|--------|-------|
| Basic Preferences Window | Complete (Phase 2 Baseline) | Theme/preset/zoom, default directory, formats, scenario, fallbacks, reader keywords, QSettings persistence implemented; subfolder scanning is always on |
| Import Window | In Progress | Folder browse, scan, validation, summary/status announcements, scenario mode display, collection selector (first header item), scan gated until collection selection (shows None when multiple collections), row selection, detail open on double-click/Ctrl+Enter, add selected/all valid implemented; duplicates are treated as errors |
| Import Detail Window | In Progress | Editable metadata fields + errors implemented; footer now supports Save & Return, Skip/Discard, and Previous/Next navigation (Alt+P/Alt+N + PageUp/PageDown) |
| Import Progress Window | Partially Implemented (Inline) | Scan progress, elapsed time, and cancel are provided in Import Window status bar/footer; separate dedicated progress window removed for accessibility |
| Scenario Modes (4) | In Progress | Scenario setting persisted and applied for series/fallback behavior via core import scanner; scenario mode displayed in Import Window header |
| Fallback Controls | Completed (Phase 2 Baseline) | Preferences fallback combos persisted and applied during scan result processing |
| Reader Extraction | Completed (Current Baseline) | Composer-first extraction in scanner plus configurable comment-keyword parsing applied in Import Window |
| Unique Multi-file Comments | Completed | Scanner keeps distinct comment values per grouped book |
| Author/Title Rules | Completed (Current Baseline) | Preferences controls implemented for enable/severity/value and applied by rules engine at scan time |
| Duplicate Rules | Completed (Current Baseline) | Preference-driven duplicate modes and fuzzy threshold are wired through validator and import scan flow |
| File Structure Rules | Completed (Current Baseline) | Pattern validation plus folder metadata extraction for missing tags implemented |
| Tag Quality Rules | Completed (Current Baseline) | Year range, missing genre, and minimum bitrate rules implemented with preferences |
| Auto-Correction Rules | Completed (Current Baseline) | Trim/cleanup/proper-case and leading "The" author normalization implemented via import scanner settings |

---

## Notes

- Follow existing window patterns (header/detail/footer layout)
- Use same status bar announcement pattern as Main Window and Update Window
- Incremental rule development: add rules to validator.py, then add preference toggles
- MS Access import behavior is the reference implementation
