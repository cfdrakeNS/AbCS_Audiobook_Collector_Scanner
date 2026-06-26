# Fall 2026 Enhancements — Master Roadmap



**Status:** Planning document (schedule for fall review)  

**Created:** June 2026  

**Purpose:** Single schedule for all `doc/plan_*.md` work — order, combinations, test gates, deferrals, and **your priority ranking**.



Individual plans hold **what** to build; this document holds **when**, **how**, and **priority order** for review.



**Related:** [plans_status.md](plans_status.md) (status tracking), [TESTING.md](../TESTING.md), [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md) (plain-language summary for testers)



---



## How to rank priority



In the tables below, fill **Your priority** with a number (**1** = do first among optional items, **2** = next, etc.). Leave **—** for items not yet ranked. Use the same number only when items are tied.



Suggested approach at fall review:



1. Complete **Core fall waves 0–3** first (fixed order).

2. Rank **Follow-on** and **Backlog** items by filling the priority column.

3. Re-sort Wave 4+ work by your ranks when scheduling.



---



## Core fall schedule (waves 0–5)



Fixed implementation order — rank column optional (these are already sequenced).



| Wave | Enhancement | Detail doc | Est. | Your priority | Notes |

|------|-------------|------------|------|---------------|-------|

| 0 | Schema batch (TBR, rating, cover, collection root) | [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md) § Wave 0 | 2–3 d | — | Prerequisite for many features |

| 1 | Want to Read | [plan_want_to_read.md](plan_want_to_read.md) | 3.5–4 d | — | Alt+T filter |

| 1 | Open audiobook location | [plan_audiobook_preview.md](plan_audiobook_preview.md) | ~1 d | — | Not a player |

| 2 | Ratings | [plan_ratings.md](plan_ratings.md) | 4–5 d | — | Numeric, not stars |

| 2 | Covers + zip backup | [Plan_covers.md](Plan_covers.md) | 5–6 d | — | Combine with ratings sprint |

| 3 | Rescan + collection root (A+B) | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) | ~2 wk | — | Not Part C organize |

| 4 | Name consistency (optional) | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | 2–3 wk | — | After rescan |

| 5 | Internationalization | [plan_Internationalization_overview.md](plan_Internationalization_overview.md) | 3–5 wk | — | After English freeze |

| — | Rescan Part C organize | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part C | 10–12 d | — | Defer; high risk |



**Fall core (Waves 0–3):** ~5–6 weeks. **+ Name consistency:** ~8–9 weeks. **i18n:** separate release.



---



## Follow-on enhancements (after wave 3 or between waves)



Rank these with **Your priority** to build Wave 4+ schedule.



| Enhancement | Detail doc | Est. | Suggested timing | Your priority | Notes |

|-------------|------------|------|------------------|---------------|-------|

| Path health report | [plan_path_health_report.md](plan_path_health_report.md) | 2–3 d | Wave 4 | — | Missing `path` on disk |

| Export library metadata | [plan_export_library_metadata.md](plan_export_library_metadata.md) | ~2 d | Wave 4 | — | CSV/JSON |

| Missing metadata filters | [plan_missing_metadata_filters.md](plan_missing_metadata_filters.md) | 2–3 d | After Wave 2 | — | No plot/cover/rating |

| Bulk want-to-read on selection | [plan_bulk_want_to_read_selection.md](plan_bulk_want_to_read_selection.md) | ~1 d | After Wave 1 | — | Main window selection |

| Want-to-read on Import Detail | [plan_want_to_read_import_detail.md](plan_want_to_read_import_detail.md) | ~1 d | After Wave 1 | — | During import review |

| Update window extensions | [plan_update_window_extensions.md](plan_update_window_extensions.md) | 2–3 d | After Wave 1 | — | Bulk TBR, reader |

| Scheduled backup reminder | [plan_scheduled_backup_reminder.md](plan_scheduled_backup_reminder.md) | 1–2 d | After zip backup | — | Prompt only |

| Statistics extensions | [plan_statistics_extensions.md](plan_statistics_extensions.md) | 1–2 d | After Wave 2 | — | TBR, avg rating |

| Reader / narrator filter | [plan_reader_filter.md](plan_reader_filter.md) | ~2 d | Wave 4 | — | View filter |

| Series number in DB | [plan_series_number_db.md](plan_series_number_db.md) | 2–3 d | Wave 0 add or Wave 4 | — | May batch schema |

| Preferences export/import | [plan_preferences_export_import.md](plan_preferences_export_import.md) | ~2 d | Anytime | — | Settings file |

| Bulk web metadata fetch | [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md) | 1–2 wk | Post-fall | — | Network heavy |

| Plot full-text search (FTS) | [plan_plot_fulltext_search.md](plan_plot_fulltext_search.md) | 3–5 d | Post-fall | — | Large libraries |



---



## Backlog (larger scope — rank if interested)



| Enhancement | Detail doc | Est. | Your priority | Notes |

|-------------|------------|------|---------------|-------|

| Third-party import (Libib, etc.) | [plan_third_party_import.md](plan_third_party_import.md) | 1–2 wk/format | — | Per-format adapters |

| Smart collections (saved filters) | [plan_smart_collections.md](plan_smart_collections.md) | 1–2 wk | — | Virtual lists |

| Reading progress / bookmark | [plan_reading_progress.md](plan_reading_progress.md) | 2–3 wk+ | — | Beyond read_date |

| Book tags (multi-label) | [plan_book_tags.md](plan_book_tags.md) | 2–3 wk | — | Many-to-many |

| macOS installer | [plan_macos_installer.md](plan_macos_installer.md) | 1–2 wk | — | Platform expansion |

| Auto-update check | [plan_auto_update.md](plan_auto_update.md) | 2–3 d | — | Check only, no silent install |



---



## Maintenance (no user feature — schedule between waves)



| Item | Detail doc | Est. | Your priority | Notes |

|------|------------|------|---------------|-------|

| CI / test hardening | [plan_ci_test_hardening.md](plan_ci_test_hardening.md) | 1–2 d | — | Ongoing discipline |

| Vulture dead-code cleanup | [plan_vulture_dead_code_cleanup.md](plan_vulture_dead_code_cleanup.md) | 0.5–1 d | — | Between waves |



---



## Cross-cutting principles



### Unit testing as you go



For **every wave**, before starting the next:



1. Add or extend tests from that plan’s test checklist.

2. Run `python -m pytest test/` — all green before merge.

3. Test **logic modules first** before heavy UI tests.

4. Mock DB, filesystem, and HTTP in CI.

5. Include tests in the **same commit/PR** as the feature.



### Schema — batch once (Wave 0)



| Table | New columns |

|-------|-------------|

| `books` | `want_to_read`, `rating`, `ratings_count`, `cover_path` |

| `collections` | `root_path` |



Optional add to Wave 0 if prioritized: `series_number` ([plan_series_number_db.md](plan_series_number_db.md)).



### Accessibility and help



NVDA/JAWS smoke after each wave ([qa_verification.md](qa_verification.md)). Ship help with each feature.



---



## What to combine vs keep separate



| Combine in one sprint? | Plans | Why |

|------------------------|-------|-----|

| **Yes** | Ratings + Covers + zip backup | Shared web metadata save path |

| **Yes** | Rescan Part A + Part B | One doc; root_path enables rescan |

| **Yes** | Want to Read + Open location | ~5 days; shared Book Details touch |

| **Yes** | Path health + Export metadata | Both library hygiene; ~4–5 days |

| **No** | i18n | After feature freeze |

| **No** | Bulk web metadata | Separate release |

| **No** | Rescan Part C organize | High risk |



---



## Wave details (summary)



### Wave 0 — Foundation (2–3 days)



Batch schema; model/query updates; tests.



**Gate:** pytest green; import and legacy backup work.



### Wave 1 — Quick UX (4–5 days)



Want to Read + Open location. See [plan_want_to_read.md](plan_want_to_read.md), [plan_audiobook_preview.md](plan_audiobook_preview.md).



**Gate:** Alt+T filter; open folder; help updated.



### Wave 2 — Web enrichment (9–11 days)



Ratings + Covers + zip backup. See [plan_ratings.md](plan_ratings.md), [Plan_covers.md](Plan_covers.md).



**Gate:** Rating column; cover on save; zip backup round-trip.



### Wave 3 — Library maintenance (10–12 days)



Rescan A+B. See [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md).



**Gate:** Rescan updates file fields; tag overwrite off by default.



### Wave 4+ — Your ranked follow-on



Pick from **Follow-on** and **Backlog** tables using **Your priority** column.



### Wave 5 — i18n



[plan_Internationalization_overview.md](plan_Internationalization_overview.md) — after English stable.



---



## Release milestones



| Release | Contents | Version |

|---------|----------|---------|

| R1 | Wave 0 + 1 | minor |

| R2 | Wave 2 | minor |

| R3 | Wave 3 | minor |

| R4 | Ranked follow-on items | minor |

| R5 | i18n | minor or major |



---



## Risks and mitigations



| Risk | Mitigation |

|------|------------|

| Book Details crowded | Wave 1 layout first; cover above grid in Wave 2 |

| Web Metadata save regression | Tests; single save refactor |

| Legacy `.db` restore | Keep `.db` path; test zip and non-zip |

| Too many follow-on items | Use **Your priority** column; defer backlog |

| i18n during features | Wave 5 only |



---



## How to use this doc



1. **Fall review** — confirm waves 0–3; rank follow-on/backlog in tables above.

2. **During implementation** — meet each wave **gate** before the next.

3. **Status** — update [plans_status.md](plans_status.md) when a plan ships.

4. **Detail** — read linked `plan_*.md` for file paths and a11y checklists.



---



## Next steps



Fill **Your priority** in the follow-on and backlog tables. Confirm Wave 0 start date. Begin schema batch + tests.


