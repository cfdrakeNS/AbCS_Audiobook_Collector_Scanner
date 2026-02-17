## Feb 17 Action Checklist

## Testing notes (latest pass)
- Retested after latest accessibility/shortcut updates.
- Focus of this pass: Preferences dialog actions, Import window table focus behavior, and Import Detail save/discard behavior.
- Result: most Import Window shortcut/focus issues are now addressed; Import Detail visual blink still needs final verification.

## Testing notes (follow-up pass)
- Additional fixes applied after retest feedback:
	- Import Window inactive table highlight now matches Main Window behavior.
	- Import Detail Discard now attempts in-place navigation (avoid close/reopen flash).
	- Import Window table now supports `Alt+3` Year, `Alt+4` Error Type, `Alt+5` File/Folder.
- Pending: please re-test to confirm visual behavior on your setup.

## General speech
- [x] Serious: JAWS `Insert+T` still reads a window title behind the active sub-window.
	- Example: with Book Detail open, `Insert+T` can read Main Window title.
	- Example: with Import Detail open, `Insert+T` can read Import Window title.
	- Current status: window-handling changes did not resolve this yet.




