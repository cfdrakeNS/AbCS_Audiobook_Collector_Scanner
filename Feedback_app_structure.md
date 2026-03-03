feedback from my friend Wayne who is totally blind.

Below is a summary of the changes most of these are I consider low impact as they don't involve complex logic changes I would suggest doing number 4 first as Time fields is used in 3 windows; main Book_detail import_detail. The other changes are all in the main window. 

Standardize function within menus 
1 remove the collection combo box and add it's function to the View menu "Collections" with a Submenu for each collection that exists
2 remove the reader combo box and add it's function to the View menu "Read" with a Submenu for All, Read Unread 
3. Remove the Order By Combo and move its function to the a new sort menu The sort menu would have an item for each of the headers in the main book table IE author title, etc. Existing custom sort orders within the code for author, title and series would be used, 
4. Time fields should be renamed to Length to avoid conflict with title.
5. remove the search box change it to a popup box that has:
- a combo with Author, title, series, genre. 
- A editable search box. 
- a check box for exact search when checked does exact search uncheck does a key word search replacing the need to type "?" 
- Status bar with proper screen reader accessibility 
- Pressing enter if found close the search box and move focus to the item found. e.g. if author is selected inn the combo move to that author. if not found update the status bar message 
- Escape also closes the search popup 
- alt+S shortcut key 
- ? add to Menu ? where ?
- Escape would still clear the search filter on main window. 
6  Maintain current status bar functionality and current focus rules related to  


