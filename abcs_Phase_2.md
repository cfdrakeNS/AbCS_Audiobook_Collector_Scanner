# AbCS Phase 2 - Import Process & Preferences

**Start Date:** February 10, 2026  
**Approach:** Incremental development following MS Access import pattern

---

## Overview

Phase 2 implements the import process and preferences system. The preferences window will be built with basic settings first, then expanded as import validation rules are developed.

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
- Include subfolders (checkbox)

**Storage:**
- Use QSettings for persistence (already in accessibility framework)

### 2. Import Window
Main import interface (mirrors MS Access version):

**Header:**
- Folder path display with Browse button (Alt+B)
- File format filter display
- Scan button (Alt+S)

**Detail:**
- Table showing scanned files with columns:
  - Status (OK, Error, Warning, Duplicate)
  - File/Folder
  - Author (from tags)
  - Title (from tags)
  - Error Type (if any)
- Multi-select support for bulk actions
- Double-click or F8 to open Import Detail Window

**Footer:**
- Import Selected (Alt+I) - Add selected books to database
- Import All Valid (Alt+V) - Import all non-error items
- Cancel (Alt+C)

**Status Bar:**
- Summary: "Scanned: 150 | Valid: 142 | Errors: 5 | Duplicates: 3"
- Screen reader announcements

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

### Planned Rule Categories:

**Author/Title Rules:**
- [ ] Flag if author name appears in title
- [ ] Flag if title appears in author
- [ ] Flag if author contains "Various" or "Unknown"
- [ ] Minimum author name length
- [ ] Minimum title length

**Duplicate Detection:**
- [ ] Match criteria: Title + Author + Year
- [ ] Match criteria: Title + Author only
- [ ] Fuzzy matching threshold (optional)

**File Structure Rules:**
- [ ] Expected folder structure (Author/Title, Year/Author/Title, etc.)
- [ ] Extract metadata from folder names if tags missing

**Tag Quality Rules:**
- [ ] Require year
- [ ] Require genre
- [ ] Flag specific genres to ignore

**Auto-Correction:**
- [ ] Trim whitespace
- [ ] Title case conversion
- [ ] Remove "The" from author start

Each rule can be:
- Enabled/Disabled
- Severity: Error (blocks import) or Warning (allows import with flag)

---

## Technical Notes

### Integration Points:
- `src/core/tag_reader.py` - Existing audio metadata extraction
- `src/core/validator.py` - Existing error detection (extend with preference rules)
- `src/accessibility/` - Scaling, themes, shortcuts (already built)
- `src/database/queries.py` - Duplicate checking queries

### New Files to Create:
- `src/ui/preferences_window.py` - Preferences dialog
- `src/ui/import_window.py` - Main import interface
- `src/ui/import_detail_window.py` - Edit individual imports
- `src/ui/import_progress_window.py` - Scan progress display
- `src/core/import_rules.py` - Rule engine for validation (later)

### Settings Storage:
```python
# QSettings keys for import preferences
"import/default_directory"
"import/include_subfolders"
"import/formats/mp3"
"import/formats/m4a"
"import/formats/flac"
"import/formats/ogg"
"import/formats/wav"
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
| Basic Preferences Window | Not Started | Theme, scaling, import directory, formats |
| Import Window | Not Started | Main scan/import interface |
| Import Detail Window | Not Started | Edit individual items |
| Import Progress Window | Not Started | Real-time scan feedback |
| Author/Title Rules | Not Started | Add to preferences later |
| Duplicate Rules | Not Started | Add to preferences later |
| File Structure Rules | Not Started | Add to preferences later |
| Tag Quality Rules | Not Started | Add to preferences later |
| Auto-Correction Rules | Not Started | Add to preferences later |

---

## Notes

- Follow existing window patterns (header/detail/footer layout)
- Use same status bar announcement pattern as Main Window and Update Window
- Incremental rule development: add rules to validator.py, then add preference toggles
- MS Access import behavior is the reference implementation
