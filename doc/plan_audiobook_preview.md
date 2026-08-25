# Open Audiobook Location — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Revised:** June 2026 — simplified to open-folder only (no play-first-track in v1)  
**Related:** [Book Details](help_docs/04_book_details.md), [plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md)

---

## What this is

Let users **open the folder (or file location)** for an audiobook from Book Details so they can play files in their own player or file manager. v1 is **open location only** — not in-app playback and not “play first track.”

AbCS stays a **collection manager** ([`README.md`](../README.md)); the user’s OS player and file manager handle listening.

---

## Problem

| Today | Gap |
|-------|-----|
| `books.path` stored in DB | User must copy path or navigate manually |
| Book Details path field | Editable `QLineEdit` only — no quick way to open the location |
| Multi-track books | `path` is often a folder; user needs to see all files |

---

## Design decisions (v1)

| Approach | v1 | Rationale |
|----------|-----|-----------|
| **Open location** (folder or file in Explorer/Finder) | **Yes** | Works for single-file and multi-track books; low risk |
| Play first file in OS default player | **No** | Weak for multi-chapter books (wrong track, sort issues); blurs “manager vs player” |
| Double-click on path field | **No** | Path is an editable line edit; poor for keyboard/screen reader users |
| Embedded Qt player | **No** | Large scope; defer to v2 only if requested |

### Why not “play track 1”?

- Filename sort may not match listening order.
- User still needs their player for the rest of the book.
- **Opening the folder** lets them pick the right file in a player they already use.

### Why not double-click path?

- `path_edit` is for viewing/editing text; double-click selects a word.
- AbCS is keyboard-first; use a **labeled button + Alt+shortcut** instead.

---

## Open location behavior

New helper [`src/core/audio_launcher.py`](../src/core/audio_launcher.py) (name may stay generic for future use):

| `books.path` | Action |
|--------------|--------|
| **Folder** (exists) | Open folder in OS file manager |
| **Single file** (exists) | Open **parent folder** with file highlighted when the OS supports it |
| Missing / empty | Disabled button; clear message on activate attempt |

### Platform notes

| OS | Folder | Single file |
|----|--------|-------------|
| Windows | `os.startfile(folder)` | `explorer /select,"{path}"` |
| macOS | `open folder` | `open -R file` (reveal in Finder) |
| Linux | `xdg-open` on parent or folder | `xdg-open` parent dir (highlight varies by file manager) |

- Reuse [`TagReader.SUPPORTED_EXTENSIONS`](../src/core/tag_reader.py) only if needed to validate “path looks like audio” — optional for v1.
- Catch errors → `exec_styled_message_box` + `set_status(..., announce=True)`.

---

## UI changes

### Book Details — [`src/ui/book_details.py`](../src/ui/book_details.py)

Add one button on the **Path** row (next to `path_edit`):

| Control | Shortcut | Action |
|---------|----------|--------|
| **Open location** | Alt+Shift+H | Open folder or reveal file per table above |

- `setAccessibleName("Open audiobook location")`
- `setAccessibleDescription("Open the folder for this book in the file manager - Alt+Shift+H")`
- Disabled when path empty or path does not exist; description explains why when disabled.

**Do not** add double-click handler on `path_edit`.

Wire into:

- `ALLOWED_ALT_KEYS` — register Alt+Shift+H (Path focus remains **Alt+H** per [`shortcuts.py`](../src/accessibility/shortcuts.py))
- [`shortcuts.py`](../src/accessibility/shortcuts.py) `BOOK_DETAILS_SHORTCUTS` — document Open location
- Path row horizontal layout: `[path_edit] [Open location] [added date fields…]`

### Main window — not in v1

No toolbar/footer Play or Open buttons until users ask. Book Details is enough for fall.

### Import Detail — not in v1

Path may not be final until import completes.

---

## Accessibility checklist

- [ ] Open location: accessible name, description, shortcut in description
- [ ] `set_status(..., announce=True)` on success and failure
- [ ] Do not auto-open on window load
- [ ] Disabled state: accessible description states missing/invalid path
- [ ] No reliance on double-click or mouse-only gestures

---

## Help

- Update [`help_docs/04_book_details.md`](../help_docs/04_book_details.md) — Open location button, Alt+Shift+H, folder vs single-file behavior.
- No separate help topic required unless Shift+F1 routing is desired later.

---

## Tests

| Test | File |
|------|------|
| Resolve folder vs file paths | `test/test_audio_launcher.py` |
| Missing path returns error | same |
| Open location disabled when path empty | book details UI test (mock launcher) |

Mock `os.startfile` / `subprocess.run` — do not launch real apps in CI.

---

## Implementation phases

| Phase | Work | Estimate |
|-------|------|----------|
| 1 | `audio_launcher.py` (open location only) + tests | 0.5 day |
| 2 | Book Details button + shortcut + status | 0.5 day |
| 3 | Help doc update | 0.25 day |

**Total v1:** ~1 day

---

## Out of scope (v1)

- Play / open in default audio app (including first track only)
- Double-click path to open
- Main window Open location
- Import Detail
- Embedded `QMediaPlayer`
- M3U playlist export

---

## Future (v2) — only if users request

| Feature | Notes |
|---------|--------|
| **Play** single-file books only | Button when `path` is one audio file, not a directory |
| Embedded player | Separate plan; 2+ weeks |
| Open location from main window | One selected book |

---

## Relation to other plans

- **Rescan / library folders** ([`plan_rescan_and_library_folders.md`](plan_rescan_and_library_folders.md)): path updates keep Open location correct.
- **Ratings / covers**: independent.

---

## Next steps

Review in fall. Small, self-contained feature (~1 day) — can ship anytime.
