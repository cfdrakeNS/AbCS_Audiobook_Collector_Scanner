# Series Number in Database — Future Improvement Plan

**Status:** Planned — Version 3 Phase 12 (needs Phase 9 schema). Scope narrowed September 2026  
**Created:** June 2026  
**Related:** [plan_schema_batch.md](plan_schema_batch.md) (v3 Phase 9), [scripts/update_series_from_catalog.py](../scripts/update_series_from_catalog.py)

---

## What this is

Persist **series number** (e.g. book 3 in a series) in SQLite and Book Details.

**Scope note (2026-09):** Fetch Web Info no longer retrieves or displays series or series number. Series entry is **manual only** via Book Details, the Update window, and the offline catalog script. This plan’s UI work targets those surfaces, not the web metadata review window.

---

## Problem

Series number is not reliably stored on `Book`. Title sometimes carries `" - 3"` suffix instead.

---

## Design

- Column: `series_number INTEGER` nullable on `books` (add in schema wave if decided before version 3 coding).
- Book Details / Update window: editable small field near Series row; strip from title when number stored separately (careful migration).
- Sort: optional series order in main table — defer.

**Estimate:** 2–3 days (coordinate with Wave 0 schema if not yet shipped)

---

## Tests

Save from Book Details / Update; title/number split migration.

---

## Accessibility

Labeled field with buddy; numeric announcement.

---

## Out of scope v1

Series reading order across multiple authors; fractional numbers (3.5).
