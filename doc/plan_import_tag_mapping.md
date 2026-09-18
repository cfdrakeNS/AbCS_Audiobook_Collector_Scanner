# Import tag mapping (title / author)

**Status:** Planned — **Version 3 Phase 3**  
**Created:** September 2026  
**Related:** [Preferences Import Settings](../src/ui/preferences_window.py), [`src/core/tag_reader.py`](../src/core/tag_reader.py), [`src/core/import_scanner.py`](../src/core/import_scanner.py), [help_docs/19_import_explained.md](../help_docs/19_import_explained.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

Add **audio tag → book field** combos on the Preferences Import Settings tab so folder import can use the tags the user’s rips actually contain, instead of always using album for title and album-artist-then-artist for author.

---

## Problem

Scan hard-codes:

- Title = album tag (`TALB` / album). Track title (`TIT2`) is read and discarded.
- Author = album artist, then artist.
- Files are grouped by album.

That matches well-tagged multi-file audiobooks. It fails for music-style or single-file rips where the book name is in the track title and the author is only in artist. Fallback-to-folder/file does not fix a *wrong* tag, only a missing one.

Book-list import already has spreadsheet **column** mapping. This plan is **audio tags**, not CSV columns. Do not reuse that table as-is.

---

## Design (v1)

### UI — Import Settings tab

New group **Tag mapping**, below the import scenario:

| AbCS field | Combo options | Default (current behavior) |
|------------|---------------|----------------------------|
| Book title | Album / Track title / Album then track title | Album |
| Author | Album artist then artist / Album artist only / Artist only | Album artist then artist |

Combo anti-noise (plain Up/Down blocked; Alt+arrows allowed), accessible names and descriptions, Alt-letter hygiene. Defaults must match today’s scan so existing libraries do not change on Save.

### Scan / import

- [`FolderScanner`](../src/core/tag_reader.py) / `scan_folder` and `scan_file` apply the saved mapping when filling `title` and `author`.
- **Grouping stays on album** even if title is mapped to track title. If grouping followed track title, a 20-part book would become 20 books. Optional later: a third combo “Group files by” (Album / Folder). Not in v1.
- Store the track title on `AudioFileInfo` (today it is not kept) so the title combo can use it.
- Placeholder handling (`unknown album`, empty album artist) still falls through to Fallback tab rules.

### Import window

No extra controls on the Import window in v1. It already loads Preferences; mapping applies during scan like scenario and fallbacks.

### Help

Update [help_docs/19_import_explained.md](../help_docs/19_import_explained.md) tag table and [help_docs/10_preferences.md](../help_docs/10_preferences.md) Import Settings section.

**Estimate:** 2–3 days

---

## Follow-on (after Phase 3 / not required for v3 gate)

- **Narrator mapping:** Composer (default) / Artist / Comment keywords only / Artist when author is album artist.
- **Rescan** ([plan_rescan_and_library_folders.md](plan_rescan_and_library_folders.md)) is **deferred after v3**; when it ships, it must read the same QSettings keys for title/author overwrite.
- Year / genre / comments stay 1:1 with tags unless a real alternate source appears.
- Series from a **tag** (ID3 grouping / content group) is a rare tag-map row — add only if needed.

---

## Series from filename — not a tag map

`series_from_filename` parses the first `(…)` in the filename and may append ` - NN` to the title. That is **path parsing**, the same family as directory / nested-directory scenarios, not an ID3 field.

Keep it as an **import scenario**. Do not add “Filename (parentheses)” to the title/author tag combos.

Later optional: a **Series source** combo (none / directory / nested directory / filename) that replaces the five scenario names. That is a layout redesign, not part of v1 tag mapping.

---

## Tests

- Default mapping: same title/author/grouping as today (regression).
- Title = track title: book title from `TIT2`; still one book when album is shared.
- Author = artist only: ignores album artist.
- Album then track title: uses album when present, else track title.
- Fallbacks still apply when the chosen tags are empty/placeholder.
- Preferences round-trip and Restore Defaults.

---

## Accessibility

- Combos: accessible name “Book title tag”, “Author tag”; description lists the options and the default.
- Do not add a mapping grid that requires arrowing through many unlabeled cells.
- Status announce on Save; Alt+/ still reads the preferences status.

---

## Out of scope v1

Grouping combo; narrator combo; series-from-tag; unifying import scenarios into Series source; book-list CSV mapping changes; changing duration/tracks/size (measured, not mapped).
