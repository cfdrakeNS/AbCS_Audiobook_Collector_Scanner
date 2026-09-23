# Version 3 Release Enhancements — Master Roadmap

**Status:** Active schedule (scoped from tester review, September 2026)  
**Created:** June 2026  
**Updated:** September 2026  

**Tester build:** 2.17 — Phases 1–4 and 6–9 complete (tester accepted). Phase 10 series number is in this build; Book Details display was confirmed. Date Read and Added since calendars show days 10–31. Non-modal fetch is out of scope for v3. Next is Phase 11 (collection root).  

**Purpose:** Single schedule for version 3 work — order, combinations, test gates, and deferrals. Individual plans hold **what** to build; this document holds **when**.

**Related:** [plans_status.md](plans_status.md), [TESTING.md](../TESTING.md), [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md), [AbCS_Version3_Release_Tester_Review.xlsx](AbCS_Version3_Release_Tester_Review.xlsx) (tester source of truth — do not overwrite filled answers)

**Branch:** work from `main` (or a short-lived phase branch per feature)

---

## Version 3 scope (from tester review)

Tester-selected items plus Phase 2 follow-ons (leading-article compare; selection-mode toolbar), keep-current-book, C01 schema, F10 series number, C07 collection root (Part A), and audiobook preview (OS default player). **Out of scope for v3 (deferred):** non-modal web fetch jobs (too risky), book ratings UI, covers UI. Everything else stays planned but **deferred after v3**.

| Phase | ID | Enhancement | Detail doc | Est. | Depends on |
|-------|----|-------------|------------|------|------------|
| 1 | F13 | Web fetch background thread + API split | [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md) | 3–5 d | — |
| 2 | F12 | Batch web metadata fetch | [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md) | 1–2 wk | Phase 1 |
| 3 | — | Leading article title compare (Path B) | [plan_leading_article_title_compare.md](plan_leading_article_title_compare.md) | 0.5–1 d | Phase 1 matching |
| 4 | — | Selection mode: block toolbar and shortcuts | [plan_selection_mode_toolbar.md](plan_selection_mode_toolbar.md) | 1–2 d | — |
| 6 | F17 | Import tag mapping (title / author) | [plan_import_tag_mapping.md](plan_import_tag_mapping.md) | 2–3 d | — |
| 7 | B05 | Check for updates | [plan_auto_update.md](plan_auto_update.md) | 2–3 d | — |
| 8 | — | Keep current book on sort and filter | [plan_keep_book_focus.md](plan_keep_book_focus.md) | 0.5–1 d | — |
| 9 | C01 | Schema batch (in-place upgrade) | [plan_schema_batch.md](plan_schema_batch.md) | 2–3 d | — |
| 10 | F10 | Series book number | [plan_series_number_db.md](plan_series_number_db.md) | 2–3 d | Phase 9 |
| 11 | C07 | Collection library root folder | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part A | 2–3 d | Adds `root_path` |
| 12 | C03 | Preview audiobook (OS default player) | [plan_audiobook_preview.md](plan_audiobook_preview.md) | 1–2 d | — |
| 13 | C09 | Name consistency check | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | 2–3 wk | — |
| 14 | F14 | View-mode field announcements | [plan_view_mode_static_text.md](plan_view_mode_static_text.md) | 2–4 d | — |

**Phase numbers 1–4 and 6–8 are historical (complete).** There is no Phase 5 in v3 — non-modal fetch was removed as too risky; see deferred. **Phase 13 is name consistency (second to last). Phase 14 (view-mode) is optional and last.** Phase 9 adds `series_number` only. Want to Read, ratings, and covers are out of v3. Collection `root_path` is added in Phase 11.

**Not in v3:** Non-modal web fetch (keep using the app during a fetch), Want to Read, book ratings, covers and zip backup, rescan (Part B), organize-on-disk (Part C), i18n, and remaining follow-on/backlog rows. Web fetch progress stays a blocking dialog. Collection root **Part A** is in v3; Parts B and C stay deferred.

---

## Phase details

### Phase 1 — Background web fetch (3–5 days)

See [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md). **Complete — tester accepted Alt+W after the split.** Google Books 429 during library testing is source cooldown (`web_source_cooldowns.json`), not a Phase 1 regression.

1. Throwaway JAWS spike — **done** (tester accepted).
2. Move fetch onto `QThread`; keep `fetch_web_metadata_for_book` blocking via `exec()` — **done** (tester accepted; Escape-only wait dialog).
3. Split `web_book_api.py` after the thread — **done** (`web_http`, `web_matching`, `web_cache` + facade). Per-source fetch and plot enrich stay on `WebBookAPI`.

**Gate:** Tester re-confirms Alt+W after the split (progress spoken, Escape cancel, no crash). Web tests green (81). UI updates only via GUI-thread bridge ([Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases)).

### Phase 2 — Batch web fetch (1–2 weeks)

See [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md). **Complete — tester accepted**, then follow-up polish (below). Progress stays modal for v3. Non-modal jobs are out of scope and will not change that.

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

See [plan_leading_article_title_compare.md](plan_leading_article_title_compare.md). **Complete.**

Path B: same-work match for optional leading A/An/The; review still **offers** the web title when the catalog includes the article. Trailing-article and series-suffix behavior from 2.14 stays.

**Gate:** Same-work match for leading article; web title still offered to save; real subtitle still differs; Alt+W and batch Review unchanged otherwise.

### Phase 4 — Selection mode toolbar and shortcuts (1–2 days)

See [plan_selection_mode_toolbar.md](plan_selection_mode_toolbar.md). **Complete.**

While selection is active, disable Add/Import/Find/Statistics/Preferences/filters. Intercept those shortcuts; announce Escape. **Alt+W**, Search Web, and footer Web fetch stay available; two or more selected run **batch** fetch. Keep Update/Delete, F1, Alt+/, Alt+L. F1 during selection lists only shortcuts that still work. Shift+Up/Down **speaks** the selection status (`announce=True`). Do not clear-and-run.

**Gate:** Blocked actions do not run; Alt+W with 2+ selected is batch; status speech is requested on selection (not only stored); Escape restores toolbar; duplicate mode unchanged.

### Phase 6 — Import tag mapping (2–3 days)

See [plan_import_tag_mapping.md](plan_import_tag_mapping.md). **Complete — tester accepted.**

Preferences Import Settings has **Tag mapping**: Book title (Album / Track title / Album then track title) and Author (Album artist then artist / Album artist only / Artist only). Defaults match the previous scan. Grouping stays on the album tag. Empty or placeholder tags still use the Fallback tab.

**Gate:** Defaults match today’s scan; grouping stays on album; prefs round-trip; new combos match Preferences accessible combo + anti-noise patterns.

### Phase 7 — Check for updates (2–3 days)

See [plan_auto_update.md](plan_auto_update.md). **Complete — tester accepted.**

Help → Check for updates reads the latest GitHub release tag and compares it to `APP_VERSION`. **Testing only:** Help → Website and Open website open `https://abcstest.carrd.co/`. Before merging to main, set `ABCS_UPDATE_DOWNLOAD_URL` back to the live site `https://abcs.auroraaccessibility.com/`. The check does not install anything. Enter activates the focused button.

**Gate:** Help → Check for updates compares GitHub latest to `APP_VERSION`; offline failure is announced; result dialog uses AccessibleDialog + styled buttons with default focus.

### Phase 8 — Keep current book on sort and filter (0.5–1 day)

See [plan_keep_book_focus.md](plan_keep_book_focus.md). **Complete — tester accepted.**

Sort (menu or header) keeps the focused book as the current row. Filters do the same when that book is still in the list. If a filter drops it, focus moves to the first remaining book.

**Gate:** JAWS: arrow to a middle book, sort by author, still that title. Unread while unread stays. Read while unread moves to the first remaining book.

### Phase 9 — C01 Schema batch (2–3 days)

See [plan_schema_batch.md](plan_schema_batch.md). **Complete — tester accepted.** The upgrade dialog was heard.

In-place `ALTER TABLE` on **first start** for existing libraries (not only new installs). Adds `series_number` on `books` only. Does not add `want_to_read`, `rating`, `ratings_count`, `cover_path`, or `collections.root_path`. No new buttons in this phase. Timestamped `schema_repair` backup before change. Announce the upgrade for dev and installed builds. Existing titles are not rewritten.

The column is used by series number (Phase 10). Collection root adds `root_path` in Phase 11. Want to Read, ratings, and covers are not part of this upgrade.

**Gate:** Old database opens with books intact; new columns present; upgrade announced once.

### Phase 10 — F10 Series book number (2–3 days)

See [plan_series_number_db.md](plan_series_number_db.md). **In tester build 2.17.** Book Details display confirmed. Needs Phase 9.

The only series-number field is on **Book Details**, a text box to the right of Series. When a book is shown and Series # is blank, a title suffix such as ` - 3` or ` - 6.5` is stored in Series #. The title stays as it is. There is no status message. When Series # is added or changed, saving puts that number on the title (` - 03` or ` - 6.5`). Clearing Series # leaves the title as it is. The main-window **Series** sort becomes series name, then series number, then year, then title. Book List Import stores a mapped Series # and appends it to the title. Series From File Name does the same for a number in the file name. No series-number column on the main table. Not on Import Detail, web fetch, or the bulk Update window.

**Gate:** Save/load from Book Details; showing a book with a blank Series # and a title suffix such as ` - 3` stores that number and leaves the title unchanged; saving after Series # is added or changed puts that number on the title; Series sort is series, series number, year, then title; JAWS reads the text box to the right of Series.

### Phase 11 — C07 Collection library root folder (2–3 days)

See [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) **Part A only**. This phase adds `collections.root_path` on first start for existing libraries, using the same upgrade path as Phase 9.

Allow setting and changing the optional root folder for a collection (example: `F:\audiobook`). Edit in Collection Manager. When the user selects or browses a collection folder, **warn** if that folder does not exist, or if it contains no recognized audiobook files (extensions from `TagReader.SUPPORTED_EXTENSIONS`). Import may pre-fill from `root_path` when present. Rescan (Part B) and organize-on-disk (Part C) stay deferred.

**Gate:** Save/load `root_path`; warn on missing folder; warn when folder has no supported audio; Import pre-fill when root is set and exists.

### Phase 12 — C03 Preview audiobook (1–2 days)

See [plan_audiobook_preview.md](plan_audiobook_preview.md).

**Preview** button on Book Details, plus a main-window **Edit** menu item (same menu as Fetch Web Info). Opens the book in the user’s **default OS media player** for that file format (file association) — not an in-app player. Book Details has no menu bar today; menu entry is on the main window.

**Gate:** Preview launches default player for a single-file book; missing path announced; JAWS can activate Preview from button and Edit menu.

### Phase 13 — Name consistency (2–3 weeks)

See [Plan_name_consistency_check.md](Plan_name_consistency_check.md).

Does **not** require rescan. Confirm-each-group; no silent merges.

**Gate:** Author/genre merge safe; import blocked while mode active; Escape restores filters; review dialog meets shared a11y/button standards.

### Phase 14 — View-mode announcements (2–4 days, optional)

See [plan_view_mode_static_text.md](plan_view_mode_static_text.md).

**Optional for v3** — decide after Phases 9–13. Spike must pass JAWS before any Book Details change.

**Gate:** JAWS spike accepted; Book Details view mode speaks name **and** value without edit or read only; edit mode still says edit.

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
| **No** | Want to Read / ratings / covers / rescan Parts B–C | Out of v3. No columns for them in Phase 9. |

---

## Deferred after v3 (keep plans)

Former “core waves 0–5” and follow-ons not selected for this release.

| Enhancement | Detail doc | Notes |
|-------------|------------|-------|
| Non-modal web fetch jobs | [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) | **Out of scope for v3** (too risky). Was former Phase 5. Progress stays modal. |
| Book ratings | [plan_ratings.md](plan_ratings.md) | **Out of scope for v3.** No rating columns in Phase 9. |
| Want to Read | [plan_want_to_read.md](plan_want_to_read.md) | **Out of scope for v3.** No `want_to_read` column in Phase 9. |
| Covers + zip backup | [Plan_covers.md](Plan_covers.md) | **Out of scope for v3.** No `cover_path` in Phase 9. |
| Rescan / update from folder (Part B) | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part B | Part A (root path) is v3 Phase 11 |
| Rescan Part C organize | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part C | High risk |
| Internationalization | [plan_Internationalization_overview.md](plan_Internationalization_overview.md) | After English freeze |
| Path health report | [plan_path_health_report.md](plan_path_health_report.md) | |
| Export library metadata | [plan_export_library_metadata.md](plan_export_library_metadata.md) | |
| Missing metadata filters | [plan_missing_metadata_filters.md](plan_missing_metadata_filters.md) | |
| Bulk want-to-read / Import Detail TBR / Update extensions | linked plans | After Want to Read |
| Scheduled backup reminder | [plan_scheduled_backup_reminder.md](plan_scheduled_backup_reminder.md) | After zip backup |
| Statistics extensions | [plan_statistics_extensions.md](plan_statistics_extensions.md) | |
| Reader / narrator filter | [plan_reader_filter.md](plan_reader_filter.md) | |
| Preferences export/import | [plan_preferences_export_import.md](plan_preferences_export_import.md) | |
| Import / Preferences toolbars | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) | |
| Third-party import | [plan_third_party_import.md](plan_third_party_import.md) | |
| Smart collections | [plan_smart_collections.md](plan_smart_collections.md) | |
| Reading progress | [plan_reading_progress.md](plan_reading_progress.md) | |
| Book tags | [plan_book_tags.md](plan_book_tags.md) | |

### Schema batch (Phase 9 / C01)

| Table | New columns |
|-------|-------------|
| `books` | `series_number` |

See [plan_schema_batch.md](plan_schema_batch.md). Want to Read, ratings, and covers are out of v3. Series number UI is Phase 10. Collection `root_path` is added in Phase 11. Name consistency is Phase 13, second to last.

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
| Name consistency merges many books | Confirm each group; no silent merges |
| Schema upgrade fails on existing DB | Backup before `ALTER TABLE`; announce failure; do not wipe library for non-critical columns |
| Collection root change vs absolute `books.path` | Part A stores root only; does not rewrite book paths. Path rewrite is Part C (deferred) |
| Preview of multi-file books | `books.path` is often a folder; plan must pick which file to launch (see preview plan) |
| Tester xlsx overwritten | Never regenerate filled `AbCS_Version3_Release_Tester_Review.xlsx` |

---

## How to use this doc

1. Implement the remaining phases in order. Non-modal fetch is not a v3 phase. Phase 9 schema must precede Phase 10. Phase 11 adds `root_path` itself. Name consistency is Phase 13, just before optional Phase 14.
2. Meet each phase **gate** before the next.
3. Update [plans_status.md](plans_status.md) when a plan ships.
4. Read linked `plan_*.md` for file paths and a11y checklists.
