# Statistics Extensions — Version 3 Phase 23 / F08

**Status:** Complete  
**Created:** June 2026  
**Estimate:** 0.5–1 day  
**Tester ID:** F08 (v3 scope: Want to Read and listening progress only)  
**Related:** [Statistics](../help_docs/14_statistics.md), [plan_want_to_read.md](plan_want_to_read.md), [plan_reading_progress.md](plan_reading_progress.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

Two rows on the **Statistics** dialog:

1. Books Want to Read (`want_to_read`)
2. Books In Progress (`listen_position_ms IS NOT NULL`)

---

## Shipped

- `Statistics.books_want_to_read` / `books_in_progress` and queries in `StatisticsQueries.get_statistics`
- Rows in `StatisticsDialog`
- Tests in `test_named_queries.py` and `test_small_dialogs.py`
- Help topic `14_statistics.md` updated

---

## Out of scope (unchanged)

Average rating; books with covers; missing path; charts; export.
