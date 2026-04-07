# Accessibility/Keyboard/Alt-Key Audit Findings (JAWS/Screen Reader)

## 1. Tab/Shift+Tab Exits Table to Next Control

**Windows/Tables Impacted:**
- MainWindow (Book Table)
- UpdateWindow (table)
- ImportWindow (table)
- NameListWindow (table)
- BackupRestoreWindow (table)
- ReadingHistoryWindow (table)

**Current State:**
Most tables use QTableWidget or QTableView. By default, Tab/Shift+Tab cycles within the table cells, not out to the next control. 
**Action Needed:**
All windows with tables will need review for this behavior. At least 10 windows are impacted.

---

## 2. Status Bar Alt+Key Hints Only with Screen Reader

**Windows Impacted:**
- MainWindow (status bar hints for Alt+U, Alt+D, Escape, etc.)
- Other windows with status bar hints (UpdateWindow, BookListImportWindow, etc.)

**Current State:**
Status bar messages for Alt+key shortcuts are only shown if a screen reader is detected.  
**Action Needed:**
Review all windows with status bar hints. At least 4–6 windows are impacted.

---

## 3. Add Alt+Keys to Windows Missing Them

**Windows Impacted:**
- All windows should have Alt+letter shortcuts for major controls.
- Some windows (e.g., PreferencesWindow, ImportProgressWindow, ImportDetailWindow, WebMetadataWindow) may be missing some Alt+key assignments.

**Current State:**
Most main windows have Alt+key shortcuts, but some secondary or dialog windows may lack full coverage.  
**Action Needed:**
Audit all 12+ windows for missing Alt+key assignments.

---

## Summary Table


## Window-by-Window List (for JAWS)

- MainWindow: Table present, status bar hints present, Alt+keys present.
- BookDetailsWindow: Table maybe present, status bar hints maybe present, Alt+keys present.
- UpdateWindow: Table present, status bar hints present, Alt+keys present.
- BookListImportWindow: Table present, status bar hints present, Alt+keys present.
- ImportWindow: Table present, status bar hints maybe present, Alt+keys present.
- ImportDetailWindow: Table present, status bar hints maybe present, Alt+keys maybe present.
- CollectionWindow: Table present, status bar hints present, Alt+keys present.
- NameListWindow: Table present, status bar hints maybe present, Alt+keys maybe present.
- BackupRestoreWindow: Table present, status bar hints present, Alt+keys present.
- PreferencesWindow: Table maybe present, status bar hints maybe present, Alt+keys maybe present.
- ReadingHistoryWindow: Table present, status bar hints present, Alt+keys present.
- ImportProgressWindow: Table maybe present, status bar hints maybe present, Alt+keys maybe present.
- WebMetadataWindow: Table maybe present, status bar hints maybe present, Alt+keys maybe present.

---

**Note:**
- "Maybe" means the feature may be present depending on implementation or context.
- JAWS/Screen reader users: These findings are based on code review and may need live testing for edge cases.
