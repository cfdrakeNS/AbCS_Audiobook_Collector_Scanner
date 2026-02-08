## I used an app called Accessibility Insights For Windows which analyzes the controls on windows apps. The good news is the IT didn't find any real errors. flagged empty fields which are not an issue.

## let's clean up move the testing files and docs for jaws nvda into a folder  to reduce clutter 

## mw#10 set a minimum width so that collection, red, order combos keep enough width to display their conntent for collection set it to the min widsh of "all collection" for Read with of "unread" order set to widht of "authors"

## mw#11 hide selected check box on book table

## mw#12 update status bar message; to show when series or genre filter is on 

## mw#13 after clearing slection the status bar doesn't revert back to showing xxx

## mw#14 alt-l should only be available when something is selected 

## mw#15 alt-n also can be remove, add ctrl+n for new and update the file and shortcut menu 

## mw#16 view menu zoom in out and reset add shortcut keys

## mw#17 view menu add to top of menu "Book Details" ctrl+enter 

## mw#18 add double mouse click to open book details 

## mw#19 change book_detail shortcut to ctrl+enter 

## mw#21 when zoom reset should set the app to 125% about 14pt but the font look like regular text on my screen. 

## mw#22 main_window adjust the table columns so when scaling is set to default 125% the table uses the full width of the windows. title, author, series and genre should stretch and shrink, all other columns should be set to a fix width for that column.

## mw#23 add shortcuts keys the book list to jump quickly to a column Author alt-1, Title alt+2 etc 

## mw#24 Alt+/ reads the status bar aloud. If no screen reader is active, show a message "No screen reader active" (for testing accessibility flags - will remove message later).

## mw#25 Focus after bulk delete: Return focus to the previous book row (the row before the deleted selection started). Table auto-refreshes after delete - no F5 refresh needed.

## mw#26 Cancel selection behavior: 
- Alt+L (Cancel button) or Esc clears selection and leaves focus on current cell
- Moving cursor without Ctrl or Shift also clears selection, focus stays on the cell where cancel happened
- F6 cycle focus removed (was for MS Access, not needed)

## mw#27 Esc key clears selection (same behavior as Cancel button)

---
## Clarifications / Not Needed:
- No checkboxes in table (select checkbox hidden per mw#11)
- F5 (refresh) removed - list auto-updates after delete
- F6 (cycle focus) removed - not needed
