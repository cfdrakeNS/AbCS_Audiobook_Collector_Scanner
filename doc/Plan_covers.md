# Covers — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Web Metadata](help_docs/07_web_metadata.md), [Book Details](help_docs/04_book_details.md), [Backup and Restore](help_docs/09_backup_restore.md), [plan_ratings.md](plan_ratings.md)

---

## What this is

Store book **cover images** as files alongside the database, fetched as part of the existing **Web Metadata** flow (no separate cover download or import-time extraction). Display covers on **Book Details** and **Import Detail**. Upgrade backup/restore to a **zip package** containing the database and `covers/` folder.

---

## Problem

| Today | Issue |
|-------|--------|
| [`src/web/web_book_api.py`](../src/web/web_book_api.py) Open Library search | Requests `cover_i` in fields but never builds URL or returns it |
| Google Books `_google_item_to_metadata` | Does not read `imageLinks` |
| Database | No `cover_path` column |
| UI | No cover display; only splash images in About/Setup |
| [`create_manual_backup`](../src/database/connection.py) | Copies `abcs.db` only — insufficient once covers are files |

---

## Design decisions

### Covers from web fetch only

- Cover URL resolved inside `get_book_metadata` — **no extra API round trip**
- Image **downloaded on Web Metadata save** (Alt+S), same transaction as other field updates
- **No import-time extraction** from audio embedded art — import stays local and fast
- **No standalone “fetch cover”** button or menu action

### Storage

- Directory: `{user_data_dir}/covers/` via [`get_user_data_dir()`](../src/app_paths.py)
- Filename: `{book_id}.jpg` (normalize to JPEG on save; replace on re-fetch)
- DB column: `cover_path TEXT` — relative path `covers/{book_id}.jpg` (not absolute)
- Nullable when no cover

### Package backup (Option A)

Each backup is a **zip** containing:

```text
abcs.db
covers/
  42.jpg
  108.jpg
```

Legacy `.db`-only backups still restore (no covers). New backups use `.zip` extension.

### Main window

**No cover column or thumbnail in the book table** — performance on 30k+ rows and poor screen-reader experience. Covers are detail-window only.

---

## Database

### Schema

In [`connection.py`](../src/database/connection.py) `column_specs["books"]`:

```text
cover_path  TEXT
```

Update [`models.py`](../src/database/models.py) `Book.cover_path: str = ""`  
Update [`queries.py`](../src/database/queries.py) `insert`, `update`, `_row_to_book`  
Update [`test/fixtures/abcdDB_def.sql`](../test/fixtures/abcdDB_def.sql)

---

## New module: `src/core/cover_storage.py`

| Function | Behavior |
|----------|----------|
| `covers_dir() -> Path` | `{user_data}/covers`, mkdir if needed |
| `relative_cover_path(book_id: int) -> str` | `covers/{book_id}.jpg` |
| `resolve_cover_path(relative: str) -> Path` | Absolute path under user data |
| `save_cover(book_id: int, image_bytes: bytes) -> str` | Write JPEG, return relative path |
| `delete_cover(book_id: int) -> None` | Remove file if exists; ignore missing |
| `load_cover_pixmap(relative: str, max_size: int) -> QPixmap \| None` | Scale for QLabel display |

Use Pillow or Qt `QImage.fromData` for decode; re-encode JPEG for consistent format. If decode fails, return None and status message.

---

## Web API — [`src/web/web_book_api.py`](../src/web/web_book_api.py)

### Open Library

In the loop building `candidate` dict (~line 1287), add:

```python
cover_i = doc.get("cover_i")
cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg" if cover_i else ""
```

Include `"cover_url": cover_url` in returned metadata.

### Google Books

In `_google_item_to_metadata`, after `volume_info`:

```python
image_links = volume_info.get("imageLinks") or {}
cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail") or ""
```

Add `"cover_url": cover_url` to dict. Prefer HTTPS; upgrade `http://` to `https://` if needed.

### Caching

`cover_url` travels inside existing metadata cache in `get_book_metadata` — no separate cache.

---

## Web Metadata — [`src/ui/web_metadata.py`](../src/ui/web_metadata.py)

### Preview (v1)

Add read-only `QLabel` `self.cover_preview` near top of form (e.g. above title row):

- On fetch success: if `web_data.get("cover_url")`, download bytes for **preview only** (or load from URL via QNetworkAccessManager / urllib)
- `setAccessibleName(f"Cover preview for {title}")`
- Max display size ~120×180 scaled via [`UIScaler`](../src/accessibility/scaling.py)
- Empty state: no widget space or text "No cover in web result"

### Save path — `on_save_clicked`

When user saves and `cover_url` is present in current web data:

1. If user has checkbox diff UI for cover (optional) **or** book has no `cover_path` yet **or** re-fetch always updates cover — **recommend:** update cover whenever `cover_url` present and user saves any web field (document in help)
2. `urllib.request.urlopen(cover_url, timeout=6)` → bytes
3. `cover_storage.save_cover(book.book_id, bytes)` → relative path
4. `book.cover_path = relative path`
5. On failure: `set_status("Cover download failed", announce=True)`; do not block other fields saving

### `compute_field_differences`

Optional: add `cover` key when URL exists and (`not book.cover_path` or URL changed from stored hash) — for diff summary only.

---

## UI — Book Details [`src/ui/book_details.py`](../src/ui/book_details.py)

### Layout

Add cover region **above the title grid** or in a horizontal split at top of form:

```text
[Cover image 120x180]  |  [existing title/author grid...]
```

Widgets:

```python
self.cover_label = QLabel()
self.cover_label.setAccessibleName("Cover image")
self.cover_placeholder = QLabel("No cover available")
```

### Load

- If `book.cover_path` and file exists: `load_cover_pixmap` → `setPixmap`
- Accessible description: `f"Cover image for {title} by {author}"`
- Else: show placeholder text (not blank silence); `setAccessibleDescription("No cover available")`

### Save

Cover not edited in Book Details — only set via Web Metadata. No cover widgets in dirty tracking.

### Tab order

Cover label: `Qt.NoFocus` if decorative with good accessible name; or `StrongFocus` if user should hear "No cover available". **Recommend StrongFocus** on placeholder; pixmap label with accessible name when image present.

---

## UI — Import Detail [`src/ui/import_detail_window.py`](../src/ui/import_detail_window.py)

Same cover display pattern as Book Details.

- Before DB insert: always placeholder (no `book_id` yet)
- After book added and user opens Import Detail again with `book_id`: load from `cover_path` if set
- If import detail used pre-insert only: cover stays "No cover available" until post-import Web Metadata — document in help

---

## Backup and restore

### [`src/database/connection.py`](../src/database/connection.py)

**`create_manual_backup`**

1. Checkpoint WAL (existing)
2. Build zip: `abcs_backup_{timestamp}.zip` in `get_backup_directory()`
3. `zipfile.ZipFile.write(db_file, arcname="abcs.db")`
4. If `covers_dir()` exists, add each file under `covers/...`
5. Return zip path
6. Keep listing compatible: `list_backups` includes `.zip` and legacy `.db`

**`restore_from_backup`**

1. If source ends with `.zip`: extract to temp dir; copy `abcs.db` to live path; **replace** entire live `covers/` directory from zip (delete old covers first)
2. If source is `.db`: current behavior (DB only); leave existing `covers/` as-is or document mismatch
3. `initialize_database()` after restore

**`full_reset_database`**

- After DB wipe: `shutil.rmtree(covers_dir())` if exists

**`delete_backup_file`**

- Unchanged; works on `.zip`

### [`src/ui/backup_restore_window.py`](../src/ui/backup_restore_window.py)

- Browse filter: `Zip Archives (*.zip);;Database Files (*.db);;All Files (*.*)`
- Restore confirmation text: *"Restore database and cover images from this backup?"* for zip
- Status: `Backup created: abcs_backup_….zip (database and covers)`

### Help — [`help_docs/09_backup_restore.md`](../help_docs/09_backup_restore.md)

- Backups now include cover images when present
- Legacy `.db` backups restore metadata only

---

## Cleanup

| Event | Code location | Action |
|-------|---------------|--------|
| Delete one book | `BookQueries.delete` | `delete_cover(book_id)` before SQL DELETE |
| Delete many | `BookQueries.delete_many` | delete cover for each id |
| Full reset | `full_reset_database` | remove `covers/` |
| Web Metadata re-save | `on_save_clicked` | `save_cover` overwrites same path |
| Book delete in Book Details | `book_details` delete handler | relies on `BookQueries.delete` |

Optional v2: Manage → remove orphan cover files not referenced in DB.

---

## Implementation phases

| Phase | Work | Estimate |
|-------|------|----------|
| 1 | Schema, `cover_storage.py`, unit tests | 1 day |
| 2 | `web_book_api.py` cover_url extraction | 0.5 day |
| 3 | Web Metadata preview + save download | 1 day |
| 4 | Book Details + Import Detail display | 1 day |
| 5 | Zip backup/restore + full reset cleanup | 1–1.5 days |
| 6 | Delete hooks, help docs | 0.5 day |

**Total:** ~5–6 days

---

## Test checklist

| Test | File |
|------|------|
| Open Library metadata includes `cover_url` | `test/test_web_book_api.py` |
| Google metadata includes `cover_url` | fixture mock |
| `save_cover` / `delete_cover` round-trip | `test/test_cover_storage.py` |
| Web Metadata save writes file + `cover_path` | `test/test_web_book_details.py` |
| `delete` removes cover file | `test/test_cover_storage.py` |
| Zip backup contains db + covers | extend `test/test_list_backups.py` |
| Restore zip replaces covers dir | `test/test_list_backups.py` |
| Legacy `.db` restore still works | existing tests |

---

## Accessibility checklist

- [ ] Cover preview/name: `setAccessibleName` with title (and author when known)
- [ ] Placeholder: "No cover available" spoken, not silent empty
- [ ] Do not auto-focus cover on window open
- [ ] Status announce on download failure
- [ ] No cover column in main table

---

## Dependencies

- Implement after or in parallel with [`plan_ratings.md`](plan_ratings.md) — no schema conflict
- Package backup should ship with covers feature
- Requires network on Web Metadata save when cover URL present

---

## Out of scope (v1)

- Embedded art from audio files at import
- Standalone cover fetch menu item
- Cover in main book table
- Cover bulk download for library
- Orphan cleanup UI (optional v2)

---

## Next steps

Review in fall with [`plan_ratings.md`](plan_ratings.md). Recommended order: ratings first, then covers + package backup.
