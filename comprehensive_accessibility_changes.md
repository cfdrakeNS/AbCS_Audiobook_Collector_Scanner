# Comprehensive Accessibility Changes - One Window at a Time

## Windows Requiring Changes (7 windows)

### 1. book_details.py - HIGH PRIORITY
**Cancel Button Standardization:**
- Remove cancel_button QPushButton and all references
- Add Escape key QShortcut for cancel functionality
- Change Alt+L from Cancel to table focus
- Update ALLOWED_ALT_LETTERS (remove B, add L)
- Update shortcut manager callback map
- Update F1 help dialog shortcuts list

**Other Standardization Issues:**
- None identified - already has good accessibility

### 2. preferences_window.py - HIGH PRIORITY
**Cancel Button Standardization:**
- Remove cancel_button QPushButton and all references
- Add Escape key QShortcut for cancel functionality
- Change Alt+L from Cancel to table focus
- Update ALLOWED_ALT_LETTERS (remove B, add L)
- Update shortcut manager callback map
- Update F1 help dialog shortcuts list

**Other Standardization Issues:**
- None identified - already has good accessibility

### 3. name_list_window.py - MEDIUM PRIORITY
**Cancel Button Standardization:**
- Remove cancel_button QPushButton and all references
- Add Escape key QShortcut for cancel functionality
- Change Alt+L from Cancel to table focus
- Update ALLOWED_ALT_LETTERS (remove B, add L)
- Update shortcut manager callback map
- Update F1 help dialog shortcuts list

**Other Standardization Issues from code_full_review_mar27.md:**
- Complex status message formatting logic (could be simplified)
- Missing accessible names for some dynamic elements
- Missing keyboard shortcuts for common operations

### 4. import_window.py - MEDIUM PRIORITY
**Cancel Button Standardization:**
- Remove cancel_button QPushButton and all references
- Add Escape key QShortcut for cancel functionality
- Change Alt+L from Cancel to table focus
- Update ALLOWED_ALT_LETTERS (remove B, add L)
- Update shortcut manager callback map
- Update F1 help dialog shortcuts list

**Other Standardization Issues:**
- None identified - already has good accessibility

### 5. import_detail_window.py - MEDIUM PRIORITY
**Cancel Button Standardization:**
- Remove cancel_button QPushButton and all references
- Add Escape key QShortcut for cancel functionality
- Change Alt+L from Cancel to table focus
- Update ALLOWED_ALT_LETTERS (remove B, add L)
- Update shortcut manager callback map
- Update F1 help dialog shortcuts list

**Other Standardization Issues from code_full_review_mar27.md:**
- Complex status mirroring to parent (could be simplified)
- Missing keyboard shortcuts for save/skip operations
- No explicit focus management after save operations
- Limited accessibility for validation error display

### 6. import_progress_window.py - LOW PRIORITY
**Cancel Button Standardization:**
- Remove cancel_button QPushButton and all references
- Add Escape key QShortcut for cancel functionality
- Change Alt+L from Cancel to table focus
- Update ALLOWED_ALT_LETTERS (remove B, add L)
- Update shortcut manager callback map
- Update F1 help dialog shortcuts list

**Other Standardization Issues from code_full_review_mar27.md:**
- Status announcement recursion issue in on_read_status_bar()
- Missing keyboard shortcuts for cancel/pause operations
- Limited accessibility for progress indicators

### 7. main_window.py - LOW PRIORITY
**Cancel Button Standardization:**
- Remove cancel_button QPushButton and all references
- Add Escape key QShortcut for cancel functionality
- Change Alt+L from Cancel to table focus
- Update ALLOWED_ALT_LETTERS (remove B, add L)
- Update shortcut manager callback map
- Update F1 help dialog shortcuts list

**Other Standardization Issues:**
- None identified - already has good accessibility

## Windows Already Compliant (No Changes Needed)

- collection_window.py - Already standardized
- update_window.py - No cancel button
- backup_restore_window.py - No cancel button
- reading_history_window.py - No cancel button

## Windows With Gaps But No Cancel Button

- web_metadata.py - No cancel button but has gaps to address:
  - Missing centralized shortcut manager integration
  - Inconsistent status implementation (basic vs helper)
  - No explicit tab order management
  - Missing focus management after operations

## Implementation Strategy

**For Each Window:**
1. Complete ALL cancel button standardization changes
2. Complete ALL other standardization issues listed
3. Test thoroughly with JAWS
4. Update documentation
5. Move to next window

**This ensures no revisiting windows for additional changes later.**

## Cancel Button Standardization Steps (for each window)

1. Remove cancel_button QPushButton and all references
2. Add Escape key QShortcut connected to cancel functionality
3. Add Alt+L QShortcut connected to table focus
4. Update ALLOWED_ALT_LETTERS (remove B, add L)
5. Update shortcut manager callback map
6. Update F1 help dialog shortcuts list
7. Test Escape and Alt+L work correctly
8. Test with JAWS screen reader

## Benefits of This Standardization

- Alt+L for "List" makes sense for screen readers (JAWS reads tables as lists)
- Escape for Cancel follows Windows standards
- More intuitive keyboard navigation
- Consistent behavior across all windows
