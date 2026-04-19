
# AbCS Preference Simplification Implementation Plan (April 2026)

## Status Summary
This section gives a factual, JAWS-friendly summary of each phase. Each phase lists what is done, not done, and what needs testing.

---

## Phase 1: Core Logic & Logic Removal


**Goal:** Remove old features and make sanitization always run.
- "Move leading article" logic removed from compare function. **(DONE)**
- "Move leading article" logic fully removed from import and web metadata. **(DONE)**
- "Flip author name" logic fully removed from web metadata. **(DONE)**
- Sanitization (proper case, trim, punctuation, special chars) is now always-on and does NOT depend on preferences. **(DONE)**

**Phase 1 Final Testing Checklist:**
- Importing or fetching metadata for a book with a title like "The Hobbit" should keep the title as "The Hobbit" (not "Hobbit, The").
- No book title should be changed to move "the", "a", or "an" to the end during import or web fetch.
- Author names should never be flipped ("John Smith" stays "John Smith").
- C: errors for title/author issues (whitespace, punctuation, special characters) must always show, even if preferences are off.

**Phase 1 is now COMPLETE.**

**Modules impacted by Phase 1:**
- src/core/validator.py (sanitize_metadata)
- src/core/import_scanner.py (sanitization, article logic)
- src/web/web_book_api.py (article and author logic)
- src/ui/import_window.py (preference handling)
- src/ui/web_metadata.py (preference handling)
- src/ui/book_details.py (preference handling)

## Phase 2: Mandatory Application in UI Windows
BookDetails, ImportDetail, NameList, and Collection windows now sanitize all key fields (**title, author, genre, series, reader, collection**) silently on FocusOut (when leaving the field) and before saving. All legacy normalization code is removed. Fields are always corrected before saving and before any add-new popup. All four windows match logic and are fully updated. UpdateWindow pending.
**Testing complete:** Typing "@+ A       TEST          book       ##@" as title, "&  A      NEW       author    %" as author, or similar for genre/series/reader/collection, stores sanitized values in DB. No status bar message appears for sanitization.


## Phase 3: Import Flow Simplification


**Goal:** Remove all review/valid mode logic and make import always auto-add valid books after scan. No Add Valid button, no valid filter, no valid counter, and no review mode.

**Status: COMPLETE (April 19, 2026)**

**What changed:**
- All review/valid mode logic, valid counters, Add Valid button, valid filter, and auto_add_clean_books preference were removed from import_window.py and import_progress_window.py.
- All references to Add Valid, valid, and review mode were removed from UI, status, and help text.
- The "Valid" option is no longer present in the error filter combo box.
- All valid counters and references are gone from status bar messages, summaries, and progress windows.
- All F1/help text and accessible descriptions were updated to remove Add Valid and review mode references.
- All Alt+V/“Import All Valid” shortcut assignments and help text were removed from shortcuts.py and UI.

**New behavior:**
- After scan, all valid books are added automatically with no extra user action.
- There is no Add Valid button, no valid filter, and no valid counter in any status or summary message.
- Status bar and progress window messages do not mention valid books or review mode.
- Alt+S only adds selected books (if selection is supported).

**Testing:**
- After scan, all valid books are added automatically with no extra user action.
- No Add Valid button, valid filter, or valid counter is present anywhere in the UI or status.
- Status bar and progress window messages do not mention valid books or review mode.

**Accessibility summary:**
- All review/valid mode logic and valid counters are removed for clarity and screen reader simplicity. Import is now always auto-add for valid books. No Add Valid button, valid filter, or valid counter remains. All status, summary, and help text is updated for JAWS/NVDA users.

## Phase 4: Preferences UI Cleanup
**Goal:** Remove all legacy preference controls and options that are no longer used, and simplify the Preferences window to only show Display and Validation Rules.

**Implementation Plan:**
1. Remove the "Options" and "Auto-Correction" group boxes and all related controls from the Preferences window UI and code.
2. Remove all references to preference options that are no longer used (e.g., move leading article, flip author, auto-correct checkboxes, review/valid mode, etc.).
3. Update the Preferences window layout to reduce height and whitespace, making it accessible and visually balanced at all zoom levels.
4. Update all help text, F1 dialogs, and shortcuts.py to reflect the new, simplified Preferences window (only Display and Validation Rules remain).
5. Test: Preferences window should only show Display and Validation Rules sections. No legacy or unused options should be present in the UI or code.

**Testing needed:**
- Preferences window only shows Display and Validation Rules sections.
- No legacy or unused options or group boxes are present.
- F1/help and shortcuts are accurate and up to date.

## Phase 5: Global Validation Audit
**Goal:** Final check of all entry points and shortcuts.
- Entry points not audited. **(NOT STARTED)**
- Alt-letter shortcuts not checked. **(NOT STARTED)**
- **Testing needed:** F1 help must show correct shortcuts.

---

**Summary:**
- Only some code cleanup is done.
- Most logic is still preference-dependent and needs to be made mandatory.
- Most UI and workflow changes are not started.
- Testing is needed after each phase to confirm C: errors always show and sanitization always runs.


