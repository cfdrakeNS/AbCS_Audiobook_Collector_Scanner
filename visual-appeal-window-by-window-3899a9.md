# Visual Appeal Window-by-Window Plan

Implement the sighted-user visual appeal improvements one window at a time, testing each window before moving to the next while preserving screen reader accessibility.

## Guiding rules

- **Accessibility first**
  - Keep visible text on all critical buttons.
  - Preserve accessible names and descriptions.
  - Preserve `Alt+/` status reread behavior.
  - Avoid new conflicting `Alt+letter` shortcuts.
  - Keep strong focus indicators.

- **Testing gate after every window**
  - Run syntax checks for edited files.
  - Launch the app when appropriate.
  - Verify keyboard navigation, focus order, status announcements, and high-contrast visibility.
  - Do not start the next window until the current window passes review.

## Step 1: Shared visual helpers

- **Files**
  - `src/accessibility/style_helpers.py`
  - Existing theme support in `src/accessibility/theme_manager.py`

- **What will change**
  - Add reusable helpers for modern accessible buttons, primary buttons, card-style group boxes, table/header polish, and toolbar buttons.
  - Use palette-based colors so existing themes and high contrast remain safe.

- **Test before next step**
  - Compile edited helper file.
  - Confirm no app-wide style regression from helper definitions alone.

## Step 2: Preferences window

- **File**
  - `src/ui/preferences_window.py`

- **What will change**
  - Add short tooltips to display, import, format, fallback, parsing, and validation controls.
  - Fill any missing accessible names/descriptions.
  - Apply card-style group boxes to existing sections.
  - Improve button styling without changing shortcuts or tab order.

- **Window test gate**
  - Open Preferences.
  - Tab through all controls.
  - Verify tooltips are concise for sighted users.
  - Verify screen reader names remain meaningful.
  - Verify high contrast and zoom do not crowd the layout.

## Step 3: Import window

- **File**
  - `src/ui/import_window.py`

- **What will change**
  - Polish the top import action area.
  - Improve Browse, Import, Add Selected, and Export button styling.
  - Add icons only if text remains visible and accessible names stay action-focused.
  - Keep current import table selection, row-header, and JAWS fixes intact.

- **Window test gate**
  - Open Import window.
  - Verify `Alt+/` rereads status.
  - Verify Browse/Import/Add Selected/Export tooltips and accessible names.
  - Verify table navigation and selection highlighting still work.
  - Verify JAWS/NVDA do not get extra row noise from the visual changes.

## Step 4: Main window

- **File**
  - `src/ui/main_window.py`

- **What will change**
  - Polish main action/filter/status areas.
  - Improve table header and selected-row visual clarity.
  - Add a simple labeled toolbar with existing actions:
    - Add Book
    - Import
    - Find
    - Search Web
    - Statistics
    - Preferences
    - Help
  - Reuse existing handlers and shortcuts.
  - Add icons only beside visible text.

- **Window test gate**
  - Launch app to Main window.
  - Verify toolbar buttons are reachable and screen-reader friendly.
  - Verify existing menus and shortcuts still work.
  - Verify table focus, selection, duplicate mode, and export duplicate behavior still work.
  - Verify high contrast and zoom behavior.

## Step 5: Book details window

- **File**
  - `src/ui/book_details.py`

- **What will change**
  - Apply button and group/card styling where safe.
  - Add or refine tooltips for edit fields and action buttons.
  - Keep existing focus and combo-box anti-noise behavior.

- **Window test gate**
  - Open a book.
  - Tab through fields.
  - Save/cancel without shortcut conflicts.
  - Verify screen reader descriptions remain clear.

## Step 6: Book list import window

- **File**
  - `src/ui/book_list_import_window.py`

- **What will change**
  - Apply consistent visual polish to mapping, preview, and import action areas.
  - Add tooltips to import/export/mapping controls.
  - Preserve collection selection and read-date import behavior.

- **Window test gate**
  - Open book list import.
  - Verify mapping controls and import buttons.
  - Verify read-date mode still respects selected collection.
  - Verify status messages remain concise.

## Step 7: Update window and related dialogs

- **Files**
  - `src/ui/update_window.py`
  - `src/ui/import_detail_window.py`
  - `src/ui/reading_history_window.py`

- **What will change**
  - Apply shared styles only where they do not disrupt complex keyboard behavior.
  - Add missing tooltips/accessibility metadata.
  - Keep existing combo-box and Alt-key hygiene patterns.

- **Window test gate**
  - Open each updated dialog.
  - Verify tab order, Escape behavior, and status/help shortcuts.
  - Verify no text-field Alt-key noise.

## Step 8: Smaller management dialogs

- **Files**
  - `src/ui/collection_window.py`
  - `src/ui/name_list_window.py`
  - `src/ui/backup_restore_window.py`
  - `src/ui/statistics_dialog.py`

- **What will change**
  - Apply shared button/card styling where safe.
  - Add simple tooltips for major actions.
  - Avoid adding unnecessary toolbar complexity.

- **Window test gate**
  - Open each dialog.
  - Verify action buttons, focus order, and screen reader names.

## Step 9: Theme review

- **Files**
  - `src/accessibility/theme_manager.py`
  - `src/ui/preferences_window.py`

- **What will change**
  - Review existing theme list before adding new themes.
  - Only add `Modern` or `Classic Accessible` if current choices do not satisfy the visual plan.
  - Keep Default/System and High Contrast behavior safe.

- **Test gate**
  - Check Default, High Contrast Dark, High Contrast Light, and one custom light/dark theme.
  - Confirm buttons, cards, tables, toolbars, and focus indicators remain readable.

## Final verification

- **Syntax checks**
  - Run `python -m py_compile` for every edited Python file.

- **Manual app check**
  - Run `py -m src.main`.
  - Verify the app opens without startup errors.

- **Accessibility review**
  - Verify `Alt+/` in major windows.
  - Verify F1 help remains usable.
  - Verify no global Enter/Return shortcut was introduced.
  - Verify button text remains visible with icons.

- **Commit checkpoint**
  - Commit only after all changed windows pass their individual test gates.
