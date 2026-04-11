# Final bug fixes

1. done update window - shortcut alt=b replace with alt+l jump to list update shortcuts.py and centralized chortcuts
2. done read_history - check the layout and formatting it has issues with the tab Selector and buttons not following theme
3. done main centre justify win read date
4. Done Book detail 1. After save or delete move focus to title. 2 after fetch web info is successful move focus to plot if not successful move focus to title.
5. Done web metadata win when web info is returned set the focus to plot if no data returned set the focus to title.
6. done read history win date range tab -  when 1st open set start date previous 3 month date from current date. Set end date to current
7. done read history win change alt+b to be alt+l update centralized shortcuts anf f1 menu
8. done main win view->collection not updating after return from backup/_restore or book/_list/_import windows
9. done book/_list/_import win - read date tester say his date are dd-mm-yy add logic to check date format  
10. done import detail make files, bitrate, size, path read only. Time fields needs a mask e.g. 12:34 as if you type in 1234 and move focus no msg. remove the msg "there are no changes to save" and change the save button so it is hidden until the window is dirty. like book/_detail works
11. done book detail - Time fields needs same format fix as in import detail
12. done preferences and book list import win - dark themes were not showing qboxes text
13. done read history win - remove lengh column
14. done queries.py - collection active mot being applied.  when active is false the books in the collection to the app they don't exist. 
15. collection win save button not working for alt+s
16. done Issue status bar announcing twice same with alt+/ reading status bar twice. the centralized routine must being called twice check all calls in all windows 
17. done read history win general tab has showing the status bar for date range 
18. done web_metadata when called from main and no data found now shows popup again (No Web Data Found) and restores focus to table.
19. done web_metadata source checking optimized: removed redundant refresh retry loop from main/book_details call path. now one call uses WebBookAPI's internal cascade (Google -> Open Library -> WikiData), reducing repeated network waits.
20. done main window F1/help/status hint now shows Escape for cancel (not Alt+L) check other shortcuts that are centralized in shortcuts.py 
21. done reading history window: month tab month field widened, date range tab date field widened for accessibility
22. book list import window - increase the width of instruction text box by 1/2 & width of options by 1/4 for better fit at high zoom
23. preferences window reduce the white space between preset control and zoom control make it the same as the distance between theme and preset  not fitting when zoom in 
24. done when in a table let the tab/shift+tab jump out to the next tab controll  this will allow keyboard users to tab to the buttons etc. windows need changeing: main, collection, import 
25. done the status bar msgs for alt+keys the blind tester say it noise. Remove all alt+key messages from main, book_detail. name_list, collection windows. 
26. done main window About popup add the graphic at the top of the window abcs_splash.png in folder c:/Users/cfran/PythonProjects/abcs/data/graphics. change the table that has the text into a text box like on book_list_import window. set the focus to the text box when the win opens. 
27. done main window license popup change the table that has the text into a text box like on book_list_import window set the focus to the text box when the win opens.
28. import and import_progress window when scan is canceled move the "cancel" part of the message to bhe beginning of the message. 
29. done import_progress window alt+/ not working while scanning however the version in archive called import_progress_window mar21.py did work. compare the alt+/ code when scanning is in progress. 
30. done book_detail & import_detail comnbos when shoosing an item that exists in the db the popup add new is showing.
31. done main window find popup change the find label to say "find xxx" where xxx is the value in the in combo box. Update the accessible name to do the same. 
32. done all windows & popup add a icon to the title bar of the windows use bCS_WinTitle.png 
36. done book list import window  update the status bar msg after import to  instead of "successfull"  "added to Book List collection" also, do the popup message after import.
37. done book detail & import detail windows - after pgup or pgdn move focus to title 
38. done main win 1. after update to read date the focus is lost keep the focus on read date. 2. can't read the title in the popup title bar let stretch out.
38. done book_list_import & web_bookk.api - before a search is it start  or compare staarts - 1. checking if a title has a number at the beginning or at the and of the end of he title for  series. it should strip the series number before doing the search. 2. The same is true for titles that have ", the" or ", an" or ". a"  the title put back to have the article at the beginning of the title before searching. or comparing 
39. done book_list_import window - after export add a confirm popup with the file and path name 
40. done import windows - after export add a confirm popup with the file and path name 
41. done import window - check the selecting with shift+up /down erros not selecting entire rows.
42. web_book.api - some titles have a number at the beginning of the title  for series number, e.g." 06 The Unquiet"  when comparing to see if title is differnt and title start with a number and they match when the number is stripped then they are the same.  same is for if the number is at the end of the title e.g. "th Anniversary - 10"
43. done book_detail - change the popup after a delete to include the title and autthor clearer for screen readers 
44. web_book.api - check to see if a series number is available we are adding it to the end of the title when we save the book. 
45.  done book_detail - after picking a existing item in a combo and press escape focus is lot 
46.  done book_detail - when a fields is changed the status bar sometime say the field you tab to instead of the fields you change 
47. done main window - 1. series and genre when opened are returning to the wrong column  2. sorrt on read date not working. 2. remove date added from sort menu. 3.  when selecting jaws is saying row and column numbers silence these as they have no relevance to the book table. 
48. done preference win increse the height by 1/3
49. done main win - Ctrl+A (Select All) is now enabled in the main window table. Restriction and blocking message removed.

# April 11th work

## By Window: Remaining Items & Likely Fixes

### Import Window
- **Shift+Up/Down selection errors (41):**
	- *Likely fix:* Review table selection logic; ensure selection model uses full row selection and handles keyboard events for Shift+Up/Down. Check for custom event filters or selection overrides.

### Web Book API
- **Title number/series comparison logic (42):**
	- *Likely fix:* Refactor title comparison to strip leading/trailing numbers before comparing. Add utility to normalize titles for comparison.
- **Series number handling (44):**
	- *Likely fix:* When series number is detected, append to title only if not already present. Add check in save logic.

### Book Detail Window 
- **after Deletinhg a book  popup after clarity for screen readers (43):**
	- **Fixed:** Delete confirmation and success dialogs now include both book title and author for screen reader clarity. No duplicated code; variables are used for accessible text in both dialogs.
- **Combo focus lost after Escape (45):**
	- *Likely fix:* On Escape, explicitly set focus back to the combo box or previous field.
- **Status bar field change message (46):**
	- *Likely fix:* Ensure status bar only announces the field that was changed, not the one tabbed to. Track last changed field and update message logic.

### Main Window
**47.1 Series/Genre column return:**
done - Table navigation and cell focus logic updated; correct column is restored after dialog closes.
**47.2 Sort on read date not working:**
done - Sorting function for read date column fixed; column index and data type handled correctly.
**47.3 Remove date added from sort menu:**
done - Sort menu options updated to exclude 'date added'.
**47.4 JAWS row/column number noise:**
done - Row/column number announcements suppressed for screen readers; accessible description set.


