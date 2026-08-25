# Ratings — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Web Metadata](help_docs/07_web_metadata.md), [Book Details](help_docs/04_book_details.md), [Import explained](help_docs/19_import_explained.md), [Plan_covers.md](Plan_covers.md)

---

## What this is

Add a dedicated **rating** field on each book, stored in SQLite, **editable by the user**, and populate-able from **Web Metadata** fetch. Rating appears on the **main book table** (score only) and on **Book Details**, **Import Detail**, and **Web Metadata** windows.

Rating is **plain numbers**, not star glyphs — required for JAWS/NVDA accessibility.

---

## Problem

| Today | Issue |
|-------|--------|
| `WebBookAPI` returns `rating` and `ratings_count` | Not stored in dedicated columns |
| Web Metadata save | Rating may be embedded in `comments` as `Rating: 4.0 (1,234 ratings)\n{plot}` via `_build_plot_text_for_db` in [`src/ui/web_metadata.py`](../src/ui/web_metadata.py) |
| `BookQueries._row_to_book` | Comment `# rating and series_number removed` — column existed historically |
| Help [`help_docs/07_web_metadata.md`](../help_docs/07_web_metadata.md) | States rating is not saved |
| Book Details / Import Detail | No rating field; plot may show rating prefix via `PlotLineList` |
| Main window table | No rating column |

---

## Design decisions

### Display: numbers only, never stars

| Surface | Visible text | Screen reader (`AccessibleTextRole` / field description) |
|---------|--------------|--------------------------------------------------------|
| Main table | `4.5` or empty | `"Rating 4.5 out of 5"` |
| Book Details / Import Detail | Editable field showing `4.5`; suffix label for count when from web | `"Rating"`, description `"Your rating from 0 to 5. Community count 1,234 ratings when from web metadata."` |
| Web Metadata | Read-only `rating_edit` (existing) | Unchanged pattern; save writes to DB columns |

Do **not** use Unicode stars (★) or custom star widgets.

### One rating value, two sources

- **`rating`** (`REAL`, nullable) — the value shown everywhere. User may type it in Book Details or Import Detail. Web Metadata may overwrite it when the user saves a fetched value.
- **`ratings_count`** (`INTEGER`, nullable) — **community count from web only**. Shown as read-only suffix text next to the rating field when present (e.g. `(1,234 ratings)`). Not editable by the user.

**Manual edit rule:** When the user changes `rating` in Book Details or Import Detail, **clear `ratings_count`** so the UI does not imply a community average for a personal score.

**Web Metadata save rule:** Set both `rating` and `ratings_count` from web data when the user applies the rating difference.

### Validation

- Allowed range: **0.0–5.0** (inclusive), one decimal place preferred (match web display `f"{rating_val:.1f}"`).
- Empty field = `NULL` in DB (no rating).
- Reject invalid input on save with accessible warning dialog (same pattern as title required in `book_details.on_save`).

### Input control

Use **`QLineEdit`** with `QDoubleValidator(0.0, 5.0, 1)` — not `QDoubleSpinBox` (spin buttons add noise for screen readers). Parse on save with clear error message if text is non-empty but invalid.

---

## Database

### Schema migration

In [`src/database/connection.py`](../src/database/connection.py) `column_specs["books"]`, add:

```text
rating         REAL
ratings_count  INTEGER
```

Existing `_ensure_legacy_schema_compatibility` adds missing columns on startup.

Update [`test/fixtures/abcdDB_def.sql`](../test/fixtures/abcdDB_def.sql) for fresh installs (and gitignored `data/abcdDB_def.sql` if used locally).

### Model and queries

[`src/database/models.py`](../src/database/models.py) — add to `Book`:

```python
rating: Optional[float] = None
ratings_count: Optional[int] = None
```

[`src/database/queries.py`](../src/database/queries.py):

- `_row_to_book` — map columns
- `insert` — add columns to INSERT and params tuple (lines ~187–211)
- `update` — add columns to UPDATE and params tuple (lines ~222–248)
- All `SELECT b.*` queries pick up new columns automatically

### One-time data migration (app startup)

New helper e.g. `src/database/rating_migration.py`:

1. `SELECT book_id, comments FROM books WHERE comments LIKE 'Rating:%'`
2. For each row, use `_split_rating_and_body` from [`src/accessibility/read_only_text.py`](../src/accessibility/read_only_text.py)
3. Parse `Rating: 4.5 (1,234 ratings)` with regex (patterns in [`test/test_read_only_text.py`](../test/test_read_only_text.py))
4. `UPDATE books SET rating=?, ratings_count=?, comments=? WHERE book_id=?` with stripped plot body
5. Run once; set marker `{user_data}/.rating_migration_done`

---

## UI changes by window

### Main window — [`src/ui/main_window.py`](../src/ui/main_window.py)

**`BookTableModel`**

1. Extend `HEADERS` — insert `"Rating"` at index **5** (after Genre, before Time):

   ```python
   HEADERS = ["Author", "Title", "Year", "Series", "Genre", "Rating", "Time", "Read"]
   ```

2. In `data()`:
   - Column 5 DisplayRole: `f"{book.rating:.1f}"` if `book.rating is not None` else `""`
   - Column 5 AccessibleTextRole: `"Rating 4.5 out of 5"` when set
   - Shift Time → column 6, Read → column 7 in all `col ==` branches
   - `TextAlignmentRole`: center Rating like Year

3. **`_SORT_KEY_TO_COLUMN`**: add `"Rating": 5`
4. **`_DIRECTION_SORT_KEYS`**: add `"Rating"`
5. **`_apply_fixed_content_column_widths`**: `5: 56` for Rating
6. Sort menu: add Rating action
7. In-memory sort: `lambda b: (b.rating is None, b.rating or 0)` — nulls last ascending

### Book Details — [`src/ui/book_details.py`](../src/ui/book_details.py)

1. Row constants — insert `ROW_RATING = 3`; increment `ROW_YEAR_TIME` through `ROW_PATH` by 1

2. Widgets after Plot row:

   ```python
   rating_label = QLabel("Rating:")
   self.rating_edit = QLineEdit()
   self.rating_edit.setAccessibleName("Rating")
   self.ratings_count_label = QLabel("")  # "(1,234 ratings)", NoFocus
   ```

3. Tab order: `plot_stack` → `rating_edit` → `year_spin`

4. **Shortcut:** `Alt+V` → `rating_edit` (add `"V"` to `ALLOWED_ALT_KEYS`; `Alt+R` remains Reader)

5. `load_book`: populate from `book.rating` / `book.ratings_count`

6. `on_save`: parse float or None; clear `ratings_count` on manual change; write to `self.book`

7. `textChanged` → `_mark_dirty`

### Import Detail — [`src/ui/import_detail_window.py`](../src/ui/import_detail_window.py)

Mirror Book Details rating row.

1. `book_data` keys: `"rating"`, `"ratings_count"`
2. `_collect_form_data` / `on_save`: same parse and clear-count rules
3. [`src/ui/import_window.py`](../src/ui/import_window.py) `_build_book_from_scan`: map rating onto `Book` before `insert`
4. `Alt+V` in `ALLOWED_ALT_LETTERS`

### Web Metadata — [`src/ui/web_metadata.py`](../src/ui/web_metadata.py)

1. **`_build_plot_text_for_db`:** plot only — no rating prefix
2. **`compute_field_differences`:** add `rating` / `ratings_count` column diffs; plot without prefix
3. **`on_save_clicked`:** set `book.rating`, `book.ratings_count` from web when applied
4. Announce "Rating" in applied fields when saved

### Update window — no change in v1

---

## Implementation phases

| Phase | Work | Estimate |
|-------|------|----------|
| 1 | Schema, model, insert/update | 0.5 day |
| 2 | Comments-prefix migration + tests | 0.5 day |
| 3 | Web Metadata save path | 1 day |
| 4 | Book Details + Import Detail UI | 1 day |
| 5 | Main table column + sort | 0.5 day |
| 6 | Help docs | 0.5 day |

**Total:** ~4–5 days

---

## Test checklist

| Test | File |
|------|------|
| Migration strips prefix, sets columns | `test/test_rating_migration.py` |
| `compute_field_differences` rating | `test/test_web_book_details.py` |
| Plot saved without prefix | `test/test_web_book_details.py` |
| Table model display + AT role | new or `test/test_main_window_*.py` |
| Book Details validation + clear count | `test/test_book_details_rating.py` |
| Import path persists rating | import test |

---

## Accessibility checklist

- [ ] Main table: numeric text + `AccessibleTextRole` (not stars)
- [ ] Rating field: buddy, name, description
- [ ] Count suffix: `NoFocus`; context in rating description
- [ ] `announce=True` on Web Metadata save when rating applied
- [ ] Alt+/ unchanged
- [ ] `is_unmapped_alt_letter` on rating_edit
- [ ] Deselect on FocusIn for rating_edit

---

## Out of scope (v1)

- Dual personal/community columns
- Bulk rating in Update window
- Rating filter on main window
- Star glyphs
- Rating from audio tags at import

---

## Next steps

Review in fall. Implement phases 1–6. Then [`Plan_covers.md`](Plan_covers.md) if approved.
