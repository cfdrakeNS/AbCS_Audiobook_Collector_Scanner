

book details window changes 
I started looking at doing these changes on my own but don't know enough about pySide6 which is mainly waht we been using to make changes. Ss we go thru these changes I want to learn more about pySide6. so as you make changes tell me why you changed it. e.g. Currently the title and author are on seperate lines and I looked but did not see what causes them to be on differnt lines.
## bd#1 set the height of all controls to be uniform same height as used in Minw_windows

## bd#2 when entering a field by tab or alt+key don't select the text too easy for blind or low fision to delete it.

## bd#3 Book Details Window - Details
## 
rearrange the fields as below - stop after eeach change so I can learn  
    • Row1 – title alt-t 
        ◦ Author alt-a 
    • Row2 –  Comments alt-o plain text field  
    • Row3 – Year alt-y  
        ◦ Time alt-m hour and minutes 
        ◦ Reader alt-r
        ◦ Read - (date read has date selector) 
    • Row3 – Series alt-I
        ◦ Genre alt-g 
        ◦ Collection alt-l 
    • Row5 – Bitrate 
        ◦ Size_mb alt-s
        ◦ File_Format 
        ◦ Source 
    • Row6 path – alt alt-h  
        ◦ Added alt-e 

## bd#4 There are six buttons as follows:
    1. New alt-w or insert-key – Clears the Window for input. Collection and date added fields  are auto filled. 
    2. Save – alt-v – this button is visible only when changes are madeWindow. 
    3. Delete alt-d or delete key – deletes the record being displayed. A message confirming the deletion will appear.
    4. Prev alt-p or Page-Up move to the previous title.
    5. Next alt-n or Page-Down move to the next title.
    6. Close alt-c or escape – close.

## bd#5 Control+Enter or double-click on path to open the path if it exists, in Windows File Explorer

## bd#6 warn on exit if any edits were made 

## bd#7 same as mw#21 when exiting from book details to the main window move in the book table to the last book views in the book details window

## bd#8 Book Details Window Header 
  A text box displays the current sort order selection e.g., Title, author which was set in the        Main_Window.
 