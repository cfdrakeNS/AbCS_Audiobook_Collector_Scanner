# Final bug fixes

1. done update window - shortcut alt=b replace with alt+l jump to list update shortcuts.py and centralized chortcuts
2. done read\_history - check the layout and formatting it has issues with the tab Selector and buttons not following theme
3. done main centre justify win read date
4. Done Book detail 1. After save or delete move focus to title. 2 after fetch web info is successful move focus to plot if not successful move focus to title.
5. Done web metadata win when web info is returned set the focus to plot if no data returned set the focus to title.
6. done read history win date range tab -  when 1st open set start date previous 3 month date from current date. Set end date to current
7. done read history win change alt+b to be alt+l update centralized shortcuts anf f1 menu
8. done main win view->collection not updating after return from backup\_restore or book\_list\_import windows
9. done book\_list\_import win - read date tester say his date are dd-mm-yy or something like that. Any ideas how to support different date format for read date?
10. done import detail make files, bitrate, size, path read only. Time fields needs a mask e.g. 12:34 as if you type in 1234 and move focus no msg. I did hear jaws say something about valid but only heard it once. remove the msg "there are no changes to save" and change the save button so it is hidden until the window is dirty. like book\_detail works
11. done book detail - Time fields needs same format fix as in import detail
12. done preferences and book list import win - dark themes were not showing qboxes text
13. done read history win - remove lengh column
14. done collection active mot being applied ?? How it was supposed to work. when active is false the books in the collection to the app they don't exist. However, that not what we have in the code and my bad for not testing prior. 1. what is the rick to implement? how many files would be need changes?
15. collection win save button not working for alt+s
16. done this has been happening for a long time but I left it alone as it took a bit of work to get the status bar to be read by jaws. Issue status bar announcing twice same with alt+/ reading status bar twice. Look at the centralized routine this and describe how it is currently implemented. Provide suggestions. Don't make any code changes.
17. done read history win general tab has showing the status bar for date range 
18. done web_metadata when called from main and no data found now shows popup again (No Web Data Found) and restores focus to table.
19. done web_metadata source checking optimized: removed redundant refresh retry loop from main/book_details call path. now one call uses WebBookAPI's internal cascade (Google -> Open Library -> WikiData), reducing repeated network waits.