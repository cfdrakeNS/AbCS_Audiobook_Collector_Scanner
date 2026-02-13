Overview
AbCS – Audio book Collector Scanner, is an Audio Book collector database application with full search capabilities for Titles, Authors, Genre, and Series. AbCS can import Audio Book details from the data stored in the ID3Tags of each audio file. The Scan will include all subfolders. The import can scan all standard audio formats. The Audio Book data that is collected during the scan are Book Title, Author, Year, Genre, Duration, etc. See Import Tag Table below. You can also manually enter new books and edit existing ones. The Update Window allows the mass addition/update of Series and Genre.

The application is designed to be accessible to those with low vision or that use a screen reader.  All controls and fields have shortcut keys using alt and a letter. Pressing F1 in any of the windows will display a list of shortcut keys for that window. All windows use scalable fonts shortcut keys to zoom in or out. In addition, font sizing and theme colors can be set by the user in preferences.

Shortcut keys
Throughout the application shortcut keys, Alt or control keys followed by a single letter, are used to provide quick access to fields, buttons, and combo boxes.  These keys are denoted by an underscore on the letter. E.G. To access the Menu combo box on the Audio Book or import window pressing alt-f will move to the File Menu. The Menu at the top of the main application window is a standard menu with include File, Edit View, etc.

Application scaling Shortcuts
    • Ctrl+Plus – zoom in
    • Ctrl+Minus zoom out
    • Ctrl-Zero reset zoom to default

Using the Application
The first time the application starts, if there is no data in the application or on the Import list a message box is displayed. Select Import to scan Audio Books located on the computer or select New to enter data manually.  If items exist in the database, then the Book Window (main Window) is displayed.

Main Window – Book list









Main Window Header
The app main menu system
    • file menu alt-f
        ◦ New Book ctrl+n
        ◦ Import ctrl+i
        ◦ Quit ctrl+q
    • View alt+v
        ◦ Book Details ctrl+enter
        ◦ Author
        ◦ Genre
        ◦ Series
        ◦ Zoom In ctrl+plus
        ◦ Zoom out ctrl+minus
        ◦ Reset zoom ctrl+0 (zero)
    • Manage alt+m
        ◦ Preferences
        ◦ Backup, Restore
        ◦ Statistics
    • Help + alt+h
        ◦ About AbCS
        ◦ Shortcut Keys F1
 
Below the menu bar, there are three combo controls and one text box, left to right.
    1. Collection alt-c - if multiple collections exist this allows you to Switch between them or all Collections.
    2. Read? alt-r – Allows filtering of books by All, Read, and Unread. Only books matching the selection are displayed.
    3. Order By alt-o Change the sort order. And search scope. choices are:
    • Title – search Titles, sorted by Titles.
    • Author – search Authors, sorted by Author, Year, Title
    • Genre – search Genre, sorted by Genre, Title. Only books with a Genre are displayed.
    • Series - search Series, sorted by Series, Year, Title. Only books with a Series are displayed.
    4. Search alt-s Search will move to the first item in the list of books. Only the current Collection is searched unless All is selected for Collection.
    • Enter text in the Search box, the list will filter as you type, if the item exists.  Pressing enter will move the focus to the first records that match the selection.
    • To do a keywords search enter a “?” question mark, followed by a word or phrase to search within an item and press enter. Only records containing the search phrase are displayed. enter will move the focus to the first records that match the selection.
    • Pressing Enter is search will move the focus into the book table into Author, Title, Genre or Series, depending upon the setting of Order By combo
    • Press the escape key to clear search result.
    5. 
Book list Window detail.
Pressing alt-b will move to the book list. The book list is A continuous list with the following columns fields. Author, Title, Year, Plot, Series, Genre, Time, Tracks, Read, Date-added
    • Press Ctrl+Enter or double-click to open the Book Details Window for viewing and editing.
    • To select books for updating or deleting;
            ▪ Keyboard press Shift+Space to enter select use shift up / down arrows to select multiple books.
            ▪ Mouse use ctrl+click or shift+click for multiple selection
        ◦ As books are selected the status will display the last book selected title and the number of books selected. Screen reader users – press alt+/ to read the status bar.
        ◦ To clear the selection press alt-l for Cancel or click Cancel button. Moving any of the arrow keys or clicking the mouse will clear the selection

Main Window Footer
The footer section has three buttons
The buttons are only visible if one or more books are selected.
    1. Update – alt-u opens the update Window where you can mass update Series, Genre and if more than one collection exists change the collection.
    2. Delete alt-d – deletes selected books, a confirmation message will appear. Choose Yes to delete the selected books or choose No to cancel.
    3. Cancel – alt-l clears any titles that are selected and hides the Update, Delete and Cancel buttons.
    4. Status Bar – show xx books in collection… sorted by title, author, etc. Search results and selection messages

Main Window Shortcut Keys
Collection – alt+c
Read – alt+r
Order by – alt+o
Search – alt+s
Book Detail – alt-b Move focus to the book detail list
Pressing Alt+ a number on the keyboard will jump to the respective column 1 through 10. e.g alt+1 Author, alt+2 Title, alt+3 Year, etc. alt+0 Date Added the last column.
Update – alt-u
Delete – alt-d
Cancel – alt-l

Book Details Window
To enter the book detail window from the book list press ctrl+enter or double clicking any book  in the book row details.
Book Details Window Header
One text box displays the current sort order. e.g., Title, author which was set in the Main  Window.
Book Details Window - Details
Single Window with fields laid out in six rows. All fields are text box unless stated otherwise. All books detail date can be updated here. As you tab through the fields the cursor is placed at the end of the text within each field. Combo boxes for Author, Collection Series and Genre are set not to use the arrow up / down keys to prevent accidental changes. TO change the value of a combo-box use alt+down arrow to expand the drop-down list. To locate an item in list use up / down arrows or type text to jump to an item in the combo list.
    • Row1 – Title alt-t,
        ◦ - Author(combo) alt-a
    • Row2 – Comments alt-o – comments such book plot, etc. (plain text format)
    • Row3 - Year alt-y
        ◦ Time alt+m format is hh:mm
        ◦ Reader alt+r
        ◦ Date Read alt+e format is 4-digit year – 2 digit month – 2 digit day. When in the date read fields use tab / shift+tab to move from year, month and day.  
    • Row4 – Series(combo) alt-I
        ◦ Genre(combo) alt+g
        ◦ Collection(combo) alt+l
    • Row5 - Bitrate alt-b
        ◦ Size alt-s – in MB
        ◦ File Format – Mp3, etc.
        ◦ Source – windows user-id of the window’s user id used to do the import.
        ◦ Row6 – Path alt-h – Location of book when imported. Ctrl+Enter or double-click to open the path if it exists.
        ◦ Date Added alt-e
Book Details Window - Footer

There are four buttons as follows:
    1. New, ctrl+N – Clears the Window for input. Collection and date added fields are auto filled.
    2. Save – alt-s – this button is visible when any changes are made to the book data.
    3. Delete alt-d – deletes the record being displayed. A message confirming the deletion will appear.
    4. Close alt-c or escape closes the Detail window and return to the Main book list window.

            ▪ Page-Up move to the previous title.
            ▪ Page-Down move to the next title.

Book Details Window Shortcut Keys
Pressing F1 in the Main Book window will show the following shortcuts in a pop up window.
Press alt follow by the key letter below:
A - Author
B - Bitrate
B - Book List
C - Close
D - Delete
E - Read Date
F - Files
G - Genre
H - Path
I - Series
L - Collection
M - Time
O - Comments
R - Reader
S - Save
T - Title
Y - Year
Z - Size    
Update Window
The update Window provides the ability to mass updates or remove; Series, Genre and Collection for selected books.

Update Window Header
Three combo boxes Series alt-s, Genre alt-g and Collection alt-l Collection is only visible if multiple collection exists. Select a series and/or genre from the list or enter a new one, or select None from the list to clear the item.
Updates occur as soon as a Series, Genre or Collection is change and either enter or tab is pressed
Window Update Details
A continuous list of books that were selected in the Book list Windows with the following fields, Title, Year, Series, Genre, and Collection.

Update Window Footer
Close button alt-c or Escape.

Update Window Shortcut Keys
Press alt follow by key letter below:
        s - Series    
        g - Genre    
        l - Collection
        c - Close
Import Process………………coming soon!
