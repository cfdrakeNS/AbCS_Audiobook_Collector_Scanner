# Phase 2: Implement Reading History Statistics feature

## 1. Enhance existing History of books read
**Current State**: Already implemented in main window with Ctrl+Enter on "Read" column.

**What Works**: 
- Date picker opens when you press Ctrl+Enter on a book
- Date is saved and table updates
- Status bar announces changes for JAWS

**Enhancements Needed**:
- **Date Range Queries**: Add "What was I reading on [specific date]?" functionality
- **Reading Statistics**: Use existing read_date values to calculate total books read, hours, averages, productive periods
- **Monthly/Yearly Breakdowns**: Show reading patterns over time
- **Dedicated History Window**: Create separate window (Alt+H) for better viewing

**Implementation Requirements**:
- Add `reading_queries.py` for statistics (NEW) - queries existing read_date values
- Add `reading_history_window.py` (NEW) - dedicated statistics viewer
- Add menu option: "View > Reading History"
- Full keyboard accessibility and screen reader support
- No database schema changes needed - use existing read_date field

**Technical Approach**:
- Query books table WHERE read_date IS NOT NULL
- Calculate statistics from existing data
- Group by month/year for breakdowns
- Display in accessible table format

---

## 2. Import book cover
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

## 3. Get book details from web
**Current State**: No web integration exists.

**Implementation Plan**:
- **API Integration**: Connect to Open Library or Google Books API
- **Book Details Window Enhancement**:
  - Add fetch button with Alt+G shortcut
  - Create popup dialog with plot/description
  - Compare existing vs fetched data (year, series, genre)
  - Allow user to selectively update fields with checkboxes
  - Announce results via status bar
  - Ensure popup is keyboard navigable and screen reader friendly
- **Error Handling**: Graceful API error handling with clear feedback

**Technical Considerations**:
- API rate limiting and error handling
- Network connectivity checks
- Data validation and sanitization
- User consent for data updates

---

## Additional Feature Ideas
- **Bulk Edit**: Multi-select books for collection management
- **Custom Collections**: Color-coded user collections
- **Statistics Dashboard**: Reading metrics and trends
- **Import/Export**: User settings and collection portability

---

## Implementation Priority
1. **High Priority**: History of books read (new feature, high user value)
2. **Medium Priority**: Import book cover (visual enhancement)
3. **Medium Priority**: Get book details from web (convenience feature)
4. **Low Priority**: App name change (cosmetic, can be done anytime)

---

## Changes We Will Lose If We Revert

### **Recent Commits That Will Be Lost**:
1. **March 20, 2026 - Table Sorting** (`3410b30`)
   - Clickable headers with sort indicators
   - Column sorting (Author, Title, Year, Error Type, File/Folder)
   - Header click handlers and toggle ascending/descending
   - Screen reader announcements for sort changes

2. **March 20, 2026 - Hover Disabling** (`4253fea`)
   - Aggressive hover disabling for display setup wizard
   - Multiple CSS hover rules for table items
   - Focus and selection styling improvements

3. **March 20, 2026 - Main Window Cell Highlighting** (`087672c`)
   - Fix main window cell highlighting
   - Display setup alternating rows improvements
   - Table styling fixes

4. **March 20, 2026 - Minor Highlight Fixes** (`2cd10f4`)
   - Minor fixes to highlight behavior
   - CSS refinements for table items

5. **March 18, 2026 - Accessibility Fixes** (`ba9ce78`)
   - Reapply accessibility fixes from today
   - Menu highlighting follows theme
   - Combo box highlighter improvements

6. **March 17, 2026 - Theme Improvements** (`bc5a6ae`)
   - Highlighted for menus now follows theme
   - Better theme consistency

### **Impact Analysis**:
- **Functionality Lost**: Table sorting in import window
- **Visual Improvements Lost**: Hover disabling, cell highlighting fixes
- **Accessibility Improvements Lost**: Menu highlighting, combo box fixes
- **Theme Consistency Lost**: Better menu theme following

### **Recommendation**:
If we revert to March 13 (d94a078), we lose:
- **All recent accessibility improvements**
- **Table sorting functionality** (user requested)
- **Theme consistency improvements**
- **Hover and highlighting fixes**

**Alternative**: Cherry-pick specific features we want to keep rather than full revert.

---

This document provides detailed implementation guidance for the next development phase, ensuring all enhancements maintain accessibility standards and robust functionality.
