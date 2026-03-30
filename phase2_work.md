# Phase 2: Web Metadata Implementation — Status & Next Steps

## ✅ Web Metadata Window (COMPLETE - Standardization Pending)
- Fully functional web metadata window with all features implemented
- All fields: Title, Author, Plot, Year, Series, Genre with web API integration
- Clean UI, vertical layout, accessible status bar, and keyboard navigation
- Save and Escape both restore focus to main window table
- Professional F1 help and status bar announcements
- Real Google Books & Open Library API integration
- Visual indicators and checkbox selection for updates
- Error/status handling for network failures
- **Standardization Required:** Cancel button removal and Alt+L table focus (see comprehensive_accessibility_changes.md)

## ✅ Main App Integration (COMPLETE)
- "Get Web Info" menu item in Edit menu
- Shortcut: Alt+E, G sequence
- Main window integration with book selection/focus
- Database integration: web metadata changes saved
- Focus returns to exact cell after Save or Escape
- Works from both main window and book_details

## ✅ Enhanced Web Features (COMPLETE)
- Real Google Books & Open Library API integration
- Auto-fetch web data on window open
- Visual indicators and checkbox selection for updates
- Error/status handling for network failures
- Series number extraction and display
- Checkbox selection for field updates
- Status bar announcements for screen readers
- Rating, source, publisher integrated into plot field

## ✅ Accessibility Foundation (COMPLETE)
- All dialogs, popups, and status messages accessible and announced
- Consistent Alt+key handling and F1 help format
- Compact layout for low vision users
- KISS principle maintained throughout

## ✅ Book Details Integration (COMPLETE)
- After saving in web metadata window, book_details reloads data and clears dirty flag
- User is not prompted to save again after web metadata update
- Uses current form values for retry workflow
- Improved workflow for JAWS and all users

## 🔄 Multi-Book Selection Update (IN PROGRESS)
**Current Status:** Planning phase - ready to implement

**Implementation Plan:**
1. ✅ Add "Get web info" button to main window footer (visible only when books selected)
2. ⏳ Create dialog with "Get Plot" and "Get All Info" options
3. ⏳ Implement background fetch process using QThread/QtConcurrent
4. ⏳ Create result summary popup with X found, Y not found counts
5. ⏳ Implement "Update All" functionality for batch database updates
6. ⏳ Add paged review mode to WebMetadataWindow for multi-book review
7. ⏳ Ensure full accessibility compliance for all new dialogs
8. ⏳ Add progress indicators and status messages for background processes

**Key Requirements:**
- Accessibility-first: All dialogs follow AbCS patterns (F1, Alt+/, status bar, focus management)
- Non-blocking: Background processing with UI responsiveness
- KISS principle: Simple, clean implementation
- Screen reader support: All status messages announced

## Files Created/Updated
- accessible_window_skeleton.py (template)
- README_accessible_skeleton.md (usage instructions)
- web_metadata.py (✅ COMPLETE - fully functional)
- Screen_Reader_and_PySide6_best_practices.md (lessons learned)
- phase2_work.md (this document - updated status)

---


## Planned Feature: Multi-Get Web Info (Batch Web Metadata Import)

### User Workflow
1. User selects one or more books in the main window (multi-select supported).
2. User presses a new button "Get web info" (appears in the footer like Update/Delete/Cancel, only when books are selected).
3. A popup appears with two buttons:
	- **Get Plot**: Only fetches plot/description from the web for selected books.
	- **Get All Info**: Fetches plot and any other metadata that differs from the database (title, author, year, series, genre, etc).
4. A temporary status message appears (like the current Edit → Get Web Info) indicating that web metadata is being fetched in the background.
5. A background process retrieves web metadata for all selected books (non-blocking, UI remains responsive).
6. When the background process completes, a popup message reports:
	- Number of books with metadata retrieved
	- Number of books where metadata was not found
	- Two buttons: **Update All** and **Review**

7. If **Update All** is pressed:
	- All books with new metadata are updated in the database (can be a background process if many books)
	- Regardless of field differences, if a DB field is empty (year, genre, series), always add the web data for that field (no checkbox needed)
8. If **Review** is pressed:
	- The WebMetadataWindow opens in a paged mode, allowing the user to review each book one by one
	- For each book, the new accessible UI (see above) is used to present differences and allow field-by-field acceptance
	- After saving a book, the window moves to the next book (no going back to already saved books)
	- When all books are reviewed, the window closes and focus returns to the main table
	- Regardless of field differences, if a DB field is empty (year, genre, series), always add the web data for that field (no checkbox needed)

### Implementation Plan

**Main Window:**
- Add a "Get web info" button to the footer, visible only when books are selected (same pattern as Update/Delete/Cancel).
- Button triggers a dialog with "Get Plot" and "Get All Info" options.
- On selection, start a background task to fetch web metadata for all selected books.
- Show a temporary status message while fetching.

**Background Fetch Process:**
- Use QThread or QtConcurrent to run web fetches in parallel (non-blocking for UI).
- For each book:
  - Fetch plot or all metadata from web APIs (Google Books, Open Library)
  - Compare with current DB data; record only fields that differ
  - Track which books had data found and which did not
- On completion, emit a signal with results (success/failure per book, diff data)

**Rate Limiting Considerations for Bulk Fetch:**
Due to API rate limits (especially Google Books HTTP 429 errors), bulk fetching needs special handling:

*Option 1: Rate-Limited Bulk Fetch*
- Add delays between requests (e.g., 1-2 seconds between each book)
- Show progress: "Fetching book 1 of 10..."
- Would be slower but more reliable
- Risk: May still hit limits if many books

*Option 2: Staggered Fetch Strategy*
- Try Google Books for first 3 books
- If rate limited, switch to Open Library for next batch
- Use WikiData as fallback
- Rotate sources to avoid hitting limits
- Most flexible approach

*Option 3: Source-Limited Bulk*
- Skip Google Books for bulk operations (use Open Library + WikiData)
- Reserve Google Books for single book searches where it's most valuable
- Faster but less comprehensive results
- User option to "Include Google Books (slower, may hit limits)"

**Result Popup:**
- Show a summary popup: "Web info found for X books, not found for Y books."
- Buttons: **Update All** (apply all changes to DB), **Review** (step through each book)

**Update All:**
- Apply all metadata changes to the DB in a batch (can be backgrounded if >10 books)
- Show a completion message and refresh the main table

**Review Mode:**
- Open WebMetadataWindow in a paged/review mode
- User reviews each book, presses Save to apply web data and move to next
- Once a book is saved, it cannot be revisited in this session
- After last book, close window and return focus to main table

**Accessibility:**
- All dialogs, popups, and review windows must follow accessibility patterns (Alt+letter shortcuts, F1 help, status bar announcements, focus management)
- Status messages must be announced for screen readers

**Possible Improvements:**
- Allow user to filter which fields to update in batch (e.g., only update plot, not title)
- Add progress bar for long-running fetches/updates
- Allow canceling the background fetch/update process
- Log/report any errors or books with ambiguous matches

**Open Questions:**
- Should "Update All" be a background process for large batches? (Recommended for >10 books)
- Should there be an undo for batch updates? (Could be complex)
- Should the review window allow skipping a book (leave unchanged)?

---

## Proven Pattern
- Copy skeleton to new window file
- Add UI elements in setup_ui()
- Add field shortcuts in setup_shortcuts()
- Test F1, Alt+/, Escape
- Avoid ampersands in button text with Alt+ shortcuts

## Remaining Priorities
- Apply skeleton to Collection Window (start here)
- Test thoroughly with JAWS
- Proceed to Preferences and Import Window

**Status:** Web metadata accessibility and integration complete. All major features and accessibility requirements are implemented.

## March 26, 2026 — Accessibility/Window Consistency Review

### Issues Discovered
- WebMetadataWindow layout did not match accessible_window_skeleton.py or other app windows (book_details, import_window, etc.).
- Excess vertical space and inconsistent field packing due to Expanding size policies and lack of skeleton pattern.
- Multiple patch attempts (spacing, margins, alignment) did not resolve the root cause.
- User requested strict adherence to the proven skeleton window pattern for all new/updated windows.

### Action Plan (In Progress)
- Refactor WebMetadataWindow to use the exact layout, spacing, and size policy pattern from accessible_window_skeleton.py.
- Remove all custom squeezing, forced alignment, and nonstandard spacing.
- Set all field containers (QGroupBox, QTextEdit) to QSizePolicy.Minimum for vertical policy.
- Remove button_layout.addStretch() if not needed for right-alignment.
- Ensure all widgets are added directly to the main QVBoxLayout, as in the skeleton.
- Test for no excess vertical space, all content packed at the top, and full accessibility (JAWS/NVDA, keyboard, status bar, F1, Escape).

### Completed Items (as of tonight)
- Accessibility skeleton and best-practice window template are present and documented.
- All keyboard shortcuts, status bar, and accessibility events work in WebMetadataWindow.
- Focus restoration after web data update/error is implemented.
- All margins and spacing now match the app standard (20, 20, 20, 20 and spacing 12).
- User feedback: layout still not matching other windows; root cause identified as size policy/container issue, not just spacing.

### Next Steps
- Refactor WebMetadataWindow to match accessible_window_skeleton.py exactly (pending).
- Review all other windows for skeleton compliance.
- Document lessons learned in Screen_Reader_and_PySide6_best_practices.md.

---

## March 29, 2026 — Data Integrity Issues Discovered

### Author/Genre/Series Case Duplication Problem
**Issue:** Database contains duplicate entries with different casing (e.g., "michael r. stern" and "Michael R. Stern") due to import settings.

**Root Cause:** 
- "Apply proper case" setting in Preferences → Import Options defaults to `False`
- Import process preserves original file/folder casing
- Database has UNIQUE constraint on names (case-sensitive)
- This creates separate entries for same entity with different cases

**Impact:**
- User confusion when selecting authors/genres/series
- Duplicate cleanup required in name_list_window
- Inconsistent data quality across the database

**Solutions Needed:**
1. **Immediate:** Enable "Apply proper case" in preferences for future imports
2. **Code Fix:** Change default value from `False` to `True` in preferences_window.py line 1266
3. **Data Cleanup:** Create utility to merge existing case-duplicate entries
4. **Import Enhancement:** Case-insensitive duplicate detection during import

**Files to Review:**
- `src/ui/preferences_window.py` (line 1266 - default value)
- `src/ui/import_window.py` (import handling)
- `src/ui/name_list_window.py` (manual cleanup capability added)

**Priority:** Medium - Data quality issue affecting user experience
