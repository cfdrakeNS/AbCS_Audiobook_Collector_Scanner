# AbCS – Audiobook Collector Scanner Quick Guide

# Overview
AbCS (Audiobook Collector Scanner) is an audiobook collector database application with full search capabilities for Titles, Authors, Genre, and Series.
AbCS can import audiobook details from the data stored in the ID3 tags of each audio file.
The scan will include all subfolders. The import can scan all standard audio formats.
The audiobook data that is collected during the scan includes Book Title, Author, Year, Genre, Duration, etc. See the Import Tag Table below.
You can also manually enter new books and edit existing ones.
The Update Window allows the mass addition/update of Series and Genre.

The application is designed to be more accessible to those folks with low vision or who use a screen reader.
Colors for the background and text provide sharp contrast without being overly bright.
All fonts used are 14-point or larger. Custom message boxes are used to provide a 14-point font instead of the default Windows message box which uses an 8-point font.
All messages and tooltips are also routed to the status bar for screen readers.
In addition, most controls and fields have shortcut keys using Alt and a letter.

Note: This prototype in MS Access lacks screen reader accessibility. The final version will likely be in Python.

# Function Keys
* **F2** – Toggles selected/unselected text within a field.
* **F3** – From the Audiobook window; moves to the search box or, if in a keyword search, clears the search.
* **F4** – Closes the currently open window and, from the Audiobook window, will cancel edit mode or, if not in edit mode, will close the application.
* **F5** – Refreshes the data displayed in the window. Generally, not required.
* **F6** – Cycles focus of the window from Header to Detail, to Footer and application menu.
* **Shift-F6** – Reverses the order.
* **F8** – When the cursor is in Author, Title, Series, or Genre collection fields, opens the associated window for that item.
* **F9** – Pressing from the Audiobook Window opens the Import Window. Pressing F9 from the Import Window is the same as pressing the Import button.
* **F10** – Moves focus to the MS Access ribbon menu.

# Shortcut Keys
Throughout the application, shortcut keys (the Alt key followed by a single letter) are used to provide quick access to fields, buttons, and combo boxes.
These keys are denoted by an underscore on the letter. E.g., to access the Menu combo box on the audiobook or import window, pressing Alt-M will move to the Menu combo box.
The Menu located on the Audiobook window allows for keyboard access to other parts of the application.
Pressing Alt-M to move to the menu, followed by the first letter of the menu item, followed by Enter, is the same as choosing an item from the dropdown menu.
E.g., Alt-M I – shows the Info/About message box.

# Using the Application
When the AbCS application starts, a splash window appears displaying the name of the database and total titles, authors, etc.
The first time the application starts, if there is no data in the application or on the Import list, a message box is displayed.
Select Import to scan audiobooks located on the computer, or select New to enter data manually.
If items exist in the database, then the Audiobook Window (main window) is displayed.

## Audiobook Window (Main Window)
[Image of Audiobook Window Screenshot]

### Audiobook Window Header
[Image of Audiobook Window Header Screenshot]

Five combo controls and one text box, left to right.
* **Collection (Alt-L)** – If multiple collections exist, this allows you to switch between them or all Collections. Pressing F8 or double-clicking will open the Collection Window.
* **Read? (Alt-R)** – Allows filtering of books by All, Read, and Unread. Only books matching the selection are displayed.
* **Order By (Alt-O)** – Changes the sort order and search scope. Choices are:
  * Title – Search Titles, sorted by Titles.
  * Author – Search Authors, sorted by Author, Year, Title.
  * Genre – Search Genre, sorted by Genre, Title.
  * Series – Search Series, sorted by Series, Year, Title.
* **Search (Alt-S or F3)** – Search will move to the first item on the window. Only the current Collection is searched unless All is selected for Collection. Enter text in the Search box, it will auto-fill as you type, if the item exists. Or press the down arrow on the Search box or press Alt-down-arrow to display the list of items. The list selector bar will move as you type. Press Enter to select the item. The focus moves to the first record that matches the selection.
  * To do a keyword search, enter an equals sign (=) followed by a word or phrase to search within an item. Unlike the search above, only records containing the search phrase are displayed. The search result is cleared when a new search begins, pressing F3, or changing the Order By combo boxes.
  * NOTE: The equals sign (=) is not required but prevents the combo box from automatically updating as matches are found in the database.
* **Menu (Alt-M)** – Combo box with ten options:
  * Import - Opens the import window.
  * New Title - Opens the detail screen for data entry.
  * Backup/Restore - See below for details.
  * Authors, Collection, Genre, Series – Each of these items opens their respective windows.
  * Show Duplicates – Duplicates are those titles having the same Title, Author, Year, and Collection. The application checks for duplicates when adding records from the import. However, duplicates can occur by manual additions or edits. All functions such as Delete and Update are available in the duplicate view. The duplicate result is cleared by a new search, pressing F3, or changing any of the combo boxes at the top of the window.
  * About
  * Quit
* **Selected (Alt-E)** – The count of records selected for delete or update.

### Audiobook Window Detail
[Image of Audiobook Window Detail Screenshot]

A continuous list with the following column fields:
Author, Title, Year, Series, Genre, Time, Tracks, Read, Date-added.

When the cursor is located within the Author, Series, or Genre field: Pressing F8 or double-clicking will open the respective windows.
If the cursor is in the Title fields, pressing Enter will open the detail window.
* **Title** – Enter or F8 or double-click opens the Book Details Window for viewing and editing.
* **Read** – A check box that, if clicked, toggles the title as read/unread. Next to that is a date field with a date-picker to the right edge of the field. Either can be used to mark a book as read.

Pressing the Spacebar when in the title fields toggles between selected or unselected for deleting or updating. The count of selected records is displayed at the top right of the window (Alt-E). The selected records will have a different color than normal items, and the title and selected or unselected status is echoed to the status bar.

### Audiobook Window Footer
[Image of Audiobook Window Footer Screenshot]

The footer section has three buttons and two text boxes.
The buttons are only visible if one or more titles are selected.
* **Update (Alt-U)** – Opens the update window where you can mass update Series, Genre, and if more than one collection exists, change the collection.
* **Delete (Alt-D or Delete Key)** – Deletes selected records; a confirmation message will appear. Selected titles and any unmatched Authors, Genres, and Series are removed.
* **Cancel (Alt-C or F4)** – Clears any titles that are selected and hides Update, Delete, and Cancel buttons.
* **Text Box** – Number of items (e.g., Titles, Authors) currently selected by the Order By combo. If it is a keyword search (using an equals sign =), then it shows the number of books that match.
* **Text Box** – Current sort order.

## Book Details Window
[Image of Book Details Window Screenshot]

### Book Details Window Header
One text box displays the current browsing selection (e.g., Title, Author) which was set in the Audiobook Window.

### Book Details Window - Details
Single window with fields laid out in eight rows and three columns; all fields are text boxes unless stated otherwise.
* **Row 1** – Title (Alt-T)
* **Row 2** – Author (Alt-A, combo of all authors, F8 or double-click to open list), Year (Alt-Y, 4-digit year the book was published), Files (Alt-F, number of files)
* **Row 3** – Series (Alt-I, combo of all Series, F8 or double-click to open the list), Genre (Alt-G, combo of all Genre, F8 or double-click to open the list)
* **Row 4** – Reader (Alt-R), Read (date read has date selector), Returned (date returned; only visible if the collection’s Borrowed field is checked).
* **Row 5** – Collection (Alt-L), Time (Alt-M, hours and minutes), Size (Alt-S, in MB), File Format (MP3, etc.)
* **Row 6** – Added (Alt-E), Bitrate (Alt-B, recording quality in kbps), Source (Windows user ID used to do the import).
* **Row 7** – Path (Alt-H, location of book when imported). F8 or double-click to open the path in Windows File Explorer.
* **Row 8** – Comments (Alt-O, comments such as book descriptions, etc.). Supports Rich Text formatting such as bold, underline, fonts, colors, etc.

### Book Details Window – Footer
[Image of Book Details Window Footer Screenshot]

There are six buttons as follows:
* **New (Alt-W or Insert key)** – Clears the window for input. Collection and date added fields are auto-filled.
* **Save (Alt-V)** – This button is visible when any changes are made to the data in the window.
* **Delete (Alt-D or Delete key)** – Deletes the record being displayed. A message confirming the deletion will appear.
* **Prev (Alt-P or Page-Up)** – Move to the previous title.
* **Next (Alt-N or Page-Down)** – Move to the next title.
* **Close (Alt-C or F4)** – Close. All edits are automatically saved when Close, Next, and Prev buttons are pressed.

## Update Window
The update window provides the ability to make mass updates to selected books from the Audiobook Window.

[Image of Update Window Screenshot]

### Update Window Header
Three combo boxes: Series (Alt-S), Genre (Alt-G), and Collection (Alt-L). Collection is only visible if multiple collections exist.
Select a series and/or genre from the list or enter a new one.
Updates occur as soon as a Series, Genre, or Collection is selected.

### Window Update Details
A continuous list with the following fields: Title, Year, Series, Genre, and Collection.

### Update Window Footer
Close button (Alt-C or F4).

## Import Window
[Image of Import Window Screenshot]

### Import Window Header
[Image of Import Window Header Screenshot]

The Header has the following controls left to right.
* **Collection (Alt-L)** combo – Choose a collection. If only one collection exists in the database, it will default to that collection. If more than one Collection exists, then choose a collection from the combo box. Pressing F8 or double-clicking will open the Collection Window.
* **Flip Author Name (Alt-F)** – Check box flips the author’s name to last, first; default is unchecked.
* **Elapsed Time (Alt-T)** – Time the import took to complete hh:mm.
* **Import List (Alt-S)** – Number of records without errors.
* **Parse Errors (Alt-P)** – Number of records that have errors, e.g., no author, etc.
* **Read Errors (Alt-R)** – Number of records caused by a corrupted file.
* **Menu (Alt-M)** – Combo box with four options:
  * Collection – Open Collection Window to add or edit a collection.
  * New Title – Open the data entry window.
  * Backup/Restore – Open the Backup/Restore Window.
  * Close the import window. If books exist in the application, the Audiobook window will open; otherwise, the application will close.

### Import Window Detail
[Image of Import Window Detail Screenshot]

A continuous list with the following fields:
Author, Title, Year, Tracks, Time, Errors. All are plain text boxes.

Pressing the Space Bar on a title will toggle the book from 'add' to 'errors' or vice versa.
Pressing F8 or double-clicking on a title with errors will open a detail window that displays all data.
This window allows you to view/edit the item with errors.

### Import Window Footer
[Image of Import Window Footer Screenshot]

Five buttons as follows:
* **Import (Alt-I or F9)** – Prompts for a folder to scan. All subfolders are scanned for tags. The prompt is a normal Windows Explorer dialog box. Select a folder and click OK.
* **Export (Alt-X)** – Exports a list of errors to a standard spreadsheet file.
* **View (Alt-V)** – Open a detailed view of the book with errors, or F8 when the cursor is in the title field.
* **Add (Alt-A)** – Add the records without errors to the database.
* **Close (Alt-C or F4)** – Close the Import Window. If there are no audiobooks in the database, the application closes. If audiobooks do exist, the Audiobook window will open.

## Import Detail Window
[Image of Import Detail Window Screenshot]

The data in this window is fully editable, thus can be changed to fix errors.

### Import Detail Error Header
Current Collection

### Import Detail Error Detail
Single window with fields laid out in seven rows and three columns; all fields are text boxes.
* **Row 1** - Title (Alt-T)
* **Row 2** - Author (Alt-A), Year (Alt-Y - year the book was published), Files (Alt-F - number of files)
* **Row 3** - Reader (Alt-R), Time (Alt-M - hours and minutes), Genre (Alt-G)
* **Row 4** - Collection (Alt-L), Bitrate (Alt-B), Size (Alt-S – in MB), File Format (MP3, etc.)
* **Row 5** - Path (Alt-H - The location of the audio files). F8 or double-click to open the path in Windows File Explorer.
* **Row 8** - Errors (Alt-O – List of the audio files and related errors). See Import Errors Description table below.

### Import Detail Error Footer
There are five buttons located at the bottom.
* **Edit Tag (Alt-I)** – Open the audiobook in a tag editor. This button is only visible if Mp3Tag or Tag Scanner is installed on your PC.
* **Keep** – Clears the error flag and moves to the next record with errors.
* **Prev (Alt-P), Next (Alt-N), or Page-Up and Page-Down** move between error records.
* **Close (Alt-C or F4)** returns to the Import Window.

## Importing:
From the Import Window:
Click the Import button or press F9 or Alt-I to start the import.
(If any books exist on the import list, you will be prompted to ask if you want to keep them. Click Keep (Alt-K) or Delete (Alt-D).)

[Image of Titles Exist on Import List Dialog]

Select the folder you want to scan and click OK.
All controls on the window are locked during the import process.
If there are many files being scanned, a Windows Shell window may appear and it will go away on its own.
The Importing Status window will display.

[Image of Importing Status Window Screenshot]

This window displays import progress and counts.
* **Title (Alt-T) and Author (Alt-A)** – The current book being processed.
* **Error (Alt-E)** – Only displays if the current book has an error.
* **Files Scanned (Alt-F)** – The number of audio files scanned.
* **Elapsed Time (Alt-T)**
* **Import List (Alt-S)** – Number of books added to the Import list.
* **Parse Errors (Alt-P)** – Number of records that have errors, e.g., no author, etc.
* **Read Errors (Alt-R)** – Number of records caused by a corrupted file.

Message box options:
* **Pause button (Alt-P)** – Pauses the import.
* **Cancel (Alt-C)** – A message box confirming will be displayed.

[Image of Cancel Import Dialog]

When the import is completed, press the Close (Alt-C) button to close the Importing Status window.
The import window will display the books that were imported and any errors.
Press the View button (Alt-V) – Open a detailed view of the book with errors, or F8 when the cursor is in the title field.
See Import Detail window below.
Click Add or Alt-A to add all books imported without errors to the database.
If there are no more books on the import list, the Import Window will close, and the Audiobook Window is displayed.
If errors exist, the Import window will remain open.

## Collection Window
[Image of Collection Window Screenshot]

### Collection Window Header
No controls.

### Collection Window Detail
Four controls:
* Delete button
* Collection name
* Borrowed checkbox – If checked, the return date field will be displayed on the Detail Window.
* Active checkbox – If checked, then the collection is shown in the Collection combo on the Audiobook and Import Windows. To hide a collection, uncheck the Active checkbox.

### Collection Window Footer
Close (Alt-C or F4).

## Author, Genre, and Series Windows
[Image of Author, Genre, and Series Windows Screenshot]

These three windows are similar with the same controls and layout.
They are for making corrections to Author, Series, or Genre.
* **Author Window Header** - Search combo box to quickly move to a particular Author.
* **Author Window Detail** - Continuous list Author Name.
* **Author Window Footer** – Close (Alt-C or F4).

Note: Author, Collection, Genre, or Series cannot be deleted if there are books associated with them.

## Backup and Restore Window
[Image of Backup/Restore Window Screenshot]

### Backup/Restore Window Header
No controls.

### Backup/Restore Window – Detail
* Listbox – List existing backups.
* Browse button – To select a backup that is located somewhere other than the default backup folder.
* Textbox – Display the name of the backup file to be restored.

### Backup/Restore Window – Footer
Four buttons:
* **Backup (Alt-B)** – Creates a backup of the application in the default backup folder.
* **Restore (Alt-R)** – Restores the application from a selected backup.
* **Full Reset (Alt-F)** – Clears all data in the application.
* **Close (Alt-C or F4)** – Close the Backup/Restore window.

Backup files are named as: `AbCS_backup_yyyy-mm-dd_ddd_hh-mm-ss`
E.g., `AbCS_backup_2024-May-17_Fri_18-15-24.accdb`

## Import Errors Description

| Error Messages | Cause / Tag Issue |
| :--- | :--- |
| Author Blank | Blank tag for Album Artist and Artist tag |
| Author name in Title | Title contains author name (not always an error) |
| Author Name is 'Artist Album' | Album Artist and Artist tag are null |
| Author Name is 'Unknown Artist' | Unknown in Album Artist and Artist tag |
| Author Name Starts with | Author name begins with non-alphabetic character |
| Duplicate Author & Title | Duplicates are those records having the same Title, Author, Year, and Collection |
| File not found | The folder/files being scanned have moved – usually caused by USB drive being disconnected from the computer. |
| Read Error | Unable to read the file. Usually due to corrupted tags in the file. |
| Title Blank | Tag for Album is blank |
| Title in Author name | Book title appears in Author Tag |

## ID3Tags scanned during import:

| Book Data Field | ID3Tag Source |
| :--- | :--- |
| Book Title | Album (13) |
| Author | Album Artist (237) if empty Artist (13) |
| Size in MB | TrackSize (1) in kb accumulated if multiple files. |
| Time in hours & minutes | Track Time (27) accumulated if multiple files. |
| Release year | Year (15) |
| Audio Quality | Bitrate (28) in kb |
| Genre | Genre (16) |
| Comments | Comments (240) accumulated if different in each file of a book. Scan for "read by", etc. |
| Reader/narrator | Composer (243) sometimes contains the narrator/reader. |

