# Functional Test Plan (Non-Screen Reader)

Date: 2026-02-10
Project: AbCS (Audio Book Collector Scanner)
Scope: Core functional workflows without screen reader requirements.
Order: Main Window, Book Detail Window, Update Window.

## 1. Main Window

### 1.1 Launch and Initial Load
- Verify splash screen shows database name and basic statistics.
- Verify main window opens and table is populated with existing books.
- Verify default filters and order-by settings are applied.

### 1.2 Filters and Sorting
- Change Collection filter and confirm table updates.
- Change Read filter and confirm table updates.
- Change Order By and confirm table updates in expected order.
- Clear filters and confirm full list returns.

### 1.3 Search
- Enter a valid title/author search term and confirm matching rows.
- Enter a term that should return no results and confirm empty state.
- Clear search and confirm full list returns.
- Repeat with partial terms and case variations.

### 1.4 Table Interaction
- Click a row and confirm selection highlight.
- Ctrl+Click multiple rows and confirm multi-select.
- Shift+Click a range and confirm range selection.
- Double-click Title cell and confirm Book Detail window opens.
- Press Enter on Title cell and confirm Book Detail window opens.

### 1.5 Bulk Actions
- Select multiple rows and verify Update/Delete/Cancel buttons appear.
- Click Cancel and confirm selection clears and buttons hide.
- Select multiple rows and click Delete; confirm dialog appears.
- Cancel delete and confirm no rows removed.
- Confirm selection count updates in header or status bar.

### 1.6 Refresh and Navigation
- Use refresh action and confirm table reloads.
- Use menu actions (if available) and confirm they open expected windows.

## 2. Book Detail Window

### 2.1 Open Existing Book
- Open from Main Window via double-click.
- Verify all fields populate correctly from database.
- Verify navigation buttons (Prev/Next) move between records.

### 2.2 Edit and Save
- Modify Title and save; confirm change persists in Main Window.
- Modify Author/Series/Genre/Year and save; confirm persistence.
- Change Read status and confirm persistence.
- Update Collection and confirm persistence.

### 2.3 Validation
- Clear required fields (Title/Author) and attempt to save.
- Confirm validation message and no database update.

### 2.4 New Record
- Click New and enter valid data.
- Save and confirm new record appears in Main Window.
- Confirm form resets or navigates as designed after save.

### 2.5 Delete Record
- Delete current record and confirm confirmation prompt.
- Confirm record removed from database and Main Window.

### 2.6 Close Behavior
- Close window and confirm focus returns to Main Window.
- Reopen and confirm no unsaved changes persist.

## 3. Update Window (Bulk Update)

### 3.1 Open and Context
- From Main Window, select multiple books and click Update.
- Confirm Update Window opens and shows selection count.

### 3.2 Update Series
- Set Series and apply update.
- Confirm all selected books reflect updated Series.

### 3.3 Update Genre
- Set Genre and apply update.
- Confirm all selected books reflect updated Genre.

### 3.4 Update Collection
- Set Collection and apply update.
- Confirm all selected books reflect updated Collection.

### 3.5 Partial Updates
- Update only one field and leave others unchanged.
- Confirm only that field updates across selection.

### 3.6 Cancel
- Cancel out of Update Window.
- Confirm no changes were applied.

## 4. Regression Checks
- Repeat a quick search and open Book Detail after bulk updates.
- Confirm no crashes or UI freezes during updates.
- Confirm database remains consistent after multiple operations.

## 5. Test Data Notes
- Use a small, known dataset (10-20 books) with varied Authors, Series, Genres, and Collections.
- Ensure at least two records share the same Author and Series for bulk update verification.

## 6. Pass/Fail Criteria
- Pass if all steps complete with expected results and no data loss.
- Fail if any operation crashes, corrupts data, or saves invalid values.
