# AbCS Accessibility Implementation Patterns (Reusable Standard)

Purpose: capture **AbCS-specific accessibility patterns** that go beyond generic PySide best practices, so new features (or new apps) keep the same behavior.

Scope: these are implementation conventions already used in this codebase.

---

## 1) Status bar pattern: `set_status(...)` + `Alt+/` readback

### Why this is unique to AbCS
- We treat status as a primary screen-reader channel.
- We optimize for JAWS behavior using controlled focus movement and explicit readback.
- We intentionally balance announcement clarity vs noise.

### Standard behavior
1. Each major window exposes a status method (`set_status(...)` or `show_status(...)`).
2. `Alt+/` calls `read_status_bar_message(status_bar, fallback=...)` — reads **only** `currentMessage()` (or fallback), no popup when no screen reader is active.
3. At status bar creation, call `configure_status_bar_accessibility(status_bar)` (empty name/description, no focus).
4. Sighted tooltips on status bars use `apply_status_bar_tooltip(...)` only — **never** set `accessibleDescription` on a status bar.
5. When `announce=True`, use `announce_status_message(...)` (clears description and sets accessible name before focus move).
6. Focus is restored safely after announcement.
7. Default status text may be stored as `_default_status_message` for fallback when the bar is empty.

### Reference implementations
- `src/accessibility/accessible_events.py` → `read_status_bar_message`, `prepare_status_bar_for_readback`, `announce_status_message`
- `src/accessibility/style_helpers.py` → `apply_status_bar_tooltip`
- Any window with `on_read_status_bar` / `on_read_status` (main, import, import detail, import progress, preferences, book details, book list import, collection, name list, backup/restore, reading history, update, web metadata)

### Implementation notes
- Do not fire announcements for every passive refresh.
- Use `announce=True` only for meaningful state changes (selection changes, validation outcomes, mode transitions).
- Keep one concise status sentence; avoid long paragraphs in status text.
- Do not prefix Alt+/ readback with labels like "Status messages for this window" or synthetic summaries not shown in the bar.

---

## 2) Combo box anti-noise pattern: block plain arrow changes

### Why this is unique to AbCS
- Plain Up/Down can silently change combo values in ways JAWS may not announce clearly.
- We intentionally require explicit dropdown interaction (`Alt+Up/Down`) to reduce accidental silent edits.

### Standard behavior
1. Install event filters on combo boxes (and editable line edits inside combos when applicable).
2. Block plain `Up/Down` keys on combo boxes.
3. Allow `Alt+Up/Down` to open/select from dropdown.
4. Beep on blocked plain arrow keys (user feedback).
5. Handle Enter in editable combos as commit action + move focus logically.
6. Use FocusOut handlers for typed values with skip flags to avoid duplicate processing.

### Reference implementations
- `src/ui/book_details.py` → combo arrow blocking rationale and behavior
- `src/ui/update_window.py` → full pattern (arrow blocking, Enter commit, FocusOut apply, skip flags)
- `src/ui/preferences_window.py` → now applies the same plain-arrow block (`Up/Down`) with `Alt+Up/Down` allowed.

### Implementation notes
- If a combo supports free typing, ensure FocusOut and Enter follow the same validation path.
- Keep tab order explicit around combo groups.

### Current adoption snapshot (Mar 01, 2026)
- **Applied (enforced):**
   - `src/ui/book_details.py`
   - `src/ui/update_window.py`
   - `src/ui/preferences_window.py`
   - `src/ui/import_detail_window.py` (for `Author`, `Series`, `Genre` combos)
- **Intentionally left as-is:**
   - `src/ui/main_window.py` (current behavior accepted for this window)
   - `src/ui/import_window.py` (current behavior accepted for this window)

Use the rule where editable combo changes can create silent/noisy value changes; keep current behavior where existing UX is validated and intentional.

Traceability:
- Validation test for `ImportDetailWindow` combo anti-noise behavior is defined as **GAP-02 / Test 02C** in `accessibility_gap_Todo.md`.

---

## 3) Alt-letter hygiene pattern: suppress unmapped Alt keys

### Why this is unique to AbCS
- In JAWS-heavy usage, stray Alt+letters can leak into editable fields and create noisy/incorrect input.
- We intentionally consume unmapped Alt-letter events.

### Standard behavior
1. Define a per-window allowlist of Alt letters.
2. In event filter, block `Alt+[A-Z]` keys not in allowlist.
3. Keep `Alt+/` and `Alt+?` available for status readback in every major window.

### Reference implementations
- `src/accessibility/key_filters.py` → `is_unmapped_alt_letter(...)`
- `src/ui/main_window.py` → search box event filter usage
- `src/ui/import_progress_window.py` → `ALLOWED_ALT_LETTERS` + event filter
- `src/ui/update_window.py` → local allowed-alt filtering for editable combos

### Implementation notes
- Always document window shortcut allowlist in the help dialog and shortcut table.

---

## 4) JAWS-specific input stability pattern

### Why this is unique to AbCS
- We include targeted widget behavior to avoid JAWS interception side-effects.

### Standard behavior
- Use custom widgets where needed to stabilize key handling under JAWS.

### Reference implementations
- `src/ui/main_window.py` → `JAWSCompatibleSearchBox` for backspace/delete reliability.

---

## 5) Modal messaging standard: styled, consistent, accessible dialogs

### Why this is unique to AbCS
- Error and confirmation messages are standardized for readability and consistent keyboard/screen-reader flow.

### Standard behavior
1. Use `exec_styled_message_box(...)` for warnings/errors/info prompts.
2. Keep button text explicit (where needed) and consistent with keyboard workflow.
3. After validation failures, return focus to the offending field.

### Reference implementations
- `src/accessibility/style_helpers.py` → `exec_styled_message_box(...)`
- Used broadly in `src/ui/*.py` windows.

### Implementation notes
- Prefer modal dialogs for errors over background-only status messages.

---

## 6) Quiet-mode/read-only info fields pattern (noise control)

### Why this is unique to AbCS
- Some data fields are intentionally non-focusable (`Qt.NoFocus`) to reduce focus churn and repetitive announcements.
- Status readback (`Alt+/`) is used as the primary access path for current state.

### Standard behavior
1. For high-frequency progress/telemetry values, non-focusable read-only fields are allowed.
2. Ensure equivalent information is available via status readback.
3. If a control is hidden or non-focusable by design, avoid misleading shortcut hints that imply direct focus navigation.

### Reference implementations
- `src/ui/import_progress_window.py` (compact mode, hidden issues row, non-focusable counters)

### Implementation notes
- This pattern is valid only when readback channel is reliable and test-verified.

---

## 7) Keyboard help dialog pattern (per-window)

### Why this is unique to AbCS
- We provide a consistent keyboard-shortcuts help surface tailored per window, optimized for screen-reader traversal.

### Standard behavior
1. `F1` opens a keyboard shortcuts dialog.
2. Dialog uses a simple one-column table/list with readable combined text.
3. Include `Alt+/` in every shortcuts list.

### Reference implementations
- `src/ui/import_detail_window.py` → `on_show_shortcuts(...)`
- Similar pattern in `main_window.py`, `update_window.py`, `import_progress_window.py`, `preferences_window.py`, `name_list_window.py`.

---

## 8) Reuse checklist for new windows/features

When building a new window, confirm:
- [ ] Has `set_status(...)` (or equivalent) + `Alt+/` readback.
- [ ] Uses approved status announcement path with safe focus restore.
- [ ] Alt-letter allowlist enforced; unmapped Alt letters suppressed.
- [ ] Combo boxes follow anti-noise arrow behavior where editing risk exists.
- [ ] Validation errors use modal dialog + focus return to invalid field.
- [ ] Has per-window shortcuts help (`F1`) including `Alt+/`.
- [ ] Any intentional noise-reduction behavior is documented inline and in test docs.

---

## 9) Decision policy: accessibility vs noise tradeoffs

Use these labels in testing/docs:
- `Confirmed defect` = user cannot access required info/action reliably.
- `Intentional design (noise reduction)` = behavior is deliberate and test-validated.
- `Needs design decision` = tradeoff unclear; decide before coding.

Rule of thumb:
- If behavior reduces noise **and** preserves reliable access via `Alt+/` or another explicit channel, it can be intentional.
- If behavior reduces noise but hides required context/actions, treat as defect.

---

## 10) Suggested extraction for future apps

If this pattern set is reused in a new app, extract into shared modules:
- `accessibility/status_contract.py` (set/read/announce helpers)
- `accessibility/combo_noise_guard.py` (event filter mixin)
- `accessibility/alt_key_policy.py` (allowlist filter)
- `accessibility/dialogs.py` (styled modal helpers)
- `accessibility/shortcut_help.py` (standard help dialog builder)

This keeps app behavior consistent while reducing per-window copy/paste drift.
