# Book Details path browse — Version 3 Phase 24

**Status:** Complete  
**Estimate:** 0.5 day  
**Related:** [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [plan_path_health_report.md](plan_path_health_report.md), [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md) Part A

---

## Goal

In Book Details **update** (and new-book) mode, a **Browse** button beside Path so the user can pick a folder or file to fix `books.path`. Typing the path still works.

---

## Shipped

- Browse beside Path; Alt+B; edit/new only
- Absolute path only; collection `root_path` unchanged
- Start dir: current path / parent → collection root → Preferences import
- Status note when path is not under the collection library root
- Helpers: `browse_start_directory`, `path_is_under_root` in `library_root.py`
- Play path resolve: stored path → remapped under collection root → Preferences import folder; same start-dir rule as Browse
- Play hidden in Book Details update/new (edit Path instead)
- Help: `04_book_details.md`, `16_shortcuts.md`
- Tests: `test_library_root.py`, `test_book_details_accessibility.py`, `test_audio_launcher.py`

---

## Gate

Passed. Browse fills path in edit mode; view mode hides Browse; root unchanged; Play remaps when the stored path is missing.
