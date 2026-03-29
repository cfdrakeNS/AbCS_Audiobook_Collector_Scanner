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
2. `Alt+/` reads the current status message on demand.
3. When `announce=True`, status is announced using one of two approved paths:
   - `announce_status_message(...)` helper (preferred where stable)
   - local focus-trick path (status bar temporarily focusable, then restore)
4. Focus is restored safely after announcement.
5. Default status text is stored for reliable readback.

### Reference implementations
- `src/accessibility/accessible_events.py` → `announce_status_message(...)`
- `src/ui/import_progress_window.py` → `set_status(...)`, `on_read_status_bar(...)`
- `src/ui/import_detail_window.py` → status mirror to parent + local read summary
- `src/ui/main_window.py` → local `set_status(...)` + `Alt+/`
- `src/ui/book_details.py` and `src/ui/update_window.py` → local status announce pattern

### Implementation notes
- Do not fire announcements for every passive refresh.
- Use `announce=True` only for meaningful state changes (selection changes, validation outcomes, mode transitions).
- Keep one concise status sentence; avoid long paragraphs in status text.

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
- [ ] Uses `exec_styled_message_box()` for all modal dialogs.
- [ ] Implements focus management after all operations (save, delete, cancel).
- [ ] Defines explicit tab order with `setTabOrder()` calls.
- [ ] Includes accessible names and descriptions for all widgets.
- [ ] Tests with both JAWS and NVDA screen readers.

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

## 11) Modal Message Box Best Practices Pattern

### Why this is unique to AbCS
- Standardized message boxes ensure consistent screen reader behavior
- Centralized styling maintains accessibility standards across all dialogs

### Standard behavior
1. Use `exec_styled_message_box(...)` for all modal dialogs
2. Always include proper icon (Warning, Information, Question, Critical)
3. Use consistent button text and default button selection
4. Return focus to relevant field after dialog closes
5. Include accessible names and descriptions for dialog content

### Reference implementations
- `src/accessibility/style_helpers.py` → `exec_styled_message_box(...)`
- `src/ui/collection_window.py` → Error handling with focus return
- `src/ui/web_metadata.py` → Confirmation dialogs before close

### Implementation notes
- Always import from `src.accessibility.style_helpers`
- Use appropriate icons for message type
- Set default button to safest option (usually No or Cancel)
- Consider JAWS users when crafting message text

---

## 12) Focus Management After Operations Pattern

### Why this is unique to AbCS
- Predictable focus behavior is critical for screen reader efficiency
- Users need to know where focus will be after each action

### Standard behavior
1. After save operations: return focus to updated/created item
2. After delete operations: return focus to first item in list
3. After cancel operations: return focus to list/table
4. Use `QTimer.singleShot()` for delayed focus when needed
5. Use helper methods like `focus_and_select_row()` and `focus_first_item()`

### Reference implementations
- `src/ui/collection_window.py` → Complete focus management after all operations
- `src/ui/book_details.py` → Focus return after save operations

### Implementation notes
- Test focus behavior with both JAWS and NVDA
- Use explicit focus setting rather than relying on default behavior
- Consider focus timing when UI updates are asynchronous

---

## 13) Tab Order Explicit Management Pattern

### Why this is unique to AbCS
- JAWS navigation relies heavily on predictable tab order
- Explicit tab order prevents focus jumping and confusion

### Standard behavior
1. Define tab order explicitly using `setTabOrder(widget1, widget2)`
2. Create tab order dynamically based on visible widgets
3. Handle tab order changes when widgets show/hide
4. Use helper methods like `_apply_tab_order()` for complex layouts

### Reference implementations
- `src/ui/collection_window.py` → Dynamic tab order for editing modes
- `src/ui/import_detail_window.py` → Complex form tab management

### Implementation notes
- Tab order should match visual layout
- Update tab order when widget visibility changes
- Test tab flow with keyboard only

---

## 15) Table Row Number Suppression Pattern

### Why this is unique to AbCS
- Row numbers are noise for data tables where content is meaningful
- JAWS announces "Row 1, Row 2" which interferes with data comprehension
- We optimize for clean screen reader experience by hiding irrelevant structural information

### Standard behavior
1. Hide vertical headers: `table.verticalHeader().setVisible(False)`
2. Set empty header labels: `table.setVerticalHeaderLabels([])`
3. Apply after table population: `setVerticalHeaderLabels([""] * rowCount)`
4. Add meaningful accessible text to table items using `Qt.AccessibleTextRole`

### Reference implementations
- `src/ui/reading_history_window.py` → General statistics table with meaningful value descriptions
- `src/ui/backup_restore_window.py` → Backup list table in `refresh_backup_list()`
- `src/ui/name_list_window.py` → Name/author lists with empty header labels
- `src/ui/main_window.py` → Book list table with hidden vertical headers

### Implementation notes
- Apply `setVerticalHeaderLabels()` after populating table data
- Use `setData(Qt.AccessibleTextRole, "meaningful text")` for value items
- Test with JAWS to ensure row numbers are not announced
- Pattern applies to all data tables where row numbers provide no functional value

---

## 16) Screen Reader-Optimized Button Enablement Pattern

### Why this is unique to AbCS
- Screen reader users benefit from consistent button behavior and clear feedback
- Disabled buttons can be confusing when the reason isn't obvious
- We enable buttons but provide meaningful error messages with context

### Standard behavior
1. **Keep buttons enabled** for better accessibility and discoverability
2. **Provide clear error messages** when buttons are clicked without valid prerequisites
3. **Use status announcements** to inform screen reader users what's happening
4. **Maintain consistent focus management** after error dialogs

### Reference implementations
- `src/ui/backup_restore_window.py` → Delete button always enabled, shows "No backup selected" message
- `src/ui/import_window.py` → Browse and action buttons with validation feedback
- `src/ui/book_details_window.py` → Save button with field validation messages

### Implementation notes
- **Delete buttons**: Always enabled, show helpful message when no selection exists
- **Action buttons**: Enable when prerequisites exist, but provide clear error feedback
- **Error messages**: Include specific guidance on what the user needs to do
- **Focus restoration**: Return focus to the relevant field after error dialogs
- **Status announcements**: Use centralized announce_status_message for consistency

### Example error message patterns
```python
# Delete button without selection
"Delete canceled: no backup row selected in Backup List"

# Restore button without file  
"Restore canceled: no backup selected"

# Import without folder
"Scan canceled: no folder selected for import"
```

---

## 18) Global Enter Shortcut Anti-Pattern

### Why this is unique to AbCS
- Global Return/Enter shortcuts interfere with button accessibility
- Screen reader users rely on Enter to activate focused buttons
- Qt's default button behavior must be preserved for accessibility

### Standard behavior
1. **NEVER use global Return/Enter shortcuts** in windows with buttons
2. **Handle Enter in keyPressEvent** instead for specific widgets (like tables)
3. **Preserve Qt's default button behavior** for Enter key activation
4. **Use setAutoDefault carefully** - it can block Enter key on buttons

### Reference implementations
- `src/ui/import_window.py` → keyPressEvent handles Enter for table, preserves button behavior
- `src/ui/book_details.py` → No global Enter shortcuts, buttons work with Enter
- `src/ui/main_window.py` → No global Enter shortcuts, default Qt behavior

### Implementation notes
- **Bad pattern**: `QShortcut(QKeySequence("Return"), self)` - blocks all Enter keys
- **Good pattern**: Handle Enter in `keyPressEvent` for specific widgets only
- **Button setup**: Avoid `setAutoDefault(False)` unless absolutely necessary
- **Testing**: Verify Enter works on all focused buttons after adding shortcuts

### Example correct implementation
```python
def keyPressEvent(self, event):
    if event.key() in (Qt.Key_Return, Qt.Key_Enter):
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QPushButton):
            # Let Qt handle Enter on buttons (default behavior)
            return super().keyPressEvent(event)
        elif self.table.hasFocus():
            # Handle Enter for specific widget
            self.on_table_action()
            return
    super().keyPressEvent(event)
```

---

## 19) Suggested extraction for future apps

If this pattern set is reused in a new app, extract into shared modules:
- `accessibility/status_contract.py` (set/read/announce helpers)
- `accessibility/combo_noise_guard.py` (event filter mixin)
- `accessibility/alt_key_policy.py` (allowlist filter)
- `accessibility/dialogs.py` (styled modal helpers)
- `accessibility/shortcut_help.py` (standard help dialog builder)
- `accessibility/focus_manager.py` (focus management helpers)
- `accessibility/tab_order.py` (tab order management)

This keeps app behavior consistent while reducing per-window copy/paste drift.
