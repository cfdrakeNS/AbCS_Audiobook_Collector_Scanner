# AbCS — Proposed Enhancements

**September 2026 · For testers and contributors**

This list describes **planned improvements** that are **not in the app yet**. Version 3 scope was set from the tester review workbook.

AbCS will stay focused on **managing your audiobook collection** with **full screen reader support** (JAWS, NVDA, and others).

---

## Planned for version 3 (next major update)

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Web fetch stays responsive** | Run web metadata fetch on a background thread so the app does not freeze during network calls. Cancel still works. |
| **Fetch web info for many books** | Select several books and fetch web metadata in one queue, with a summary and options to apply all or review each. |
| **Import tag mapping** | In Preferences, choose which audio tags fill title and author (album vs track title, album artist vs artist). Multi-part books still group by album. |
| **Check for updates** | Help menu option to see if a newer AbCS version is available and open the download page. No silent install. |
| **Keep current book on sort and filter** | Sorting and filtering leave you on the same book when it is still in the list. |
| **Database upgrade on first start** | Existing libraries gain storage for ratings, series number, and later features without recreating the database. |
| **Book ratings** | Store a numeric rating on each book; fill from web metadata. |
| **Series book number** | Store book 3 in the series as its own field instead of only in the title. |
| **Name consistency check** | Find similar spellings of author names, titles, and genres and help you merge them — similar to Duplicate Check. You confirm each group. |
| **View-mode field announcements** *(optional)* | In Book Details view mode, tabbing a field speaks the name and value without JAWS saying edit or read only. Decide after the other v3 items. |

---

## Planned for a later update (deferred after version 3)

| Enhancement | What it would add |
| ----------- | ----------------- |
| **Want to Read** | Mark books you plan to listen to without moving them to a different collection. Filter the main list to your queue. |
| **Open audiobook location** | From Book Details, open the folder (or show the file) so you can play in your own player. |
| **Cover images** | Save cover images from web fetch; show in Book Details and Import Detail. |
| **Better backups** | Zip package with database plus covers. |
| **Collection library folder** | Optional folder path per collection for import/rescan defaults. |
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

- **In-app audiobook player** — open files in the folder or your default app.
- **Automatic move of all files on import** — organizing on disk stays optional.
- **Cloud sync or online library** — AbCS remains local.
- **Mac installer** — macOS from source (see INSTALL.md).
- **Plot full-text search** — dropped from the roadmap.

---

## How to give feedback

1. Which enhancements would help you most (top 3–5).
2. Anything missing you would use regularly.
3. Anything here you would **not** use.

Internal schedule: [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md). Tester workbook: [AbCS_Version3_Release_Tester_Review.xlsx](AbCS_Version3_Release_Tester_Review.xlsx).

**Status:** Version 3 in progress — tester build **2.16**. Phases 1–4, 6, and 7 are in the app. Phase 8 (keep current book on sort/filter) is in 2.16 for test. Phase 5 is skipped.
