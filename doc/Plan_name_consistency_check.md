# Name Consistency — Version 3 Phase 13

**Status:** Phase 13 — **Complete** (name-list merge on duplicate in tester build 2.18; Tab/Ctrl find-focus bugs fixed; Copy documented; library-wide fuzzy scan deferred after v3)  
**Created:** June 2026  
**Updated:** September 2026  
**Related:** [Name List Process](../help_docs/15_name_list.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What Phase 13 is (v3)

When you edit an **author**, **series**, or **genre** in the Name List and type a name that already exists, AbCS asks whether to move that name’s books onto the existing name.

Example: editing **87 Precinct** to **87th Precinct**.

1. Save asks: `A series with this name already exists. Update 4 books from 87 Precinct to 87th Precinct?` Yes / No. **No** is the default.
2. **No** leaves names and books unchanged (`Duplicate series name.`).
3. **Yes** reassigns every book from the name being edited onto the existing name, deletes the old name row, then shows `4 books. Series changed from 87 Precinct to 87th Precinct.` The same sentence is the status announcement. Series numbers on books stay as they are.
4. A case-only change on the **same** row still uses the two-step rename. No merge question.
5. **Collections** keep the warning only. A collection also has an active flag and a library root, so moving its books is a different decision.
6. After Save, focus moves to the updated or kept list row.
7. Tab stops on the list (Find → list → Name → buttons). Alt+L also focuses the list. Escape in Find clears the filter if needed and returns focus to the list without closing the window. Ctrl+C and other chords stay on the list while a find filter is active.
8. **Copy:** Right-click a row (or Menu key) → **Copy**, or **Ctrl+C**, copies the selected name. Status shows `Copied.` without moving focus. Same pattern on the main book list for the focused cell — see [Find and Filters](../help_docs/03_find_filters.md) and [Name List](../help_docs/15_name_list.md).

### Follow-up bug fixes (tester)

**Status:** Fixed.

| Issue | Fix |
|-------|-----|
| After Find, pressing Ctrl moved focus back to Find (Ctrl+C failed) | List keeps StrongFocus during a filter; typing-to-Find ignores Ctrl/Alt/Meta and modifier-only keys |
| Tab skipped the list | Tab order is Find → list → Name → buttons; Alt+L still works |

### Implementation

| Area | Location |
|------|----------|
| Save prompt and result | [`src/ui/name_list_window.py`](../src/ui/name_list_window.py) |
| Reassign + delete source | `AuthorQueries.merge` / `SeriesQueries.merge` / `GenreQueries.merge` in [`src/database/queries.py`](../src/database/queries.py) |
| Copy (Ctrl+C / right-click) | [`src/ui/table_clipboard.py`](../src/ui/table_clipboard.py); wired in name list and main book list |
| Help | [`help_docs/15_name_list.md`](../help_docs/15_name_list.md), [`help_docs/03_find_filters.md`](../help_docs/03_find_filters.md), [`help_docs/16_shortcuts.md`](../help_docs/16_shortcuts.md) |
| Tests | [`test/test_name_list_merge.py`](../test/test_name_list_merge.py), [`test/test_table_clipboard.py`](../test/test_table_clipboard.py) |

### Gate

- Yes moves books and deletes the edited name; No changes nothing
- Same-row case change does not ask
- Author, series, and genre share the path; collection stays warning-only
- JAWS hears the question and the result sentence
- After Save, focus is on the kept or updated row
- Tab stops on the list; Escape in Find returns to the list; Ctrl chords stay on the list during find
- Ctrl+C and right-click Copy put the selected name on the clipboard

---

## Deferred after Version 3 — library-wide fuzzy scan

The original plan was a post-import cleanup tool modeled on **Duplicate Mode**: scan the library for similar author, title, and genre spellings, group them, and merge after the user confirms each group. That flow is more powerful for finding spellings you have not opened, but it is heavier and less discoverable than the name-list offer.

Partial engine and review UI already exist and are **not** on a menu:

- [`src/core/name_consistency.py`](../src/core/name_consistency.py)
- [`src/ui/name_consistency_window.py`](../src/ui/name_consistency_window.py)
- [`help_docs/23_name_consistency.md`](../help_docs/23_name_consistency.md)

If revived later: wire Manage menu, finish series support, confirm-each-group (no silent merges), and meet shared a11y standards. Do **not** run during import.
