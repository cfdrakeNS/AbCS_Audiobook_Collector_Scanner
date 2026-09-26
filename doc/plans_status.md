# AbCS Development Plans — Status

**Last updated:** September 2026 (tester build **2.19**. v3 Phases 1–4 and 6–13 complete; 1–4 and 6–12 tester accepted. Phase 13 name-list merge implemented. Phases 15 and 17 covers implemented. Phases 19, 18, 20, 22, 21, and 23 complete (18–20 tester accepted; 22 Import Detail layout done; 21 full Play player implemented; 23 Statistics Want to Read / In Progress). Next: Phase 24 F01 Path health, Phase 25 Want to read and playing; optional Phase 14; Phase 16 help last. Ratings, tags, and web cover files stay out of v3. Library-wide fuzzy name scan deferred.)

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
| 6 | Import tag mapping (title / author) | [plan_import_tag_mapping.md](plan_import_tag_mapping.md) | Complete — tester accepted |
| 7 | Auto-update check | [plan_auto_update.md](plan_auto_update.md) | Complete — tester accepted |
| 8 | Keep current book on sort and filter | [plan_keep_book_focus.md](plan_keep_book_focus.md) | Complete — tester accepted |
| 9 | Schema batch (in-place upgrade) | [plan_schema_batch.md](plan_schema_batch.md) | Complete — tester accepted |
| 10 | Series book number | [plan_series_number_db.md](plan_series_number_db.md) | Complete — tester accepted |
| 11 | Collection library root (Part A) | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part A | Complete — tester accepted |
| 12 | Preview audiobook (in-app player) | [plan_audiobook_preview.md](plan_audiobook_preview.md) | Complete — tester accepted |
| 13 | Name-list merge on duplicate | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | Complete — implemented in 2.18; library scan deferred |
| 15 | Preview cover (embedded art) | [plan_preview_cover.md](plan_preview_cover.md) | Implemented |
| 17 | Book Details cover (embedded art) | [plan_book_details_cover.md](plan_book_details_cover.md) | Implemented |
| 19 | Want to read and listening progress columns | [plan_want_to_read.md](plan_want_to_read.md), [plan_reading_progress.md](plan_reading_progress.md) | Tester accepted |
| 18 | Book Details layout, cover on the right | [plan_book_details_layout.md](plan_book_details_layout.md) | Tester accepted. Date/year validation bug fix done — [fix_read_date.md](fix_read_date.md). |
| 20 | Want to read | [plan_want_to_read.md](plan_want_to_read.md) | Tester accepted. Filter, View menu, Edit → Add to want to read, and selection Add and Clear. Import Detail stays deferred. |
| 22 | Import Detail layout, no cover | [plan_import_detail_layout.md](plan_import_detail_layout.md) | Complete — layout, Keep/Discard, status bar; tester. |
| 21 | Full Play player | [plan_preview_player_later.md](plan_preview_player_later.md) | Implemented — next/prev, seek, speed, resume, In progress filter |
| 23 | F08 Statistics (Want to Read + listening progress) | [plan_statistics_extensions.md](plan_statistics_extensions.md) | Complete — Books Want to Read and Books In Progress rows |
| 24 | F01 Path health report | [plan_path_health_report.md](plan_path_health_report.md) | Planned — next after Phase 23 |
| 25 | Want to read and playing filter | [plan_want_to_read_and_playing_filter.md](plan_want_to_read_and_playing_filter.md) | Planned — after Phase 24 |
| 14 | View-mode static text (JAWS) | [plan_view_mode_static_text.md](plan_view_mode_static_text.md) | Planned — optional, before help |
| 16 | Help docs review | [plan_help_docs_review.md](plan_help_docs_review.md) | Planned — last |
| — | First-start screen reader Zoom message | [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md) | To do. First start with a screen reader sets Zoom to Normal, then speaks that once and how to change it in Preferences. |

---

## Deferred after version 3

| Plan | Location |
|------|----------|
| Non-modal web fetch jobs | [plan_web_fetch_nonmodal_job.md](plan_web_fetch_nonmodal_job.md) — out of scope for v3 (too risky) |
| Book ratings | [plan_ratings.md](plan_ratings.md) — out of scope for v3 UI |
| Covers + zip backup | [Plan_covers.md](Plan_covers.md) — web cover files; out of scope for v3 UI |
| Library-wide fuzzy name scan | Deferred after v3 — see [Plan_name_consistency_check.md](Plan_name_consistency_check.md) |
| Internationalization | [plan_Internationalization_overview.md](plan_Internationalization_overview.md) |
| Export library metadata | [plan_export_library_metadata.md](plan_export_library_metadata.md) |
| Missing metadata filters | [plan_missing_metadata_filters.md](plan_missing_metadata_filters.md) |
| Bulk want-to-read on selection | [plan_bulk_want_to_read_selection.md](plan_bulk_want_to_read_selection.md) |
| Want-to-read on Import Detail | [plan_want_to_read_import_detail.md](plan_want_to_read_import_detail.md) |
| Update window extensions | [plan_update_window_extensions.md](plan_update_window_extensions.md) |
| Scheduled backup reminder | [plan_scheduled_backup_reminder.md](plan_scheduled_backup_reminder.md) |
| Reader filter | [plan_reader_filter.md](plan_reader_filter.md) |
| Preferences export/import | [plan_preferences_export_import.md](plan_preferences_export_import.md) |
| Import window action toolbar | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) |
| Preferences mini-toolbar | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) |
| Third-party import | [plan_third_party_import.md](plan_third_party_import.md) |
| Smart collections | [plan_smart_collections.md](plan_smart_collections.md) |
| Book tags | [plan_book_tags.md](plan_book_tags.md) — out of scope for v3 |

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
- **Date and year validation bug fix** (testing miss after Phase 18/20): [fix_read_date.md](fix_read_date.md) — typed fields for screen readers, Preferences year range, no future dates, Clear/blank classic dates, single-letter scaled calendars. Keep out of AGENTS/standards until a broader review.

Treat this document and [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md) as the source of truth.

---

## Related

- Manual QA log: [qa_verification.md](qa_verification.md)
- Dead-code review: [CLEANUP_VULTURE_FINDINGS.md](CLEANUP_VULTURE_FINDINGS.md)
- Messages reference: [import_and_web_metadata_messages_reference.md](import_and_web_metadata_messages_reference.md)
- Archived (local `archive/`, gitignored): cancelled macOS installer plan, Linux fixes sign-off, launch open questions, July 2026 tester changelog, git history CSVs, Sep 2026 code inventory
