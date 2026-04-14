copilot plan to remove flip and article processing 
# Remove_flip_article Plan

## 1. Overview
Remove all code, settings, and UI related to "flip author" and "move article to end" (article handling in titles) from the AbCS project. Organized by window/module for clarity and review.

## 2. MainWindow (src/ui/main_window.py)
- Remove menu items, buttons, shortcuts, and logic for flip/move features
- Remove related status/help text
- Test: Menus/toolbars/shortcuts/status bar/help dialogs

## 3. BookDetailsWindow (src/ui/book_details.py)
- Remove flip/move controls and logic
- Remove help/tooltips
- Test: No controls/help, save/edit works

## 4. Import/Tag Reader (src/core/tag_reader.py, src/core/validator.py, ImportWindow)
- Remove flip/move logic and settings
- Remove related import error messages/options
- Test: Import with articles/commas, check logs

## 5. Preferences/Settings (src/accessibility/..., Preferences Dialog)
- Remove QSettings/config for flip/move
- Remove UI controls in Preferences
- Test: Preferences UI/settings file

## 6. Database Layer (src/database/queries.py, src/database/models.py, migrations)
- Remove fields/queries/scripts for flip/move
- Test: Schema, queries

## 7. Accessibility/Shortcuts (src/accessibility/shortcuts.py, help dialogs)
- Remove flip/move shortcuts/help
- Test: Shortcuts/help dialogs

## 8. Tests & Verification (test/, manual QA)
- Remove flip/move tests/data
- Test: All tests/regression

## 9. Documentation (README.md, guides, help)
- Remove all flip/move references
- Test: Search docs

## 10. Order of Operations
1. Remove UI
2. Remove backend logic
3. Remove settings
4. Remove tests/docs
5. Verify with QA/tests

## 11. Affected Files/Modules
- main_window.py
- book_details.py
- tag_reader.py
- validator.py
- queries.py
- models.py
- shortcuts.py
- Preferences dialog (planned)
- ImportWindow, ImportDetailWindow (planned)
- test/
- README.md, guides, help

## 12. Final Review
- Search for "flip author", "move article", etc. to confirm removal
- Run full regression and manual QA

---

You can now save this as Remove_flip_article.md in your project for future reference or editing. Let me know if you want any changes or a more detailed breakdown!