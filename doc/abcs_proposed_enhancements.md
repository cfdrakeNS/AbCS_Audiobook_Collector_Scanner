# AbCS — Proposed Enhancements

**September 2026 · For testers and contributors**

This list describes **planned improvements**. Version 3 scope was set from the tester review workbook and later schedule decisions.

AbCS will stay focused on **managing your audiobook collection** with **full screen reader support** (JAWS, NVDA, and others).

---

## Planned for version 3 (next major update)

Already in tester build **2.19:** web fetch background thread, batch web fetch, import tag mapping, check for updates, keep current book on sort/filter, the first-start series-number upgrade, and series number on Book Details. Selection-mode toolbar and leading-article title compare are also in. Date Read and Added since calendars show days 10 through 31. Collection library root (Phase 11) and in-app audiobook preview (Phase 12) are tester accepted. Name-list merge on duplicate (Phase 13) is in 2.18: when you rename an author, series, or genre onto an existing name, AbCS asks whether to move that name’s books. Play and Book Details show a picture when that picture is stored inside the audio file. Book Details layout is tester accepted: cover on the right, Want to read and read date save without Update, and a read date clears Want to read. The main list can show only books marked want to read (View → Want to read, or Alt+T). Edit → Add to want to read marks the focused book or the selection. The mark stays when the filter is turned off. Import Detail uses the same two-column layout as Book Details (no cover), with **Keep** (Alt+K) to add one reviewed book and move on, and **Discard** (Alt+D). The Play window supports next/previous file, seek, rewind/fast-forward, one speed for every book, resume from the saved position, and an In progress filter. Statistics includes Want to Read and In Progress counts.

Still planned for v3:

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Path health report** *(F01, next)* | Manage list of books whose stored file path is missing or no longer on disk. |
| **Want to read and playing filter** | One View filter that shows only books marked Want to read, or in progress (playing), or both. |
| **View-mode field announcements** *(optional)* | In Book Details view mode, tabbing a field speaks the name and value without JAWS saying edit or read only. |
| **Help review** | Last. Help topics match the finished windows. Unused topics are removed. Section names do not start with “Steps”. |
| **First-start screen reader message** | The first time AbCS starts with a screen reader running, Zoom is set to Normal. It speaks once that text size is Normal, and that a different size is chosen in Preferences, Theme and Zoom. |

---

## Planned for a later update (deferred after version 3)

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Non-modal web fetch** | Keep using the main window while a fetch runs. Out of scope for v3 (too risky). Fetch progress stays a blocking dialog. |
| **Book ratings** | Store a numeric rating on each book; fill from web metadata. Out of scope for v3. |
| **Book tags** | Several labels on one book. Out of scope for v3. |
| **Cover images** | Save cover images from web fetch; show in Book Details and Import Detail. Out of scope for v3. The Preview window picture is separate and is in version 3. |
| **Better backups** | Zip package with database plus covers. |
| **Rescan / update from folder** | Scan again and update books already in the library. |
| **Library-wide name consistency scan** | Find similar author, series, and genre spellings across the library and merge after you confirm each group. Deferred; Version 3 uses name-list merge when you rename onto an existing name. |
| **Organize files into library folder** | Optional wizard to copy/move folders into a tidy layout (high risk; later). |
| **Multiple languages** | UI in French, Spanish, etc., after English feature freeze. |

---

## Additional ideas (follow-on, after version 3)

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Export library to spreadsheet** | Export book list to CSV — reverse of Import Book List. |
| **Missing info filters** | Show only books with no plot, cover, rating, or path. |
| **Mark several books Want to Read** | Bulk Want to Read on the main list. |
| **Want to Read during import** | Set Want to Read in Import Detail. |
| **More bulk update options** | Update Want to Read, reader, or year for many books. |
| **Backup reminder** | Gentle reminder if you have not backed up recently. |
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

**Status:** Version 3 in progress — tester build **2.19**. Phases 1–4 and 6–13 are in (1–4 and 6–12 tester accepted; Phase 13 name-list merge implemented). Play cover, the Book Details picture, the new columns, the Book Details layout, Want to read, Import Detail layout, the full Play player, and Statistics Want to Read / In Progress are done. Next, in order: Path health report (F01), Want to read and playing filter, optional view-mode, then help last. Non-modal fetch, ratings, tags, and web cover files are out of scope for v3. Library-wide fuzzy name scan deferred. Changes since 2.14: [release_notes_2.19.md](release_notes_2.19.md).
