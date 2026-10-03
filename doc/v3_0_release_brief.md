# AbCS Version 3 — Release Brief (pre-release)

**Current build:** 2.28 (`APP_VERSION` in `src/build_config.py`) — still in tester sign-off; **not** labeled 3.0 in the app until release.  
**Target public version:** 3.0 when manual testing is complete.  
**Branch:** `feature/background-fetch-v3`  
**Testing:** Full pytest suite — 825 passed (October 3, 2026). Accessibility review defect fixes passed tester JAWS/NVDA retest (October 4, 2026).  
**Audience:** Checklist for what ships when you promote the build to **v3.0**.

User-facing overview: [What's New in Version 3](whats_new_in_v3.md). Step-by-step help: bundled `help_docs/` and **Shift+F1** in each window.

---

## Enhancements

### Find, import, and metadata

- Background web metadata fetch with shared HTTP, cache, and budget; batch fetch for a selection with review summary.
- Leading-article title matching (A, An, The) for imports and comparisons.
- Import tag mapping: choose which audio tags supply title and author.
- Import Book List from spreadsheets; Import Detail layout with Keep/Discard.
- Plot fetch quality and performance improvements (2.22+).
- Optional startup check for a newer AbCS release.
- Selection mode on the toolbar: bulk actions without losing keyboard workflows.

### Organize, listen, and statistics

- **Collections** as virtual libraries with an optional **collection folder** on disk (portable libraries / removable drives).
- Series number on books; sort Series by number then year; table shows series number without storing it in the title.
- **Want to Read** flag, filter, and Statistics row.
- **Listen** (in-app player): play inside AbCS, next/previous track by disc/track tags, seek, 30-second rewind/forward, playback speed, resume position, **In progress** filter.
- Embedded cover art in Book Details and Listen; Listen can fill missing length/track count for book-list imports when files are found.
- Listen resolves paths via collection folder remap; book-list imports can be found under the collection folder with clear messages when missing.
- Listen progress as percent of whole book when length is known.
- Statistics: Want to Read and In Progress counts.

### Maintain and export

- Book Details **Browse** beside path; path open in file manager.
- **Manage → Check Book Locations** (formerly Check Books Path): scan for blank, missing, or off-root paths using the **same path lookup as Listen** (`locate_book_path`); auto-correct paths found under the collection folder; filters; CSV export; open Book Details from a row; Import-style progress for large scans.
- **File → Export Library** to CSV (UTF-8 BOM) or JSON for the visible list or selection.
- Name-list merge when renaming duplicates (author, series, genre).
- Standard shortcuts: **Ctrl+L** Listen, **Ctrl+S** save where applicable, **Edit** menu mnemonic, Narrator label on book list import, and related toolbar/menu cleanup.

### Accessibility and help

- Help system refresh (Phase 16): topics aligned to shipped windows; Listen help topic **26_listen_to_a_book.md**; Check Book Locations **24_check_book_locations.md**.
- Listen: **Alt+/** includes play position; seek controls announce **Play position** as time (not raw seconds); tab order includes time display and seek slider when a file is loaded.
- Clearer progress and status during long scans and batch operations.

---

## Bugs and fixes

### Listen and audio

- In-app player no longer loses screen reader focus to an external OS player.
- Legacy Linux (Qt 6.3 / HP 6000-class): avoid crash by keeping the compatible audio sink.
- Seek slider: stop screen reader from speaking a second raw second count after the time; restore tab to the slider when the accessible interface was invalid.
- Main-window Listen error/status text matches tests when a title prefix is included.

### Book Details, dates, and UI

- Read date and year validation after Phase 18/20 (typed fields, no future dates, Clear behavior, scaled calendars).
- Book Details opens on small Linux VMs and high zoom (window clamped to screen, scroll cap).
- Shared or permission-restricted folders: permission errors treated as missing paths so Book Details and Listen still open.
- Faster ordinary Book Details open (single path lookup and cached cover read).
- Do not auto-store a series number parsed from title on open.
- Return focus to the first selected book after Update closes.
- Duplicate mode: Delete behavior fixed.
- Collection window tab order after batch web fetch; main list clears appropriately after batch fetch.
- Book Details theme reuse for quicker open.

### Import, paths, and data

- Collection library root remap for Listen and path checks without silently rewriting stored paths.
- Check Book Locations logic and UI aligned with collection folders; in-window guide no longer references Listen.
- Import skips iTunes/MusicBrainz/encoder noise in Comments; one-time cleanup script for existing libraries.
- Google Books rate limit shown in minutes on batch summary; skip Google for the rest of the cooldown.

### Build and maintenance

- PyInstaller legacy build: pass output folders correctly.
- CI pytest and dead-code maintenance passes documented in archive plans.

---

## When ready for v3.0

- Bump `APP_VERSION` and `build_installer.iss` to **3.0**, then tag and ship installers.
- User summary at launch: [whats_new_in_v3.md](whats_new_in_v3.md). This brief lists enhancements and fixes for the branch.
