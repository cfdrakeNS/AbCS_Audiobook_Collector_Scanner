# Preferences & Auto-correct Removal Refactor Plan

## Overview
This document outlines the steps to remove the Options and Auto-correct sections from the AbCS preferences, and to eliminate related logic and UI complexity. The goal is to simplify the application by removing low-value, confusing, or redundant features and ensuring consistent data handling.

---

## 1. Remove "Review clean books before adding"
- **UI:**
  - Remove the "add valid" button and any related controls from import and import progress windows.
  - Update status bar messages, F1 help, and `shortcuts.py` to remove references to this feature.
- **Logic:**
  - Remove all code paths that support reviewing/approving "clean" books before adding.
  - Update import logic to add valid books directly, without user review.

## 2. Remove "Flip author name" logic
- **Preferences:**
  - Remove the preference and any UI for flipping author names.
- **Logic:**
  - Remove all code that compares, normalizes, or flips author names (e.g., "Smith, John" <-> "John Smith") in `book_list_import`, `web_metadata`, and related modules.
  - Ensure author names are imported and compared as-is, with no flipping or normalization.

## 3. Remove "Move leading 'the', 'a', 'an' to end of title" logic
- **Preferences:**
  - Remove the preference and any UI for moving leading articles.
- **Logic:**
  - Remove all code that moves leading articles to the end of the title for comparison or normalization in `book_list_import`, `web_metadata`, etc.
  - Ensure titles are imported and compared as-is, with no article movement.

## 4. Remove "Apply Proper Case", "Trim Whitespace", "Trim Leading Punctuation", "Remove Special Characters" preferences
- **Preferences:**
  - Remove these four preferences and their UI.
- **Logic:**
  - Always apply these normalizations before saving to the database, in all relevant modules (`book_list_import`, `web_metadata`, `book_detail`, `import_detail`, `name_list`, `collection`, `update`, etc.).
  - Remove any user option to disable these normalizations.

## 5. Update/Refactor Related Modules
- **Affected modules:**
  - `validator.py`, `import_rules.py`, `import_scanner.py`, and any other modules that reference these preferences or logic.
- **Remove dead code:**
  - Delete any helper functions, tests, or documentation related to the removed features.

---

## Testing & Documentation
- Update F1 help and user documentation to reflect the simplified preferences.
- Test all import, edit, and update flows to ensure data is cleaned as intended and no removed logic is accidentally triggered.
- Verify that all UI elements and status messages referencing these features are gone.
- Document all removed options and logic in the changelog or migration guide.

---

## Practical Steps for Implementation
1. Search for all references to the removed preferences and options in the codebase.
2. Remove related UI elements, menu items, and controls.
3. Refactor or delete logic and helper functions tied to these features.
4. Update tests to remove or adjust cases that depended on the old preferences or logic.
5. Update documentation and help files.
6. Perform regression testing on all import, edit, and update workflows.

---

## Effective Testing Approach
- Use a variety of book imports and edits to confirm that all normalization is applied as intended and that no removed logic is triggered.
- Confirm that the UI is simplified and that no references to the removed preferences remain.
- Validate that status bar messages and F1 help are accurate and up to date.
- Review the changelog to ensure all removals are documented for users and developers.
