# iTunes Technical Tags in Comments — Version 3 Phase 28

**Status:** Implemented (September 2026) — import fix and one-time script done; awaiting tester check. Next in v3 before Phase 16 help.  
**Created:** September 2026  
**Related:** [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), [plan_export_library_metadata.md](plan_export_library_metadata.md) (found during Phase 27 testing), [comment_cleanup.py](../src/core/comment_cleanup.py), [tag_reader.py](../src/core/tag_reader.py), [clean_technical_comments.py](../scripts/clean_technical_comments.py)

---

## What this is

Import copied iTunes technical tags into a book's **Comments**: long blocks of hex numbers and CD database IDs that mean nothing to a listener. Import now leaves them out, and a one-time script removes them from books already in the library.

---

## Problem

- MP3 files tagged by iTunes carry ID3 comment frames named `iTunNORM` (volume), `iTunSMPB` and `iTunPGAP` (gapless playback), and `iTunes_CDDB_1`, `iTunes_CDDB_IDs`, `iTunes_CDDB_TrackNumber` (CD database). `TagReader._read_mp3_tags` read **every** `COMM` frame, so these ended up in Comments beside the real comment.
- A multi-file book gets one block per track, joined with `; `, so Comments grew very large (81,087 characters for one book).
- Found when LibreOffice Calc would not open a Phase 27 CSV export: "The data could not be loaded completely because the maximum number of characters per cell was exceeded."

Kinds of technical data found in the tester library:

| Kind | Example |
|------|---------|
| Hex block (iTunNORM, iTunSMPB) | `0000028A 0000028A 00002C35 ...` (9 or more 8- or 16-digit hex groups) |
| CD disc ID (iTunes_CDDB_1) | `4711E807+343975+7+150+2660+...` |
| CD track IDs (iTunes_CDDB_IDs) | `22+813AEE62CA3EACE9668FF7396BC3995C+12573191` |
| Track number (iTunes_CDDB_TrackNumber) | `1`, `14++` |
| Empty pieces left between them | `; ; ;` |

---

## Design (as built)

### Part A — Import fix (all formats)

- `_read_mp3_tags` skips comment frames whose description starts with `iTun` (case-insensitive). Frames with an empty or any other description are kept.
- `TagReader.read_file` passes every format's comment through `clean_comment_text` as a safety net (M4B `©cmt`, FLAC/Vorbis `comment`, generic), because those formats do not name the frame.
- `clean_comment_text` leaves text **unchanged** unless it contains a hex block or a CD database ID. When it does, it drops those pieces, bare track numbers, empty pieces, and repeated pieces, and joins the rest with `; ` (or a blank line when the original had no `;`). Plots, notes, and reader lines are kept.

### Other technical data (added after review)

- MP3 comment frames whose description names MusicBrainz, AcoustID, CD database (`CDDB`), or encoder data (`Encoder`, `Encoded by`) are skipped, like `iTun*` frames.
- These comment pieces are technical when they are the **whole** piece: a MusicBrainz or AcoustID ID (bare or labelled UUID); encoder versions (`LAME3.99r`, `Lavf58.29.100`, `iTunes 12.3.1.23`); converter stamps (`fre:ac - free audio converter <...>`, `online-audio-converter.com`, `Exact Audio Copy ...`, `dBpoweramp ...`, `Encoded with/by ...`).
- Kept: web links inside real text (LibriVox source link, Pseudopod license), rip-detail lines such as `Encoder.....Fraunhofer [FhG]`, and phrases like "Audible Rip" or "iTunes exclusive edition".
- Tester library: no MusicBrainz IDs or encoder versions found; three converter stamps (Lust Killer, The Light We Lost, Glass Houses), each the whole comment.

### Part B — One-time cleanup script

`scripts/clean_technical_comments.py`, same style as `update_series_number_from_title.py`:

- Preview by default; `--apply` writes. `--db PATH` (default `data/abcs.db`), `--report PATH` for the full list.
- `--apply` copies the database to `abcs.bak.YYYYMMDD_HHMMSS.db` first.
- Only rows whose Comments contain technical data are changed. Running it again changes nothing.
- Close AbCS before `--apply`.

Preview on the tester library (September 2026): 804 books with comments; **81 would be cleaned** (78 iTunes, 3 converter stamps); 76 left empty; about 433,000 characters removed; no technical data left in any row afterwards.

Some kept plots end mid-sentence (for example Night Passage ends "He can't"). That cut is in the file's own tag, not caused by the cleanup.

---

## Implementation

| Area | Change |
|------|--------|
| New | `src/core/comment_cleanup.py` — `is_technical_comment_frame`, `is_technical_comment_piece`, `clean_comment_text` |
| [`tag_reader.py`](../src/core/tag_reader.py) | Skip `iTun*` comment frames; clean `info.comment` in `read_file` |
| New | `scripts/clean_technical_comments.py` — one-time cleanup |
| New | `test/test_comment_cleanup.py` (16 tests) |

No database schema change. No UI change. No help change (Comments simply no longer show the junk).

---

## Tests

`test/test_comment_cleanup.py`: frame descriptions; technical vs normal pieces (years, short numbers, ISBNs, a single hex word stay); text without technical data unchanged; junk-only becomes empty; real text kept and repeats dropped; blank-line joined frames; running twice changes nothing more; MP3 import with real `COMM` plus `iTunNORM`, `iTunSMPB`, `iTunes_CDDB_1`, `iTunes_CDDB_TrackNumber` keeps only the real comment; `read_file` cleans any format; script dry run writes nothing and makes no backup; script `--apply` backs up, cleans, and a second run finds nothing; MusicBrainz frame skipped; MusicBrainz IDs, encoder versions, and converter stamps removed; links in real text, rip-detail lines, and "Audible Rip" kept. Full suite: 650 passed, 1 skipped.

---

## Tester check

### 1. One-time cleanup

1. Close AbCS.
2. Preview: `python scripts/clean_technical_comments.py --report comments_report.txt`
3. Apply: `python scripts/clean_technical_comments.py --apply`
4. Start AbCS and open these books in Book Details:

| Book | Author | Before | Expected Comments after |
|------|--------|--------|-------------------------|
| The Stranger Beside Me | Ann Rule | 81,087 characters of hex | Empty |
| Death Is Now My Neighbour - 12 | Colin Dexter | 726 characters of hex | Empty |
| Classic In The Barn - 01 | Amy Myers | Series details mixed with hex | Series details only (starts "Series.......Car Detective") |
| Night Passage | Robert B. Parker | Plot followed by hex (M4B file) | Plot only, ending "He can't" |
| Practice To Deceive | Ann Rule | CD IDs, track numbers, and author name | "Ann Rule" |
| Lust Killer | Ann Rule, Andy Stack | `http://online-audio-converter.com` | Empty |
| The Leavenworth Case | (LibriVox) | Archive.org source link | Unchanged (link kept) |

5. File → Export Library to CSV: LibreOffice Calc opens it without the "maximum number of characters per cell" message, and the status does not report shortened books.

### 2. Import

Import one of these folders into a test collection (or view it in Import Detail) and confirm Comments show no hex blocks or CD IDs:

- `D:\Stans Audio books\Ann Rule\The Stranger Beside Me` (MP3; expect empty Comments)
- `D:\Stans Audio books\Amy Myers\Classic In The Barn` (MP3; expect series details only)
- `F:\Audio Books\Robert B. Parker\Night Passage` (M4B; expect plot only)

**Gate:** The books above match the table; Calc opens the export; importing the three folders gives clean Comments; full test suite green.

---

## Decisions and outstanding questions

| # | Question | Answer |
|---|----------|--------|
| 1 | Automatic cleanup on first start, or manual? | **Decided:** one-time script in `scripts/`, run by hand. No in-app cleanup. |
| 2 | Keep the 32,767-character CSV cut after cleanup? | **Decided (Sept 27, 2026):** yes. Plots and notes can still be long. No code change. |
| 3 | Also skip other technical comment tags (MusicBrainz IDs, encoder names)? | **Decided (Sept 27, 2026):** yes. Implemented — see "Other technical data" below. |

---

## Out of scope

Rewriting audio file tags on disk; cleaning other fields.
