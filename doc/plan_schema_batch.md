# Schema batch (in-place upgrade) — Version 3 Phase 9 / C01

**Status:** Planned — Version 3 Phase 9 (next after Phase 8 tester accept)  
**Created:** June 2026  
**Updated:** September 2026  
**Related:** [connection.py](../src/database/connection.py), [plan_ratings.md](plan_ratings.md), [plan_series_number_db.md](plan_series_number_db.md), [plan_want_to_read.md](plan_want_to_read.md), [Plan_covers.md](Plan_covers.md)

---

## What this is

Behind-the-scenes database upgrade on **first start** of a new AbCS build. Adds storage for later features. **No new buttons** in this phase.

Existing libraries keep their books. A timestamped `schema_repair` backup is taken before `ALTER TABLE`.

---

## Columns (one upgrade)

`books`:

- `want_to_read INTEGER DEFAULT 0`
- `rating REAL`
- `ratings_count INTEGER`
- `cover_path TEXT`
- `series_number INTEGER`

`collections`:

- `root_path TEXT`

Want to Read and covers **UI** stay deferred. Ratings (Phase 11) and series number (Phase 12) use these columns after this phase.

---

## How

[`_ensure_legacy_schema_compatibility`](../src/database/connection.py) already adds missing names from `column_specs`. Also update `table_create_sql` and [`test/fixtures/abcdDB_def.sql`](../test/fixtures/abcdDB_def.sql) for new databases. Do **not** add these names to `critical_columns` (that path rebuilds the file).

Map new fields on `Book` / `Collection` with defaults so `SELECT b.*` stays safe.

Announce the upgrade on first start for **dev and installed** builds (accessible dialog or status), not only the frozen native popup.

---

## Tests

Open a copy of the current schema, call `initialize_database()`, assert new columns exist, existing rows unchanged, `want_to_read` is 0, other new columns NULL, backup file created.

---

## Gate

Old `abcs.db` opens, books still there, new columns present, screen reader hears the upgrade line once.
