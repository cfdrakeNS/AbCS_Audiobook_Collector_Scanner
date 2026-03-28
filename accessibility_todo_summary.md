# Accessibility TODO Summary - March 28, 2026

## Windows Requiring Cancel Button Standardization (7 windows)

### Priority 1: book_details.py
**Changes Needed:**
- Remove Cancel button
- Add Escape key for cancel
- Change Alt+L from Cancel to table focus
- Update F1 help dialog
- Test with JAWS

### Priority 2: preferences_window.py  
**Changes Needed:**
- Remove Cancel button
- Add Escape key for cancel
- Change Alt+L from Cancel to table focus
- Update F1 help dialog
- Test with JAWS

### Priority 3: name_list_window.py
**Changes Needed:**
- Remove Cancel button
- Add Escape key for cancel
- Change Alt+L from Cancel to table focus
- Update F1 help dialog
- Test with JAWS

### Priority 4: import_window.py
**Changes Needed:**
- Remove Cancel button
- Add Escape key for cancel
- Change Alt+L from Cancel to table focus
- Update F1 help dialog
- Test with JAWS

### Priority 5: import_detail_window.py
**Changes Needed:**
- Remove Cancel button
- Add Escape key for cancel
- Change Alt+L from Cancel to table focus
- Update F1 help dialog
- Test with JAWS

### Priority 6: import_progress_window.py
**Changes Needed:**
- Remove Cancel button
- Add Escape key for cancel
- Change Alt+L from Cancel to table focus
- Update F1 help dialog
- Test with JAWS

### Priority 7: main_window.py
**Changes Needed:**
- Remove Cancel button
- Add Escape key for cancel
- Change Alt+L from Cancel to table focus
- Update F1 help dialog
- Test with JAWS

## Windows Already Compliant (No Changes Needed)

- collection_window.py - Already standardized
- web_metadata.py - No cancel button
- update_window.py - No cancel button
- backup_restore_window.py - No cancel button
- reading_history_window.py - No cancel button

## Implementation Steps for Each Window

1. Remove cancel_button QPushButton and all references
2. Add Escape key QShortcut connected to cancel functionality
3. Add Alt+L QShortcut connected to table focus
4. Update ALLOWED_ALT_LETTERS (remove B, add L)
5. Update shortcut manager callback map
6. Update F1 help dialog shortcuts list
7. Test Escape and Alt+L work correctly
8. Test with JAWS screen reader

## Benefits

- Alt+L for "List" makes sense for screen readers
- Escape for Cancel follows Windows standards
- More intuitive keyboard navigation
- Consistent behavior across all windows
