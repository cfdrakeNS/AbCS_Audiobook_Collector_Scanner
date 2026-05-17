# Final bug fixes
1. complete - update window - shortcut alt=b replace with alt+l jump to list update shortcuts.py and centralized chortcuts
2. complete - readh_history - check the layout and formatting it has issues with the tab Selector and buttons not following theme
3. complete - main centre justify win read date
4. complete - Book detail 1. After save or delete move focus to title. 2 after fetch web info is successful move focus to plot if not successful move focus to title.
5. complete - web metadata win when web info is returned set the focus to plot if no data returned set the focus to title.
6. complete - read history win date range tab -  when 1st open set start date previous 3 month date from current date. Set end date to current
7. complete - read history win change alt+b to be alt+l update centralized shortcuts anf f1 menu
8. complete - main win view->collection not updating after return from backup/h_restore or book/h_list/h_import windows
9. complete - book/h_list/h_import win - read date tester say his date are dd-mm-yy add logic to check date format
10. complete - import detail make files, bitrate, size, path read only. Time fields needs a mask e.g. 12:34 as if you type in 1234 and move focus no msg. remove the msg "there are no changes to save" and change the save button so it is hidden until the window is dirty. like book/h_detail works
11. complete - book detail - Time fields needs same format fix as in import detail
12. complete - preferences and book list import win - dark themes were not showing qboxes text
13. complete - read history win - remove lengh column
14. complete - queries.py - collection active mot being applied.  when active is false the books in the collection to the app they don't exist.
15. collection win save button not working for alt+s
16. complete - Issue status bar announcing twice same with alt+/ reading status bar twice. the centralized routine must being called twice check all calls in all windows
17. complete - read history win general tab has showing the status bar for date range
18. complete - webh_metadata when called from main and no data found now shows popup again (No Web Data Found) and restores focus to table.
19. complete - webh_metadata source checking optimized: removed redundant refresh retry loop from main/bookh_details call path. now one call uses WebBookAPI's internal cascade (Google -> Open Library -> WikiData), reducing repeated network waits.
20. complete - main window F1/help/status hint now shows Escape for cancel (not Alt+L) check other shortcuts that are centralized in shortcuts.py

21. complete - reading history window: month tab month field widened, date range tab date field widened for accessibility

22. book list import window - increase the width of instruction text box by 1/2 h& width of options by 1/4 for better fit at high zoom

23. preferences window reduce the white space between preset control and zoom control make it the same as the distance between theme and preset  not fitting when zoom in

24. complete - when in a table let the tab/shift+tab jump out to the next tab controll  this will allow keyboard users to tab to the buttons etc. windows need changeing: main, collection, import

25. complete - the status bar msgs for alt+keys the blind tester say it noise. Remove all alt+key messages from main, bookh_detail. nameh_list, collection windows.

26. complete - main window About popup add the graphic at the top of the window abcsh_splash.png in folder c:/Users/cfran/PythonProjects/abcs/data/graphics. change the table that has the text into a text box like on bookh_listh_import window. set the focus to the text box when the win opens.

27. complete - main window license popup change the table that has the text into a text box like on bookh_listh_import window set the focus to the text box when the win opens.

28. complete - import and importh_progress window when scan is canceled move the "Cancel Scan" test to bhe beginning of the message not at the end.

29. complete - importh_progress window alt+/ not working while scanning however the version in archive called importh_progressh_window mar21.py did work. compare the alt+/ code when scanning is in progress.

30. complete - bookh_detail h& importh_detail comnbos when shoosing an item that exists in the db the popup add new is showing.

31. complete - main window find popup change the find label to say "find xxx" where xxx is the value in the in combo box. Update the accessible name to do the same.

32. complete - all windows h& popup add a icon to the title bar of the windows use bCSh_WinTitle.png

33. complete - book list import window  update the status bar msg after import to  instead of "successfull"  "added to Book List collection" also, do the popup message after import.

34. complete - book detail h& import detail windows - after pgup or pgdn move focus to title

35. complete - main win 1. after update to read date the focus is lost keep the focus on read date. 2. can't read the title in the popup title bar let stretch out.

36. complete - bookh_listh_import h& webh_bookk.api - before a search is it start  or compare staarts - 1. checking if a title has a number at the beginning or at the and of the end of he title for  series. it should strip the series number before doing the search. 2. The same is true for titles that have ", the" or ", an" or ". a"  the title put back to have the article at the beginning of the title before searching. or comparing

37. complete - bookh_listh_import window - after export add a confirm popup with the file and path name

38. complete - import windows - after export add a confirm popup with the file and path name

39. complete - import window - check the selecting with shift+up /down erros not selecting entire rows.

40. webh_book.api - some titles have a number at the beginning of the title  for series number, e.g." 06 The Unquiet"  when comparing to see if title is differnt and title start with a number and they match when the number is stripped then they are the same.  same is for if the number is at the end of the title e.g. "th Anniversary - 10"

41. complete - bookh_detail - change the popup after a delete to include the title and autthor clearer for screen readers

42. webh_book.api - check to see if a series number is available we are adding it to the end of the title when we save the book.

43. complete - bookh_detail - after picking a existing item in a combo and press escape focus is lot

44. complete - bookh_detail - when a fields is changed the status bar sometime say the field you tab to instead of the fields you change

45. complete - main window - 1. series and genre when opened are returning to the wrong column  2. sorrt on read date not working. 2. remove date added from sort menu. 3.  when selecting jaws is saying row and column numbers silence these as they have no relevance to the book table.

46. complete - preference win increse the height by 1/3

47. complete - main win - Ctrl+A (Select All) is now enabled in the main window table. Restriction and blocking message removed.

48. title bar icons not showing on built install check if they are included in the build

49. complete - import window 1. highligheter not highlighintng entire row when selecting; look at main win code for selecting highlighting

50. complete - import window  - add the same slection status bar messaging like main window. don't change the normal status bar msg that exist for non-selection

51. bookh_detail window - the labels for Time h& Read seem to be left justifyed they sshuld be right justifyes as there the labels are closer to the field to the left not their own fields

52. bookh_detail windows - genre fields should be vertically aligned under the reader fields

53. complete - main window find for genre h& series returning to wrong column

54. cmplete - main windows - when in find mode sort returns no records

55. not needed main windows - add alt+l to move focus to the book list update f1 and shortcuts.py

56. main window h& book detail windows --- book detail window takes a long time to open can we improve this?

57. complete - main window - when no screen reader is present don't put out a popup msg remove that not wanted this appears to happen in other window. remove this no point in the popup.

58. complete -import window -alt+b is registered as a shortcut for browse remove as alt+w is brows

59. webh_metadata h& bookh_api.py -- tighten the search so that at least the author last name is in the webh_author and 50% of the words in the title match web data

60. complete - main window - after a restore in backuph_restore the main window is sometimes empty after a restore set set collection to all collections to avoid empty window.

61. complete import win when error type is filtered and you press ctrl+A the status bar selected counter show the total number of books in the import table not the filter selected.

62. complete - the sanitization of title and author is removing punctuation with in the fields when it should only remove punctuation at the beginning of the field.

63. complete - update window  is not using the sanitization. It should do that before the popup to add new genre or series and also saved as sanitized.

64. complete - bookh_detail, importh_detail sanitization of author should remove  beginning punctuation

65. complete - nameh_list window author - sanitization of author should remove  beginning punctuation

66. complete -import window  - when the import button is clicked or the shortcut for it pressed lock the collection so it can't be accedentally change when reviewing book still on the import list.]

67. complete - when a collection is selected in main win other then "all collections" the new book bookh_detail collection should default to the main window current collection. if main win collection is "all collections" and there is more than one collection then let book detail collection empty  if only one collection than default to that collection

68. complete - bookh_detail h& importh_detail check the unsave warning popup as it seems sometimes pgup pgdn then press escape it will popup

69. complete - book detail h& importh_detail when dirty and pgup/down warn popup yes/no yes save and page  no don't save and page. remove the current blocking for paging when dirty.

70. complete - import window default the collection the same way as it does for bookh_detail  for collection when a collection is selected in main win other then "all collections" the import window collection should default to the main window current collection. if main win collection is "all collections" and there is more than one collection then let import window leave collection empty  if only one collection than default to that collection

71. complete - book detail window: Alt+O now jumps to Format field (centralized, F1/help updated, shortcuts.py updated). Source field is now editable. (2026-04-22: Verified Alt+O only moves to Format, not Plot. Fixed any mapping issues.)

72. complete - bookh_listh_import window: During import, the source field in books table is now set to Bookh_list.

73. complete - bookh_listh_importh_window: Add collection combo for collection to the top of the options section. When a collection is selected in main win other than "all collections" the bookh_listh_import window should default to the main window current collection. If main win collection is "all collections" and there is more than one collection, leave collection empty; if only one collection, default to that collection. (See import window for logic.) Popup warning if no collection is selected.

74. complete - Preference window: Added "Restore Defaults" button with Alt+E shortcut. Shows confirmation popup before resetting all settings to defaults per AbCS_default_preference.md. Resets: Display (default theme, 150% zoom), Import (empty directory, all formats, mass_standard scenario, fallback enabled), Reader keywords, Validation rules (author in title=warning, title in author=error, unknown=error, min title=3/disabled, file structure=warning/enabled, year consistency=warning/enabled), Duplicate checking (title_author_year, 90% fuzzy).

75. ppreference window - 1. year cons when pick error import error list show W: not E: 2. year const label right justify it.

76. complete - preferences window year consistency label right justify

77. complete - default preference for min title length is 3 add waring it is current none

78. complete - book_detail window if read date is not set to a vulue when using the date picker set the date to current

79. complete - import, import_progress window - status bar change the literal "Fixed" to "Corrected"

80. complete - book_detail window - f1 help needs to be updated missing alt+/, alt+n new, alt+d delete, check to see that it is using centrlaized shortcuts.py

81. complete - button in window footer consistency all right align needed; book detail, book list import, import detail backup restore, and main window

82. complete - book detail window - is applying sanitization function on data that is in the db. e.g. proper case. This is causing the window to prompt for save which is confusing. Only apply the sanitization to a field if it is dirty when field lost focus. This might also be happening in import detail window as well.

83. complete - preference window - change the shortcut for browse to alt+w update centralized shortcut and f1 menu

84. complete book list import window - apply sensitization to fields before saving to db. title, author, reader, genre, series,  using the same rules for sensitization as import window

85. complete - check all windows for accessibility - shortcuts and f1 menu to ensure they are following centralized standards. refer to the PySide6_.. doc located in the docs folder. put your finding in abcs_accessibility_check.md

86. complete statistics window - stop table row anouncment to screen readers, look at  f1 shortut style.

87. read CLEANUP_VULTURE_FINDINGS noting the false positives that are document. Do a vulture scan of the code and update the doc with your finding. do not remove existing text add your finding under the heading April 24 2026 finding.

88. complete - generate a user guide for the app keeping in mind that the app will be used both by sighted, low vision and blind users, who would use text magnifying or screen reader software. read AbCS_MSA_Guide located in the doc folder I  wrote this AbCS_MSA_Guide for the former version of AbCS which was written in MS Access. Keep in mind the functionality is similar the user interface is different with the the python version using menus and proper status bars.

89. complete - book detail and web metadata windows - plot need to expand more check the windows height setting

90. complete - main window - when in duplicate mode and a export button that will export to csv file with author, title, year, collection and date added. simular to import window export.

91. complete - book_detail window - 1. alt+t is set to both title and time should be only title alt+m is time check centalized shortcut in shortcut.py. When exiting update the save popup appears it should only appear if it is dirty

92. complete - when you run the abcs.ext created by the installer, exporting in import win and main win are defaulting to the program filesabcs folder - can this be changed to the user's documents folder or home folder?

93. complete - BOOK DETAIL WINDOW - 1. when you press update the new and delete button should be hidden just save button should be visible 2. can't tab to format fields in view/read mode.

94. what is involved in fixing this? - linux version window icons and graphic in the about_dialogue are not showing.

95. Accessible events – change timing from hard coded 300ms to be based on screen reader; jaws 300ms, nvda 1500ms, orca 800ms. No screen reader 0ms. See screen_reader as it check for a screen reader.

96. import window –
    1. the import should be applying the format filter prior to scanning the file when it creates the directory list. Improve import time in some cases.  
    2. check to see why there is hard coded “reader” text. Reader should be found by checking the composer tag then if empty look in comments for the words defined in the reader keywords in preferences window.
    3. 2. Comment are not accumulating. If not the same they should be accumulated. Some books have plot in comments.
97. Statistic window -
    1. collection that have zero books are not showing
    2. change the table so that the label and the value speak as you arrow up/down

98. import window 
   1. selecting not working 
   2. table row are being announced by jaws 
   3. alt+x is not working for export button 
   4. don't include trimmed author or title in corrected list 

# performance tuining bugs

1. complete - if the timing prints are no longer required remove those

2. complete - New book combos display works when you do ctrl+n from main win but not when in

3. complete - Update mode field unlocking  combos appear but other fields are locked

4. complete - editing button appears when you press update only save button should show not fetch web info

5. complete - new should only show save no update button

6. complete Title label alignment -- look at import detail very similar layout

7. complete box accessibility - tab order is not normalized new fields come after fetch web info button, alt+a i g c don't work check centralized shortcuts in shortcuts.py

8. complete - was onfocus to button but doesn't trigger update. look at delete button

9. complete - on update move focus to title not author

