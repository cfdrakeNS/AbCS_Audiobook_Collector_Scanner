# Preview Audiobook — Version 3 Phase 12 / C03

**Status:** Complete — tester accepted (Version 3 Phase 12). Tester build 2.18.  
**Created:** June 2026  
**Revised:** September 2026 — in-app Preview after OS-player trial  
**Related:** [Book Details](help_docs/04_book_details.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md)

---

## What shipped

Preview plays **inside AbCS** so screen reader focus stays in the app. An OS-default player was tried first; it stole focus. The in-app player is what testers accepted.

| Control | Action |
|---------|--------|
| **Play/Pause** | Enter plays or pauses. Focus starts on this button. No Alt letter. |
| Title / Author / Series / Length | Book title, author, series (name and number when set), and stored `hh:mm` to the right of the button. JAWS Insert+B reads the full lines. |
| Status | **Playing. Press Escape to exit.** or **Paused. Press Escape to exit.** |
| Escape | Closes Preview and stops playback. From the main window, focus returns to the Title cell. |
| F1 | Preview shortcut list (Shift+F1 once). Shift+F1 opens help for the window that opened Preview (main window or Book Details). |

**Preview** is on Book Details, the main window **Edit** menu, and the main toolbar after Find. Shortcut is **Alt+Shift+P**. Preview is off in selection mode. Duplicate mode keeps Preview on so you can hear which copy to keep.

Resolve path in [`src/core/audio_launcher.py`](../src/core/audio_launcher.py). When the book’s collection has a library root, Preview remaps the stored import path onto that folder (author and title folders stay) so a portable drive can move. `books.path` is not rewritten. If the remapped folder is missing, the stored path is tried next. Play in [`src/ui/preview_window.py`](../src/ui/preview_window.py) with Qt Multimedia. FFmpeg console chatter is quieted while Preview is open.

---

## Problem

| Today (before Phase 12) | Gap |
|-------|-----|
| `books.path` stored in DB | User must copy path or navigate manually |
| Book Details path field | Editable `QLineEdit` only — no quick Preview |
| Multi-track books | Import stores `path` as the book **folder** (`import_window` uses `data.get("folder")`), not a single file |

---

## Design decisions (v3)

| Approach | v3 | Rationale |
|----------|-----|-----------|
| **Preview** in OS default player | Replaced | Left the app; screen reader focus was lost |
| Open folder in file manager only | Deferred / optional helper | User asked for Preview play, not Explorer reveal |
| Double-click on path field | **No** | Poor for keyboard/screen reader users |
| Embedded `QMediaPlayer` | **Yes — shipped** | Play/Pause in a Preview window so focus stays in AbCS |

### Resolve behavior

Helper: [`src/core/audio_launcher.py`](../src/core/audio_launcher.py).

| `books.path` | Action |
|--------------|--------|
| **Single audio file** (exists, supported extension) | Play that file in Preview |
| **Folder** (exists) | Resolve one playable file inside (see multi-file rule), then play that file |
| Collection has `root_path` | Remap stored path onto that folder, then play |
| Missing / empty / no playable file | Announce **No file path is set.** or **Book not found in -** and the remapped or stored path |

Supported audio extensions: [`TagReader.SUPPORTED_EXTENSIONS`](../src/core/tag_reader.py) — `.mp3`, `.m4a`, `.m4b`, `.flac`, `.ogg`, `.oga`, `.wma`, `.wav`, `.aac`, `.opus`.

### Multi-file rule

When `path` is a directory (typical multi-track import):

1. Scan immediate children (and, if none, one level of subfolders).
2. Keep files whose extension is in `SUPPORTED_EXTENSIONS`.
3. Sort by file name (case-insensitive) and play the **first** file.

Filename sort may not match listening order; chapter 10 can sort before chapter 2. Documented in help. Phase 21 changes the starting file and next/previous to track number, with disc number first when it is present.

Catch errors → `exec_styled_message_box` + `set_status(..., announce=True)`.

---

## UI changes

### Book Details — [`src/ui/book_details.py`](../src/ui/book_details.py)

**Preview** button near the footer action buttons (same styled `QPushButton` pattern as Fetch Web Info). Shortcut **Alt+Shift+P**. Alt+P stays Plot.

### Main window — Edit menu — [`src/ui/main_window.py`](../src/ui/main_window.py)

**Preview** next to Fetch Web Info on Book Details, and on the main toolbar after Find. Enabled when a book is focused, except in selection mode. Duplicate mode keeps Preview on. Missing path still announces so the user hears why Preview failed.

### Import Detail — not in v3

Path may not be final until import completes.

---

## Accessibility checklist

- [x] Preview button: accessible name, description, shortcut in description
- [x] Edit → Preview: menu text only (no `setAccessibleName` on `QAction`)
- [x] Status announces Playing/Paused with Escape to exit
- [x] Do not auto-play on Book Details load
- [x] Disabled or missing path: clear spoken error
- [x] Enter activates Play/Pause; Escape closes
- [x] F1 shortcut list; Shift+F1 process help
- [x] Insert+B reads Title/Author/Length values
- [x] Close from the main window restores table focus
- [x] No reliance on double-click or mouse-only gestures

---

## Help

- [`help_docs/04_book_details.md`](../help_docs/04_book_details.md) — Preview button, in-app player, first-file rule
- [`help_docs/16_shortcuts.md`](../help_docs/16_shortcuts.md) — Edit → Preview and Preview window keys

---

## Tests

| Test | File |
|------|------|
| Resolve file vs folder → first audio file | `test/test_audio_launcher.py` |
| Missing path returns error | same |
| Preview window shows title, author, length | same (FakePlayer) |
| Preview disabled when path empty | `test/test_book_details_accessibility.py` |
| Edit menu Preview; blocked in selection mode | `test/test_main_window_menus_shortcuts.py` |

Tests use a FakePlayer. They do not start real Qt Multimedia decode in CI.

---

## Out of scope (v3)

- Playlist / play all tracks
- Open location in file manager
- Import Detail Preview
- Double-click path to play
- Open in default OS player (optional later helper)

---

## Relation to other plans

- **Collection root / rescan** ([`plan_rescan_and_library_folders.md`](plan_rescan_and_library_folders.md)): path updates keep Preview correct; changing root alone does not rewrite `books.path`.
- **Ratings / web covers**: independent; web cover files stay out of v3. Embedded art on the Preview window is [plan_preview_cover.md](plan_preview_cover.md) (Phase 15).
- **Later player:** next/previous, seek, global speed, resume, and an in-progress filter are [plan_preview_player_later.md](plan_preview_player_later.md).

---

## Next

Phase 15 Preview cover is implemented. The full player is Phase 21. Help review is last. See [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md).
