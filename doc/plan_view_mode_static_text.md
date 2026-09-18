# View-mode static text (silence JAWS edit / read-only noise)

**Status:** Planned (not yet implemented)  
**Created:** September 2026  
**Related:** [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md), Book Details view mode in [`src/ui/book_details.py`](../src/ui/book_details.py)

---

## What this is

In **view** mode, form fields should be announced as display values (name + value), **without** JAWS saying “edit” or “read only.” Edit mode keeps real editable controls.

---

## Problem

- View fields today use `QLineEdit` / `QSpinBox` / `QDateEdit` with `setReadOnly(True)`.
- JAWS correctly says **read only**, but that is noisy when tabbing many fields.
- Clearing `readOnly` and blocking keys (tried Sept 2026) made JAWS say **edit**, which is misleading for view mode. That approach was **reverted**.

Screen readers need the **actual mode**: view = not an edit; edit mode = edit.

---

## Design (option 2)

Keep view/edit stacks where they already exist (author, series, genre, collection). Extend the pattern:

1. **View mode:** show static/display controls (e.g. focusable `QLabel`, or `QLineEdit` with a custom accessible interface reporting **StaticText** / non-editable role — pick the approach that JAWS and NVDA both accept after a short spike).
2. **Edit mode:** show the real `QLineEdit` / combo / spin / date widgets (unchanged behavior).
3. Apply the same pattern to other always-display form fields (Import Detail metadata, Web Metadata compare rows, path fields, Preferences scenario/rules text if appropriate).

**Do not** clear Qt `readOnly` on edit widgets while leaving their EditableText role — that causes “edit” announcements.

**Leave unchanged:** Help / About / Setup / License body text (`create_accessible_read_only_text`) — “read only” is useful there.

**Estimate:** 2–4 days (spike half day + Book Details + other windows + JAWS/NVDA check)

---

## Spike first

Confirm with JAWS and NVDA which control reports cleanly:

- Focusable `QLabel` (name + value, TabFocus)
- vs custom `QAccessibleInterface` on a styled line edit reporting StaticText

Ship only the approach that speaks name and value with neither “edit” nor “read only.”

---

## Tests

- View mode: accessible role/state is not EditableText + ReadOnly for display fields.
- Edit mode: fields remain editable; Alt+U / Save flow unchanged.
- Typing in view mode does not change values.

---

## Accessibility checklist

- Tab order preserved in view and edit mode
- Alt+/ status readback unchanged
- Page Up/Down title focus still speaks title only
- Plot review stays as `PlotLineList` (already non-edit)

---

## Out of scope v1

Changing Help/About document viewers; Import Progress `NoFocus` fields.
