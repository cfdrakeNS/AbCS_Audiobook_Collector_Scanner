# Third-Party Library Import — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Import Book List](help_docs/20_import_book_list_explained.md)

---

## What this is

Import metadata from **other apps' export formats** (e.g. Libib CSV, Audible library export, Goodreads) — beyond AbCS book list template.

---

## Problem

Users migrating from other tools must manually map columns or edit spreadsheets.

---

## Design

- Per-format adapters in `src/core/import_adapters/` mapping columns → AbCS book fields.
- UI: **Import → From other app…** wizard — pick format, map preview, import like book list.
- Legal/API: use **user-exported files only**; no Audible API scraping.

**Estimate:** 1–2 weeks per format; start with one popular CSV export

---

## Tests

Fixture CSV per format; duplicate handling.

---

## Risks

Export format changes from third parties; maintenance burden.

---

## Out of scope v1

Live API sync; DRM content import.
