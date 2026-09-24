# AbCS — Proposed Enhancements

**September 2026 · For testers and contributors**

This list describes **planned improvements**. Version 3 scope was set from the tester review workbook and later schedule decisions.

AbCS will stay focused on **managing your audiobook collection** with **full screen reader support** (JAWS, NVDA, and others).

---

## Planned for version 3 (next major update)

Already in tester build **2.18:** web fetch background thread, batch web fetch, import tag mapping, check for updates, keep current book on sort/filter, the first-start series-number upgrade, and series number on Book Details. Selection-mode toolbar and leading-article title compare are also in. Date Read and Added since calendars show days 10 through 31. Collection library root (Phase 11) and in-app audiobook preview (Phase 12) are tester accepted.

Still planned for v3:

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Name consistency check** | Find similar spellings of author names, titles, and genres and help you merge them — similar to Duplicate Check. You confirm each group. |
| **View-mode field announcements** *(optional)* | In Book Details view mode, tabbing a field speaks the name and value without JAWS saying edit or read only. Decide after the other v3 items. |

---

## Planned for a later update (deferred after version 3)

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Non-modal web fetch** | Keep using the main window while a fetch runs. Out of scope for v3 (too risky). Fetch progress stays a blocking dialog. |
| **Want to Read** | Mark books you plan to listen to without moving them to a different collection. Filter the main list to your queue. Out of scope for v3. |
| **Book ratings** | Store a numeric rating on each book; fill from web metadata. Out of scope for v3. |
| **Cover images** | Save cover images from web fetch; show in Book Details and Import Detail. Out of scope for v3. |
| **Better backups** | Zip package with database plus covers. |
| **Rescan / update from folder** | Scan again and update books already in the library. |
| **Organize files into library folder** | Optional wizard to copy/move folders into a tidy layout (high risk; later). |
| **Multiple languages** | UI in French, Spanish, etc., after English feature freeze. |

---

## Additional ideas (follow-on, after version 3)

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Path health report** | Books whose file path no longer exists on disk. |
| **Export library to spreadsheet** | Export book list to CSV — reverse of Import Book List. |
| **Missing info filters** | Show only books with no plot, cover, rating, or path. |
| **Mark several books Want to Read** | Bulk Want to Read on the main list. |
| **Want to Read during import** | Set Want to Read in Import Detail. |
| **More bulk update options** | Update Want to Read, reader, or year for many books. |
| **Backup reminder** | Gentle reminder if you have not backed up recently. |
| **Richer statistics** | Counts for Want to Read, average rating, covers, etc. |
| **Filter by narrator** | Show only books read by a chosen narrator. |
| **Export / import settings** | Save preferences to a file for another computer. |
| **Import / Preferences toolbars** | Labeled action toolbars for common actions. |

---

## Larger ideas (backlog)

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Import from other apps** | Import exports from tools like Libib. |
| **Saved smart lists** | Save a filter combination and reuse it. |
| **Reading progress** | How far you got (not just finished) — mainly if playback deepens later. |
| **Tags on books** | Multiple labels without changing collection. |

---

## What we are not planning

- **Full in-app library player** — Preview plays one book inside AbCS (Play/Pause). There is no playlist or listen-from-here player.
- **Automatic move of all files on import** — organizing on disk stays optional and deferred.
- **Cloud sync or online library** — AbCS remains local.
- **Mac installer** — macOS from source (see INSTALL.md).
- **Plot full-text search** — dropped from the roadmap.

---

## How to give feedback

1. Which enhancements would help you most (top 3–5).
2. Anything missing you would use regularly.
3. Anything here you would **not** use.

Internal schedule: [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md). Tester workbook: [AbCS_Version3_Release_Tester_Review.xlsx](AbCS_Version3_Release_Tester_Review.xlsx).

**Status:** Version 3 in progress — tester build **2.18**. Phases 1–4 and 6–12 are tester accepted. Non-modal fetch, Want to Read, ratings, and covers are out of scope for v3. Next is Phase 13 name consistency. View-mode announcements are optional and last.
