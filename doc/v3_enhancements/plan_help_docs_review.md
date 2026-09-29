# Help docs review — Version 3 Phase 16

**Status:** Complete — September 28, 2026. Book Details, Import Detail, Want to read, the full player, Check Books Path, and Export Library are in place.  
**Created:** September 2026  
**Related:** [plan_enhancements_version3_release.md](../plan_enhancements_version3_release.md), [help_docs_authoring.md](../help_docs_authoring.md), [help_docs/01_overview.md](../../help_docs/01_overview.md)

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

- **Listen on the main window** in `help_docs/03_find_filters.md`: **Edit → Listen**, toolbar **Listen**, **Ctrl+L**, plays inside AbCS, unavailable while books are selected. Point to Book Details for Listen window keys. Duplicate mode already documents Listen.
- **Phase 29 keys:** after Phase 29 ships, check every topic against [plan_standard_shortcuts.md](plan_standard_shortcuts.md): Book Details Edit (Alt+E), Narrator (Alt+N), Read date (Alt+R), Series (Alt+S), Save Ctrl+S, New Ctrl+N; name list Ctrl+F and Ctrl+S; Ctrl+S in Preferences, Collection, Import Detail, Web Metadata; no Import on the toolbar.
- Confirm these are still accurate, and add a sentence only where they are absent: series number ` - nn` on the main title, name-list merge, Tab on the name list, Escape in Find, Ctrl chords on the list during find, **Copy** (Ctrl+C / right-click) on the main book list and name list, double-click to edit, collection library root, check for updates.

### Export Library (Phase 27)

Topic `help_docs/25_export_library.md` shipped with Phase 27 and is listed in `help_docs/01_overview.md`. Export Library has no window of its own: it is a File menu item that opens the system save dialog. There is no Shift+F1 routing and no `WINDOW_HELP_MAP` entry.

- Check topic 25 against the shipped behavior: **File → Export Library** (**Alt+F**, then **X**), exports the main list as shown (filters, search, sort), exports only the selection when books are selected, unavailable in duplicate mode, CSV or JSON, suggested name `abcs_library_` plus date and time in Documents, spoken count, focus back on the book list. Update it for anything changed by the JAWS smoke.
- Topic 25 already uses `## How to export`, not a “Steps” heading. Keep it that way.
- Main window help, `help_docs/03_find_filters.md`: add one sentence that the current filtered list can be saved with **File → Export Library**, with a link to topic 25.
- `help_docs/16_shortcuts.md`: add **Alt+F, X — Export Library** where the main window menu shortcuts are listed. If that file has no menu-shortcut list, add it to the main window section.
- Add a link to topic 25 under Related documentation in `help_docs/09_backup_restore.md` (export is not a backup) and `help_docs/11_import_book_list.md` (an export can be re-imported).
- In `help_docs/08_duplicate_mode.md`, keep **Export Duplicates** (**Alt+X**) separate from Export Library. Add one sentence only if users could confuse the two.

### Rename Preview / Play → Listen

User-facing name for the in-app audiobook player is **Listen** (not Preview or Play), shortcut **Ctrl+L** (Phase 29; Alt+Shift+P removed). Topics 01, 04, 07, 08, 16, and 24 were updated on Sept 27, 2026. When reviewing help, use **Edit → Listen**, toolbar **Listen**, **Listen** window, and **Listen** in shortcut tables. The Play / Pause transport button inside the Listen window keeps its name. Keep internal module names (`preview_window.py`) as they are. Do not confuse with Preferences theme/zoom “preview immediately.”

## Gate

Topics 22 and 23 are gone and nothing in user help links to them. Section names in the help list do not start with “Steps”. Shift+F1 on the main window mentions Listen. Help uses **Listen** (not Preview or Play) for opening the audiobook player, and no topic mentions Alt+Shift+P. Topic 25 Export Library matches the shipped menu item. Main window help, the shortcuts topic, Backup and Restore, and Import Book List link to it.
