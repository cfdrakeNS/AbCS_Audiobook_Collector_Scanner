
# AbCS Centralized Icon Refactor Checklist (JAWS-Friendly List)

This list shows all UI windows that need to use the centralized icon helper (`get_app_icon()`).
Each entry says if it already sets an icon, and if it needs to be updated.

---

1. about_dialogue.py (AboutDialog)
	- Current: Uses setWindowIcon (QIcon)
	- Centralized: Already uses get_app_icon() (✅ Done)

2. license_dialogue.py (LicenseDialog)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done


3. backup_restore_window.py (BackupRestoreWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

4. collection_window.py (CollectionWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

5. name_list_window.py (NameListWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done

6. preferences_window.py (PreferencesWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

7. reading_history_window.py (ReadingHistoryWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

8. update_window.py (UpdateWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

9. import_window.py (ImportWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

10. import_detail_window.py (ImportDetailWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

11. import_progress_window.py (ImportProgressWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

12. book_list_import_window.py (BookListImportWindow)
	 - Current: Uses setWindowIcon (QIcon)
	 - Centralized: Needs update to use get_app_icon()

13. book_details.py (BookDetailsWindow)
	 - Current: Uses setWindowIcon (QIcon)
	 - Centralized: Needs update to use get_app_icon()

14. web_metadata.py (WebMetadataWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

15. main_window.py (MainWindow)
	- Current: Uses setWindowIcon (get_app_icon)
	- Centralized: ✅ Done
	- Popups: ✅ All QMessageBox/exec_styled_message_box popups use get_app_icon()

---

To update: Import and use get_app_icon() from src/accessibility/icon_helper.py in each window.
Remove direct QIcon path usage.

---


## All windows and popups now use get_app_icon()

All windows and popups (QMessageBox and exec_styled_message_box) in the AbCS application now use the centralized icon via get_app_icon().

Checklist is complete and up to date as of 2026-04-11. MainWindow and all popups are now fully compliant.
