# Series Number in Database — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Web Metadata](../src/ui/web_metadata.py), [plan_ratings.md](plan_ratings.md) (Wave 0 schema batch)

---

## What this is

Persist **series number** (e.g. book 3 in a series) in SQLite and Book Details — today web metadata shows it but DB persistence is incomplete (`series_number` removed from queries historically).

---

## Problem

Series number appears in Web Metadata UI; not reliably stored on `Book`. Title sometimes carries `" - 3"` suffix instead.

---

## Design

- Column: `series_number INTEGER` nullable on `books` (add in schema wave if decided before fall coding).
- Web Metadata save writes column; strip from title when number stored separately (careful migration).
- Book Details: optional read-only or editable small field near Series row.
- Sort: optional series order in main table — defer.

**Estimate:** 2–3 days (coordinate with Wave 0 schema if not yet shipped)

---

## Tests

Save from web metadata; title/number split migration.

---

## Accessibility

Labeled field with buddy; numeric announcement.

---

## Out of scope v1

Series reading order across multiple authors; fractional numbers (3.5).
