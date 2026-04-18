
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
**Goal:** Remove "Review clean books" and "Add Valid" button.
- "Add Valid" button still present. **(NOT STARTED)**
- Valid books not auto-added. **(NOT STARTED)**
- Status bar messaging not updated. **(NOT STARTED)**
- **Testing needed:** Alt+A should add all valid books, no review mode.

## Phase 4: Preferences UI Cleanup
**Goal:** Remove old controls from Preferences window.
- "Options" and "Auto-Correction" group boxes still present. **(NOT STARTED)**
- Window height/layout not updated. **(NOT STARTED)**
- update shortcuts and f1 menu and shortcuts.py 
- **Testing needed:** Preferences window should only show Display and Validation Rules.

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


