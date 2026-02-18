# Main Window
- View menu action updated to **Open Focused Item (Ctrl+Enter/Ctrl+Return)**.
- Added fallback support for Ctrl+Return to keep compatibility.
- Keyboard Shortcuts help dialog now includes context-sensitive behavior for Ctrl+Enter.

# Name List Window (Authors / Genre / Series / Collections)
- Added shared manager window for Author/Genre/Series/Collection.
- Added Find workflow (`Alt+F`, `Enter`, `F3`, `Shift+F3`) and list focus shortcut (`Alt+B`).
- Collections support Active field; Authors are correction-only (New/Delete disabled).

# Collection Window
- Added explicit tab order across header fields, table, and footer buttons.
- Added table event filter so Tab moves focus to New button and Shift+Tab moves focus back to Active checkbox.
- Imported and used QEvent for keyboard focus handling in the table.

# Import Window
- Remove the word "warning" from displayed rule messages.
- Match message prefixes to the Preferences severity setting:
	- Error: prefix message with "E: "
	- Warning: prefix message with "W: "
	- Duplicate: do not add a prefix; show "Duplicate"
- Check whether message prefixing is implemented in multiple places and consolidate into a single shared location if possible.

# General Database
- Review existing indexes and add or adjust indexes as needed for query performance and duplicate detection.





