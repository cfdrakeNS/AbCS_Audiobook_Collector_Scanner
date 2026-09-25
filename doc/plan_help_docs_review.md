# Help docs review — Version 3 Phase 16

**Status:** Planned — last version 3 item, after Book Details, Import Detail, Want to read, the full player, and optional view-mode.  
**Created:** September 2026  
**Related:** [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [help_docs_authoring.md](help_docs_authoring.md), [help_docs/01_overview.md](../help_docs/01_overview.md)

---

## What to build

Review in-app help against the windows that exist now. Help topics are discovered from `help_docs/`. Shift+F1 on the main window opens `03_find_filters.md`. The left list speaks each `##` heading, so a heading that starts with “Steps” is extra noise.

### Remove topics 22 and 23

Delete `help_docs/22_web_metadata_title_compare.md` and `help_docs/23_name_consistency.md`. Neither is a shipped window. Remove links from:

- `help_docs/01_overview.md`
- `help_docs/07_web_metadata.md`
- `help_docs/20_import_book_list_explained.md`
- `help_docs/21_web_metadata_explained.md`
- `doc/help_docs_authoring.md` (explained range stays 19–21)
- `doc/Web_Metadata_Title_Compare_Reference.md`
- `doc/Plan_name_consistency_check.md`

Keep the developer title-compare reference. Do not put that material back into user help. Do not document Name Consistency Check.

### Remove “Steps” from section headings

Numbered lists stay. Only the heading text changes.

- `## Steps — Find (search)` becomes `## Find (search)`. Same for the other `## Steps — …` headings in topics 03, 04, 05, and 06.
- A bare `## Steps` (topics 02 and 07–15) becomes a short action title for that guide.
- Update the section example in `help_docs/01_overview.md` and the recommended-section text in `doc/help_docs_authoring.md`.
- Leave the converter test in `test/test_help_router.py` that uses `## Steps` as sample markdown.

### Fill missing user actions

Add only actions a user can do now.

- **Preview on the main window** in `help_docs/03_find_filters.md`: **Edit → Preview**, toolbar **Preview**, **Alt+Shift+P**, plays inside AbCS, unavailable while books are selected. Point to Book Details for Preview window keys. Duplicate mode already documents Preview.
- Confirm these are still accurate, and add a sentence only where they are absent: series number ` - nn` on the main title, name-list merge, Tab skipping the name list, Escape in Find, double-click to edit, collection library root, check for updates.

## Gate

Topics 22 and 23 are gone and nothing in user help links to them. Section names in the help list do not start with “Steps”. Shift+F1 on the main window mentions Preview.
