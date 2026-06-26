# AbCS — Proposed Enhancements

**June 2026 · For testers and contributors**

This list describes **planned improvements** that are **not in the app yet**. We are sharing it to gather feedback on what would be most useful to you. Nothing here is a commitment to build or a fixed release date.

AbCS will stay focused on **managing your audiobook collection** with **full screen reader support** (JAWS, NVDA, and others). These ideas build on that goal.

---

## Planned for the next major update (core)

These are the main features under active planning for a fall 2026 development cycle (core work first, then name consistency and multiple languages if schedule allows).

| Enhancement | What it would add |
|-------------|-------------------|
| **Want to Read** | Mark books you plan to listen to without moving them to a different collection. Filter the main list to show only your “to be read” queue. The flag clears when you mark a book as read. |
| **Open audiobook location** | From Book Details, open the folder where the audiobook files live (or show the file in your file manager) so you can play them in your own player. |
| **Book ratings** | Store a rating (as a number, e.g. 4.5) on each book. You can type your own rating or fill it from web metadata. See ratings in the main book list and in Book Details. |
| **Cover images** | When you fetch web metadata for a book, save its cover image and show it in Book Details and Import Detail. |
| **Better backups** | Backups would include cover images as well as your database, in one package file, so restore brings everything back together. |
| **Collection library folder** | Optional folder path for each collection (e.g. where your Audible rips live). Import and rescan would default to that folder. |
| **Rescan / update from folder** | Scan a folder again and **update** books already in your library (length, file path, track count, etc.) instead of only adding new ones. You choose what to update. |
| **Name consistency check** | Find similar spellings of author names, titles, and genres (e.g. “Connolly” vs “Connelly”) and help you merge them into one spelling — similar to Duplicate Check. Planned after rescan (fall wave 4). |
| **Multiple languages** | UI text, menus, and messages in languages such as French and Spanish, with English as the default. Help docs would be translated separately. Planned after English UI is stable (fall wave 5). |

---

## Planned for a later update (optional)

These may follow the fall work if time and priority allow.

| Enhancement | What it would add |
|-------------|-------------------|
| **Organize files into library folder** | Optional wizard to copy or move audiobook folders into a tidy layout under your collection folder and update paths in AbCS. For users who want files in one place. |

---

## Additional ideas (follow-on)

Smaller or supporting features that complement the core plans.

| Enhancement | What it would add |
|-------------|-------------------|
| **Path health report** | A report listing books whose file path no longer exists on disk (moved, deleted, or wrong drive). |
| **Export library to spreadsheet** | Export your book list to CSV or similar for Excel, backup, or sharing — the reverse of Import Book List. |
| **Missing info filters** | Quick filters on the main window: show only books with no plot, no cover, no rating, or no file path. |
| **Mark several books “Want to Read”** | Select multiple books on the main list and mark or clear “Want to Read” in one step. |
| **Want to Read during import** | Set “Want to Read” while reviewing a book in Import Detail, before it is added to the library. |
| **More bulk update options** | Extend the Update window so you can change “Want to Read,” reader, or year for many selected books at once. |
| **Backup reminder** | A gentle reminder to create a backup if you have not done so in a while (you choose whether to act). |
| **Richer statistics** | Statistics screen counts for “Want to Read,” average rating, books with covers, and similar. |
| **Filter by narrator** | Show only books read by a chosen narrator or reader. |
| **Series book number** | Store “book 3 in the series” as its own field instead of only in the title. |
| **Export / import settings** | Save your preferences to a file and load them on another computer. |
| **Fetch web info for many books** | Queue web metadata fetch for a selection of books with progress and cancel — instead of one book at a time. |
| **Better plot search** | Faster search inside long plot summaries on very large libraries. |

---

## Larger ideas (backlog)

Bigger projects we might consider if there is strong demand. Not scheduled yet.

| Enhancement | What it would add |
|-------------|-------------------|
| **Import from other apps** | Import a library export from another tool (e.g. Libib or similar CSV formats) with less manual editing. |
| **Saved smart lists** | Save a combination of filters (e.g. “unread sci-fi with a plot”) and reuse it with one click. |
| **Reading progress** | Remember how far you got in a book (not just “finished” or not) — mainly useful if we add deeper playback support later. |
| **Tags on books** | Multiple labels per book (e.g. “gift,” “book club”) without changing its collection. |
| **Mac installer** | A packaged install for macOS testers, similar to the Windows installer. |
| **Check for updates** | Help menu option to see if a newer AbCS version is available and open the download page. |

---

## What we are not planning

To set expectations:

- **In-app audiobook player** — We plan to open your files in the folder or your default app, not build a full player inside AbCS.
- **Automatic move of all files on import** — Organizing files on disk would stay optional, not forced.
- **Cloud sync or online library** — AbCS remains a local collection manager on your computer.

---

## How to give feedback

If you test AbCS, tell us:

1. Which enhancements would help you most (top 3–5).
2. Anything missing from this list you would use regularly.
3. Anything here you would **not** use.

Internal planning details live in [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md). This document is the plain-language summary for sharing.

**Status:** Proposed — not yet implemented (June 2026).
