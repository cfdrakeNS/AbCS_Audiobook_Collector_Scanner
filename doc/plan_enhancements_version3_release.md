# Version 3 Release Enhancements — Master Roadmap

**Status:** Active schedule (scoped from tester review, September 2026)  
**Created:** June 2026  
**Updated:** September 2026  

**Purpose:** Single schedule for version 3 work — order, combinations, test gates, and deferrals. Individual plans hold **what** to build; this document holds **when**.

**Related:** [plans_status.md](plans_status.md), [TESTING.md](../TESTING.md), [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md), [AbCS_Version3_Release_Tester_Review.xlsx](AbCS_Version3_Release_Tester_Review.xlsx) (tester source of truth — do not overwrite filled answers)

**Branch:** work from `main` (or a short-lived phase branch per feature)

---

## Version 3 scope (from tester review)

Tester-selected items plus Phase 2 follow-ons (leading-article compare; selection-mode toolbar) and **non-modal fetch jobs**. Everything else stays planned but **deferred after v3**.

| Phase | ID | Enhancement | Detail doc | Est. | Depends on |
|-------|----|-------------|------------|------|------------|
| 1 | F13 | Web fetch background thread + API split | [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md) | 3–5 d | — |
| 2 | F12 | Batch web metadata fetch | [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md) | 1–2 wk | Phase 1 |
| 3 | — | Leading article title compare (Path B) | [plan_leading_article_title_compare.md](plan_leading_article_title_compare.md) | 0.5–1 d | Phase 1 matching |
| 4 | — | Selection mode: block toolbar and shortcuts | [plan_selection_mode_toolbar.md](plan_selection_mode_toolbar.md) | 1–2 d | — |
| 5 | — | Non-modal web fetch jobs (keep using the app) | [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) | 3–5 d | Phase 1–2 |
| 6 | F17 | Import tag mapping (title / author) | [plan_import_tag_mapping.md](plan_import_tag_mapping.md) | 2–3 d | — |
| 7 | B05 | Check for updates | [plan_auto_update.md](plan_auto_update.md) | 2–3 d | — |
| 8 | C09 | Name consistency check | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | 2–3 wk | — |
| 9 | F14 | View-mode field announcements | [plan_view_mode_static_text.md](plan_view_mode_static_text.md) | 2–4 d | — |

Phases 6–9 are independent of each other after Phase 1 exists. **Phase 9 (view-mode) is optional** — include only if still wanted after Phases 1–8.

**Not in v3:** Want to Read, ratings, covers, zip backup, collection library folder, rescan, i18n, organize-on-disk, and remaining follow-on/backlog rows. No schema-batch Wave 0 in this release.

---

## Phase details

### Phase 1 — Background web fetch (3–5 days)

See [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md). **Complete — tester accepted Alt+W after the split.** Google Books 429 during library testing is source cooldown (`web_source_cooldowns.json`), not a Phase 1 regression.

1. Throwaway JAWS spike — **done** (tester accepted).
2. Move fetch onto `QThread`; keep `fetch_web_metadata_for_book` blocking via `exec()` — **done** (tester accepted; Escape-only wait dialog).
3. Split `web_book_api.py` after the thread — **done** (`web_http`, `web_matching`, `web_cache` + facade). Per-source fetch and plot enrich stay on `WebBookAPI`.

**Gate:** Tester re-confirms Alt+W after the split (progress spoken, Escape cancel, no crash). Web tests green (81). UI updates only via GUI-thread bridge ([Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases)).

### Phase 2 — Batch web fetch (1–2 weeks)

See [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md). **Complete — tester accepted**, then follow-up polish (below). Progress remains modal until Phase 5.

Multi-select starts from **Alt+W**, toolbar **Search Web**, or footer **Web fetch**. There is no main-window Alt+B. N/M progress; summary with Apply all / Review. Escape closes the summary.

Follow-up after accept:

- Issue column: **Plot found**, **Metadata found**, or **Plot and metadata up to date.** Title column keeps a readable width; long issue text may ellipsize. Speech still has the full issue.
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

**Next:** Phase 5 is not started. It drops the blocking `exec()` wait so the main window stays usable. Treat it as a separate, larger change.

### Phase 5 — Non-modal web fetch jobs (3–5 days)

See [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md).

Progress `show()` not `exec()`; main window usable; **Alt+J** returns to the job; one job at a time; finish raises review or modal batch summary. JAWS spike before production.

**Gate:** List usable during fetch; Alt+J returns; second fetch refused; finish announced in front; Escape cancels progress.

### Phase 6 — Import tag mapping (2–3 days)

See [plan_import_tag_mapping.md](plan_import_tag_mapping.md).

**Gate:** Defaults match today’s scan; grouping stays on album; prefs round-trip; new combos match Preferences accessible combo + anti-noise patterns.

### Phase 7 — Check for updates (2–3 days)

See [plan_auto_update.md](plan_auto_update.md).

**Gate:** Help → Check for updates compares GitHub latest to `APP_VERSION`; offline failure is announced; result dialog uses AccessibleDialog + styled buttons with default focus.

### Phase 8 — Name consistency (2–3 weeks)

See [Plan_name_consistency_check.md](Plan_name_consistency_check.md).

Does **not** require rescan. Confirm-each-group; no silent merges.

**Gate:** Author/genre merge safe; import blocked while mode active; Escape restores filters; review dialog meets shared a11y/button standards.

### Phase 9 — View-mode announcements (2–4 days, optional)

See [plan_view_mode_static_text.md](plan_view_mode_static_text.md).

**Optional for v3** — decide after Phases 1–8. Spike must pass JAWS before any Book Details change.

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
| **Yes** | Batch UI then non-modal jobs | Same progress/summary; drop `exec()` |
| **No** | Leading article vs batch UI | Same Path B keys; separate plan and tester gate |
| **No** | Selection toolbar vs batch UI | Same selection footer; block unrelated actions |
| **No** | Tag mapping / updates / view-mode / name consistency with fetch | Independent |
| **No** | Deferred Want to Read / ratings / covers / rescan | Out of v3 |

---

## Deferred after v3 (keep plans)

Former “core waves 0–5” and follow-ons not selected for this release.

| Enhancement | Detail doc | Notes |
|-------------|------------|-------|
| Schema batch (TBR, rating, cover, collection root) | this doc § historical Wave 0 | Prerequisite for deferred features |
| Want to Read | [plan_want_to_read.md](plan_want_to_read.md) | |
| Open audiobook location | [plan_audiobook_preview.md](plan_audiobook_preview.md) | |
| Ratings | [plan_ratings.md](plan_ratings.md) | |
| Covers + zip backup | [Plan_covers.md](Plan_covers.md) | |
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
| Series number in DB | [plan_series_number_db.md](plan_series_number_db.md) | |
| Preferences export/import | [plan_preferences_export_import.md](plan_preferences_export_import.md) | |
| Import / Preferences toolbars | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) | |
| Third-party import | [plan_third_party_import.md](plan_third_party_import.md) | |
| Smart collections | [plan_smart_collections.md](plan_smart_collections.md) | |
| Reading progress | [plan_reading_progress.md](plan_reading_progress.md) | |
| Book tags | [plan_book_tags.md](plan_book_tags.md) | |

### Historical schema batch (when deferred features start)

| Table | New columns |
|-------|-------------|
| `books` | `want_to_read`, `rating`, `ratings_count`, `cover_path` |
| `collections` | `root_path` |

Optional: `series_number` ([plan_series_number_db.md](plan_series_number_db.md)).

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
| Non-modal job loses JAWS | Real window + Alt+J; steal focus on finish; never NoFocus overlay for answers |
| Tag mapping changes existing imports | Defaults = current album / album-artist-then-artist; grouping stays on album |
| Name consistency merges many books | Confirm each group; no silent merges |
| Tester xlsx overwritten | Never regenerate filled `AbCS_Version3_Release_Tester_Review.xlsx` |

---

## How to use this doc

1. Implement phases in order (or 6–9 in parallel after Phase 1 if staffing allows).
2. Meet each phase **gate** before the next.
3. Update [plans_status.md](plans_status.md) when a plan ships.
4. Read linked `plan_*.md` for file paths and a11y checklists.
