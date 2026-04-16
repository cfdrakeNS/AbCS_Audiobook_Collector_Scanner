build a plan to remove from preferences the Options and Auto-correct section and there option. refactor the code as required. crate a doc outlining the changes and a practical approach to change to permit effective testing.

# Preferences Options & Auto-correct Removal: Logical Implementation & Testing Plan

This plan outlines the step-by-step order for removing the Options and Auto-correct preferences, refactoring related code, and ensuring all changes are testable and verifiable.

---

## Step 1: Remove UI and Shortcut References

**1.1. Remove "Options" and "Auto-correct" sections from Preferences Window**
	- Update `preferences_window.py` to remove these sections (UI and logic)
	- Remove related shortcut registrations in `shortcuts.py` and any handler code
	- Test: Preferences window displays correctly, no extra vertical space, no references in F1 help or status bar

**1.2. Remove "Add valid" button and logic**
	- Update preferences, import, and import progress windows to remove this button and related logic
	- Update status bar messages, F1 help, and shortcuts.py for new logic
	- Test: No "Add valid" button, status bar and help reflect new workflow

---

## Step 2: Remove Obsolete Normalization Logic

**2.1. Remove "Flip author name" logic**
	- Remove all code for flipping author names in `book_list_import`, `web_metadata`, and related modules
	- Remove any normalization/comparison logic for author flipping
	- Test: Author names are not flipped anywhere, import and search work as expected

**2.2. Remove all article-moving logic for titles**
	- Remove all code that moves leading articles ("the", "a", "an") to the end or beginning of titles before comparison or normalization
	- Specifically update:
		- `_normalize_title_for_match` and related logic in `book_list_import_window.py`
		- `_move_article_to_beginning`, `_move_article_to_end`, and related logic in `web_book_api.py`
	- Ensure no normalization or search code moves articles in any direction
	- Test: Titles are not altered for leading articles, import and search work as expected

**2.3. Preserve series number processing**
	- Ensure all series and series number extraction, mapping, and appending logic remains intact
	- Do not remove or alter any code related to series number handling in these modules
	- Test: Series number is still correctly processed and displayed after article logic is removed

---

## Step 3: Refactor Auto-correct to Always Apply

**3.1. Remove preferences for:**
	- Apply Proper Case
	- Trim Whitespace
	- Trim Leading Punctuation
	- Remove Special Characters

**3.2. Refactor so these corrections are always applied before saving to DB**
	- Update all relevant modules: `book_list_import`, `web_metadata`, `book_detail`, `import_detail`, `name_list`, `collection`, `update`, `import_scanner`, `queries`
	- Maintain flagging for "Trim Leading Punctuation" and "Remove Special Characters" in import window as required
	- Test: All corrections are always applied, no user preference toggles, import window still flags as needed

---

## Step 4: Clean Up and Finalize

**4.1. Remove all references in:**
	- `validator.py`, `import_rules.py`, `import_scanner.py`, and any other modules referencing removed preferences
	- Test: No code or UI references to removed preferences or options

**4.2. Final regression test:**
	- Test all import, edit, and update workflows for correct normalization and no missing features
	- Verify accessibility (shortcuts, status bar, F1 help) is correct and up to date

---

## Testing Approach

1. After each step, run the application and verify the UI and logic changes in the affected windows/modules.
2. Use sample imports and edits to confirm normalization and auto-correct are always applied.
3. Use screen reader and keyboard navigation to verify accessibility is not impacted.
4. Document any issues or regressions for follow-up.

---

**By following this order, each change can be tested in isolation before moving to the next, ensuring a smooth and verifiable transition.**
 