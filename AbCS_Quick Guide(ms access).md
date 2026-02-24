# Overview 

AbCS – Audiobook Collector Scanner, is an Audiobook collector database
application with full search capabilities for Titles, Authors, Genre,
and Series. AbCS can import audiobook details from the data stored in
the ID3Tags of each audio file. The Scan will include all subfolders.
The import can scan all standard audio formats. The audiobook data that
is collected during the scan are Book Title, Author, Year, Genre,
Duration, etc. See Import Tag Table below. You can also manually enter
new books and edit existing ones. The Update Window allows the mass
addition/update of Series and Genre.

The application is designed to be more accessible to those folks with
low vision or that use a screen reader. Colors for background and text
that provide sharp contrast without being overall too bright. All fonts
used are 14-points or larger. Custom message boxes are used to provide14
point font instead of the default windows message box which uses an
8-point font. All messages and tooltips are also routed to the status
bar for screen readers. In addition, most controls and fields have
shortcut keys using alt and a letter.

Note: This prototype in MS Access lacks screen reader accessibility. The
final version will be likely in Python.

## function keys

- F2 – toggles selected/unselected text within a field.

- F3 – From the Audiobook window; move to the search box or if in a
  keyword search clears the search.

- F4 – Closes the currently open window and From the Audiobook window
  will cancel edit mode or if not in edit mode will close the
  application.

- F5 – Refreshes the data displayed in the window. Generally, not
  required.

- F6 – Cycle focus of the window from Header to Detail, to Footer and
  application menu. Pressing shift-F6 reverses the order.

- F8 – When the cursor is in Author, Title, Series, Genre collection
  fields opens the associated window for that item.

- F9 – Pressing from the Audiobook Window Open the Import Windows.
  Pressing F9 from the Import Window is the same as pressing the Import
  button.

- F10 – move focus to the MS Access ribbon menu.

## Shortcut keys 

Throughout the application shortcut keys, Alt key followed by a single
letter, are used to provide quick access to fields, buttons, and combo
boxes. These keys are denoted by an underscore on the letter. E.g. To
access the <u>M</u>enu combo box on the audiobook or import window
pressing alt-m will move to the Menu combo box.

The Menu located on the Audiobook window allows for keyboard access to
other parts of the application. Pressing alt-m to move to the menu
followed by the first letter of the menu item followed by enter is the
same as choosing an item from the dropdown menu.

E.g. alt-m I – show the Infor/about message box.

# Using the Application 

When the AbCS application starts a splash Window appears displaying the
name of the Database and total titles, author, etc.

The first time the application starts, if there is no data in the
application or on the Import list a message box is displayed. Select
Import to scan audiobooks located on the computer or select New to enter
data manually. If items exist in the database, then the Audiobook Window
(main Window) is displayed.

## Audiobook Window (main Window)

> 

### Audiobook Window Header 

Five combo controls and one text box, left to right.

1.  Collection alt-l - if multiple collections exist this allows you to
    Switch between them or all Collections. Pressing F8 or
    double-clicking will open the Collection Window.

2.  Read? alt-r – Allows filtering of books by All, Read, and Unread.
    Only books matching the selection are displayed.

3.  Order By alt-o Change the sort order. And search scope. choices are:

- Title – search Titles, sorted by Titles.

- Author – search Authors, sorted by Author, Year, Title

- Genre – search Genre, sorted by Genre, Title

- Series - search Series, sorted by Series, Year, Title

4.  Search alt-s or F3 – Search will move to the first item on the
    Window. Only the current Collection is searched unless All is
    selected for Collection.

- Enter text in the Search box, it will auto fill as you type, if the
  item exists.

- Or press the down arrow on the Search box or press alt-down-arrow to
  display the list of items. The list selector bar will move as you
  type. Press Enter to select the item. The focus moves to the first
  records that match the selection.

- To do keywords search enter an = “equals sign” followed by a word or
  phrase to search within an item. Unlike the search above only records
  containing the search phrase are displayed. The search result is
  cleared when a new search, pressing F3 or changing the Order By combo
  boxes. *NOTE: The equal “=” is not required but prevents the combo box
  from automatically updating as matches are found in the database.*

5.  Menu alt-m – Combo box with ten options

- Import - opens the import window.

- New Title -opens the detail screen for data entry.

- Backup/Restore - See below for details.

- Authors, Collection, Genre, Series – each of these items opens their
  respective windows.

- Show Duplicates – Duplicates are those titles having the same Title,
  Author, Year and Collection. The application checks for duplicates
  when adding records from the import. However, duplicate can occur by
  manual additions or edits. All functions such as Delete, Update is
  available in the duplicate view. The duplicate result is cleared by
  new search, pressing F3 or changing any of the combo boxes at the top
  of the window.

- About

- Quit

6.  Selected alt-e – The count of records selected for delete or update.

### Audiobook Window detail. 

A continuous list with the following columns fields.

Author, Title, Year, Series, Genre, Time, Tracks, Read, Date-added

- When the cursor is located within the Author, Series, Genre field:
  Pressing F8 or double-clicking will open the respective Windows. If
  the cursor is in the Title fields pressing enter will open the detail
  window.

<!-- -->

- Title – Enter or F8 or double-click open the Book Details Window for
  viewing and editing.

- Read – A check box that if click toggles the title as read/unread.
  Next to that is a date field with a date-picker to the right edge of
  the field. Either can be used to mark a book as read.

- Pressing the Spacebar when in the title fields toggles between
  selected or unselected for deleting or updating. The count of Selected
  records is displayed at the top right of the Window alt-e. The
  selected records will have a different color than normal items and the
  title and selected or unselected is echoed to the status bar.

### Audiobook Window Footer 

The footer section has three buttons and two text boxes.

The buttons are only visible if one or more titles are selected.

1.  Update – alt-u opens the update Window where you can mass update
    Series, Genre and if more than one collection exists change the
    collection.

2.  Delete alt-d or Delete Key – deletes selected records, a
    confirmation message will appear. Selected titles and any unmatched
    Authors, Genre and series are removed.

3.  Cancel – alt-c or F4 clears any titles that are selected and hides
    Update, Delete and Cancel buttons.

4.  Text Box - Number of items e.g., Titles, Authors in current selected
    by the Order By combo. If a keyword-search, (using an “=” equal”)
    then it shows the number of books that match.

5.  Text Box – current sort order

##  Book Details Window

### Book Details Window Header 

One text box displays the current browsing selection e.g., Title, author
which was set in the Audiobook Window.

### Book Details Window - Details

Single Window with fields laid out in eight rows and three columns all
fields are textbox unless stated otherwise.

- Row1 – title alt-t

- Row2 – Author alt-a combo of all authors. F8 or double-click to open
  list.

  - Year alt-y – 4-digit year the book was published.

  - Files alt-f - number of files

- Row3 – Series alt-I – combo of all Series. F8 or double-click to open
  the list.

  - Genre alt-g - combo of all Genre. F8 or double-click to open the
    list.

- Row4 – Reader alt-r

  - Read - (date read has date selector)

  - Returned – date returned (only visible if the collection’s Borrowed
    field is checked).

- Row5 – Collection alt-l

  - Time alt-m hour and minutes

  - Size alt-s – in MB

  - File Format – Mp3, etc.

- Row6 – Added alt-e

  - Bitrate alt-b recording quality in kbps

  - Source – windows user-id of the window’s user id used to do the
    import.

- Row7 – Path alt-h – Location of book when imported. F8 or double-click
  to open the path in Windows File Explorer

- Row8 – Comments alt-o – comments such book descriptions, etc. Supports
  Rich Text formatting such as bold, underline, fonts, color, etc.

### Book Details Window – Footer 

There are six buttons as follows:

1.  New alt-w or insert-key – Clears the Window for input. Collection
    and date added fields are auto filled.

2.  Save – alt-v – this button is visible when any changes are made to
    the data in the Window.

3.  Delete alt-d or delete key – deletes the record being displayed. A
    message confirming the deletion will appear.

4.  Prev alt-p or Page-Up move to the previous title.

5.  Next alt-n or Page-Down move to the next title.

6.  Close alt-c or F4 – close.

All edits are automatically saved when Close, Next and Prev buttons are
pressed.

## Update Window 

The update Window provides the ability to mass updates to selected books
from the Audiobook Window.

> 

### Update Window Header

Three combo boxes Series alt-s, Genre alt-g and Collection alt-l
Collection is only visible if multiple collection exists. Select a
series and/or genre from the list or enter a new one. Updates occur as
soon as a Series, Genre or Collection is selected.

### Window Update Details

A continuous list with the following fields, Title, Year, Series, Genre,
and Collection

Update Window Footer

Close button alt-c or F4.

## Import Window 

### Import Window Header 

The Header has the following controls left to right.

1.  Collection (alt-l) combo choose a collection. If only one collection
    exists in the database. It will default to that collection. If more
    than one Collection exists, then choose a collection from the combo
    box. Pressing F8 or double-clicking will open the Collection Window.

2.  Flip Author Name (alt-f) Check box flips the author’s name to last,
    first, default is unchecked.

3.  Elapsed Time: alt-t time the import took to complete hh:mm.

4.  Import List: alt-s number of records without errors.

5.  Parse Errors: alt-p, number of records that have errors, e.g., no
    author, etc.

6.  Read Errors: alt-r number of records, caused by corrupted file.

7.  Menu alt-m – Combo box with four options

- Collection – Open Collection Window to add or edit a collection.

- New Title – open the data entry window.

- Backup/Restore – Open the backup/Restore Window.

- Close the import window and if books exist in the application the
  Audiobook window will open, otherwise the application will close.

### Import Window detail

A continuous list with the following fields.

Author, Title, Year, Tracks, Time, Errors. All are plain text boxes.

Pressing Space Bar on a title will toggle the book from add to errors or
vice versa.

Pressing F8 or double-clicking on a title with errors will open a detail
Window that displays all data. This Window allows you to view/edit the
item with errors.

### Import Window Footer 

Five buttons as follows:

1.  Import alt-I or F9 – Prompts for a folder to scan. All subfolders
    are scanned for tags. The prompt is a normal windows explorer dialog
    box. Select folder and click OK.

2.  Export alt-x – Exports a list of errors to a standard spreadsheet
    file.

3.  View alt-v – Open a detailed view of the book with errors, or F8
    when cursor is in the title field.

4.  Add alt-a - Add the records without errors to the database.

5.  Close alt-c or F4 - close the Import Window. If there are no
    audiobooks in the database, the application closes. If audiobooks do
    exist, the Audiobook window will open.

### Import Detail Window

> 

**The data in this window is fully editable thus can be changed with no
edits.**

### import Detail Error Header 

Current Collection

### import Detail Error Detail 

Single Window with fields laid out in seven rows and three columns all
fields are textboxs.

- Row1 - title alt-t

- Row2 -Author alt-a

  - Year alt-y - year the book was published.

  - Files alt-f - number of files

- Row3 - Reader alt-r

  - Time alt-m hour and minutes

  - Genre alt-g

- Row4 - Collection alt-l

  - Bitrate alt-b

  - Size alt-s – in MB

  - File Format – Mp3, etc.

- Row5 - Path alt-h - The location of the audio files. F8 or
  double-click to open the path in Windows File Explorer

- Row8 - Errors alt-o – List of the audio files and related errors. See
  Import Errors Description table below.

### import Detail Error Footer 

**There are five buttons located at the bottom.**

- **Edit Tag – alt-I –open the audiobook in a tag editor. This button is
  only visible if Mp3Tag or Tag Scanner is installed on your PC.**

<!-- -->

- **Keep – clears the error flag and moves to the next record with
  errors.**

- **Prev alt-p, Next alt-n, or page-up and Page-down move between error
  records**

- **Close alt-c or F4 returns to the Import Window.**

# Importing:

From the Import Window:

1.  Click the Import button or press F9 or alt-I to start the import.
    (If any books exist on the import list you will be prompted to ask
    if you want to keep them. Click Keep alt-k or Delete alt-d .)

    1.  

2.  Select the folder you want to scan and click OK.

3.  All controls on the window are locked during the import process. If
    there are many files being scanned a windows Shell Window may appear
    and it will go away on its own.

4.  The Importing Status window will display.

> 
>
> **This window displays import progress and counts.**

- **Title: alt-t and Author alt-a the current book being processed**

- **Error alt-e – only display if the current book has an error.**

- **Files Scanned alf-f the number of audio files scanned.**

- **Elapsed Time alt-t**

- **Import List alt-s – number of books added to the Import list.**

- Parse Errors: alt-p, number of records that have errors, e.g., no
  author, etc.

- Read Errors: alt-r number of records, caused by corrupted file.

- Message box.

- Pause button alt-p – pauses the import.

- Cancel alt-c – A message box confirming will be displayed.

> 

When the import is completed press the Close alt-c button to close the
Importing Status window.

The import window will display the books that were imported and any
errors.

- Press the View button alt-v – Open a detailed view of the book with
  errors, or F8 when cursor is in the title field. See **Import Detail
  window below**.

- Click Add or alt-a to add all books imported without errors to the
  database.

- If there are no more books on the import list the import Window will
  close, and the Audiobook Window is displayed. If errors exists the
  Import window will remain open.

## Collection Window 

> 

**Collection Window Header –** no controls

**Collection Window Detail**

> Four controlls

- Delete button

- Collection name

- Borrowed checkbox – If checked the return date field will be displayed
  on the Detail Window.

- Active checkbox – If checked then the collection is shown in the
  Collection combo on the Audiobook and Import Windows. To hide a
  collection uncheck the Active checkbox.

**Collection Window Footer –** Close alt-c or F4.

## Author, Genre, and Series Windows

> 

**These three Windows are similar with the same controls and layout.
They are for making corrections to Author, Series or Genre.**

**Author Window Header -** Search combo box to quickly move to a
particular Author.

**Author Window Detail -** Continuous list Author Name.

**Author Window Footer –** Close alt-c or F4.

*Note: Author, Collection, Genre, or Series cannot be deleted if there
are books associated with them.*

## Backup/Restore Window

> 

**Backup/Restore Window Header – no controls**

### Backup/Restore Window – detail

- **Listbox –** list existing backups

- **Browse button –** to select a backup that is located somewhere other
  than the default backup folder

- **Textbox** – Display the name of the backup file to be restored.

### Backup/Restore Window – Footer 

> Four buttons:

- **Backup** alt-b – creates a backup of the application in the default
  bacckup folder

- **Resore** alt-r – Restores the application from a selected backup

- **Full Reset** alt-f – Clears all data in the application.

- **Close** alt-c or F4 – Close the Backup/Restore window.

Backup files are names are: AbCS_backup_yyyy-mm-dd_ddd_hh-mm-ss

e.g. AbCS_backup_2024-May-17_Fri_18-15-24.

# Import Errors Description 

| **Error messages** | **Cause / tag issue** |  |
|----|----|----|
| Author Blank | Blank tag for Album Artist and Artist tag |  |
| Author name in Title | Title contains author name (not always an error) |  |
| Author Name is 'Artist Album' | Album Artist and Artist tag are null |  |
| Author Name is 'Unknown Artist' | Unknown in Album Artist and Artist tag |  |
| Author Name Starts with | Author name begins with non-alphabetic character |  |
| Duplicate Author & Title | Duplicates are those records having the same Title, Author, Year and Collection |  |
| File not found | The folder/files being scanned have move – usually caused by USB drive being disconnected from the computer. |  |
| Read Error | Unable to read the file. Usually due to corrupted tags in the file. |  |
| Title Blank | Blank tag for Album is blank |  |
| Title in Author name | Book title appears in Author Tag |  |

# ID3Tags scanned during import:

| Book Data Field | ID3Tag Source |
|----|----|
| Book Title | Album (13) |
| Author | Album Artist (237) if empty Artist (13) |
| Size in MB | TrackSize (1) in kb accumulated if multiple files. |
| Time in hours & minutes | Track Time (27) accumulated if multiple files. |
| Release year | Year (15) |
| Audio Quality | Bitrate (28) in kb |
| Genre | Genre (16) |
| Comments | Comments (240 accumulated if different in each file of a book. Scan for “read by”, etc. |
| Reader/narrator | Composer (243) sometimes contains the narrator/reader. |
