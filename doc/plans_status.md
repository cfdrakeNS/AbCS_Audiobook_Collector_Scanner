# AbCS Development Plans — Status



**Last updated:** September 2026 (doc archive tidy + Version 3 rename)



**Version 3 release schedule master:** [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md) — waves, combined sprints, test gates, **priority ranking column**.

**Tester summary (plain language):** [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md)

**Public launch plan:** [launch_plan.md](launch_plan.md) — decisions and pre-launch checklist (repo visibility, license wording, code signing, macOS scope, donation link).



All Cursor development plans from the 2025–2026 AbCS rollout are **complete** except the items listed under Active (future work) below.



## Active — core version 3 (waves 0–3)



| Plan | Location | Status |

|------|----------|--------|

| **Version 3 release roadmap** | [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md) | Schedule master |

| Want to Read | [plan_want_to_read.md](plan_want_to_read.md) | Planned |

| Open audiobook location | [plan_audiobook_preview.md](plan_audiobook_preview.md) | Planned |

| Ratings | [plan_ratings.md](plan_ratings.md) | Planned |

| Covers + zip backup | [Plan_covers.md](Plan_covers.md) | Planned |

| Rescan / library folders | [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) | Planned |



## Active — optional / later waves



| Plan | Location | Status |

|------|----------|--------|

| Name Consistency Check | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | Planned — wave 4 optional |

| Internationalization | [plan_Internationalization_overview.md](plan_Internationalization_overview.md) | Planned — wave 5 |



## Active — follow-on enhancements (rank in roadmap)



| Plan | Location |

|------|----------|

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

| Bulk web metadata | [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md) |

| Web fetch background thread + API split | [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md) |

| Import window action toolbar | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) — deferred June visual appeal item |

| Preferences mini-toolbar | [visual-appeal-full-plan-3899a9.md](../archive/visual-appeal-full-plan-3899a9.md) — deferred June visual appeal item |

| View-mode static text (JAWS) | [plan_view_mode_static_text.md](plan_view_mode_static_text.md) — silence edit/read-only noise without misleading “edit” |




## Active — backlog (larger scope)



| Plan | Location |

|------|----------|

| Third-party import | [plan_third_party_import.md](plan_third_party_import.md) |

| Smart collections | [plan_smart_collections.md](plan_smart_collections.md) |

| Reading progress | [plan_reading_progress.md](plan_reading_progress.md) |

| Book tags | [plan_book_tags.md](plan_book_tags.md) |

| Auto-update check | [plan_auto_update.md](plan_auto_update.md) |



## Active — maintenance



| Plan | Location |

|------|----------|

| CI / test hardening | [plan_ci_test_hardening.md](plan_ci_test_hardening.md) |

| Vulture dead-code cleanup | [plan_vulture_dead_code_cleanup.md](plan_vulture_dead_code_cleanup.md) |



## Cancelled / dropped

| Plan | Location | Why |
|------|----------|-----|
| macOS installer | [plan_macos_installer.md](../archive/plan_macos_installer.md) | Dropped from roadmap — too complex/expensive for the value; macOS still supported by running from source. See [launch_plan.md](launch_plan.md). |

## Completed



The following plan areas were implemented and verified in code:



- Help system rollout (dynamic `help_docs/`, Help window navigation, Shift+F1 routing)

- README, INSTALL, AGENTS, and user guide refresh

- Status bar unification

- Plot filter and title-plot indicator

- Recently added filter

- Screen reader row reading and Narrator detection

- Web fetch/matching improvements

- **Web fetch Phases 1–5 (complete in 2.10):** budget, cooperative cancel, shared HTTP, cache, `web_fetch_service`, inert-pref removal, cleanup, tests — Phase 6 deferred: [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md)

- **Web fetch series removal + title/author compare (complete):** drop series enrichment and Series row; tolerant title/author matching; plot cache/stub/status polish — commit `74341ee`; background thread still deferred

- Name list accessibility and focus

- Book details layout and performance

- JAWS Book Details label fix (Insert+W pilot — code complete; formal verification checklist closed, not tracked)

- Toolbar/filter shortcuts

- Book List Import progress window + 2.10 cancel/counter parity ([plan_book_list_import_progress.md](../archive/plan_book_list_import_progress.md))

- Linux combo and packaging fixes (VM sign-off complete — see [abcs_linux_fixes.md](../archive/abcs_linux_fixes.md))

- Dynamic SQLite pragmas

- Duplicate mode, import, collections, backup/restore, reading history, statistics, preferences



Cursor plan files under `.cursor/plans/` on the development machine may still show stale `pending` todos for superseded work. Treat this document and [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md) as the source of truth.



## Related



- Manual QA log: [qa_verification.md](qa_verification.md)

- Dead-code review: [CLEANUP_VULTURE_FINDINGS.md](CLEANUP_VULTURE_FINDINGS.md)

- Messages reference (import + web): [import_and_web_metadata_messages_reference.md](import_and_web_metadata_messages_reference.md)

- Archived (local `archive/`, gitignored): cancelled macOS installer plan, Linux fixes sign-off, launch open questions, July 2026 tester changelog, git history CSVs, Sep 2026 code inventory
