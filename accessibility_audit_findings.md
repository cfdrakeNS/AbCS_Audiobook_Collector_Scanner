# Accessibility/Keyboard/Alt-Key Audit Findings (JAWS/Screen Reader)

## reference documents read before starting coding 
- PySide6_Accessibility_Patterns_and_Implementation_Reference
- PySide6_Screen_Reader_Accessibility_Best_Practices

## 1. Tab/Shift+Tab Exits Table to Next Control

- Impacted windows (all use QTableWidget or QTableView):
	- MainWindow
	- UpdateWindow
	- BookListImportWindow
	- ImportWindow
	- ImportDetailWindow
	- CollectionWindow
	- NameListWindow
	- BackupRestoreWindow
	- ReadingHistoryWindow
	- PreferencesWindow (if table present)
	- ImportProgressWindow (if table present)
	- WebMetadataWindow (if table present)
- **At least 10 windows.**
- Current: Tab/Shift+Tab cycles within the table cells. 
- Change needed: Override table key handling or use an event filter so Tab/Shift+Tab moves focus out of the table to the next/previous widget (standard accessibility pattern).

## 2. Status Bar Alt+Key Hints Only with Screen Reader

- Impacted windows:
	- MainWindow
	- UpdateWindow
	- BookListImportWindow
	- CollectionWindow
	- BackupRestoreWindow
	- ReadingHistoryWindow
	- (possibly others)
- **At least 6 windows.**
- Current: Uses announce_status_message() from accessibility/accessible_events.py. This checks QAccessible.isActive() (screen reader presence). If a screen reader is active, it moves focus to the status bar and announces the message. If not, it just updates the status bar visually.
- Change needed: If you want Alt+key hints to always show, remove the QAccessible.isActive() check or always call showMessage.

## 3. Add Alt+Keys to Windows Missing Them

- Impacted windows:
	- All main windows have Alt+key shortcuts (see src/accessibility/shortcuts.py)
	- Some dialogs (ImportDetailWindow, PreferencesWindow, ImportProgressWindow, WebMetadataWindow) may be missing full Alt+key coverage
- **At least 4–6 windows need review.**
- Change needed: Audit each window for missing Alt+key assignments and add them using the centralized ShortcutManager.

## Window-by-Window Summary

- MainWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- UpdateWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- BookListImportWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- ImportWindow: Table, Alt+keys (status bar hints maybe missing, Tab/Shift+Tab needs fix)
- ImportDetailWindow: Table, Alt+keys maybe missing, Tab/Shift+Tab needs fix
- CollectionWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- NameListWindow: Table, Alt+keys maybe missing, Tab/Shift+Tab needs fix
- BackupRestoreWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- ReadingHistoryWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- PreferencesWindow: Table maybe present, Alt+keys maybe missing, Tab/Shift+Tab needs fix
- ImportProgressWindow: Table maybe present, Alt+keys maybe missing, Tab/Shift+Tab needs fix
- WebMetadataWindow: Table maybe present, Alt+keys maybe missing, Tab/Shift+Tab needs fix

---

This file is at the project root for easier access.
# Accessibility/Keyboard/Alt-Key Audit Findings (JAWS/Screen Reader)

## 1. Tab/Shift+Tab Exits Table to Next Control

- Impacted windows: MainWindow, UpdateWindow, BookListImportWindow, ImportWindow, ImportDetailWindow, CollectionWindow, NameListWindow, BackupRestoreWindow, ReadingHistoryWindow, PreferencesWindow (if table), ImportProgressWindow, WebMetadataWindow (if table)
- At least 10 windows. All use QTableWidget or QTableView. Tab/Shift+Tab currently cycles within the table. Change needed: override table key handling or use event filter so Tab/Shift+Tab moves focus out of the table to the next/previous widget.

## 2. Status Bar Alt+Key Hints Only with Screen Reader

- Impacted windows: MainWindow, UpdateWindow, BookListImportWindow, CollectionWindow, BackupRestoreWindow, ReadingHistoryWindow, and possibly others. At least 6 windows.
- Approach: Uses announce_status_message() from accessibility/accessible_events.py. This checks QAccessible.isActive() (screen reader presence). If a screen reader is active, it moves focus to the status bar and announces the message. If not, it just updates the status bar visually. Change needed: If you want Alt+key hints to always show, remove the QAccessible.isActive() check or always call showMessage.

## 3. Add Alt+Keys to Windows Missing Them

- Impacted windows: All main windows have Alt+key shortcuts (see src/accessibility/shortcuts.py). Some dialogs (ImportDetailWindow, PreferencesWindow, ImportProgressWindow, WebMetadataWindow) may be missing full Alt+key coverage. At least 4–6 windows need review.
- Change needed: Audit each window for missing Alt+key assignments and add them using the centralized ShortcutManager.

## Window-by-Window Summary

- MainWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- UpdateWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- BookListImportWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- ImportWindow: Table, Alt+keys (status bar hints maybe missing, Tab/Shift+Tab needs fix)
- ImportDetailWindow: Table, Alt+keys maybe missing, Tab/Shift+Tab needs fix
- CollectionWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- NameListWindow: Table, Alt+keys maybe missing, Tab/Shift+Tab needs fix
- BackupRestoreWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- ReadingHistoryWindow: Table, status bar hints, Alt+keys (all present, but Tab/Shift+Tab needs fix)
- PreferencesWindow: Table maybe present, Alt+keys maybe missing, Tab/Shift+Tab needs fix
- ImportProgressWindow: Table maybe present, Alt+keys maybe missing, Tab/Shift+Tab needs fix
- WebMetadataWindow: Table maybe present, Alt+keys maybe missing, Tab/Shift+Tab needs fix

---
# Plan: Accessibility/Keyboard/Alt-Key Remediation by Window

## TL;DR
Implement accessibility fixes window by window for:
1. Tab/Shift+Tab exits table to next control
2. Status bar Alt+key hints always visible (or configurable)
3. Add missing Alt+keys to all major controls

## Steps (by window)

### 1. MainWindow
- Add setTabKeyNavigation(False) to book table
- Review tab order so Tab/Shift+Tab moves focus to next/previous control
- Confirm Alt+key status bar hints use centralized helper
- Confirm all major controls have Alt+key shortcuts

### 2. UpdateWindow
- Add setTabKeyNavigation(False) to table
- Review tab order
- Confirm status bar hint logic
- Confirm Alt+keys

### 3. BookListImportWindow
- Add setTabKeyNavigation(False) to mapping table
- Review tab order
- Confirm status bar hint logic
- Confirm Alt+keys

### 4. ImportWindow
- Add setTabKeyNavigation(False) to table
- Review tab order
- Confirm status bar hint logic (may be missing)
- Confirm Alt+keys

### 5. ImportDetailWindow
- Add setTabKeyNavigation(False) to table
- Review tab order
- Confirm status bar hint logic (may be missing)
- Add missing Alt+keys

### 6. CollectionWindow
- Add setTabKeyNavigation(False) to table
- Review tab order
- Confirm status bar hint logic
- Confirm Alt+keys

### 7. NameListWindow
- Add setTabKeyNavigation(False) to table
- Review tab order
- Add missing Alt+keys

### 8. BackupRestoreWindow
- Confirm setTabKeyNavigation(False) present
- Review tab order
- Confirm status bar hint logic
- Confirm Alt+keys

### 9. ReadingHistoryWindow
- Add setTabKeyNavigation(False) to tables
- Review tab order
- Confirm status bar hint logic
- Confirm Alt+keys

### 10. PreferencesWindow
- If table present, add setTabKeyNavigation(False)
- Review tab order
- Add missing Alt+keys

### 11. ImportProgressWindow
- If table present, add setTabKeyNavigation(False)
- Review tab order
- Add missing Alt+keys

### 12. WebMetadataWindow
- If table present, add setTabKeyNavigation(False)
- Review tab order
- Add missing Alt+keys

## Centralized Alt+key Status Bar Logic
- Confirm all windows use get_accessible_shortcuts_list from shortcut_helpers.py
- If always-on Alt+key hints are desired, update helper to remove screen reader check

## Verification
- Manual test with JAWS/NVDA for each window
- Confirm Tab/Shift+Tab exits table
- Confirm Alt+key hints always visible (if required)
- Confirm all major controls have Alt+key shortcuts

## Scope
- No code changes yet; this is a window-by-window implementation plan based on audit findings

