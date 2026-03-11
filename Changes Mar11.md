# Changes March 11

---
# Prioritized Checklist (March 11)

 - [x] Preferences Window: Move description box above controls for accessibility
 - [x] Preferences Window: Alt+R and Alt+A now focus description box in Validation Rules and Auto-Correction sections
 - [x] Backup Window: Fix delete behavior so user can delete a file by clicking to select it in the list and pressing delete (now works for mouse or keyboard selection)
 - [x] Backup Window: Update F1 shortcut list
 - [x] Name List Window: Update F1 shortcut list
 - [x] Main Window (Find Box): Default Exact Match to unchecked
 - [x] Main Window (Find Box): Remember Exact Match setting
 - [x] Main Window (Find Box): Clear filter on no match/new search/close
 - [x] Collection Window: Prevent deletion of collections with books
 - [x] Backup Window: Update shortcuts (Backup: Alt+K, Backup List: Alt+B, Browse: Alt+W)
 - [x] Import Window: Set default size to 1400x800
## Summary of Changes (March 11)

	- All checklist items completed:
		- Preferences Window accessibility improvements
		- Backup Window delete and shortcut fixes
		- Name List Window F1 shortcut list updated
		- Main Window Find Box: Exact Match default, remembers setting, clears filter on no match/new search/close, popup for no match
		- Collection Window: Prevent deletion of collections with books
		- Import Window: Default size set
		- All F1 shortcut lists reflect correct keys
	- All March 11 changes are now complete and verified.


# Original Change Log



import win size 

w 1024 h 600 

File: src/main window
Function: find box
Change: the code was added, not working. fix exact match check box to default to unchecked and to remember setting from find to find.
Do not touch: unrelated items
Done when: Find box on first open will default to Exact Match unchecked and on subsequence open will remember settings for Exact Match checkbox


File: src/main window
Function: find box
Change: when no match 1, clear filter on book table so a new search can work. 2. on no match clear book table filter when find box closes
Do not touch: unrelated items
Done when: no match filter clears for new search and clears on close for no match

File: src/Preferences_windows
Function: .. window layout to improve accessibility so that the description is before the controls 
Change:  in validation rules section move the description box to be the 1st item in the section above the controls 
Change:  in Auto_correct section move the description box to be the 1st item in the section above the controls
Do not touch: unrelated code
Done when: sections are above the controls 

File: src/Preferences_windows
Function: shortcut
Change: in validation rules section Alt+R now focuses description box
Change: in Auto_correct section Alt+A now focuses description box
Do not touch: unrelated code
Done when: Alt+R and Alt+A move focus to description box at top of each section

File: src/backup_restore_window
Function: select file
Change: I select a file to delete from the list to delete then press the delete button i  get a message "Focus Backup list...." 
Do not touch: unrelated code
Done when: be able to select a file and click delete

File: src/backup_restore_window
Function: Shortcut
Change: shortcut for "Backup" is Alt+K (no mnemonic, triggers backup action directly)
Change: shortcut for "Backup List" is Alt+B (focuses backup list, no mnemonic conflict)
Change: shortcut for "Browse" is Alt+W (triggers browse action)
Change: F1 shortcut list updated to reflect new shortcuts
Do not touch: unrelated code
Done when: Alt+K triggers backup, Alt+B focuses list, Alt+W triggers browse, F1 help lists correct keys, no mnemonic conflicts

File: src/name_list_window
Function: shortcuts
Change: f1 shortcut list needs updating
Do not touch: other shortcuts
Done when: f1 shortcuts list the correct shortcuts

File: src/book_detail_window & File: src/Import_detail_window
Function: shortcuts
Change: Collection shortcut updated from Alt+K to Alt+C in both BookDetailsWindow and ImportDetailWindow. Mnemonic 'K' removed from collection label. Alt+C now correctly moves focus to the collection combo box (does not enter 'C' in text field). In ImportDetailWindow, the collection field is now read-only and always enabled for focus. F1 shortcut list updated to show Alt+C for Collection in both windows.
Do not touch: other shortcuts
Done when: F1 shortcuts list the correct keys and Alt+C focuses collection field in both windows (read-only in ImportDetailWindow).

File: src/Collection_window
Function: shortcuts
Change: don't allow deletion of collections that have books
Do not touch: unrelated code
Done when: won't be able to delete a collection with books

File: src/main window
Function: find box
Change: when no match popup a message saying "No Match found for: xxxx" This will help screen readers users 
Do not touch: unrelated items
Done when: on no match popup messge occurs 
