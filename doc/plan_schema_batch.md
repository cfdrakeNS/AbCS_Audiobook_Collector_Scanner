# Schema batch (in-place upgrade) — Version 3 Phase 9 / C01

**Status:** Complete — tester accepted. Version 3 Phase 9.  
**Created:** June 2026  
**Updated:** September 2026  
**Related:** [connection.py](../src/database/connection.py), [plan_series_number_db.md](plan_series_number_db.md), [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part A, [plan_ratings.md](plan_ratings.md), [plan_want_to_read.md](plan_want_to_read.md), [Plan_covers.md](Plan_covers.md)

---

## What this is

Behind-the-scenes database upgrade on **first start** of a new AbCS build. Converts **existing** libraries in place (not only new installs). Adds storage for series number only. **No new buttons** in this phase. Want to Read, ratings, and covers are out of v3, so this upgrade does not add their columns. Collection `root_path` is added in Phase 11, not here.

Existing libraries keep their books. A timestamped `schema_repair` backup is taken before `ALTER TABLE`.

---

## Columns (one upgrade)

`books`:

- `series_number REAL`

**Used by v3 UI after this phase:** `series_number` (Phase 10).

Do not add `want_to_read`, `rating`, `ratings_count`, `cover_path`, or `collections.root_path` in this upgrade. Want to Read, ratings, and covers are out of v3. `root_path` is added when Phase 11 is built.

---

## How

[`_ensure_legacy_schema_compatibility`](../src/database/connection.py) already adds missing names from `column_specs`. Also update `table_create_sql` and [`test/fixtures/abcdDB_def.sql`](../test/fixtures/abcdDB_def.sql) for new databases. Do **not** add these names to `critical_columns` (that path rebuilds / wipes the file).

Map new fields on `Book` / `Collection` with defaults so `SELECT b.*` stays safe.

Announce the upgrade on first start for **dev and installed** builds (accessible dialog or status), not only the frozen native popup.

**Failure / backup:** If `ALTER TABLE` fails after backup, leave the live DB as-is, surface the error, and point the user at the `schema_repair` backup file. Do not treat missing optional columns as `critical_columns` (rebuild path). AbCS uses a single user `abcs.db` path from `get_user_data_dir()`; there is no multi-DB migration loop in this phase.

---

## Tests

Open a copy of the current schema, call `initialize_database()`, assert `series_number` exists, existing rows unchanged, `series_number` is NULL, backup file created. Assert `want_to_read`, `rating`, and `cover_path` were not added. Phase 11 later adds `collections.root_path` on the same first-start path; a fully legacy library now receives both columns.

---

## Gate

Old `abcs.db` opens, books still there, new columns present, screen reader hears the upgrade line once.
