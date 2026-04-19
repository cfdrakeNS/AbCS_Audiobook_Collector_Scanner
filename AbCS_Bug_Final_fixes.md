# Final bug fixes

1. complete - update window - shortcut alt=b replace with alt+l jump to list update shortcuts.py and centralized chortcuts
2. complete - read\_history - check the layout and formatting it has issues with the tab Selector and buttons not following theme
3. complete - main centre justify win read date
4. complete - Book detail 1. After save or delete move focus to title. 2 after fetch web info is successful move focus to plot if not successful move focus to title.
5. complete - web metadata win when web info is returned set the focus to plot if no data returned set the focus to title.
6. complete - read history win date range tab -  when 1st open set start date previous 3 month date from current date. Set end date to current
7. complete - read history win change alt+b to be alt+l update centralized shortcuts anf f1 menu
8. complete - main win view->collection not updating after return from backup/\_restore or book/\_list/\_import windows
9. complete - book/\_list/\_import win - read date tester say his date are dd-mm-yy add logic to check date format
10. complete - import detail make files, bitrate, size, path read only. Time fields needs a mask e.g. 12:34 as if you type in 1234 and move focus no msg. remove the msg "there are no changes to save" and change the save button so it is hidden until the window is dirty. like book/\_detail works
11. complete - book detail - Time fields needs same format fix as in import detail
12. complete - preferences and book list import win - dark themes were not showing qboxes text
13. complete - read history win - remove lengh column
14. complete - queries.py - collection active mot being applied.  when active is false the books in the collection to the app they don't exist.
15. collection win save button not working for alt+s
16. complete - Issue status bar announcing twice same with alt+/ reading status bar twice. the centralized routine must being called twice check all calls in all windows
17. complete - read history win general tab has showing the status bar for date range
18. complete - web\_metadata when called from main and no data found now shows popup again (No Web Data Found) and restores focus to table.
19. complete - web\_metadata source checking optimized: removed redundant refresh retry loop from main/book\_details call path. now one call uses WebBookAPI's internal cascade (Google -> Open Library -> WikiData), reducing repeated network waits.
20. complete - main window F1/help/status hint now shows Escape for cancel (not Alt+L) check other shortcuts that are centralized in shortcuts.py
21. complete - reading history window: month tab month field widened, date range tab date field widened for accessibility
22. book list import window - increase the width of instruction text box by 1/2 \& width of options by 1/4 for better fit at high zoom
23. preferences window reduce the white space between preset control and zoom control make it the same as the distance between theme and preset  not fitting when zoom in
24. complete - when in a table let the tab/shift+tab jump out to the next tab controll  this will allow keyboard users to tab to the buttons etc. windows need changeing: main, collection, import
25. complete - the status bar msgs for alt+keys the blind tester say it noise. Remove all alt+key messages from main, book\_detail. name\_list, collection windows.
26. complete - main window About popup add the graphic at the top of the window abcs\_splash.png in folder c:/Users/cfran/PythonProjects/abcs/data/graphics. change the table that has the text into a text box like on book\_list\_import window. set the focus to the text box when the win opens.
27. complete - main window license popup change the table that has the text into a text box like on book\_list\_import window set the focus to the text box when the win opens.
28. complete - import and import\_progress window when scan is canceled move the "Cancel Scan" test to bhe beginning of the message not at the end.
29. complete - import\_progress window alt+/ not working while scanning however the version in archive called import\_progress\_window mar21.py did work. compare the alt+/ code when scanning is in progress.
30. complete - book\_detail \& import\_detail comnbos when shoosing an item that exists in the db the popup add new is showing.
31. complete - main window find popup change the find label to say "find xxx" where xxx is the value in the in combo box. Update the accessible name to do the same.
32. complete - all windows \& popup add a icon to the title bar of the windows use bCS\_WinTitle.png
33. complete - book list import window  update the status bar msg after import to  instead of "successfull"  "added to Book List collection" also, do the popup message after import.
34. complete - book detail \& import detail windows - after pgup or pgdn move focus to title
35. complete - main win 1. after update to read date the focus is lost keep the focus on read date. 2. can't read the title in the popup title bar let stretch out.
36. complete - book\_list\_import \& web\_bookk.api - before a search is it start  or compare staarts - 1. checking if a title has a number at the beginning or at the and of the end of he title for  series. it should strip the series number before doing the search. 2. The same is true for titles that have ", the" or ", an" or ". a"  the title put back to have the article at the beginning of the title before searching. or comparing
37. complete - book\_list\_import window - after export add a confirm popup with the file and path name
38. complete - import windows - after export add a confirm popup with the file and path name
39. complete - import window - check the selecting with shift+up /down erros not selecting entire rows.
40. web\_book.api - some titles have a number at the beginning of the title  for series number, e.g." 06 The Unquiet"  when comparing to see if title is differnt and title start with a number and they match when the number is stripped then they are the same.  same is for if the number is at the end of the title e.g. "th Anniversary - 10"
41. complete - book\_detail - change the popup after a delete to include the title and autthor clearer for screen readers
42. web\_book.api - check to see if a series number is available we are adding it to the end of the title when we save the book.
43. complete - book\_detail - after picking a existing item in a combo and press escape focus is lot
44. complete - book\_detail - when a fields is changed the status bar sometime say the field you tab to instead of the fields you change
45. complete - main window - 1. series and genre when opened are returning to the wrong column  2. sorrt on read date not working. 2. remove date added from sort menu. 3.  when selecting jaws is saying row and column numbers silence these as they have no relevance to the book table.
46. complete - preference win increse the height by 1/3
47. complete - main win - Ctrl+A (Select All) is now enabled in the main window table. Restriction and blocking message removed.
48. title bar icons not showing on built install check if they are included in the build
49. complete - import window 1. highligheter not highlighintng entire row when selecting; look at main win code for selecting highlighting
50. complete - import window  - add the same slection status bar messaging like main window. don't change the normal status bar msg that exist for non-selection
51. book\_detail window - the labels for Time \& Read seem to be left justifyed they sshuld be right justifyes as there the labels are closer to the field to the left not their own fields
52. book\_detail windows - genre fields should be vertically aligned under the reader fields
53. complete - main window find for genre \& series returning to wrong column
54. cmplete - main windows - when in find mode sort returns no records
55. not needed main windows - add alt+l to move focus to the book list update f1 and shortcuts.py
56. main window & book detail windows --- book detail window takes a long time to open can we improve this?
57. complete - main window - when no screen reader is present don't put out a popup msg remove that not wanted this appears to happen in other window. remove this no point in the popup.
58. complete -import window -alt+b is registered as a shortcut for browse remove as alt+w is brows 
60. web_metadata & book_api.py -- tighten the search so that at least the author last name is in the web_author and 50% of the words in the title match web data 
61. complete -  main window - after a restore in backup_restore the main window is sometimes empty after a restore set set collection to all collections to avoid empty window.
62. import win when error type is filtered and you press ctrl+A the status bar selected counter show the total number of books in the import table not the filter selected.