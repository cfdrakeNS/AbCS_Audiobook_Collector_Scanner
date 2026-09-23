# View-mode static text (silence JAWS edit / read-only noise)

**Status:** Planned — **Version 3 Phase 14 (optional)**  
**Created:** September 2026  
**Updated:** September 2026 (findings from failed first attempt)  
**Related:** [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), Book Details view mode in [`src/ui/book_details.py`](../src/ui/book_details.py)

---

## What this is

In **view** mode, form fields should be announced as display values (name **and** value), **without** JAWS saying “edit” or “read only.” Edit mode keeps real editable controls.

---

## Problem

- View fields today use `QLineEdit` / `QSpinBox` / `QDateEdit` with `setReadOnly(True)`.
- JAWS correctly says **read only**, but that is noisy when tabbing many fields.
- Clearing `readOnly` and blocking keys (tried Sept 2026) made JAWS say **edit**, which is misleading for view mode. That approach was **reverted**.

Screen readers need the **actual mode**: view = not an edit; edit mode = edit.

---

## Findings (Sept 2026 — do not repeat)

A first pass shipped focusable `QLabel` stacks across Book Details (value in `accessibleDescription`, name in `accessibleName`). **JAWS on Tab spoke only the field label** — e.g. “Author” with no value. That build was **fully reverted** with the rest of the rushed v3 code.

Lessons:

1. **JAWS often does not speak `accessibleDescription` on Tab focus.** Putting the value only in description is not enough.
2. **Spike must be accepted with JAWS (and NVDA) before any Book Details change.** A throwaway harness is required; unit tests alone do not catch this.
3. **Do not convert the whole form at once.** After a spike passes, change one field group, pause for tester JAWS check, then continue.
4. Candidates to try in the spike (pick what actually speaks name + value):
   - Focusable `QLabel` with **accessible name = `"Author: Jane Austen"`** (value in the name), blank or secondary description
   - Focusable `QLabel` whose **visible text** is what JAWS reads (verify name vs text)
   - Custom `QAccessibleInterface` reporting StaticText / non-editable with name+value
   - Keep read-only line edits if no static control beats “read only” for both JAWS and NVDA — noisy but correct beats silent values

**Pass criteria for the spike:** Tab to the control; JAWS says the field identity **and** the current value; neither “edit” nor “read only” (unless we deliberately keep read-only as the fallback).

---

## Design (after spike only)

Keep view/edit stacks where they already exist (author, series, genre, collection). Extend only the pattern the spike approved:

1. **View mode:** display control that JAWS/NVDA already proved speaks name + value.
2. **Edit mode:** real `QLineEdit` / combo / spin / date widgets (unchanged).
3. Later: other view-mode forms (Import Detail, Web Metadata rows, etc.) — same pattern, same per-window JAWS check.

**Do not** clear Qt `readOnly` on edit widgets while leaving their EditableText role — that causes “edit” announcements.

**Leave unchanged:** Help / About / Setup / License body text (`create_accessible_read_only_text`) — “read only” is useful there.

**Estimate:** 2–4 days (spike half day + Book Details in small batches + other windows + JAWS/NVDA check)

---

## Spike first (gate)

Throwaway script (e.g. `test/view_mode_static_text_spike.py`) with Tab-able rows comparing candidates side by side. **Stop for tester JAWS/NVDA confirmation before editing `book_details.py`.**

Ship only the approach that meets the pass criteria above.

---

## Implementation order (Book Details)

1. Spike approved.
2. One stacked combo group (e.g. author only) → JAWS check.
3. Remaining stacked combos (series, genre, collection) → JAWS check.
4. Other view fields (title, year, reader, …) in small batches → JAWS check after each batch.
5. Page Up/Down title focus still speaks title only; Alt+/ unchanged.

---

## Tests

- Spike harness remains runnable after the chosen approach is picked.
- View mode: value is present in whatever accessible property JAWS actually speaks (not description-only unless spike proved otherwise).
- Edit mode: fields remain editable; Alt+U / Save flow unchanged.
- Typing in view mode does not change values.

---

## Accessibility checklist

Follow the master checklist: [Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases).

- Tab order preserved in view and edit mode
- Alt+/ status readback unchanged
- Page Up/Down title focus still speaks title only
- Plot review stays as `PlotLineList` (already non-edit)
- **Tester JAWS confirmation after spike and after each Book Details batch**
- Edit-mode buttons (Save, Cancel, etc.) keep existing accessible button styling — do not restyle as part of this phase

---

## Out of scope v1

Changing Help/About document viewers; Import Progress `NoFocus` fields.
