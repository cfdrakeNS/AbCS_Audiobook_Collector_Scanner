# Preview Audiobook — Version 3 Phase 12 / C03

**Status:** Implemented — pending tester (Version 3 Phase 12)  
**Created:** June 2026  
**Revised:** September 2026 — Preview via OS default media player (not open-folder-only)  
**Related:** [Book Details](help_docs/04_book_details.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md)

---

## What this is

Let the user **preview** an audiobook by launching it in the **default OS media player** for that file format (file association). Not an in-app player. AbCS stays a collection manager ([`README.md`](../README.md)).

---

## Problem

| Today | Gap |
|-------|-----|
| `books.path` stored in DB | User must copy path or navigate manually |
| Book Details path field | Editable `QLineEdit` only — no quick Preview |
| Multi-track books | Import stores `path` as the book **folder** (`import_window` uses `data.get("folder")`), not a single file |

---

## Design decisions (v3)

| Approach | v3 | Rationale |
|----------|-----|-----------|
| **Preview** in OS default player | **Yes** | Matches “play in your player”; no embedded Qt player |
| Open folder in file manager only | Deferred / optional helper | User asked for Preview play, not Explorer reveal |
| Double-click on path field | **No** | Poor for keyboard/screen reader users |
| Embedded `QMediaPlayer` | **No** | Out of project scope |

### Launch behavior

New helper (e.g. [`src/core/audio_launcher.py`](../src/core/audio_launcher.py)):

| `books.path` | Action |
|--------------|--------|
| **Single audio file** (exists, supported extension) | Open with OS default association (`os.startfile` / `open` / `xdg-open`) |
| **Folder** (exists) | Resolve one playable file inside (see multi-file rule below), then open that file |
| Missing / empty / no playable file | Disable Preview; announce clear error on activate |

Supported audio extensions: [`TagReader.SUPPORTED_EXTENSIONS`](../src/core/tag_reader.py) — `.mp3`, `.m4a`, `.m4b`, `.flac`, `.ogg`, `.oga`, `.wma`, `.wav`, `.aac`, `.opus`.

### Multi-file rule (explicit)

When `path` is a directory (typical multi-track import):

1. Scan immediate children (and, if none, one level of subfolders if that matches how scans group books — document the chosen depth in implementation).
2. Keep files whose extension is in `SUPPORTED_EXTENSIONS`.
3. Sort by file name (case-insensitive) and launch the **first** file.

Announce that Preview started that file (filename in status). Do **not** build a playlist or queue tracks.

**Plan issue:** Filename sort may not match listening order; chapter 10 can sort before chapter 2. Acceptable for v3 Preview; document in help.

Catch errors → `exec_styled_message_box` + `set_status(..., announce=True)`.

---

## UI changes

### Book Details — [`src/ui/book_details.py`](../src/ui/book_details.py)

Book Details has **no menu bar**. Add a **Preview** button near the Path row / footer action buttons (same styled `QPushButton` pattern as Fetch Web Info).

| Control | Suggested shortcut | Action |
|---------|-------------------|--------|
| **Preview** | Alt+Shift+P | Launch default player for resolved file |

Alt+P is already Plot on Book Details (`BOOK_DETAILS_SHORTCUTS`). Do not reuse it.

- `setAccessibleName("Preview audiobook")`
- `setAccessibleDescription("Play this book in your default media player - Alt+Shift+P")`
- Disabled when path empty, missing, or no playable file; description explains why when disabled.

Wire into `ALLOWED_ALT_KEYS` / shortcut maps and [`shortcuts.py`](../src/accessibility/shortcuts.py) `BOOK_DETAILS_SHORTCUTS`.

### Main window — Edit menu — [`src/ui/main_window.py`](../src/ui/main_window.py)

Edit menu today: Delete, Update, Fetch Web Info. Add **Preview** next to Fetch Web Info (same book-action group). Enables when one focused/selected book has a resolvable path. Does not require Book Details to be open.

No separate Book Details menu — that window has none.

### Import Detail — not in v3

Path may not be final until import completes.

---

## Accessibility checklist

- [ ] Preview button: accessible name, description, shortcut in description
- [ ] Edit → Preview: menu text only (no `setAccessibleName` on `QAction`)
- [ ] `set_status(..., announce=True)` on success and failure
- [ ] Do not auto-play on window load
- [ ] Disabled state: accessible description states missing/invalid path
- [ ] No reliance on double-click or mouse-only gestures

---

## Help

- Update [`help_docs/04_book_details.md`](../help_docs/04_book_details.md) — Preview button, shortcut, OS player, multi-file first-file rule.
- Update main-window shortcuts help for Edit → Preview.

---

## Tests

| Test | File |
|------|------|
| Resolve file vs folder → first audio file | `test/test_audio_launcher.py` |
| Missing path returns error | same |
| Preview disabled when path empty | book details UI test (mock launcher) |
| Edit menu Preview enabled/disabled with selection | main window menu test |

Mock `os.startfile` / `subprocess.run` — do not launch real apps in CI.

---

## Implementation phases

| Phase | Work | Estimate |
|-------|------|----------|
| 1 | `audio_launcher.py` (resolve + open) + tests | 0.5–1 day |
| 2 | Book Details Preview button + main Edit menu | 0.5 day |
| 3 | Help doc update | 0.25 day |

**Total:** ~1–2 days

---

## Out of scope (v3)

- In-app / embedded player
- Playlist / play all tracks
- Open location in file manager (possible later helper; not this phase’s primary action)
- Import Detail Preview
- Double-click path to play

---

## Relation to other plans

- **Collection root / rescan** ([`plan_rescan_and_library_folders.md`](plan_rescan_and_library_folders.md)): path updates keep Preview correct; changing root alone does not rewrite `books.path`.
- **Ratings / covers**: independent; out of scope for v3 UI.

---

## Next steps

Implement as v3 Phase 12 per [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md).
