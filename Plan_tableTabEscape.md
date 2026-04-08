# Plan: Global Table Tab Navigation for Accessibility

This feature will allow keyboard users to use Tab/Shift+Tab to move focus out of any table (QTableView/QTableWidget) to the next/previous focusable widget, instead of being trapped inside the table cells. This is critical for accessibility and aligns with best practices for screen reader and keyboard navigation.

---

## Global Implementation Plan

**Goal:**
- Make Tab/Shift+Tab escape from all tables a global, consistent behavior across the entire application.

**Steps**

1. **Discovery & Analysis**
   - Identify all windows with tables (main window, book details, import, etc.).
   - Review how keyboard navigation is currently handled in these tables.
   - Check if any custom event filters or keyPressEvent overrides exist.

2. **Design & Implementation**
   - Create a reusable event filter or base class (e.g., `TableTabEscapeEventFilter`) that can be attached to any QTableView/QTableWidget.
   - In the event filter, on Tab/Shift+Tab:
     - If at the last cell (Tab) or first cell (Shift+Tab), move focus to the next/previous widget outside the table using QWidget's focusNextPrevChild().
     - Otherwise, allow normal cell navigation.
   - Apply this event filter globally to all table widgets during their initialization (e.g., in a base window class or via a utility function).
   - Ensure this works with both QTableView and QTableWidget.
   - Test with screen readers (JAWS/NVDA) to confirm focus announcements.

3. **Accessibility Integration**
   - Ensure focus transitions are announced in the status bar for screen readers.
   - Confirm that Alt+key shortcuts and other navigation patterns are not disrupted.

4. **Testing**
   - Manual test: Tab/Shift+Tab from table moves focus as expected.
   - Screen reader test: Focus change is announced.
   - Regression test: Multi-select and cell editing still work.

**Relevant files**
- `src/ui/main_window.py` — Main book table
- `src/ui/book_details.py` — Any tables present
- `src/ui/import_window.py` (planned) — Import table
- `src/accessibility/accessibility_event.py` or similar — For centralized event handling, if used

**Verification**
1. Tab/Shift+Tab from any table moves focus to the next/previous widget outside the table.
2. Screen reader announces the new focus widget.
3. No regression in table cell navigation or editing.

**Decisions**
- Implementation will use a reusable event filter or base class for all tables.
- If a centralized accessibility event handler exists, integrate there for consistency.
- Applies to all windows with tables, present and future.

**Further Considerations**
1. This will be a global behavior for all tables for consistency and accessibility.
2. If using a centralized handler, ensure it does not interfere with custom per-window logic.
