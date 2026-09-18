# Version 3 Release Enhancements — Master Roadmap

**Status:** Active schedule (scoped from tester review, September 2026)  
**Created:** June 2026  
**Updated:** September 2026  

**Purpose:** Single schedule for version 3 work — order, combinations, test gates, and deferrals. Individual plans hold **what** to build; this document holds **when**.

**Related:** [plans_status.md](plans_status.md), [TESTING.md](../TESTING.md), [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md), [AbCS_Version3_Release_Tester_Review.xlsx](AbCS_Version3_Release_Tester_Review.xlsx) (tester source of truth — do not overwrite filled answers)

**Branch:** `feature/background-fetch-v3`

---

## Version 3 scope (from tester review)

Six items marked for v3. Everything else stays planned but **deferred after v3**.

| Phase | ID | Enhancement | Detail doc | Est. | Depends on |
|-------|----|-------------|------------|------|------------|
| 1 | F13 | Web fetch background thread + API split | [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md) | 3–5 d | — |
| 2 | F12 | Batch web metadata fetch | [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md) | 1–2 wk | Phase 1 |
| 3 | F17 | Import tag mapping (title / author) | [plan_import_tag_mapping.md](plan_import_tag_mapping.md) | 2–3 d | — |
| 4 | B05 | Check for updates | [plan_auto_update.md](plan_auto_update.md) | 2–3 d | — |
| 5 | F14 | View-mode field announcements | [plan_view_mode_static_text.md](plan_view_mode_static_text.md) | 2–4 d | — |
| 6 | C09 | Name consistency check | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | 2–3 wk | — |

Phases 3–6 are independent of each other after Phase 1 exists. Recommended order follows tester priority, with Check for updates as Phase 4 (small, unranked).

**Not in v3:** Want to Read, ratings, covers, zip backup, collection library folder, rescan, i18n, organize-on-disk, and remaining follow-on/backlog rows. No schema-batch Wave 0 in this release.

---

## Phase details

### Phase 1 — Background web fetch (3–5 days)

See [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md).

1. Throwaway JAWS spike (fake worker + real progress dialog + completion).
2. Move fetch onto `QThread`; keep `fetch_web_metadata_for_book` blocking via `exec()`.
3. Split `web_book_api.py` after the thread (not with it).

**Gate:** Spike scenarios pass; Alt+W fetch stays responsive; cancel works; existing web tests green.

### Phase 2 — Batch web fetch (1–2 weeks)

See [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md).

Multi-select **Web fetch** button; N/M progress; accessible summary with Apply all / Review each / Cancel.

**Gate:** Summary announced by JAWS; Apply all and Review each work; Alt+W unchanged for one book.

### Phase 3 — Import tag mapping (2–3 days)

See [plan_import_tag_mapping.md](plan_import_tag_mapping.md).

**Gate:** Defaults match today’s scan; grouping stays on album; prefs round-trip.

### Phase 4 — Check for updates (2–3 days)

See [plan_auto_update.md](plan_auto_update.md).

**Gate:** Help → Check for updates compares GitHub latest to `APP_VERSION`; offline failure is announced.

### Phase 5 — View-mode announcements (2–4 days)

See [plan_view_mode_static_text.md](plan_view_mode_static_text.md).

**Gate:** JAWS spike accepted; Book Details view mode does not say edit or read only; edit mode still says edit.

### Phase 6 — Name consistency (2–3 weeks)

See [Plan_name_consistency_check.md](Plan_name_consistency_check.md).

Does **not** require rescan. Confirm-each-group; no silent merges.

**Gate:** Author/genre merge safe; import blocked while mode active; Escape restores filters.

---

## Cross-cutting principles

1. Add or extend tests from each plan’s checklist before starting the next phase.
2. Run `python -m pytest test/` — all green before merge.
3. Test logic modules first; mock HTTP and DB in CI.
4. Include tests in the same commit/PR as the feature.
5. NVDA/JAWS smoke after each phase ([qa_verification.md](qa_verification.md)). Ship help with each feature.

Optional at Phase 1 start: fix pre-existing plot-length test fixtures in `test_web_api_unit.py` / `test_web_api_fetch.py`.

---

## What to combine vs keep separate

| Combine? | Plans | Why |
|----------|-------|-----|
| **Yes** | Background thread then API split | Split after thread so patch targets move once |
| **Yes** | Background thread then batch fetch | Batch reuses the worker |
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
| Tag mapping changes existing imports | Defaults = current album / album-artist-then-artist; grouping stays on album |
| Name consistency merges many books | Confirm each group; no silent merges |
| Tester xlsx overwritten | Never regenerate filled `AbCS_Version3_Release_Tester_Review.xlsx` |

---

## How to use this doc

1. Implement phases in order (or 3–6 in parallel after Phase 1 if staffing allows).
2. Meet each phase **gate** before the next.
3. Update [plans_status.md](plans_status.md) when a plan ships.
4. Read linked `plan_*.md` for file paths and a11y checklists.
