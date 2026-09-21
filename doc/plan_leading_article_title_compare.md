# Leading Article Title Compare — Version 3 Phase 3

**Status:** Planned — Phase 3  
**Created:** September 2026  
**Related:** [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md), [Web_Metadata_Title_Compare_Reference.md](Web_Metadata_Title_Compare_Reference.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

Path B review compare (`web_titles_match` / `web_compare_title_key`) still treats a **leading** A/An/The on one side only as a title change. That is a gap after 2.14, not covered by batch UI work.

**Shipped in 2.14** (`74341ee`): **trailing** article position (`The Hobbit` = `Hobbit, The`) and series suffixes (`Triptych` = `Triptych - 01`). Help calls this “article position.” Tests cover that pair only.

**Still open:** `A Second Chance - 05` vs `Second Chance - 05` (keys `asecondchance` vs `secondchance`). Same for `The` / `An`. Review checkboxes and batch “new information” can both flag a false title difference.

---

## To correct

1. Tests in the existing web matching suite: `A Second Chance - 05` vs `Second Chance - 05`, plus `The` / `An`, and a negative case that a real extra subtitle still differs.
2. Fold optional leading A/An/The in `web_compare_title_key` (see `src/utils/text_utils.py`) without hiding subtitle differences.
3. Update [Web_Metadata_Title_Compare_Reference.md](Web_Metadata_Title_Compare_Reference.md) and help if it still oversells “article position.”

Does **not** change Path A search ranking. Review/compare Path B only.

---

## Tester gate

1. Book titled `Second Chance - 05` vs web `A Second Chance - 05` (or the reverse) does **not** show a title change.
2. Trailing article and series-suffix cases from 2.14 still match.
3. A genuine extra subtitle still shows as a title difference.
4. Alt+W and batch Review still behave as before aside from this compare.

---

## Out of scope

Changing Path A overlap search; author compare; hiding real subtitle or series-name differences.
