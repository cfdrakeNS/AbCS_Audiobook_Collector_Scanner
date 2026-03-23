# Phase 2: Implement Reading History Statistics feature

## 1. Enhance existing History of books read ✅ **COMPLETED**
**Current State**: Fully implemented with comprehensive accessibility support.

**What Works**: 
- ✅ Date picker opens when you press Ctrl+Enter on a book
- ✅ Date is saved and table updates
- ✅ Status bar announces changes for JAWS
- ✅ **NEW**: Dedicated Reading History Window (Alt+H) with full statistics
- ✅ **NEW**: Date range queries with filtering
- ✅ **NEW**: Monthly/yearly breakdowns with accessible tables
- ✅ **NEW**: Reading statistics (total books, hours, averages)
- ✅ **NEW**: Full keyboard navigation and screen reader support

**Implementation Completed**:
- ✅ Added `reading_queries.py` for statistics queries
- ✅ Added `reading_history_window.py` - dedicated statistics viewer
- ✅ Added menu option: "View > Reading History"
- ✅ Full accessibility with Alt+H shortcut
- ✅ Used existing read_date field - no schema changes needed

**Technical Features Implemented**:
- ✅ Query books table WHERE read_date IS NOT NULL
- ✅ Calculate statistics from existing data
- ✅ Group by month/year for breakdowns
- ✅ Display in accessible table format
- ✅ Date range filtering with search functionality
- ✅ Ultra-compact layout for low vision users
- ✅ JAWS-compatible message displays

---

## 2. Import book cover 🟡 **NEXT PRIORITY**
**Current State**: No cover import functionality exists.

**Implementation Plan**:
- **Database Schema**: Add BLOB or file path storage for cover images
- **Book Details Window Changes**:
  - Add cover image display area
  - Add import button with Alt+letter shortcut
  - Support JPG/PNG file selection
  - Store image in database or managed folder
  - Move Author field to new line for cover space
  - Ensure image area is accessible with alt text and keyboard focus
  - Validate image size and format on import
- **Import Process Integration**: Cover images imported as part of standard book import workflow
- **Main Window Enhancement**: Show cover thumbnails in book list after import

**Files to Modify**:
- Update database schema for image storage
- Modify `book_details.py` layout and functionality
- Update `import_window.py` to include cover import options
- Add image validation and processing

---

## 3. Get book details from web 🟢 **NEXT PRIORITY**
**Current State**: No web integration exists.

**Implementation Plan**:
- **API Integration**: Connect to Google Books API and Open Library API
- **Libraries Required**: `requests`, `isbnlib`, `thefuzz` for fuzzy matching
- **Database Schema**: NO CHANGES REQUIRED - use existing structure
  - `books.comments` field - store plot/summary (already exists)
  - `series` table - link via existing `books.series_id` foreign key
  - `genres` table - link via existing `books.genre_id` foreign key
  - `authors` table - link via existing `books.author_id` foreign key

**Technical Implementation**:
- **Search Logic**: Use `isbnlib.isbn_from_words()` to find ISBN from title/author
- **Fuzzy Matching**: Use `thefuzz.fuzz.ratio()` to compare scanned vs API data
- **API Services**: Google Books API (free) + Open Library API (open source)
- **Data Validation**: Levenshtein distance for spelling corrections

**Book Details Window Enhancement**:
- **New Window**: Create `web_book_details_window.py` modeled from `book_details_window.py`
- **Accessibility**: Inherit all accessibility features from existing book details window
- **Alt+G Shortcut**: "Get book details from web" opens new web details window

**Web Book Details Window Modifications**:
- **Remove Fields**: collection, reader, date read, files, bitrate, size, format, path, date added
- **Change Combo Boxes to Text Fields**: author, genre, series (remove combo box code)
- **Field Properties**: All fields set to read-only but accessible to screen readers (like period message in reading_history_window)
- **Remove Messaging**: No field update messages/status announcements
- **Layout Changes**: Vertical alignment with one field per line and comments/plot at the bottom 
- **Web Data Indicators**: Add accessible indicators to right of each field showing if web data differs (check mark or similar accessible element)
- **Button Changes**: "Add Plot" and "Update All" buttons

**Technical Implementation**:
- **Window Class**: `WebBookDetailsWindow` inherits from `BookDetailsWindow`
- **Field Layout**: Vertical form layout for screen reader navigation
- **Accessibility Indicators**: Use `QLabel` with accessible names for web data differences
- **Read-Only Fields**: Use `QLineEdit` with `setReadOnly(True)` and proper accessibility
- **Button Functions**: 
  - "Add Plot": Add plot summary to comments field
  - "Update All": Apply all web data changes to original book record

**Error Handling**:
- **Network Connectivity**: Graceful API error handling
- **Rate Limiting**: Respect API limits with retry logic
- **Data Validation**: Sanitize and validate API responses
- **User Consent**: Clear prompts before data updates

**Files to Modify**:
- `src/database/models.py` - NO CHANGES (use existing structure)
- `src/ui/book_details.py` - Add fetch button to open web details window
- `src/ui/web_book_details_window.py` - NEW: modeled from book_details_window.py
- `src/database/queries.py` - Add API metadata update methods
- `src/main.py` - Add required library imports

**Batch Processing (Future Enhancement)**:
- main window add new button to the selection process "DownLoad Metadata"
- Multi-select books for bulk metadata fetching
- Progress bar with screen reader announcements
- "Scanning book 5 of 10..." accessibility feedback
- when scan is complete, show message box with buttons: "Auto Update" AND "Review Changes
- if "Auto Update" is selected, update all books with web data
- if "Review Changes" is selected, open web details window for each book 
- allow pgup / pgddn to move through books
---

## Additional Feature Ideas
- **Bulk Edit**: Multi-select books for collection management
- **Custom Collections**: Color-coded user collections
- **Statistics Dashboard**: Reading metrics and trends
- **Import/Export**: User settings and collection portability

---

## Implementation Priority
1. ✅ **COMPLETED**: History of books read (new feature, high user value)
2. � **NEXT**: Get book details from web (convenience feature)
3. � **LATER**: Import book cover (visual enhancement - requires database changes)
4. 🟢 **FUTURE**: App name change (cosmetic, can be done anytime)

---

## Current Status Summary

**Phase 2 Progress**: ✅ **READING HISTORY FULLY COMPLETED**
- All reading history features implemented and accessible
- Comprehensive statistics and date range queries
- Full keyboard navigation and screen reader support
- Ultra-compact layout optimized for low vision users
- Version updated to 1.8.6 with all features working

**Next Recommended Work**: � **GET BOOK DETAILS FROM WEB**
- API integration with Open Library or Google Books
- Popup dialog for data comparison and selective updates
- No database schema changes required
- Lower risk implementation path
- Can be developed and tested independently

---

## Changes We Will Lose If We Revert

### **Recent Commits That Will Be Lost**:
1. **March 23, 2026 - Reading History Window** (`33f67ff` to `ba86c30`)
   - Complete reading history window implementation
   - Date range queries and filtering
   - Ultra-compact layout for low vision users
   - Full accessibility support (JAWS/NVDA)
   - Alt+H shortcut and menu integration

2. **March 20, 2026 - Table Sorting** (`3410b30`)
   - Clickable headers with sort indicators
   - Column sorting (Author, Title, Year, Error Type, File/Folder)
   - Header click handlers and toggle ascending/descending
   - Screen reader announcements for sort changes

3. **March 20, 2026 - Hover Disabling** (`4253fea`)
   - Aggressive hover disabling for display setup wizard
   - Multiple CSS hover rules for table items
   - Focus and selection styling improvements

4. **March 20, 2026 - Main Window Cell Highlighting** (`087672c`)
   - Fix main window cell highlighting
   - Display setup alternating rows improvements
   - Table styling fixes

5. **March 20, 2026 - Minor Highlight Fixes** (`2cd10f4`)
   - Minor fixes to highlight behavior
   - CSS refinements for table items

6. **March 18, 2026 - Accessibility Fixes** (`ba9ce78`)
   - Reapply accessibility fixes from today
   - Menu highlighting follows theme
   - Combo box highlighter improvements

7. **March 17, 2026 - Theme Improvements** (`bc5a6ae`)
   - Highlighted for menus now follows theme
   - Better theme consistency

### **Impact Analysis**:
- **Functionality Lost**: Complete reading history system, table sorting in import window
- **Visual Improvements Lost**: Hover disabling, cell highlighting fixes
- **Accessibility Improvements Lost**: Menu highlighting, combo box fixes, reading history accessibility
- **Theme Consistency Lost**: Better menu theme following
- **Major Feature Lost**: Entire reading history statistics system

### **Recommendation**:
If we revert to March 13 (d94a078), we lose:
- **Complete reading history system** (major feature)
- **All recent accessibility improvements**
- **Table sorting functionality** (user requested)
- **Theme consistency improvements**
- **Hover and highlighting fixes**

**Alternative**: Cherry-pick specific features we want to keep rather than full revert.

---

This document provides detailed implementation guidance for the next development phase, ensuring all enhancements maintain accessibility standards and robust functionality.
