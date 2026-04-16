---

## Status Update (April 16, 2026)

### What is implemented so far
- The Preferences window still contains the “Options” and “Auto-Correction” sections, including checkboxes for:
  - Review clean books before adding (“Add Valid” logic)
  - Flip Author Name
  - Apply Proper Case
  - Move leading 'The', 'A', 'An' to end of title
- The codebase (import_scanner.py and related modules) still references flags for punctuation, proper case, and other auto-correct options.
- No removal or refactor of these options has been completed yet; the UI and logic are still present.

### What’s next (plan)
1. **Remove UI elements:**
   - Delete the “Options” and “Auto-Correction” groups and all related checkboxes from PreferencesWindow. IMPORTANT!: ensure no extra vertical spacing is applied where the old sections were.
   - Remove any code that loads/saves these preferences from QSettings.
2. **Refactor logic:**
   - Remove all code paths that check these flags in import_scanner.py, book_list_import, web_metadata, and related modules.
   - Make proper case, trim whitespace, punctuation, and special character cleanup always apply before saving to the DB (no user toggle).
   - Remove “flip author” and “move leading articles” logic entirely.
   - Remove “Add Valid” button and logic from import windows; update status bar and shortcut help accordingly.

3. **Update documentation and tests:**
   - Update this file to reflect these removals.
   - Add a checklist for manual and automated testing to ensure all options are gone and normalization is always applied.

### Practical approach for effective testing
- After code changes, verify:
  - Preferences window no longer shows removed options.
  - Importing books always applies normalization (proper case, trim, etc.).
  - No “flip author” or “move leading article” logic is present.
  - “Add Valid” button and related status/shortcuts are gone.
  - All modules (import, book details, update, etc.) behave as expected with new normalization defaults.

---
