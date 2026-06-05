**Testing summary — recent changes**

**Duplicate check (main window)**
- Duplicate matching options updated and reordered (strictest first).
- **Title + Author + Collection** now only flags duplicates in the **same** collection.
- New option: **Title + Author** (matches across collections; ignores year).
- If you start **Import** or **Import Book List** while duplicate mode is on, duplicate mode ends first and the normal book list returns.

**Import window / import progress**
- Status bar no longer shows a **Valid** count.
- During add, status shows scanned, added, corrected, errors, warnings, and duplicates.

**Book list import**
- Duplicate detection uses the same matching rules as above.

**Preferences**
- **Ctrl+Tab** / **Ctrl+Shift+Tab** move between preference tabs (also listed in F1 help).
- Duplicate match options match the main window duplicate check list.

**Bug list**
- Items 108–111 marked complete in `AbCS_Bug_Final_fixes.md`.
108. complete - import window & import progress window remove valid counter from status bar. left over from older process.
109. complete - preference window f1 help add: Move between tabs control+tab / control+shift+tab.
110. complete - main window - duplicate mode matching by title + Author + Collection is not working correctly
111. complete - main window - if import is selected and in duplicate mode exit duplicate mode before opening import window or book list import 


## Testing Summary — June 5, 2026 (v1.9.71)

### Duplicate checking
- Duplicate match options reordered (strictest first).
- **Title + Author + Collection** — only flags duplicates in the **same** collection.
- New option: **Title + Author** — matches across collections; ignores year.
- Starting **Import** or **Import Book List** while in duplicate mode exits duplicate mode first.
- Book List Import uses the same duplicate rules.
- Preferences duplicate options match the main window list.

### Import windows
- **Valid** count removed from import progress status bar.
- During add, status shows: scanned, added, corrected, errors, warnings, duplicates.

### Preferences
- **Ctrl+Tab** / **Ctrl+Shift+Tab** move between tabs (also in F1 help).

### Book details
- Collection label displays correctly when viewing a book.
- Closing Book Details without save/delete/web apply no longer refreshes the main book list.
- Main list refreshes only after save, delete, or successful web apply.

### Web metadata / fetch
- Improved plot and series enrichment (ISBN reuse from search results).
- Re-fetch shows the same progress dialog as initial fetch.
- Tab order restored correctly after fetch completes.
- Fetch progress announcements improved for screen readers.
- Author matching improved for **Last, First** format in the database.

### Name list windows
- Screen reader announces both the item and “no books” states.
- **Find** from main window: pressing Enter moves focus to the selected item in the name list.

### Performance (background)
- SQLite memory settings (`cache_size`, `mmap_size`) now scale with database size and system RAM — should feel snappier on large libraries; no visible UI change.

---

**Bugs marked complete today:** #108–111 in `AbCS_Bug_Final_fixes.md` (import valid counter, preferences tab shortcuts, duplicate matching fix, exit duplicate mode before import).