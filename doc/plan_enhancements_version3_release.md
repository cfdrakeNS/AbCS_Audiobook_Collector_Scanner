# Version 3 Release Enhancements — Master Roadmap

**Status:** Active schedule (scoped from tester review, September 2026)  
**Created:** June 2026  
**Updated:** September 2026  

**Tester build:** **2.22** — Phases 1–4 and 6–13 complete (Phases 1–4 and 6–12 tester accepted; Phase 13 name-list merge implemented in 2.18). Preview plays inside AbCS. Series number is display-only ` - nn` on the main table. Book Details save, Book List Import, and Series From File Name confirmed. Startup update check confirmed. Date Read and Added since calendars show days 10–31. Phase 15 Preview cover and Phase 17 Book Details cover are implemented. Phases 19, 18, and 20 are tester accepted. Phase 22 Import Detail layout is complete. Phase 21 full Play player is implemented. Phase 23 Statistics Want to Read / In Progress is complete. Phase 24 Book Details path browse is complete. Phase 25 Path health (Check Books Path) is complete. Phase 26 Check Books Path progress is complete. Phase 27 Export library metadata is implemented (File → Export Library; awaiting JAWS smoke). Phase 28 iTunes technical tags in Comments is implemented (import fix and one-time script; awaiting tester check). Phase 31 plot fetch improvements are implemented; awaiting JAWS/NVDA review. **Next:** Phase 16 help last. Non-modal fetch, ratings, tags, web cover files, and view-mode announcements (former Phase 14) stay out of v3. Library-wide fuzzy name scan deferred after v3. See [release_notes_2.19.md](release_notes_2.19.md).

**Purpose:** Single schedule for version 3 work — order, combinations, test gates, and deferrals. Individual plans hold **what** to build; this document holds **when**.

**Related:** [plans_status.md](plans_status.md), [TESTING.md](../TESTING.md), [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md), [AbCS_Version3_Release_Tester_Review.xlsx](AbCS_Version3_Release_Tester_Review.xlsx) (tester source of truth — do not overwrite filled answers)

Completed phase detail plans are in [v3_enhancements](v3_enhancements/); this master roadmap and unfinished/pending plans remain in `doc/`.

**Branch:** work from `main` (or a short-lived phase branch per feature)

---

## Version 3 scope (from tester review)

Tester-selected items plus Phase 2 follow-ons (leading-article compare; selection-mode toolbar), keep-current-book, C01 schema, F10 series number, C07 collection root (Part A), audiobook preview (in-app player), Preview embedded cover (Phase 15), a help-doc review (Phase 16), Want to read, listening progress, the full player, F08 Statistics (Want to Read and listening progress only), Book Details path browse, F01 Path health report, and Export library metadata (Phase 27). **Out of scope for v3 (deferred):** non-modal web fetch jobs (too risky), book ratings, tags, web cover files and zip backup, and the combined Want to read and playing filter (separate filters already ship). Everything else stays planned but **deferred after v3**.

| Phase | ID | Enhancement | Detail doc | Est. | Depends on |
|-------|----|-------------|------------|------|------------|
| 1 | F13 | Web fetch background thread + API split | [plan_web_fetch_background_thread.md](v3_enhancements/plan_web_fetch_background_thread.md) | 3–5 d | — |
| 2 | F12 | Batch web metadata fetch | [plan_bulk_web_metadata.md](v3_enhancements/plan_bulk_web_metadata.md) | 1–2 wk | Phase 1 |
| 3 | — | Leading article title compare (Path B) | [plan_leading_article_title_compare.md](v3_enhancements/plan_leading_article_title_compare.md) | 0.5–1 d | Phase 1 matching |
| 4 | — | Selection mode: block toolbar and shortcuts | [plan_selection_mode_toolbar.md](v3_enhancements/plan_selection_mode_toolbar.md) | 1–2 d | — |
| 6 | F17 | Import tag mapping (title / author) | [plan_import_tag_mapping.md](v3_enhancements/plan_import_tag_mapping.md) | 2–3 d | — |
| 7 | B05 | Check for updates | [plan_auto_update.md](v3_enhancements/plan_auto_update.md) | 2–3 d | — |
| 8 | — | Keep current book on sort and filter | [plan_keep_book_focus.md](v3_enhancements/plan_keep_book_focus.md) | 0.5–1 d | — |
| 9 | C01 | Schema batch (in-place upgrade) | [plan_schema_batch.md](v3_enhancements/plan_schema_batch.md) | 2–3 d | — |
| 10 | F10 | Series book number | [plan_series_number_db.md](v3_enhancements/plan_series_number_db.md) | 2–3 d | Phase 9 |
| 11 | C07 | Collection library root folder | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part A | 2–3 d | Adds `root_path` |
| 12 | C03 | Preview audiobook (in-app player) | [plan_audiobook_preview.md](v3_enhancements/plan_audiobook_preview.md) | 1–2 d | — |
| 13 | C09 | Name-list merge on duplicate | [Plan_name_consistency_check.md](v3_enhancements/Plan_name_consistency_check.md) | 1–2 d | — |
| 15 | — | Preview cover (embedded art) | [plan_preview_cover.md](v3_enhancements/plan_preview_cover.md) | 0.5–1 d | Phase 12 |
| 17 | — | Book Details cover (embedded art) | [plan_book_details_cover.md](v3_enhancements/plan_book_details_cover.md) | 0.5 d | Phase 15 |
| 19 | — | Want to read and listening progress columns | [plan_want_to_read.md](v3_enhancements/plan_want_to_read.md), [plan_reading_progress.md](v3_enhancements/plan_reading_progress.md) | 0.5–1 d | — |
| 18 | — | Book Details layout, cover on the right | [plan_book_details_layout.md](v3_enhancements/plan_book_details_layout.md) | 1 d | Phase 19 |
| 20 | — | Want to read | [plan_want_to_read.md](v3_enhancements/plan_want_to_read.md) | 2–3 d | Phase 18 |
| 22 | — | Import Detail layout, no cover | [plan_import_detail_layout.md](v3_enhancements/plan_import_detail_layout.md) | 1 d | Phase 18 |
| 21 | — | Full Play player | [plan_preview_player_later.md](v3_enhancements/plan_preview_player_later.md) | 3–5 d | Phase 19 |
| 23 | F08 | Statistics: Want to Read and listening progress | [plan_statistics_extensions.md](v3_enhancements/plan_statistics_extensions.md) | 0.5–1 d | Phase 20, Phase 21 |
| 24 | — | Book Details path browse | [plan_book_details_path_browse.md](v3_enhancements/plan_book_details_path_browse.md) | 0.5 d | — |
| 25 | F01 | Path health report (Check Books Path) | [plan_path_health_report.md](v3_enhancements/plan_path_health_report.md) | 1–2 d | Phase 24 |
| 26 | — | Check Books Path progress | [plan_check_books_path_progress.md](v3_enhancements/plan_check_books_path_progress.md) | 0.5–1 d | Phase 25 |
| 27 | — | Export library metadata (CSV / JSON) | [plan_export_library_metadata.md](plan_export_library_metadata.md) | ~2 d | Phase 19 columns |
| 28 | — | iTunes technical tags in Comments (import fix + one-time script) | [plan_itunes_comment_cleanup.md](plan_itunes_comment_cleanup.md) | 1 d | Found in Phase 27 |
| 29 | — | Standard shortcuts (tester feedback: Edit, Ctrl+S, Ctrl+F, Narrator, Listen Ctrl+L) | [plan_standard_shortcuts.md](v3_enhancements/plan_standard_shortcuts.md) | 1–2 d | — |
| 30 | — | Sept 27 tester feedback (import/export, dialogs, zoom) | [plan_sept27_tester_feedback.md](v3_enhancements/plan_sept27_tester_feedback.md) | 3–5 d | Phase 29 |
| 31 | — | Plot fetch quality, performance, and source compliance | [plan_plot_fetch_improvements.md](plan_plot_fetch_improvements.md) | 5 batches | Phase 2 and Phase 30 |
| 16 | — | Help docs review | [plan_help_docs_review.md](v3_enhancements/plan_help_docs_review.md) | 1 d | Phases 18–30 |

**To do in version 3 (not the next build item):** On the first start, if a screen reader is running, set Zoom to Normal, then speak once: "Screen reader detected. Text size is set to Normal. To choose a different size, open Preferences, then Theme and Zoom." Do not repeat it on later starts. Do not reset Zoom if they have already changed it.

**Phase numbers 1–4 and 6–13 are complete** (1–4 and 6–12 tester accepted; Phase 13 implemented in 2.18). There is no Phase 5 in v3 — non-modal fetch was removed as too risky; see deferred. There is no Phase 14 in v3 — view-mode announcements are out of scope; see deferred. **Phase 15 (Preview cover), Phase 17 (Book Details cover), Phase 19 (book columns), Phase 18 (Book Details layout), Phase 20 (Want to read), Phase 22 (Import Detail layout), and Phase 21 (full Play player) are done** (18–20 tester accepted). **Phase 27 (Export library metadata), Phase 28 (iTunes technical tags in Comments), Phase 29 (standard shortcuts), Phase 30 (Sept 27 tester feedback, batches A–E), and Phase 16 (help docs review) are complete (tester accepted where applicable).** Phase 31 plot fetch quality, performance, and source compliance is implemented in 2.22 and awaits JAWS/NVDA review. Do not start the next phase until the current gate passes. Phase 9 adds `series_number` only. Ratings, tags, and web cover files are out of v3. Collection `root_path` is added in Phase 11. **Phase 23 F08 (Statistics Want to Read and In Progress) is done. Phase 24 (Book Details path browse) is done. Phase 25 F01 (Check Books Path) is done. Phase 26 (Check Books Path progress) is done.** Combined Want to read and playing filter dropped — separate filters already ship.

**Not in v3:** Non-modal web fetch (keep using the app during a fetch), book ratings, tags, web cover files and zip backup, rescan (Part B), organize-on-disk (Part C), i18n, and remaining follow-on/backlog rows. Web fetch progress stays a blocking dialog. Collection root **Part A** is in v3; Parts B and C stay deferred. Want to read on Import Detail and Update-window extensions stay deferred.

---

## Phase details

### Phase 1 — Background web fetch (3–5 days)

See [plan_web_fetch_background_thread.md](v3_enhancements/plan_web_fetch_background_thread.md). **Complete — tester accepted Alt+W after the split.** Google Books 429 during library testing is source cooldown (`web_source_cooldowns.json`), not a Phase 1 regression.

1. Throwaway JAWS spike — **done** (tester accepted).
2. Move fetch onto `QThread`; keep `fetch_web_metadata_for_book` blocking via `exec()` — **done** (tester accepted; Escape-only wait dialog).
3. Split `web_book_api.py` after the thread — **done** (`web_http`, `web_matching`, `web_cache` + facade). Per-source fetch and plot enrich stay on `WebBookAPI`.

**Gate:** Tester re-confirms Alt+W after the split (progress spoken, Escape cancel, no crash). Web tests green (81). UI updates only via GUI-thread bridge ([Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases)).

### Phase 2 — Batch web fetch (1–2 weeks)

See [plan_bulk_web_metadata.md](v3_enhancements/plan_bulk_web_metadata.md). **Complete — tester accepted**, then follow-up polish (below). Progress stays modal for v3. Non-modal jobs are out of scope and will not change that.

Multi-select starts from **Alt+W**, toolbar **Search Web**, or footer **Web fetch**. There is no main-window Alt+B. N/M progress; summary with Apply all / Review. Escape closes the summary.

Follow-up after accept:

- Issue column: **Plot found**, **Metadata found**, **Plot and metadata up to date.**, **No match found**, or **Match found. No plot was found.** Title and Issue both stretch. The summary opens wider so the Issue text is visible.
- Batch progress opens about one third wider and keeps that width. Long titles wrap. The bar is thicker and uses the highlight color.
- After a Google Books limit, later books in that batch are not sent to Google. Those rows still say **No match found**. The summary at the top says **Google Books limit hit. Try in N minutes.**
- Enter in the summary list does nothing. Apply all and Review are not default buttons.
- Review hides the summary. Save or Skip returns to the summary without re-speaking the queue status.
- With a screen reader, summary status is **Alt+A Apply all**, **Alt+R Review** (or Review each), and Escape. Without a screen reader, the status is the count line.
- Web metadata F1 does not list Series or Series #.

**Gate:** Summary usable with JAWS; Apply all and Review work; Alt+W is one book or the selection; footer **Web fetch** uses shared button style and shows at two or more selected.

### Phase 3 — Leading article title compare (0.5–1 day)

See [plan_leading_article_title_compare.md](v3_enhancements/plan_leading_article_title_compare.md). **Complete.**

Path B: same-work match for optional leading A/An/The; review still **offers** the web title when the catalog includes the article. Trailing-article and series-suffix behavior from 2.14 stays.

**Gate:** Same-work match for leading article; web title still offered to save; real subtitle still differs; Alt+W and batch Review unchanged otherwise.

### Phase 4 — Selection mode toolbar and shortcuts (1–2 days)

See [plan_selection_mode_toolbar.md](v3_enhancements/plan_selection_mode_toolbar.md). **Complete.**

While selection is active, disable Add/Import/Find/Statistics/Preferences/filters. Intercept those shortcuts; announce Escape. **Alt+W**, Search Web, and footer Web fetch stay available; two or more selected run **batch** fetch. Keep Update/Delete, F1, Alt+/, Alt+L. F1 during selection lists only shortcuts that still work. Shift+Up/Down **speaks** the selection status (`announce=True`). Do not clear-and-run.

**Gate:** Blocked actions do not run; Alt+W with 2+ selected is batch; status speech is requested on selection (not only stored); Escape restores toolbar; duplicate mode unchanged.

### Phase 6 — Import tag mapping (2–3 days)

See [plan_import_tag_mapping.md](v3_enhancements/plan_import_tag_mapping.md). **Complete — tester accepted.**

Preferences Import Settings has **Tag mapping**: Book title (Album / Track title / Album then track title) and Author (Album artist then artist / Album artist only / Artist only). Defaults match the previous scan. Grouping stays on the album tag. Empty or placeholder tags still use the Fallback tab.

**Gate:** Defaults match today’s scan; grouping stays on album; prefs round-trip; new combos match Preferences accessible combo + anti-noise patterns.

### Phase 7 — Check for updates (2–3 days)

See [plan_auto_update.md](v3_enhancements/plan_auto_update.md). **Complete — tester accepted.**

Help → Check for updates reads the latest GitHub release tag and compares it to `APP_VERSION`. **Testing only:** Help → Website and Open website open `https://abcstest.carrd.co/`. Before merging to main, set `ABCS_UPDATE_DOWNLOAD_URL` back to the live site `https://abcs.auroraaccessibility.com/`. The check does not install anything. Enter activates the focused button.

**Gate:** Help → Check for updates compares GitHub latest to `APP_VERSION`; offline failure is announced; result dialog uses AccessibleDialog + styled buttons with default focus.

### Phase 8 — Keep current book on sort and filter (0.5–1 day)

See [plan_keep_book_focus.md](v3_enhancements/plan_keep_book_focus.md). **Complete — tester accepted.**

Sort (menu or header) keeps the focused book as the current row. Filters do the same when that book is still in the list. If a filter drops it, focus moves to the first remaining book.

**Gate:** JAWS: arrow to a middle book, sort by author, still that title. Unread while unread stays. Read while unread moves to the first remaining book.

### Phase 9 — C01 Schema batch (2–3 days)

See [plan_schema_batch.md](v3_enhancements/plan_schema_batch.md). **Complete — tester accepted.** The upgrade dialog was heard.

In-place `ALTER TABLE` on **first start** for existing libraries (not only new installs). Adds `series_number` on `books` only. Does not add `want_to_read`, `rating`, `ratings_count`, `cover_path`, or `collections.root_path`. No new buttons in this phase. Timestamped `schema_repair` backup before change. Announce the upgrade for dev and installed builds. Existing titles are not rewritten.

The column is used by series number (Phase 10). Collection root adds `root_path` in Phase 11. Want to Read, ratings, and covers are not part of this upgrade.

**Gate:** Old database opens with books intact; new columns present; upgrade announced once.

### Phase 10 — F10 Series book number (2–3 days)

See [plan_series_number_db.md](v3_enhancements/plan_series_number_db.md). **Complete — tester accepted** display-only title suffix, Book Details save, Book List Import, and Series From File Name in tester build 2.17. Needs Phase 9.

The only series-number field is on **Book Details**, a text box to the right of Series. Saving stores Series # and leaves the title as it is. The main-window Title column shows ` - 03` or ` - 6.5` from that column. Opening a book does not copy a title suffix into Series #. A one-time script fills a blank Series # from a title suffix. The main-window **Series** sort is series name, then series number, then year, then title. Book List Import and Series From File Name store Series # and leave the title clean. No series-number column on the main table. Not on Import Detail, web fetch, or the bulk Update window.

**Gate:** Save/load from Book Details; showing a book with a blank Series # and a title suffix leaves Series # blank and leaves the title unchanged; saving after Series # is added or changed leaves the title unchanged; the Title column shows ` - nn`; Series sort is series, series number, year, then title; JAWS reads the text box to the right of Series.

### Phase 11 — C07 Collection library root folder (2–3 days)

See [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) **Part A only**. **Complete — tester accepted.** This phase adds `collections.root_path` on first start for existing libraries, using the same upgrade path as Phase 9.

Allow setting and changing the optional root folder for a collection (example: `F:\audiobook`). Edit in Collection Manager. When the user selects or browses a collection folder, **warn** if that folder does not exist, or if it contains no recognized audiobook files (extensions from `TagReader.SUPPORTED_EXTENSIONS`). Import may pre-fill from `root_path` when present. Changing the root does not rewrite `books.path`. If there is only one collection, an empty library root and an empty Preferences import folder fill from each other. Rescan (Part B) and organize-on-disk (Part C) stay deferred.

**Gate:** Save/load `root_path`; warn on missing folder; warn when folder has no supported audio; Import pre-fill when root is set and exists.

### Phase 12 — C03 Preview audiobook (1–2 days)

See [plan_audiobook_preview.md](v3_enhancements/plan_audiobook_preview.md). **Complete — tester accepted** in tester build 2.18.

**Preview** button on Book Details, plus a main-window **Edit** menu item (same menu as Fetch Web Info). Plays the book **inside AbCS** (Play/Pause, title, author, length). Book Details has no menu bar today; menu entry is on the main window. Shortcut was **Alt+Shift+P**; Phase 29 renamed the opener to **Listen** with **Ctrl+L** and removed Alt+Shift+P. Enter plays or pauses. Escape closes and stops. Preview is blocked in selection mode. Closing Preview from the main window returns focus to the book table. When the collection has a library root, Preview remaps the stored path onto that folder. Shift+F1 follows the window that opened Preview.

**Gate:** Preview plays inside AbCS; missing path announced; JAWS can activate Preview from button and Edit menu; focus stays in AbCS.

### Phase 13 — Name-list merge on duplicate (1–2 days)

See [Plan_name_consistency_check.md](v3_enhancements/Plan_name_consistency_check.md). **Complete — implemented in tester build 2.18.**

When Save in the Name List hits an existing author, series, or genre name, ask Yes/No (default No). Yes moves books onto the existing name and deletes the edited name. Collections keep the warning only. Library-wide fuzzy scan is deferred after v3. Tab stops on the list; Escape in Find returns to the list; Ctrl chords stay on the list during find. **Ctrl+C** / right-click **Copy** copies the selected name (same Copy on the main book list for the focused cell).

**Gate:** Yes reassigns books and removes the source name; No changes nothing; same-row case change does not ask; JAWS hears the question and the result sentence.

**Follow-up bug fix (tester):** After Find, Ctrl no longer steals focus to Find (Ctrl+C works on the list). Tab stops on the list. See [Plan_name_consistency_check.md](v3_enhancements/Plan_name_consistency_check.md).

### Phase 15 — Preview cover (0.5–1 day)

See [plan_preview_cover.md](v3_enhancements/plan_preview_cover.md). **Implemented.** Show embedded art from the file Preview is playing. No database column. Not the deferred web-cover plan.

**Gate:** Art shows and is not in the tab order; no art means no extra announcement; Play/Pause keeps focus.

### Phase 17 — Book Details cover (0.5 day)

See [plan_book_details_cover.md](v3_enhancements/plan_book_details_cover.md). **Implemented.** Show the same embedded art as Preview at the top of Book Details. No database column. The picture stays outside the header card that is hidden for screen readers.

**Gate:** Art shows and is not in the tab order; no art means no extra announcement; the title field keeps focus.

### Phase 19 — Want to read and listening progress columns (0.5–1 day)

**Tester accepted.** Add three columns on `books` with the same in-place upgrade as `series_number`. One upgrade announcement. Do not add rating, tag, or cover columns. Names: `want_to_read`, `listen_position_ms`, `listen_file_name`.

- `want_to_read` integer, default 0
- listening position in milliseconds, empty when the book has not been started
- listening file name, empty unless the book is a folder of tracks

These columns are the only store for listen progress. The player and Book Details use the same values. A percent is not its own column.

**Gate:** An old library opens with its books intact. The three columns exist. A second start does not announce the upgrade again.

### Phase 18 — Book Details layout (1 day)

**Tester accepted.** See [plan_book_details_layout.md](v3_enhancements/plan_book_details_layout.md) and [book_details_layout.png](book_details_layout.png). Cover on the right, and it is a tab stop: Book cover or No cover. A missing cover shows `graphics/no_book_cover_512x512.png`. Read date and Want to read save without Update. A read date clears Want to read. Files, Format, Bitrate, and Size have no shortcut. Want to read is Alt+K.

**Gate:** Passed.

**Follow-up bug fix (testing miss):** Date and year validation across Book Details, main read-date popup, Reading History, and Import Detail Year — see [fix_read_date.md](fix_read_date.md). Alt+Up/Down on `QDateEdit` abandoned; screen readers use typed fields. Classic calendars use single-letter day names and scale with UI zoom. Not promoted to AGENTS/standards yet — wait for a broader review.

**Follow-up performance fix:** Book Details now performs one lightweight audiobook-source lookup and one cached cover read during an ordinary open instead of repeated full playlist scans and metadata sorts. See [plan_book_details_open_performance.md](v3_enhancements/plan_book_details_open_performance.md).

### Phase 20 — Want to read (2–3 days)

**Tester accepted.** See [plan_want_to_read.md](v3_enhancements/plan_want_to_read.md). The Book Details checkbox saves without Update, and a read date clears Want to read. The main list filters to Want to read (View → Want to read, or Alt+T). Edit → Add to want to read marks the focused book or the selection and saves immediately. With books selected, the footer and Edit → Clear want to read clear the mark for that selection. Import Detail stays deferred.

**Gate:** Passed. The checkbox saves. A read date clears it. The main-list filter shows only marked books and does not delete the marks when cleared.

### Phase 22 — Import Detail layout (1 day)

**Complete.** See [plan_import_detail_layout.md](v3_enhancements/plan_import_detail_layout.md). Same column arrangement as Book Details. No cover. No Want to read and no Listen progress. **Keep** (Alt+K) adds an OK/Warning book and advances; **Discard** (Alt+D) removes and advances; both announce on the status bar. Duplicates may open for edit/Save but not Keep. Unreadable-file rows do not open detail. Status bar sits above the buttons (text-field look). No Alt for Files, Format, Bitrate, or Size. Errors stays under Path.

**Gate:** Passed. Columns line up with Book Details. No picture. Tab and Alt+letter still reach the same fields. Keep/Discard speak status.

### Phase 21 — Full Play player (3–5 days)

See [plan_preview_player_later.md](v3_enhancements/plan_preview_player_later.md). **Implemented.** Next and previous file in track-number order (disc number first when it is present), 30-second fast-forward and rewind, one speed for every book in `QSettings`, and resume into the Phase 19 position and file. Escape keeps the position. The end of the last file clears it. The main list has an In progress filter for books with a saved position.

**Gate:** Transport and speed work. Resume uses the same columns as Book Details. The in-progress filter does not delete saved positions.

### Phase 23 — F08 Statistics: Want to Read and listening progress (0.5–1 day)

See [plan_statistics_extensions.md](v3_enhancements/plan_statistics_extensions.md). **Complete.**

Statistics rows for **Books Want to Read** and **Books In Progress** only. No rating, cover, or other new rows.

**Gate:** Passed. Both rows appear in Statistics; queries covered by tests.

### Phase 24 — Book Details path browse (0.5 day)

See [plan_book_details_path_browse.md](v3_enhancements/plan_book_details_path_browse.md). **Complete.**

Browse beside Path in Book Details update/new mode. Writes absolute `books.path` only; does not change collection `root_path`. Start dialog from current path, else collection root, else Preferences import folder. Play uses the same start-dir fallbacks when the stored path is missing; Play is hidden in update/new so Path can be fixed first.

**Gate:** Passed. Browse fills path in edit mode; Save persists; view mode has no Browse; root unchanged; Alt+B and status work with JAWS.

### Phase 25 — F01 Path health report (1–2 days)

See [plan_path_health_report.md](v3_enhancements/plan_path_health_report.md). **Complete.**

Manage → Check Books Path lists books whose stored path is blank, missing, or not under the library root. Open Book Details from a row; fix with Path browse or typing; Export CSV; no silent path rewrites. Play-aligned resolve so remapped playable paths are Incorrect, not Missing.

**Gate:** Passed. Report dialog is keyboard- and JAWS-usable; empty and mixed-path libraries behave as in the detail plan.

### Phase 26 — Check Books Path progress (0.5–1 day)

See [plan_check_books_path_progress.md](v3_enhancements/plan_check_books_path_progress.md). **Complete.**

Import-style progress on Scan for large collections and NAS paths. Live **Missing**, **Incorrect**, and **Valid** counts while running; Escape cancel; results table unchanged after completion.

**Gate:** Passed. Progress shows the three counts; Escape cancels; Check Books Path remains usable on large/NAS libraries; Phase 25 path rules unchanged.

### Phase 27 — Export library metadata (~2 days)

See [plan_export_library_metadata.md](plan_export_library_metadata.md). **Implemented — awaiting JAWS smoke.**

**File → Export Library** (Alt+F, X) writes the main list as shown (all filters, search, and sort) to CSV (UTF-8 with BOM for Excel) or JSON. With books selected, only the selection is exported. Blocked in duplicate mode (Export Duplicates stays there). Columns include the v3 fields: Series Number, Want to Read, Listen Position, and Listen File. CSV headers match Book List Import field names, so an export re-imports. Status speaks the count; focus returns to the book list. Help topic `25_export_library.md`. Logic in `src/core/library_export.py`; 14 tests in `test/test_library_export.py`; full suite green (634 passed, 1 skipped). CSV cells over 32,767 characters are cut with ` [truncated]` so LibreOffice Calc and Excel load the file; JSON keeps full text.

**Gate:** Export matches visible filter; headers correct; empty library handled; status announces row count; keyboard and JAWS usable. Automated parts pass; JAWS smoke pending.

### Phase 28 — iTunes technical tags in Comments (1 day)

See [plan_itunes_comment_cleanup.md](plan_itunes_comment_cleanup.md). **Implemented — awaiting tester check.**

Import skips iTunes comment frames (`iTunNORM`, `iTunSMPB`, `iTunes_CDDB_*`) and MusicBrainz / AcoustID / encoder frames, and cleans hex blocks, CD database IDs, MusicBrainz IDs, and encoder or converter stamps from every format's comment; real text is kept. One-time script `scripts/clean_technical_comments.py` (preview by default, `--apply` backs up first) cleans existing books: 81 books in the tester library, 76 left empty. The Phase 27 CSV cut at 32,767 characters stays. No schema or UI change. Logic in `src/core/comment_cleanup.py`; 16 tests in `test/test_comment_cleanup.py`; full suite green (650 passed, 1 skipped).

**Gate:** The test books in the plan match after the script; LibreOffice Calc opens the export; importing the three listed folders gives clean Comments.

### Phase 29 — Standard shortcuts (1–2 days)

See [plan_standard_shortcuts.md](v3_enhancements/plan_standard_shortcuts.md). **Complete — Sept 27, 2026.**

Book Details: **Edit** (Alt+E); Read date Alt+R; **Narrator** (Alt+N); Series Alt+S; Save **Ctrl+S**; New book Ctrl+N. Name list: **Ctrl+F** and **Ctrl+S**. Preferences, Collection, Import Detail, Web Metadata: **Ctrl+S** Save. Main toolbar: Import removed. Reading History: Search **Alt+S** only (Date Range tab Alt+R). **Narrator** on Book List Import (Alt+R; Alt+N Series number). Listen **Ctrl+L** (Alt+Shift+P removed). Help topic 16 and related shortcut tables updated; Phase 16 may refine other topics.

**Gate:** Each window's F1 list matches the real keys; Save is Ctrl+S everywhere; no Alt letter does two things in one window; JAWS/NVDA smoke.

### Phase 30 — Sept 27 tester feedback (3–5 days, batched)

See [plan_sept27_tester_feedback.md](v3_enhancements/plan_sept27_tester_feedback.md). **Complete — batches A–E tester accepted.**

**Batch A:** Book List Import (**Plot** last, header auto-map). Export (column order, **Narrator**, **Collection** after **Tracks**, **Cover**, export popup with filters).

**Batch B:** Web Metadata **Plot** focus and scroll; Google cooldown / brief status messages; author-prefixed titles match Open Library.

**Batch C:** Read date **OK**+**Clear** (calendar); Recently Added typed date for SR; clear want/listen on focused row; web fetch cell highlight.

**Batch D:** Book Details idle status and sighted summary show main-window **filters and sort** (not title/author); vertical scroll at high zoom. Feedback 3.1 (skip empty Series in view tab order) is **out of scope**.

**Batch E:** Name list sort and edit exit; Preferences/Help highlight sliders and scroll; Collection editor layout; Help **F1** at Help zoom.

**Gate (full phase):** Full `python -m pytest test/` green; JAWS/NVDA on each touched window.

### Phase 31 — Plot fetch quality, performance, and source compliance (5 batches)

See [plan_plot_fetch_improvements.md](plan_plot_fetch_improvements.md). **Implemented in 2.22; awaiting JAWS/NVDA review.**

Begin with a source-attribution and API-terms review covering display, modification, caching, storage, and linking. Then deliver candidate instrumentation, identifier reuse and cache versioning, identity-first ranking, and bounded source concurrency while preserving the modal, cancellable workflow and `WebBookAPI` compatibility facade.

**Gate:** Provider requirements recorded before implementation; required attribution and source links preserved through quiet help or on-demand details; provider names are not announced during progress or Plot focus and add nothing to the normal Tab order; no unresolved provider used for distributed plot text; faster agreed cases without more wrong-work selections; deterministic single/batch results; request budgets, cooldowns, cancellation, cache integrity, and JAWS/NVDA behavior preserved.

### Phase 16 — Help docs review (1 day)

See [plan_help_docs_review.md](v3_enhancements/plan_help_docs_review.md). **Complete.** Topics 22 and 23 removed; section headings no longer start with “Steps”; main-window help covers Listen and Export Library; shortcuts topic lists **Alt+F, X**; cross-links updated.

**Gate:** Topics 22 and 23 are gone; section names do not start with “Steps”; main-window help mentions Listen (Ctrl+L); topic 25 and Export Library links in place.

---

## Cross-cutting principles

1. Add or extend tests from each plan’s checklist before starting the next phase.
2. Run `python -m pytest test/` — **all** tests green before merge, including files this phase did not touch. Collection must succeed (a SyntaxError in any `test_*.py` fails the suite).
3. Test logic modules first; mock HTTP and DB in CI.
4. Include tests in the same commit/PR as the feature.
5. NVDA/JAWS smoke after each phase ([qa_verification.md](qa_verification.md)). Ship help with each feature.
6. Every UI phase must meet **Accessibility and UI formatting standards** below (buttons, dialogs, focus, styles).

Plot-length fixtures in `test_web_api_unit.py` / `test_web_api_fetch.py` now meet `PLOT_MIN_LENGTH` 80.

---

## Accessibility and UI formatting standards (all phases)

Mandatory for any new or changed window, dialog, footer button, combo, or status path in v3. Match existing main-window / Book Details / Preferences patterns — do not invent one-off styles or announcement paths.

### Screen reader (JAWS / NVDA)

- Dialogs subclass [`AccessibleDialog`](../src/ui/accessible_dialog.py) (or reuse `exec_styled_message_box` for simple prompts).
- Set **accessible name** and **description** on the dialog and on every interactive control (buttons, combos, lists, edits). `QAction` menu items use menu text only — do **not** call `setAccessibleName` on `QAction` (not supported).
- Meaningful state changes: `set_status(..., announce=True)` via [`announce_status_message`](../src/accessibility/accessible_events.py). Do not rely on `QStatusBar.showMessage()` alone.
- Every major window/dialog: **Alt+/** re-reads status ([`read_status_bar_message`](../src/accessibility/accessible_events.py)).
- After modal close: restore focus intentionally (`restore_main_focus_after_modal` / focus title or table as the parent window already does).
- Modal completion after background work: `raise_()` + `activateWindow()` + focus on the **default button** before announce (learned from fetch/Calibre issues).
- Worker threads must not touch widgets. Progress/UI updates go through a **GUI-thread `QObject` bridge** with `QueuedConnection` to `@Slot` methods — plain Python callables are not enough.
- Block unmapped Alt+letter in text fields (`is_unmapped_alt_letter`). Editable combos: block plain Up/Down; allow with Alt (Preferences / Book Details / Update pattern).
- No global Enter/Return shortcuts that steal default button activation.
- Help: F1 shortcuts; Shift+F1 process help via [`help_router.py`](../src/ui/help_router.py); ship or update `help_docs/` with the feature.

External reference (patterns + principles):

- [PySide6 Accessibility Patterns](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md)
- [Screen Reader Best Practices](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md)

### Buttons, footers, and control formatting

- New **QPushButton**s use [`build_accessible_button_style`](../src/accessibility/style_helpers.py) with scaled height from `UIScaler` (same as Update / Delete / Import footers). Do not invent per-dialog button CSS.
- Footer action buttons on the main window follow `update_selection_ui()` visibility/enable rules (multi-select patterns like Update/Delete).
- Default button: `setDefault(True)` on the primary action; ensure Tab order reaches it; screen reader focus lands on it when the dialog opens when that is the intended start.
- Decorative icons only via [`apply_decorative_action_icon`](../src/accessibility/icon_helper.py) / `get_app_icon()` — icons must not be the only label.
- Combos: [`build_accessible_combo_box_style`](../src/accessibility/style_helpers.py) where other prefs/main combos already use it; set accessible name/description; anti-noise event filter when editable.
- Checkboxes: [`build_accessible_checkbox_style`](../src/accessibility/style_helpers.py) when adding new check groups.
- Message boxes: [`exec_styled_message_box`](../src/accessibility/style_helpers.py) with scaled font and app window icon — not raw `QMessageBox` with default look.
- Scaling: respect `UIScaler` / theme; no hard-coded px that break zoom or high-contrast themes.
- Tooltips: pair short sighted tooltips with SR descriptions via existing helpers (`apply_visual_tooltip_map`) where the parent window already does.

### Per-phase gate (add to JAWS smoke)

Before marking a phase done:

1. Tab through every new control; JAWS/NVDA speaks a useful name (and value where applicable).
2. Activate primary and Cancel/Close with keyboard only (including Alt+letter if registered).
3. Alt+/ reads the latest status after a meaningful action.
4. Focus returns to a sensible place after the dialog closes.
5. New buttons look and focus like existing AbCS buttons (highlight focus ring, scaled height).

---

## What to combine vs keep separate

| Combine? | Plans | Why |
|----------|-------|-----|
| **Yes** | Background thread then API split | Split after thread so patch targets move once |
| **Yes** | Background thread then batch fetch | Batch reuses the worker |
| **No** | Batch UI vs non-modal jobs | Non-modal jobs out of scope for v3; progress stays modal |
| **No** | Leading article vs batch UI | Same Path B keys; separate plan and tester gate |
| **No** | Selection toolbar vs batch UI | Same selection footer; block unrelated actions |
| **No** | Tag mapping / updates / view-mode / name consistency with fetch | Independent |
| **Yes** | C01 schema then F10 series number | Phase 9 adds `series_number` only |
| **No** | Collection root column vs Phase 9 | `root_path` is added in Phase 11 |
| **Yes** | Phase 19 columns, then Want to read and the full player | One `want_to_read` column and one listen-progress pair. The player does not add a second progress store. |
| **No** | Ratings / tags / web covers / rescan Parts B–C | Out of v3. No columns for them in Phase 9 or Phase 19. |

---

## Deferred after v3 (keep plans)

Former “core waves 0–5” and follow-ons not selected for this release.

| Enhancement | Detail doc | Notes |
|-------------|------------|-------|
| Non-modal web fetch jobs | [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) | **Out of scope for v3** (too risky). Was former Phase 5. Progress stays modal. |
| View-mode field announcements (F14) | [plan_view_mode_static_text.md](plan_view_mode_static_text.md) | **Out of scope for v3.** Was former Phase 14. Needs a JAWS spike before any Book Details change. |
| Book ratings | [plan_ratings.md](plan_ratings.md) | **Out of scope for v3.** No rating columns in Phase 9. |
| Covers + zip backup | [Plan_covers.md](Plan_covers.md) | **Out of scope for v3.** No `cover_path` in Phase 9 or Phase 19. |
| Book tags | [plan_book_tags.md](plan_book_tags.md) | **Out of scope for v3.** |
| Rescan / update from folder (Part B) | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part B | Part A (root path) is v3 Phase 11 |
| Rescan Part C organize | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part C | High risk |
| Internationalization | [plan_Internationalization_overview.md](plan_Internationalization_overview.md) | After English freeze |
| Combined Want to read and playing filter | [plan_want_to_read_and_playing_filter.md](plan_want_to_read_and_playing_filter.md) | **Dropped.** Separate Want to read and In progress filters already ship |
| Missing metadata filters | [plan_missing_metadata_filters.md](plan_missing_metadata_filters.md) | |
| Bulk want-to-read / Import Detail TBR / Update extensions | linked plans | After Want to Read |
| Scheduled backup reminder | [plan_scheduled_backup_reminder.md](plan_scheduled_backup_reminder.md) | After zip backup |
| Reader / narrator filter | [plan_reader_filter.md](plan_reader_filter.md) | |
| Preferences export/import | [plan_preferences_export_import.md](plan_preferences_export_import.md) | |
| Import / Preferences toolbars | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) | |
| Third-party import | [plan_third_party_import.md](plan_third_party_import.md) | |
| Smart collections | [plan_smart_collections.md](plan_smart_collections.md) | |
| Reading progress | [plan_reading_progress.md](v3_enhancements/plan_reading_progress.md) | |
| Book tags | [plan_book_tags.md](plan_book_tags.md) | |
| Export Library options window | [plan_export_library_options_window.md](plan_export_library_options_window.md) | Proposed after Phase 27; for review |
### Schema batch (Phase 9 / C01)

| Table | New columns |
|-------|-------------|
| `books` | `series_number` |

See [plan_schema_batch.md](v3_enhancements/plan_schema_batch.md). Want to Read, ratings, and covers are out of v3. Series number UI is Phase 10. Collection `root_path` is added in Phase 11. Name-list merge on duplicate is Phase 13, second to last. Library-wide fuzzy name scan is deferred after v3.

---

## Maintenance (between phases)

| Item | Detail doc | Est. |
|------|------------|------|
| CI / test hardening | [plan_ci_test_hardening.md](plan_ci_test_hardening.md) | 1–2 d |
| Vulture dead-code cleanup | [plan_vulture_dead_code_cleanup.md](plan_vulture_dead_code_cleanup.md) | 0.5–1 d |

---

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| First production background thread | JAWS spike before real work; no UI from worker; `threading.Event` cancel |
| Batch completion silent to JAWS | Modal `AccessibleDialog` + `raise_`/`activateWindow`/focus (avoid Calibre overlay pattern) |
| Non-modal job loses JAWS | Not in v3 (out of scope). If revived later: real window + Alt+J; steal focus on finish; never a NoFocus overlay for answers |
| Tag mapping changes existing imports | Defaults = current album / album-artist-then-artist; grouping stays on album |
| Name-list merge moves many books | Confirm Yes/No; default No; no silent merges |
| Schema upgrade fails on existing DB | Backup before `ALTER TABLE`; announce failure; do not wipe library for non-critical columns |
| Collection root change vs absolute `books.path` | Part A stores root only; does not rewrite book paths. Path rewrite is Part C (deferred) |
| Preview of multi-file books | `books.path` is often a folder; plan must pick which file to launch (see preview plan) |
| Tester xlsx overwritten | Never regenerate filled `AbCS_Version3_Release_Tester_Review.xlsx` |

---

## How to use this doc

1. Phases 19, 18, 20, 22, 21, 23, 24, 25, 26, and 27 are done (18–20 tester accepted; 22 Import Detail layout complete; 21 full Play player implemented; 23 Statistics Want to Read / In Progress; 24 Book Details path browse; 25 Check Books Path; 26 Check Books Path progress; 27 Export library metadata implemented, JAWS smoke pending; 28 iTunes technical tags in Comments implemented, tester check pending). **Next: Phase 16 help last.** Combined Want to read and playing filter dropped. Also to do in v3: first-start screen reader Zoom message. Date/year validation bug fix is done ([fix_read_date.md](fix_read_date.md)); keep out of AGENTS/standards until a broader review. Phase 15 and Phase 17 are already implemented. Non-modal fetch is not a v3 phase. Phase 9 schema must precede Phase 10. Phase 11 adds `root_path` itself. Phase 13 name-list merge is complete in 2.18.
2. Meet each phase **gate** before the next.
3. Update [plans_status.md](plans_status.md) when a plan ships.
4. Read linked `plan_*.md` for file paths and a11y checklists.
