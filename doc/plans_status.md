# AbCS Development Plans — Status



**Last updated:** June 2026



**Fall schedule master:** [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md) — waves, combined sprints, test gates, **priority ranking column**.

**Tester summary (plain language):** [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md)



All Cursor development plans from the 2025–2026 AbCS rollout are **complete** except the items listed under Active (future work) below.



## Active — core fall (waves 0–3)



| Plan | Location | Status |

|------|----------|--------|

| **Fall 2026 roadmap** | [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md) | Schedule master |

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

| Plot full-text search | [plan_plot_fulltext_search.md](plan_plot_fulltext_search.md) |



## Active — backlog (larger scope)



| Plan | Location |

|------|----------|

| Third-party import | [plan_third_party_import.md](plan_third_party_import.md) |

| Smart collections | [plan_smart_collections.md](plan_smart_collections.md) |

| Reading progress | [plan_reading_progress.md](plan_reading_progress.md) |

| Book tags | [plan_book_tags.md](plan_book_tags.md) |

| macOS installer | [plan_macos_installer.md](plan_macos_installer.md) |

| Auto-update check | [plan_auto_update.md](plan_auto_update.md) |



## Active — maintenance



| Plan | Location |

|------|----------|

| CI / test hardening | [plan_ci_test_hardening.md](plan_ci_test_hardening.md) |

| Vulture dead-code cleanup | [plan_vulture_dead_code_cleanup.md](plan_vulture_dead_code_cleanup.md) |



## Completed



The following plan areas were implemented and verified in code:



- Help system rollout (dynamic `help_docs/`, Help window navigation, Shift+F1 routing)

- README, INSTALL, AGENTS, and user guide refresh

- Status bar unification

- Plot filter and title-plot indicator

- Recently added filter

- Screen reader row reading and Narrator detection

- Web fetch/matching improvements

- Name list accessibility and focus

- Book details layout and performance

- JAWS Book Details label fix (Insert+W pilot — code complete; formal verification checklist closed, not tracked)

- Toolbar/filter shortcuts

- Linux combo and packaging fixes (VM sign-off complete — see [abcs_linux_fixes.md](../abcs_linux_fixes.md))

- Dynamic SQLite pragmas

- Duplicate mode, import, collections, backup/restore, reading history, statistics, preferences



Cursor plan files under `.cursor/plans/` on the development machine may still show stale `pending` todos for superseded work. Treat this document and [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md) as the source of truth.



## Related



- Manual QA log: [qa_verification.md](qa_verification.md)

- Dead-code review: [CLEANUP_VULTURE_FINDINGS.md](../CLEANUP_VULTURE_FINDINGS.md)


