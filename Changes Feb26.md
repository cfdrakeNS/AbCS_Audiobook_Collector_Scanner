## Changes - 2026-02-26

1. Import Progress Window
- Add elapsed time to the status bar during both phases:
	- Scanning
	- Adding
	- Implemented status format: `Scanning x/x | Elapsed mm:ss` and `Adding x/x | Elapsed mm:ss`

2. Update `AbCS_Guide_(Draft).md`
- Main Window: document keyword/phrase search using `?` prefix.
- Name List Window (Author/Genre/Series/Collections): remove references to `F3` / `Shift+F3` if those shortcuts are not implemented.
- Import Window: remove references to `Valid` in the error filter combo if it is not present.
- Remove references to `JAWS` so wording is neutral for all screen-reader users.
- Verify all listed shortcuts against current implementation.

3. Remove `Audit Display` from Preferences window and shortcut help.
- Remove button and `Alt+U` shortcut from `src/ui/preferences_window.py`.
- Update guide/footer shortcut list to match.
- Add one-command checker script: `test/run_shortcut_checks.bat`.

4. Backup/Restore window
- Make backup selection list match Name List table visual density (single-line rows, no double spacing).
- Align selection/focus visuals with other list/table views.

5. Backup/Restore window
- arrow key not working in list of backups compare table handling with name_list win 
- alt=/ not reading the status bar compare with main window 
- add a delete button and confirm message to delete old backups 
- ✅ Completed:
	- Backup list moved to table-style handling (matching Name List behavior), arrow keys working.
	- `Alt+/` status read aligned and working.
	- Delete button + confirmation implemented, with context-sensitive visibility.

6. import window status bar not updating after scan completes or scan cancelled 
- ✅ Completed:
	- End-of-scan status now updates reliably for both complete and canceled scans.
	- Final scan/cancel message is set after summary refresh so it is not overwritten.

7. name_list window I notice we have a column called books. lets populate that for each of of Author, series, etc. when in the list of items alt+/ change the status message to be .Author's name - books xx, alt-e Edit, alt-c Close
- ✅ Completed:
	- Books column now populates correctly for Author/Genre/Series/Collections.
	- `Alt+/` now reads selected row as: `Name - books xx, Alt+E Edit, Alt+C Close`.

8. import win and progress status are not the same on scan complete scanned counts are different. Change valid to fixed to include aut-correct C: and FallBack Counts 
- ✅ Completed:
	- Import window and Progress window now use the same final scanned count on completion/cancel.
	- Summary label changed from `Valid` to `Fixed`.
	- `Fixed` now counts books with auto-correct (`C:`) and/or fallback (`F:`) outcomes.

9. Update Window
- Series and Genre combos: Series combo is very small; make Series and Genre combo widths the same.
- ✅ Completed:
	- Series and Genre combo widths are now aligned to the same minimum width.
	- Width behavior is scale-aware so both stay matched at different zoom levels.

10. Import Window
- Error filter: Warning should not include Corrected or Fallback items.
- ✅ Completed:
	- Warning filter now excludes rows marked Corrected (`C:`) and Fallback (`F:`).

11. Import window status bar message on scan complete: Change "issues" to "Errors/Warnings" check to make sure "fixed" counter is both Fallback and auto-correct, and  "Errors/Warnings" counter  includes both errors and warning 
- ✅ Completed:
	- Scan-complete status label changed from `Issues` to `Errors/Warnings`.
	- `Fixed` counter includes both fallback (`F:`) and auto-correct (`C:`) outcomes.
	- `Errors/Warnings` counter includes only true errors and true warnings (excludes `F:`/`C:` entries).
- ran test using files in "E:\test mass import books",  s
	- status bar fixed says 6 errors/warning says 6 both are wrong 
	- there are 6 auto-correct and 2 fallback, Fixed=8 
	- no warning or errors
	- ✅ Follow-up fix applied: fixed-only outcomes no longer inflate `Errors/Warnings`.
	- ✅ Regression test updated to validate: 6 auto-correct + 2 fallback => `Fixed: 8`, `Errors: 0`, `Warnings: 0`.
- ran test counters Ok new issues 
	- book that have auto-correct, Fallback or warning stay in the import list for review and can be added by selecting them 
	-   books that have errors or duplicate say in list and can't be added.
	- ✅ Follow-up fix applied: only clean books auto-add during scan.
	- ✅ Auto-correct (`C:`), Fallback (`F:`), and Warning rows stay in review list and remain addable via Add Selected.
	- ✅ Error and Duplicate rows stay in review list and remain non-addable.

12. Main Window focus after Import closes
- On closing Import window, restore focus to Main Window first Title cell in the table.
- ✅ Completed:
	- Main Window now activates and focuses row 1, Title column after Import window closes.
	- Follow-up audit: windows launched from Main Window now restore focus back to Main table Title cell after close.
	- Updated focus return after: Preferences, Statistics, About, and Keyboard Shortcuts dialogs.
	- Initial focus set on opened dialogs for accessibility:
		- Statistics: table (or message text when no books)
		- About: about text
		- Keyboard Shortcuts: shortcuts table

14. Main Window safety guard for large libraries
- Block `Ctrl+A` in Main Window table to prevent accidental select-all on very large datasets.
- ✅ Completed:
	- `Ctrl+A` is now ignored in Main Window table.
	- Status message explains why: disabled to prevent accidental bulk actions.

15. Database bulk operations hardening (root fix)
- Prevent `sqlite3.OperationalError: too many SQL variables` when very large book selections are processed.
- ✅ Completed:
	- `BookQueries.delete_many(...)` now executes in safe chunks.
	- `BookQueries.bulk_update_series(...)` now executes in safe chunks.
	- `BookQueries.bulk_update_genre(...)` now executes in safe chunks.
	- `BookQueries.bulk_update_collection(...)` now executes in safe chunks.
	- Added regression tests: `test/test_book_queries_chunking.py` (2 passing tests).

16. Test stability and validation pass
- Fixed a test/runtime stability issue in status-bar focus restoration when a widget was already deleted.
- ✅ Completed:
	- `accessibility/accessible_events.py` now safely ignores deleted focus targets during delayed focus restore.
	- `test/test_import_window_collection_rules.py` updated to match current close-prompt counting logic.
	- Validation pass complete: 27 targeted tests passed.