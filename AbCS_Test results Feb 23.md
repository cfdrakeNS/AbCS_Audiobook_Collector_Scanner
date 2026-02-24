# AbCS Test results 
Manual coverage note: exercised all editable fields across all windows; remaining work is import scenario testing.

## isssues found and corrected 
## preference windows 
1. change reader field so text is not selected move cursor to end of text when field gets focused 
2. This message box "Auto-Correction: applies to Author, Series, Genre, and Narrator. Trim whitespace always applies to Title." is announced before "Author and title rules description read only edit"; remove that preface.
3. Auto-Correction: - change label "Move leading 'The' in Title" to "Move leading 'The' to end of Title"

## book detail window 
1. when genre and series has no value don't display none in the fields 
2. can't enter text into files, bitrate, size, format source and path  field 
3. date read leave empty when no date 
4. After entering a new author the New author message sometime pops up when edit other fields like title  this is happening with series and genre ?
5. Proper case isn't working conversion on fields isn't working being added as typed to the db.
6. Don't prepopulate author or year, or collection if more than 1 collection 
7. When not in edit mode show status bar message "alt+n New, alt-D Delete, alt+C close:

# main window 
1. when clicking table headers author, title, series and genre when sorting apply the same sort order as if selected the item from the order combo. all other heading sort as usual 

# name_list_window 
1 Author find doesn't work 

# import window 
1. alt+/ seem not to work 
2. change the exit message tesx "Close import window now? to " There are nnn valid books not added!"

# import detail window 
1. add same checks for addding author, genre, & series that is in book detail 
2. Lock all fields except title, author, comments, series, genre, reader 
3. apply proper case to title, author, comments, series, genre, reader 
4. can't tab to year 
5. 
## verification (automated)
1. Ran targeted Name List tests:
	- `python -m pytest test/test_name_list_find_matching.py test/test_name_list_status_formatting.py -q`
	- Result: `10 passed in 0.19s`

2. Ran Import Window regression tests (includes Alt+/ status-sync check during scan progress):
	- `python -m pytest test/test_import_window_collection_rules.py -q`
	- Result: `4 passed in 0.42s`

3. Ran Import Detail regression tests (combo checks, field locks, proper-case scope, and exit-message context):
	- `python -m pytest test/test_import_detail_combo_checks.py -q`
	- Result: `12 passed in 12.71s`

4. Ran Import Window regression tests (includes close prompt valid-count messaging):
	- `python -m pytest test/test_import_window_collection_rules.py -q`
	- Result: `5 passed in 0.58s`

5. Ran Import Window regression tests (includes zero valid-count close prompt):
	- `python -m pytest test/test_import_window_collection_rules.py -q`
	- Result: `6 passed in 0.51s`


