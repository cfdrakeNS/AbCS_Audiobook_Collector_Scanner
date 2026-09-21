# AbCS Development Plans — Status

**Last updated:** September 2026 (v3 Phases 1–4 complete. Later batch polish: wider progress and summary, short Issue text, Google limit sentence on the summary. Phase 5 not started.)

**Version 3 release schedule master:** [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md). Cross-cutting **Accessibility and UI formatting standards** (buttons, dialogs, focus, styles) apply to every phase.

**Tester summary (plain language):** [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md)

**Tester workbook (do not overwrite filled answers):** [AbCS_Version3_Release_Tester_Review.xlsx](AbCS_Version3_Release_Tester_Review.xlsx)

**Public launch plan:** [launch_plan.md](launch_plan.md)

**Branch:** work from `main` (or a short-lived phase branch per feature)

All Cursor development plans from the 2025–2026 AbCS rollout are **complete** except the items listed below.

---

## Active — version 3

| Phase | Plan | Location | Status |
|-------|------|----------|--------|
| — | **Version 3 release roadmap** | [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md) | Schedule master |
| 1 | Web fetch background thread + API split | [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md) | Complete — tester accepted |
| 2 | Bulk web metadata | [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md) | Complete — tester accepted |
| 3 | Leading article title compare (Path B) | [plan_leading_article_title_compare.md](plan_leading_article_title_compare.md) | Complete |
| 4 | Selection mode toolbar and shortcuts | [plan_selection_mode_toolbar.md](plan_selection_mode_toolbar.md) | Complete |
| 5 | Non-modal web fetch jobs | [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) | Not started — next, separate from Phases 1–4 |
| 6 | Import tag mapping (title / author) | [plan_import_tag_mapping.md](plan_import_tag_mapping.md) | Planned — Phase 6 |
| 7 | Auto-update check | [plan_auto_update.md](plan_auto_update.md) | Planned — Phase 7 |
| 8 | Name Consistency Check | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | Planned — Phase 8 |
| 9 | View-mode static text (JAWS) | [plan_view_mode_static_text.md](plan_view_mode_static_text.md) | Planned — Phase 9 (optional) |

---

## Deferred after version 3

| Plan | Location |
|------|----------|
| Want to Read | [plan_want_to_read.md](plan_want_to_read.md) |
| Open audiobook location | [plan_audiobook_preview.md](plan_audiobook_preview.md) |
| Ratings | [plan_ratings.md](plan_ratings.md) |
| Covers + zip backup | [Plan_covers.md](Plan_covers.md) |
| Rescan / library folders | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) |
| Internationalization | [plan_Internationalization_overview.md](plan_Internationalization_overview.md) |
| Path health report | [plan_path_health_report.md](plan_path_health_report.md) |
| Export library metadata | [plan_export_library_metadata.md](plan_export_library_metadata.md) |
| Missing metadata filters | [plan_missing_metadata_filters.md](plan_missing_metadata_filters.md) |
| Bulk want-to-read on selection | [plan_bulk_want_to_read_selection.md](plan_bulk_want_to_read_selection.md) |
| Want-to-read on Import Detail | [plan_want_to_read_import_detail.md](plan_want_to_read_import_detail.md) |
| Update window extensions | [plan_update_window_extensions.md](plan_update_window_extensions.md) |
| Scheduled backup reminder | [plan_scheduled_backup_reminder.md](plan_scheduled_backup_reminder.md) |
| Statistics extensions | [plan_statistics_extensions.md](plan_statistics_extensions.md) |
| Reader filter | [plan_reader_filter.md](plan_reader_filter.md) |
| Series number in DB | [plan_series_number_db.md](plan_series_number_db.md) |
| Preferences export/import | [plan_preferences_export_import.md](plan_preferences_export_import.md) |
| Import window action toolbar | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) |
| Preferences mini-toolbar | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) |
| Third-party import | [plan_third_party_import.md](plan_third_party_import.md) |
| Smart collections | [plan_smart_collections.md](plan_smart_collections.md) |
| Reading progress | [plan_reading_progress.md](plan_reading_progress.md) |
| Book tags | [plan_book_tags.md](plan_book_tags.md) |

---

## Active — maintenance

| Plan | Location |
|------|----------|
| CI / test hardening | [plan_ci_test_hardening.md](plan_ci_test_hardening.md) |
| Vulture dead-code cleanup | [plan_vulture_dead_code_cleanup.md](plan_vulture_dead_code_cleanup.md) |

---

## Cancelled / dropped

| Plan | Location | Why |
|------|----------|-----|
| macOS installer | [plan_macos_installer.md](../archive/plan_macos_installer.md) | Dropped — too complex/expensive; macOS from source. See [launch_plan.md](launch_plan.md). |
| Plot full-text search | (deleted) | Dropped — mis-framed as web fetch speedup; not selected for v3. |

---

## Completed

- Help system rollout (dynamic `help_docs/`, Help window navigation, Shift+F1 routing)
- README, INSTALL, AGENTS, and user guide refresh
- Status bar unification
- Plot filter and title-plot indicator
- Recently added filter
- Screen reader row reading and Narrator detection
- Web fetch/matching improvements
- **Web fetch Phases 1–5 (complete in 2.10):** budget, cooperative cancel, shared HTTP, cache, `web_fetch_service` — Phase 6 is now v3 Phase 1: [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md)
- **Web fetch series removal + title/author compare (complete):** commit `74341ee`
- Name list accessibility and focus
- Book details layout and performance
- JAWS Book Details label fix
- Toolbar/filter shortcuts
- Book List Import progress window
- Linux combo and packaging fixes
- Dynamic SQLite pragmas
- Duplicate mode, import, collections, backup/restore, reading history, statistics, preferences

Treat this document and [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md) as the source of truth.

---

## Related

- Manual QA log: [qa_verification.md](qa_verification.md)
- Dead-code review: [CLEANUP_VULTURE_FINDINGS.md](CLEANUP_VULTURE_FINDINGS.md)
- Messages reference: [import_and_web_metadata_messages_reference.md](import_and_web_metadata_messages_reference.md)
- Archived (local `archive/`, gitignored): cancelled macOS installer plan, Linux fixes sign-off, launch open questions, July 2026 tester changelog, git history CSVs, Sep 2026 code inventory
