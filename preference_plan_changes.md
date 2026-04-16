# AbCS Preference Simplification Implementation Plan

## Phase 1: Core Logic & Logic Removal [COMPLETED]
**Goal:** Remove retired features and create the mandatory sanitization engine.
*   **Task 1.1:** Simplify `normalize_title_for_compare` to remove leading article logic. [DONE]
*   **Task 1.2:** Remove `flip_author_name` method. [DONE]
*   **Task 1.3:** Implement `sanitize_metadata` in `validator.py` to always apply Proper Case and Trimming. [DONE]
*   **Done Check:** `src/core/validator.py` no longer contains flipping/article logic and is ready to clean data.

## Phase 2: Mandatory Application in UI Windows [IN PROGRESS]
**Goal:** Ensure every save point calls the mandatory sanitization.
*   **Task 2.1:** Update `BookDetails.save` and `ImportDetail.save` to call `validator.sanitize_metadata`.
*   **Task 2.2:** Update `NameList`, `Collection`, and `UpdateWindow` save logic.
*   **Done Check:** Manually typing "#title" and saving results in "Title" in the database immediately.

## Phase 3: Import Flow Simplification
**Goal:** Remove "Review clean books" complexity.
*   **Task 3.1:** In `import_window.py`, remove the "Add Valid" button.
*   **Task 3.2:** Redirect all valid (non-error) books to the primary "Add" path.
*   **Task 3.3:** Update status bar messaging.
*   **Done Check:** Alt+A adds all valid books; no "Review" mode is triggered.

## Phase 4: Preferences UI Cleanup
**Goal:** Physically remove the retired controls and adjust layout.
*   **Task 4.1:** Delete "Options" and "Auto-Correction" group boxes from `preferences_window.py`.
*   **Task 4.2:** Recalculate window height to ensure no "dead space" for screen readers.
*   **Done Check:** Preferences window (Alt+M -> P) only shows Display and Validation Rules.

## Phase 5: Global Validation Audit
**Goal:** Final verification.
*   **Task 5.1:** Audit all entry points (Manual New, Edit, Bulk Update).
*   **Task 5.2:** Verify Alt-letter hygiene and shortcut stability.
*   **Done Check:** F1 help shows correct current shortcuts.


Gemini
Responding with 3 Flash Preview
Outlining the Execution
I have read GEMINI.MD and fully understand the requirements for JAWS screen reader accessibility. I will keep my responses clear, structured with descriptive headings, and focused on providing a stable, incremental path forward to avoid further work loss.

Based on the requirements in Preference_changes.md and the need for a testable, phased approach, here is the detailed implementation plan. We will move from core logic (the "Always-On" rules) toward UI removal.

Phased Implementation Plan: Preference Simplification
Phase 1: Mandatory Sanitization (Core Logic)
Goal: Make the "Auto-Correction" rules mandatory so they always apply before a database save, regardless of UI settings.

Task 1.1: Modify the Validator class (in src/core/validator.py) to always apply Proper Case, Trim Whitespace, Trim Leading Punctuation, and Remove Special Characters.
Task 1.2: Ensure the C: (Correction) flag is still generated for Trim Leading Punctuation and Special Characters so the user is notified via the status bar/import list, even though the fix is automatic.
Done Check: Manually adding a book with " test title " or "#Title" results in "Test Title" or "Title" in the database immediately.
Phase 2: Removal of Author and Title Transformation Logic
Goal: Strip out the "Flip Author" and "Leading Articles" logic which are being retired.

Task 2.1: Remove flip_author_name and move_articles_to_end logic from validator.py and import_rules.py.
Task 2.2: Remove the comparison/normalization overrides in book_list_import.py and web_metadata.py that relied on these preferences.
Done Check: Importing "The Great Gatsby" no longer attempts to rename it "Great Gatsby, The" and author names stay in the format provided by the tag/file.
Phase 3: Import Flow Simplification
Goal: Remove the "Review clean books" complexity.

Task 3.1: In import_window.py, remove the "Add Valid" button.
Task 3.2: Simplify the import logic so that all books without "Errors" are processed as a single group.
Task 3.3: Update status bar messaging to reflect that valid books are added directly.
Done Check: Pressing "Add" (Alt+A) adds all valid books; no "Review" mode is triggered.
Phase 4: Preferences UI Cleanup
Goal: Physically remove the retired controls and adjust the window layout.

Task 4.1: Delete the Options and Auto-Correction group boxes from preferences_window.py.
Task 4.2: Remove the corresponding variables from the Settings management logic and the database initialization (if applicable).
Task 4.3: Adjust the Tab Order and Geometry: Since sections are removed, the window height should be recalculated to ensure no "dead space" for JAWS to navigate through.
Done Check: The Preferences window (Alt+M -> P) shows only Display and Validation Rules; the retired sections are gone.
Phase 5: Global Validation Audit
Goal: Ensure all entry points (Manual New, Edit, Bulk Update) utilize the mandatory rules from Phase 1.

Task 5.1: Audit book_detail.py, import_detail.py, name_list.py, collection_window.py, and update_window.py.
Task 5.2: Verify that clicking "Save" (Alt+S) in any of these windows triggers the global sanitization before the queries.py insert/update methods are called.
Done Check: Saving an author name in the NameListWindow with trailing spaces results in a trimmed name in the database.
How would you like to start? I recommend starting with Phase 1, as it ensures data integrity before we start removing the UI checkboxes that currently control those features.