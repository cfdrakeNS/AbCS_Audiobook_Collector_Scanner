# Version 3 Release Enhancements — Master Roadmap

**Status:** Active schedule (scoped from tester review, September 2026)  
**Created:** June 2026  
**Updated:** September 2026  

**Tester build:** 2.16 — Phases 1–4, 6, and 7 complete (tester accepted). Phase 5 skipped. Phase 8 keep-current-book is in this build, ready to test. Next coding after Phase 8 accept is Phase 9 (C01 in-place schema).  

**Purpose:** Single schedule for version 3 work — order, combinations, test gates, and deferrals. Individual plans hold **what** to build; this document holds **when**.

**Related:** [plans_status.md](plans_status.md), [TESTING.md](../TESTING.md), [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md), [AbCS_Version3_Release_Tester_Review.xlsx](AbCS_Version3_Release_Tester_Review.xlsx) (tester source of truth — do not overwrite filled answers)

**Branch:** work from `main` (or a short-lived phase branch per feature)

---

## Version 3 scope (from tester review)

Tester-selected items plus Phase 2 follow-ons (leading-article compare; selection-mode toolbar), keep-current-book, C01 schema, C04 ratings, and F10 series number. Non-modal fetch jobs are **skipped for v3**. Everything else stays planned but **deferred after v3**.

| Phase | ID | Enhancement | Detail doc | Est. | Depends on |
|-------|----|-------------|------------|------|------------|
| 1 | F13 | Web fetch background thread + API split | [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md) | 3–5 d | — |
| 2 | F12 | Batch web metadata fetch | [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md) | 1–2 wk | Phase 1 |
| 3 | — | Leading article title compare (Path B) | [plan_leading_article_title_compare.md](plan_leading_article_title_compare.md) | 0.5–1 d | Phase 1 matching |
| 4 | — | Selection mode: block toolbar and shortcuts | [plan_selection_mode_toolbar.md](plan_selection_mode_toolbar.md) | 1–2 d | — |
| 5 | — | Non-modal web fetch jobs | [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) | — | **Skipped for v3.** Fetch stays modal. |
| 6 | F17 | Import tag mapping (title / author) | [plan_import_tag_mapping.md](plan_import_tag_mapping.md) | 2–3 d | — |
| 7 | B05 | Check for updates | [plan_auto_update.md](plan_auto_update.md) | 2–3 d | — |
| 8 | — | Keep current book on sort and filter | [plan_keep_book_focus.md](plan_keep_book_focus.md) | 0.5–1 d | — |
| 9 | C01 | Schema batch (in-place upgrade) | [plan_schema_batch.md](plan_schema_batch.md) | 2–3 d | — |
| 10 | C09 | Name consistency check | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | 2–3 wk | — |
| 11 | C04 | Book ratings | [plan_ratings.md](plan_ratings.md) | 4–5 d | Phase 9 |
| 12 | F10 | Series book number | [plan_series_number_db.md](plan_series_number_db.md) | 2–3 d | Phase 9 |
| 13 | F14 | View-mode field announcements | [plan_view_mode_static_text.md](plan_view_mode_static_text.md) | 2–4 d | — |

**Phase 5 is skipped.** **Phase 13 (view-mode) is optional.** Want to Read and covers UI stay deferred; Phase 9 still adds their columns so later features do not need a second first-start migration.

**Not in v3:** Non-modal web fetch (keep using the app during a fetch), Want to Read UI, covers UI, zip backup, collection library folder, rescan, i18n, organize-on-disk, and remaining follow-on/backlog rows. Web fetch progress stays a blocking dialog.

---

## Phase details

### Phase 1 — Background web fetch (3–5 days)

See [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md). **Complete — tester accepted Alt+W after the split.** Google Books 429 during library testing is source cooldown (`web_source_cooldowns.json`), not a Phase 1 regression.

1. Throwaway JAWS spike — **done** (tester accepted).
2. Move fetch onto `QThread`; keep `fetch_web_metadata_for_book` blocking via `exec()` — **done** (tester accepted; Escape-only wait dialog).
3. Split `web_book_api.py` after the thread — **done** (`web_http`, `web_matching`, `web_cache` + facade). Per-source fetch and plot enrich stay on `WebBookAPI`.

**Gate:** Tester re-confirms Alt+W after the split (progress spoken, Escape cancel, no crash). Web tests green (81). UI updates only via GUI-thread bridge ([Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases)).

### Phase 2 — Batch web fetch (1–2 weeks)

See [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md). **Complete — tester accepted**, then follow-up polish (below). Progress stays modal for v3. Phase 5 will not change that.

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

### Phase 5 — Non-modal web fetch jobs

**Skipped for v3.** The plan stays in [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) if it is wanted later. Fetch progress keeps blocking `exec()` so the main window waits until the fetch finishes.

### Phase 6 — Import tag mapping (2–3 days)

See [plan_import_tag_mapping.md](plan_import_tag_mapping.md). **Complete — tester accepted.**

Preferences Import Settings has **Tag mapping**: Book title (Album / Track title / Album then track title) and Author (Album artist then artist / Album artist only / Artist only). Defaults match the previous scan. Grouping stays on the album tag. Empty or placeholder tags still use the Fallback tab.

**Gate:** Defaults match today’s scan; grouping stays on album; prefs round-trip; new combos match Preferences accessible combo + anti-noise patterns.

### Phase 7 — Check for updates (2–3 days)

See [plan_auto_update.md](plan_auto_update.md). **Complete — tester accepted.**

Help → Check for updates reads the latest GitHub release tag and compares it to `APP_VERSION`. **Testing only:** Help → Website and Open website open `https://abcstest.carrd.co/`. Before merging to main, set `ABCS_UPDATE_DOWNLOAD_URL` back to the live site `https://abcs.auroraaccessibility.com/`. The check does not install anything. Enter activates the focused button.

**Gate:** Help → Check for updates compares GitHub latest to `APP_VERSION`; offline failure is announced; result dialog uses AccessibleDialog + styled buttons with default focus.

### Phase 8 — Keep current book on sort and filter (0.5–1 day)

See [plan_keep_book_focus.md](plan_keep_book_focus.md). **Implemented — ready to test in 2.16.**

Sort (menu or header) keeps the focused book as the current row. Filters do the same when that book is still in the list. If a filter drops it, focus moves to the first remaining book.

**Gate:** JAWS: arrow to a middle book, sort by author, still that title. Unread while unread stays. Read while unread moves to the first remaining book.

### Phase 9 — C01 Schema batch (2–3 days)

See [plan_schema_batch.md](plan_schema_batch.md). **Next after Phase 8 tester accept.**

In-place `ALTER TABLE` on first start. Adds `want_to_read`, `rating`, `ratings_count`, `cover_path`, `series_number` on `books`, and `root_path` on `collections`. No new buttons. Backup before change. Announce the upgrade for dev and installed builds.

**Gate:** Old database opens with books intact; new columns present; upgrade announced once.

### Phase 10 — Name consistency (2–3 weeks)

See [Plan_name_consistency_check.md](Plan_name_consistency_check.md). Was Phase 8.

Does **not** require rescan. Confirm-each-group; no silent merges.

**Gate:** Author/genre merge safe; import blocked while mode active; Escape restores filters; review dialog meets shared a11y/button standards.

### Phase 11 — C04 Book ratings (4–5 days)

See [plan_ratings.md](plan_ratings.md). Needs Phase 9.

Numeric rating on each book; main table, Book Details, Import Detail, web save. Numbers only (no stars).

**Gate:** Save/load rating; web fill sets count; manual edit clears count; shared a11y/button/scaling rules.

### Phase 12 — F10 Series book number (2–3 days)

See [plan_series_number_db.md](plan_series_number_db.md). Needs Phase 9.

Manual series number on Book Details and Update. Not on web fetch. No series-order sort in this phase.

**Gate:** Save/load series number; title/number split does not drop existing titles.

### Phase 13 — View-mode announcements (2–4 days, optional)

See [plan_view_mode_static_text.md](plan_view_mode_static_text.md). Was Phase 9.

**Optional for v3** — decide after Phases 9–12. Spike must pass JAWS before any Book Details change.

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
| **No** | Batch UI vs non-modal jobs | Non-modal jobs skipped for v3; progress stays modal |
| **No** | Leading article vs batch UI | Same Path B keys; separate plan and tester gate |
| **No** | Selection toolbar vs batch UI | Same selection footer; block unrelated actions |
| **No** | Tag mapping / updates / view-mode / name consistency with fetch | Independent |
| **Yes** | C01 schema then C04 ratings and F10 series number | One first-start `ALTER TABLE` |
| **No** | Deferred Want to Read UI / covers / rescan | Out of v3; columns added in C01 |

---

## Deferred after v3 (keep plans)

Former “core waves 0–5” and follow-ons not selected for this release.

| Enhancement | Detail doc | Notes |
|-------------|------------|-------|
| Non-modal web fetch jobs | [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) | Skipped for v3. Was Phase 5. Progress stays modal. |
| Want to Read UI | [plan_want_to_read.md](plan_want_to_read.md) | Column added in Phase 9 |
| Open audiobook location | [plan_audiobook_preview.md](plan_audiobook_preview.md) | |
| Covers + zip backup | [Plan_covers.md](Plan_covers.md) | `cover_path` added in Phase 9 |
| Rescan + collection root (A+B) | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) | Not Part C |
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
| `books` | `want_to_read`, `rating`, `ratings_count`, `cover_path`, `series_number` |
| `collections` | `root_path` |

See [plan_schema_batch.md](plan_schema_batch.md). Want to Read and covers UI stay deferred.

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
| Non-modal job loses JAWS | Not in v3. If revived later: real window + Alt+J; steal focus on finish; never a NoFocus overlay for answers |
| Tag mapping changes existing imports | Defaults = current album / album-artist-then-artist; grouping stays on album |
| Name consistency merges many books | Confirm each group; no silent merges |
| Tester xlsx overwritten | Never regenerate filled `AbCS_Version3_Release_Tester_Review.xlsx` |

---

## How to use this doc

1. Implement the remaining phases in order. Phase 5 is skipped. After Phase 8 tester accept, Phase 9 schema must precede Phases 11 and 12.
2. Meet each phase **gate** before the next.
3. Update [plans_status.md](plans_status.md) when a plan ships.
4. Read linked `plan_*.md` for file paths and a11y checklists.
