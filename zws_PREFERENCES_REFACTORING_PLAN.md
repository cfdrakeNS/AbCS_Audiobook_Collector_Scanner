# Preferences Refactoring Plan

## Overview
This document outlines the plan to remove complexity from the AbCS preferences by eliminating the "Options" and "Auto-Correction" sections and their associated preferences. The removed options will become standard behavior applied consistently throughout the app.

## Preferences Being Removed

### 1. Review Clean Books Before Adding
- **Current Location**: Preferences > Import > Options > "Review Clean Books Before Adding"
- **Current Behavior**: When enabled, valid books are kept in Import Window for review; shows "Add Valid" button
- **New Behavior**: Always auto-add clean books; remove "Add Valid" button entirely
- **Settings Key**: `import/auto_add_clean_books`

### 2. Flip Author Name
- **Current Location**: Preferences > Import > Options > "Flip Author Name Last, First"
- **Current Behavior**: When enabled, author names are flipped from "First Last" to "Last, First" during import and web fetch
- **New Behavior**: Always normalize author names for comparison; internal logic handles the flip transparently
- **Settings Key**: `import/flip_author_name`

### 3. Move leading 'The', 'A', 'An' to end of title
- **Current Location**: Preferences > Import > Options > "Move leading 'The', 'A', 'An' to end of title"
- **Current Behavior**: When enabled, moves articles like "The Hobbit" to "Hobbit, The" for title comparison and web search
- **New Behavior**: Always normalize titles for comparison; store original title format in database
- **Settings Key**: `import/autocorrect/move_leading_the_title`

### 4. Four Auto-Correction Preferences (Always Apply)
- **Current Location**: Preferences > Import > Auto-Correction section
- **Settings Keys**:
  - `import/autocorrect/trim_whitespace` - "Trim whitespace"
  - `import/autocorrect/strip_leading_punctuation` - "Strip leading punctuation"
  - `import/autocorrect/remove_non_alphanumeric` - "Remove special characters"
  - `import/autocorrect/proper_case` - "Apply proper case"
- **New Behavior**: Always apply all these corrections before saving to database

---

## Affected Modules and Changes Required

### 1. Preferences Window (`src/ui/preferences_window.py`)
**Changes Required:**
- Remove `options_group` QGroupBox containing:
  - `auto_add_clean_books_check` checkbox
  - `flip_author_check` checkbox
  - `autocorrect_proper_case_check` checkbox
  - `autocorrect_move_the_check` checkbox
- Remove entire `autocorrect_block_group` QGroupBox containing:
  - `autocorrect_section_text` QTextEdit
  - `autocorrect_group` QGroupBox with checkboxes
  - `autocorrect_trim_check`, `autocorrect_strip_punct_check`, `autocorrect_non_alnum_check`
- Remove associated styling code in `apply_theme()`
- Remove settings loading code in `load_settings()`
- Remove settings saving code in `save_settings()`
- Remove state capture in `_capture_state()`
- Update F1 help text and shortcuts if needed

### 2. Import Window (`src/ui/import_window.py`)
**Changes Required:**
- Remove `auto_add_clean_books` instance variable and loading code
- Remove "Add Valid" button (`add_valid_button`) entirely
- Remove `_update_add_valid_button_visibility()` method
- Remove `_configure_error_filter_options()` and associated filter logic
- Update status bar messages to reflect auto-add behavior
- Remove `flip_author_names` preference loading
- Remove `autocorrect_*` preference loading (still need to pass to ImportScanner, but always True)
- Remove `if self.flip_author_names` conditional in import logic
- Update F1 help text
- Update shortcuts documentation

### 3. Import Progress Window (`src/ui/import_progress_window.py`)
**Changes Required:**
- Remove references to "Add Valid" button if any
- Update status messages to reflect auto-add behavior

### 4. Book List Import Window (`src/ui/book_list_import_window.py`)
**Changes Required:**
- Remove `flip_author` preference reading
- Remove `move_articles` preference reading
- Change title/author comparison to always use normalized versions
- The `normalize_title_for_compare()` and `normalize_author_for_compare()` functions should always apply

### 5. Web Metadata Window (`src/ui/web_metadata.py`)
**Changes Required:**
- Remove `_read_user_preferences()` method
- Remove `move_articles` and `flip_author` parameters from all methods
- Update `clean_web_data_for_storage()` to always apply transformations
- Update web fetch calls to not pass these preferences

### 6. Main Window (`src/ui/main_window.py`)
**Changes Required:**
- Remove `move_articles` and `flip_author` preference reading in web fetch sections
- Update web API calls to not pass these preferences

### 7. Book Detail Window (`src/ui/book_details.py`)
**Changes Required:**
- Remove `move_articles` and `flip_author` preference reading in web fetch sections
- Update web API calls to not pass these preferences

### 8. Update Window (`src/ui/update_window.py`)
**Changes Required:**
- Remove `_is_proper_case_enabled()` method
- Update `_normalize_name_field()` to always apply proper case

### 9. Name List Window (`src/ui/name_list_window.py`)
**Changes Required:**
- Update name normalization to always apply all corrections

### 10. Collection Window (`src/ui/collection_window.py`)
**Changes Required:**
- Update name/title normalization to always apply all corrections

### 11. Import Detail Window (`src/ui/import_detail_window.py`)
**Changes Required:**
- Update field normalization to always apply all corrections

### 12. Import Scanner (`src/core/import_scanner.py`)
**Changes Required:**
- Keep `configure()` method but change defaults:
  - `trim_whitespace=True`
  - `strip_leading_punctuation=True`
  - `remove_non_alphanumeric=True`
  - `proper_case_fields=True`
  - `move_leading_the_title=True`
- Remove conditional checks in `_apply_auto_corrections()` - always apply all corrections
- Simplify `apply_preferences()` to always apply all corrections

### 13. Validator (`src/core/validator.py`)
**Changes Required:**
- Keep `flip_author_name()` method for internal use
- Keep `normalize_title_for_compare()` method - always use it
- Update to always apply all auto-corrections in `normalize_title_for_compare()`

### 14. Web Book API (`src/web/web_book_api.py`)
**Changes Required:**
- Remove `move_articles` and `flip_author` parameters from methods
- Always apply title/author transformations in search and comparison
- `clean_web_data_for_storage()` always applies transformations

---

## Implementation Approach

### Phase 1: Core Logic Changes (Foundation)
1. Update `import_scanner.py` - Always apply all auto-corrections
2. Update `validator.py` - Always normalize for comparison
3. Update `web_book_api.py` - Remove preference parameters, always apply

### Phase 2: UI Window Updates (Preferences First)
1. Update `preferences_window.py` - Remove UI elements and settings code
2. Update `import_window.py` - Remove "Add Valid" button and preference checks
3. Update `import_progress_window.py` - Update status messages

### Phase 3: Window-by-Window Updates
1. `book_list_import_window.py`
2. `web_metadata.py`
3. `main_window.py`
4. `book_details.py`
5. `update_window.py`
6. `name_list_window.py`
7. `collection_window.py`
8. `import_detail_window.py`

### Phase 4: Testing
1. Test import flow end-to-end
2. Test web metadata fetch
3. Test book list import
4. Test all CRUD operations on book details
5. Test name list and collection management

---

## Testing Checklist

### Import Flow
- [ ] Scan books with errors and without errors
- [ ] Verify clean books are automatically added (no "Add Valid" button)
- [ ] Verify error books are flagged and require manual review
- [ ] Verify author normalization works correctly
- [ ] Verify title normalization works correctly
- [ ] Verify all auto-corrections are applied (trim, strip punct, proper case)

### Web Metadata
- [ ] Fetch web metadata for book
- [ ] Verify author transformation works
- [ ] Verify title transformation works
- [ ] Verify data is cleaned before storage

### Book List Import
- [ ] Import book list from CSV
- [ ] Verify title/author matching with series numbers
- [ ] Verify title/author matching with articles ("The", "A", "An")

### CRUD Operations
- [ ] Create new book - verify auto-corrections applied
- [ ] Read book - verify display format
- [ ] Update book - verify auto-corrections applied on save
- [ ] Delete book - verify works as expected

### Name Management
- [ ] Add new author/genre/narrator - verify proper case applied
- [ ] Edit existing names - verify auto-corrections applied

---

## Benefits of This Refactoring

1. **Simplified User Experience**: Users no longer need to understand complex preferences
2. **Consistent Behavior**: All data is cleaned consistently throughout the app
3. **Reduced Code Complexity**: Remove conditional logic checking preferences
4. **Fewer Bugs**: Less configuration means fewer edge cases and bugs
5. **Better Data Quality**: All database entries will have consistent formatting
6. **Easier Maintenance**: Fewer code paths to maintain

---

## Migration Notes

- Existing user settings will be ignored but remain in their settings files
- New behavior will be immediately active after update
- Database entries will be progressively cleaned as books are edited
- No database schema migration required
