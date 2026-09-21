# Leading Article Title Compare — Version 3 Phase 3

**Status:** Complete — Phase 3 (revised after tester: same-work match, still offer web title)

Path B: optional leading A/An/The means **the same work** (`web_titles_match`). The review window **still offers the web title** when the catalog has A/An/The and the library does not, so you can save the web wording. Trailing `Hobbit, The` vs `The Hobbit` is not offered.

Does **not** change Path A search ranking.

---

## Tester gate

1. Book titled `Second Chance - 05` vs web `A Second Chance - 05` is still a match, and the review window **offers** the web title.
2. Trailing article and series-suffix cases from 2.14 still match and are not offered as title changes.
3. A genuine extra subtitle still shows as a title difference.
4. Alt+W and batch Review still behave as before aside from this compare.

---

## Out of scope

Changing Path A overlap search; author compare; hiding real subtitle or series-name differences.
