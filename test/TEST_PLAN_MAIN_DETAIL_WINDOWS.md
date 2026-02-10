# AbCS Test Plan - Main Window and Book Details Window

**Based on:** AbCS Quick Guide (February 2026)  
**Test Date:** _____________  
**Tester:** _____________  
**Version:** _____________

---

## Prerequisites

- [ ] Application installed and launches successfully
- [ ] Database contains test data (at least 5-10 books with varied Authors, Series, Genres)
- [ ] At least 2 Collections exist for collection switching tests
- [ ] Mix of Read and Unread books exist
- [ ] Screen reader available for accessibility tests (JAWS or NVDA)

---

## Section 1: Application Startup

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 1.1 | First launch - empty database | Start app with empty database | Message box displays with Import/New options | | |
| 1.2 | Normal launch - data exists | Start app with existing data | Main Window displays with book list | | |
| 1.3 | Splash screen statistics | Observe splash screen on startup | Shows DB name, title count, author count | | |

---

## Section 2: Application Scaling (Zoom)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 2.1 | Zoom In | Press Ctrl+Plus | All fonts and UI elements increase in size | | |
| 2.2 | Zoom Out | Press Ctrl+Minus | All fonts and UI elements decrease in size | | |
| 2.3 | Reset Zoom | Press Ctrl+0 (zero) | Zoom resets to default (100%) | | |
| 2.4 | Multiple zoom in | Press Ctrl+Plus 3 times | Progressive size increase each time | | |
| 2.5 | Multiple zoom out | Press Ctrl+Minus 3 times | Progressive size decrease each time | | |
| 2.6 | Zoom persistence | Zoom in, close app, reopen | Zoom level persists between sessions | | |

---

## Section 3: Main Window - Menu System

### 3.1 File Menu (Alt+F)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 3.1.1 | Open File menu | Press Alt+F | File menu opens | | |
| 3.1.2 | New Book | Alt+F → New Book (or Ctrl+N) | Book Details window opens in new mode | | |
| 3.1.3 | Import | Alt+F → Import | Import window opens | | |
| 3.1.4 | Quit | Alt+F → Quit (or Ctrl+Q) | Application closes | | |

### 3.2 View Menu (Alt+V)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 3.2.1 | Open View menu | Press Alt+V | View menu opens | | |
| 3.2.2 | Book Details | Alt+V → Book Details (or Ctrl+Enter) | Book Details window opens for selected book | | |
| 3.2.3 | Author | Alt+V → Author | Author management window opens | | |
| 3.2.4 | Genre | Alt+V → Genre | Genre management window opens | | |
| 3.2.5 | Series | Alt+V → Series | Series management window opens | | |
| 3.2.6 | Zoom In via menu | Alt+V → Zoom In | UI zooms in | | |
| 3.2.7 | Zoom Out via menu | Alt+V → Zoom Out | UI zooms out | | |
| 3.2.8 | Reset Zoom via menu | Alt+V → Reset Zoom | Zoom resets to default | | |

### 3.3 Manage Menu (Alt+M)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 3.3.1 | Open Manage menu | Press Alt+M | Manage menu opens | | |
| 3.3.2 | Preferences | Alt+M → Preferences | Preferences dialog opens | | |
| 3.3.3 | Backup/Restore | Alt+M → Backup, Restore | Backup/Restore window opens | | |
| 3.3.4 | Statistics | Alt+M → Statistics | Statistics display shown | | |

### 3.4 Help Menu (Alt+H)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 3.4.1 | Open Help menu | Press Alt+H | Help menu opens | | |
| 3.4.2 | About AbCS | Alt+H → About AbCS | About dialog displays version info | | |
| 3.4.3 | Shortcut Keys | Alt+H → Shortcut Keys (or F1) | Shortcut keys help displayed | | |

---

## Section 4: Main Window - Header Controls

### 4.1 Collection Combo (Alt+C)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 4.1.1 | Access Collection | Press Alt+C | Focus moves to Collection combo | | |
| 4.1.2 | Switch collection | Select different collection | Book list filters to selected collection | | |
| 4.1.3 | All collections | Select "All" | All books from all collections displayed | | |
| 4.1.4 | Collection count | Switch collection | Status bar shows correct book count | | |

### 4.2 Read Filter Combo (Alt+R)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 4.2.1 | Access Read filter | Press Alt+R | Focus moves to Read filter combo | | |
| 4.2.2 | Filter All | Select "All" | All books displayed (read and unread) | | |
| 4.2.3 | Filter Read | Select "Read" | Only read books displayed | | |
| 4.2.4 | Filter Unread | Select "Unread" | Only unread books displayed | | |
| 4.2.5 | Read filter count | Change filter | Status bar shows correct filtered count | | |

### 4.3 Order By Combo (Alt+O)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 4.3.1 | Access Order By | Press Alt+O | Focus moves to Order By combo | | |
| 4.3.2 | Sort by Title | Select "Title" | Books sorted by Title; Search searches titles | | |
| 4.3.3 | Sort by Author | Select "Author" | Books sorted by Author, Year, Title | | |
| 4.3.4 | Sort by Genre | Select "Genre" | Books sorted by Genre, Title; only books with Genre shown | | |
| 4.3.5 | Sort by Series | Select "Series" | Books sorted by Series, Year, Title; only books with Series shown | | |
| 4.3.6 | Status bar update | Change sort order | Status bar reflects new sort order | | |

### 4.4 Search Box (Alt+S)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 4.4.1 | Access Search | Press Alt+S | Focus moves to Search box | | |
| 4.4.2 | Type-ahead search | Type partial text | List filters as you type | | |
| 4.4.3 | Search Enter | Type text and press Enter | Focus moves to first matching record in book table | | |
| 4.4.4 | Search Title mode | Order By = Title, search | Searches within titles | | |
| 4.4.5 | Search Author mode | Order By = Author, search | Searches within authors | | |
| 4.4.6 | Search Genre mode | Order By = Genre, search | Searches within genres | | |
| 4.4.7 | Search Series mode | Order By = Series, search | Searches within series | | |
| 4.4.8 | Keyword search | Type "?keyword" and Enter | Filters to records containing keyword | | |
| 4.4.9 | Keyword phrase | Type "?word1 word2" and Enter | Filters to records containing phrase | | |
| 4.4.10 | Clear search | Press Escape | Search cleared, full list restored | | |
| 4.4.11 | No results | Search for non-existent text | Appropriate feedback (empty list or message) | | |
| 4.4.12 | Collection scope | Collection="Specific", search | Only searches within current collection | | |
| 4.4.13 | All Collections scope | Collection="All", search | Searches across all collections | | |

---

## Section 5: Main Window - Book List (Detail Section)

### 5.1 Book List Display

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 5.1.1 | Column display | View book list | Columns: Author, Title, Year, Plot, Series, Genre, Time, Tracks, Read, Date-added | | |
| 5.1.2 | Navigate with arrows | Use Up/Down arrow keys | Selection moves through list | | |
| 5.1.3 | Focus to book list | Press Alt+B | Focus moves to book detail list | | |

### 5.2 Opening Book Details

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 5.2.1 | Open via Ctrl+Enter | Select book, press Ctrl+Enter | Book Details window opens for selected book | | |
| 5.2.2 | Open via double-click | Double-click on book row | Book Details window opens for clicked book | | |

### 5.3 Multi-Selection

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 5.3.1 | Enter select mode | Press Shift+Space | Selection mode entered | | |
| 5.3.2 | Extend selection keyboard | Shift+Up/Down arrows | Multiple books selected | | |
| 5.3.3 | Ctrl+Click select | Ctrl+Click on books | Individual books added to selection | | |
| 5.3.4 | Shift+Click range | Click first, Shift+Click last | Range of books selected | | |
| 5.3.5 | Selection status | Select multiple books | Status shows last book title and count selected | | |
| 5.3.6 | Buttons appear | Select one or more books | Update, Delete, Cancel buttons become visible | | |
| 5.3.7 | Clear via Cancel | Press Alt+L or click Cancel | Selection cleared, buttons hidden | | |
| 5.3.8 | Clear via arrow | Press arrow key | Selection cleared | | |
| 5.3.9 | Clear via mouse | Click without Ctrl/Shift | Selection cleared | | |

---

## Section 6: Main Window - Footer

### 6.1 Button Visibility

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 6.1.1 | Buttons hidden default | View footer with no selection | Update, Delete, Cancel buttons hidden | | |
| 6.1.2 | Buttons visible | Select one or more books | Update, Delete, Cancel buttons visible | | |

### 6.2 Update Button (Alt+U)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 6.2.1 | Access Update | Select books, press Alt+U | Update Window opens | | |
| 6.2.2 | Update single book | Select 1 book, Update | Update Window shows 1 book selected | | |
| 6.2.3 | Update multiple books | Select 5 books, Update | Update Window shows 5 books selected | | |

### 6.3 Delete Button (Alt+D)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 6.3.1 | Access Delete | Select books, press Alt+D | Confirmation message appears | | |
| 6.3.2 | Confirm delete | Select Yes in confirmation | Selected books deleted, list updated | | |
| 6.3.3 | Cancel delete | Select No in confirmation | Books not deleted, selection intact | | |
| 6.3.4 | Delete single | Select 1 book, delete, confirm | Book deleted | | |
| 6.3.5 | Delete multiple | Select 3 books, delete, confirm | All 3 books deleted | | |

### 6.4 Cancel Button (Alt+L)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 6.4.1 | Access Cancel | Press Alt+L | Selection cleared, buttons hidden | | |
| 6.4.2 | Click Cancel | Click Cancel button | Selection cleared, buttons hidden | | |

### 6.5 Status Bar

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 6.5.1 | Book count display | View status bar | Shows "xx books in collection" | | |
| 6.5.2 | Sort order display | Change Order By | Status bar shows current sort order | | |
| 6.5.3 | Search results | Perform search | Status bar shows search results info | | |
| 6.5.4 | Selection message | Select books | Status bar shows selection count | | |

---

## Section 7: Main Window - All Shortcut Keys

| ID | Shortcut | Action | Expected Result | Pass/Fail | Notes |
|----|----------|--------|-----------------|-----------|-------|
| 7.1 | Alt+C | Collection | Focus moves to Collection combo | | |
| 7.2 | Alt+R | Read filter | Focus moves to Read combo | | |
| 7.3 | Alt+O | Order By | Focus moves to Order By combo | | |
| 7.4 | Alt+S | Search | Focus moves to Search box | | |
| 7.5 | Alt+B | Book Detail | Focus moves to book list | | |
| 7.6 | Alt+U | Update | Opens Update window (if selected) | | |
| 7.7 | Alt+D | Delete | Triggers delete (if selected) | | |
| 7.8 | Alt+L | Cancel | Clears selection | | |
| 7.9 | Ctrl+N | New Book | Opens Book Details in new mode | | |
| 7.10 | Ctrl+Q | Quit | Closes application | | |
| 7.11 | Ctrl+Enter | Book Details | Opens Book Details for selected | | |

---

## Section 8: Book Details Window - Header

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 8.1 | Sort order display | Open Book Details | Header shows current sort order (e.g., "Title, author") | | |
| 8.2 | Sort reflects main | Change Order By in Main, open Details | Header reflects Main Window sort setting | | |

---

## Section 9: Book Details Window - Form Fields

### 9.1 Row 1 - Title and Author

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 9.1.1 | Access Title | Press Alt+T | Focus moves to Title field | | |
| 9.1.2 | Edit Title | Type new title | Title updates | | |
| 9.1.3 | Access Author | Press Alt+A | Focus moves to Author combo | | |
| 9.1.4 | Author no arrow change | Press Up/Down in Author combo | Value does NOT change (prevents accidental changes) | | |
| 9.1.5 | Author expand | Press Alt+Down Arrow | Author dropdown expands | | |
| 9.1.6 | Author type-to-find | Type in expanded Author list | Jumps to matching author | | |
| 9.1.7 | Author select | Navigate and press Enter | Author selected | | |

### 9.2 Row 2 - Comments

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 9.2.1 | Access Comments | Press Alt+O | Focus moves to Comments field | | |
| 9.2.2 | Edit Comments | Type comment text | Comments field accepts plain text | | |
| 9.2.3 | Multi-line Comments | Enter line breaks | Multi-line text supported | | |

### 9.3 Row 3 - Year, Time, Reader, Date Read

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 9.3.1 | Access Year | Press Alt+Y | Focus moves to Year field | | |
| 9.3.2 | Access Time | Press Alt+M | Focus moves to Time field | | |
| 9.3.3 | Time format | Enter time value | Format is hh:mm | | |
| 9.3.4 | Access Reader | Press Alt+R | Focus moves to Reader field | | |
| 9.3.5 | Access Date Read | Press Alt+E | Focus moves to Date Read field | | |
| 9.3.6 | Date Read format | Enter date | Format is YYYY-MM-DD (4-digit year, 2-digit month, 2-digit day) | | |
| 9.3.7 | Date Read tab navigation | Tab within Date Read | Tab moves between year, month, day components | | |

### 9.4 Row 4 - Series, Genre, Collection

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 9.4.1 | Access Series | Press Alt+I | Focus moves to Series combo | | |
| 9.4.2 | Series no arrow change | Press Up/Down in Series combo | Value does NOT change | | |
| 9.4.3 | Series expand | Press Alt+Down Arrow | Series dropdown expands | | |
| 9.4.4 | Access Genre | Press Alt+G | Focus moves to Genre combo | | |
| 9.4.5 | Genre no arrow change | Press Up/Down in Genre combo | Value does NOT change | | |
| 9.4.6 | Genre expand | Press Alt+Down Arrow | Genre dropdown expands | | |
| 9.4.7 | Access Collection | Press Alt+L | Focus moves to Collection combo | | |
| 9.4.8 | Collection no arrow change | Press Up/Down in Collection combo | Value does NOT change | | |
| 9.4.9 | Collection expand | Press Alt+Down Arrow | Collection dropdown expands | | |

### 9.5 Row 5 - Bitrate, Size, File Format, Source

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 9.5.1 | Access Bitrate | Press Alt+B | Focus moves to Bitrate field | | |
| 9.5.2 | Access Size | Press Alt+S | Focus moves to Size field | | |
| 9.5.3 | Size display | View size field | Size shown in MB | | |
| 9.5.4 | File Format display | View File Format | Shows format (MP3, etc.) | | |
| 9.5.5 | Source display | View Source field | Shows Windows user-id from import | | |

### 9.6 Row 6 - Path, Date Added

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 9.6.1 | Access Path | Press Alt+H | Focus moves to Path field | | |
| 9.6.2 | Open Path Ctrl+Enter | Press Ctrl+Enter in Path | Opens folder in file explorer (if exists) | | |
| 9.6.3 | Open Path double-click | Double-click Path field | Opens folder in file explorer (if exists) | | |
| 9.6.4 | Access Date Added | Press Alt+E | Focus moves to Date Added field | | |

### 9.7 Field Navigation

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 9.7.1 | Tab through fields | Press Tab repeatedly | Focus moves through all fields in order | | |
| 9.7.2 | Shift+Tab reverse | Press Shift+Tab | Focus moves backwards through fields | | |
| 9.7.3 | Cursor position | Tab to text field | Cursor placed at end of existing text | | |

---

## Section 10: Book Details Window - Footer Buttons

### 10.1 New Button (Ctrl+N / Alt+W)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 10.1.1 | Access New | Press Ctrl+N or Alt+W | Window clears for new entry | | |
| 10.1.2 | Collection auto-fill | Click New | Collection field auto-filled | | |
| 10.1.3 | Date Added auto-fill | Click New | Date Added field auto-filled with current date | | |
| 10.1.4 | New clears fields | Click New | All other fields cleared | | |

### 10.2 Save Button (Alt+V)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 10.2.1 | Save hidden initially | Open existing book, no changes | Save button not visible | | |
| 10.2.2 | Save visible on change | Modify any field | Save button becomes visible | | |
| 10.2.3 | Save record | Modify field, press Alt+V | Changes saved to database | | |
| 10.2.4 | Save new record | Create new, fill required, Save | New book saved to database | | |
| 10.2.5 | Save confirmation | Save changes | Appropriate feedback (status bar or message) | | |

### 10.3 Delete Button (Alt+D)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 10.3.1 | Access Delete | Press Alt+D | Confirmation message appears | | |
| 10.3.2 | Confirm delete | Select Yes | Book deleted, window behavior appropriate | | |
| 10.3.3 | Cancel delete | Select No | Book not deleted, window remains | | |

### 10.4 Close Button (Alt+C / Escape)

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 10.4.1 | Close via Alt+C | Press Alt+C | Window closes, returns to Main Window | | |
| 10.4.2 | Close via Escape | Press Escape | Window closes, returns to Main Window | | |
| 10.4.3 | Close via button | Click Close button | Window closes, returns to Main Window | | |
| 10.4.4 | Unsaved changes | Make changes, try to close | Prompt to save or discard (if applicable) | | |

### 10.5 Navigation - Previous/Next

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 10.5.1 | Previous via PageUp | Press Page Up | Moves to previous book in list | | |
| 10.5.2 | Next via PageDown | Press Page Down | Moves to next book in list | | |
| 10.5.3 | Previous via Alt+P | Press Alt+P | Moves to previous book | | |
| 10.5.4 | Next via Alt+N | Press Alt+N | Moves to next book | | |
| 10.5.5 | At first book | On first book, try Previous | Appropriate behavior (message or stay) | | |
| 10.5.6 | At last book | On last book, try Next | Appropriate behavior (message or stay) | | |

---

## Section 11: Book Details Window - All Shortcut Keys

| ID | Shortcut | Target | Expected Result | Pass/Fail | Notes |
|----|----------|--------|-----------------|-----------|-------|
| 11.1 | Alt+T | Title | Focus moves to title_edit | | |
| 11.2 | Alt+A | Author | Focus moves to author_combo | | |
| 11.3 | Alt+Y | Year | Focus moves to year_edit | | |
| 11.4 | Alt+F | Files | Focus moves to files_edit | | |
| 11.5 | Alt+I | Series | Focus moves to series_combo | | |
| 11.6 | Alt+G | Genre | Focus moves to genre_combo | | |
| 11.7 | Alt+R | Reader | Focus moves to reader_edit | | |
| 11.8 | Alt+L | Collection | Focus moves to collection_combo | | |
| 11.9 | Alt+M | Time | Focus moves to time_edit | | |
| 11.10 | Alt+S | Size | Focus moves to size_edit | | |
| 11.11 | Alt+B | Bitrate | Focus moves to bitrate_edit | | |
| 11.12 | Alt+H | Path | Focus moves to path_edit | | |
| 11.13 | Alt+O | Comments | Focus moves to comments_edit | | |
| 11.14 | Alt+E | Date Added | Focus moves to added_edit | | |
| 11.15 | Alt+W | New Book | Activates new_button | | |
| 11.16 | Alt+V | Save | Activates save_button | | |
| 11.17 | Alt+D | Delete | Activates delete_button | | |
| 11.18 | Alt+P | Previous | Activates prev_button | | |
| 11.19 | Alt+N | Next | Activates next_button | | |
| 11.20 | Alt+C | Close | Activates close_button | | |

---

## Section 12: Accessibility Testing

### 12.1 Screen Reader Compatibility

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 12.1.1 | Field labels announced | Tab to each field with JAWS/NVDA | Screen reader announces field name | | |
| 12.1.2 | Button labels announced | Tab to each button | Screen reader announces button name | | |
| 12.1.3 | Combo values announced | Focus on combo box | Screen reader announces current value | | |
| 12.1.4 | Status bar read | Status bar updates | Screen reader announces status messages | | |
| 12.1.5 | Selection feedback | Select books in list | Screen reader announces selection count | | |
| 12.1.6 | Menu navigation | Navigate menus | Screen reader announces menu items | | |

### 12.2 Keyboard Navigation

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 12.2.1 | Full keyboard access | Use only keyboard | All features accessible without mouse | | |
| 12.2.2 | Focus visible | Tab through controls | Focus indicator clearly visible | | |
| 12.2.3 | Logical tab order | Tab through window | Focus moves in logical order | | |
| 12.2.4 | No focus traps | Tab through all areas | Can exit all controls and areas | | |

### 12.3 Visual Accessibility

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 12.3.1 | Minimum font size | View with default settings | All text at least 14pt | | |
| 12.3.2 | Scaled fonts | Zoom to 150% | All fonts scale proportionally | | |
| 12.3.3 | High contrast theme | Apply High Contrast theme | All elements visible with high contrast | | |
| 12.3.4 | Shortcut underlines | View controls | Shortcut letters underlined | | |

---

## Section 13: Edge Cases and Error Handling

| ID | Test Case | Steps | Expected Result | Pass/Fail | Notes |
|----|-----------|-------|-----------------|-----------|-------|
| 13.1 | Search empty results | Search for non-existent text | Clear feedback, no crash | | |
| 13.2 | Delete last book | Delete only remaining book | Appropriate empty state | | |
| 13.3 | Save with blank title | Try to save book with empty title | Validation error or prevention | | |
| 13.4 | Save with blank author | Try to save book with empty author | Validation error or prevention | | |
| 13.5 | Invalid date format | Enter invalid date in Date Read | Validation error or auto-format | | |
| 13.6 | Invalid time format | Enter invalid time | Validation error or auto-format | | |
| 13.7 | Path not found | Ctrl+Enter on non-existent path | Error message, no crash | | |
| 13.8 | Very long title | Enter 500+ character title | Handles gracefully | | |
| 13.9 | Special characters | Enter special chars in fields | Saved and displayed correctly | | |
| 13.10 | Unicode characters | Enter unicode/international chars | Saved and displayed correctly | | |

---

## Test Summary

| Section | Total Tests | Passed | Failed | Blocked | Notes |
|---------|-------------|--------|--------|---------|-------|
| 1. Startup | 3 | | | | |
| 2. Scaling | 6 | | | | |
| 3. Menus | 17 | | | | |
| 4. Header Controls | 25 | | | | |
| 5. Book List | 12 | | | | |
| 6. Footer | 14 | | | | |
| 7. Main Shortcuts | 11 | | | | |
| 8. Details Header | 2 | | | | |
| 9. Details Fields | 24 | | | | |
| 10. Details Buttons | 16 | | | | |
| 11. Details Shortcuts | 20 | | | | |
| 12. Accessibility | 14 | | | | |
| 13. Edge Cases | 10 | | | | |
| **TOTAL** | **174** | | | | |

---

## Issues Found

| Issue # | Severity | Section | Description | Steps to Reproduce | Status |
|---------|----------|---------|-------------|-------------------|--------|
| | | | | | |
| | | | | | |
| | | | | | |

---

## Sign-off

**Tested By:** _______________________________ **Date:** _______________

**Reviewed By:** ______________________________ **Date:** _______________

**Notes:**
