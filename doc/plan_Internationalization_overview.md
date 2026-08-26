# AbCS Internationalization — High-Level Overview

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Preferences](help_docs/10_preferences.md), [Help docs authoring](help_docs_authoring.md)

---

## Scope of Change

No i18n infrastructure exists today. All UI text is hardcoded inline English across 22 UI files and several accessibility modules. A codebase review counted roughly **1,500–2,000 user-facing string literals/templates** across:

- `src/ui/` — labels, buttons, window titles, status messages, QMessageBox text, table headers, menus
- `src/accessibility/shortcuts.py` — ~100 keyboard shortcut description strings
- `src/accessibility/theme_manager.py` / `theme_picker.py` — theme display names
- `src/accessibility/style_helpers.py` — dialog button accessible names
- `help_docs/` (22 `.md` files) — full help content (separate pipeline)

Heaviest files: `import_detail_window.py`, `preferences_window.py`, `book_details.py`, `main_window.py`, `import_window.py`, `book_list_import_window.py`.

---

## Recommended Approach: Custom Strings Catalog

Qt Linguist (the "standard" Qt way) requires wrapping every string in `self.tr()` and running external build tools. A simpler **custom strings catalog** fits the project better because:

- Accessible names and visible labels are often *different text* for the same control — a translation file needs to hold both together
- Dynamic f-strings with variables need format-string templates, which a dict handles more naturally than Qt's `.ts` XML
- No external toolchain dependency; translators edit a plain Python dict or JSON file

### Architecture

```
src/
  i18n/
    __init__.py       # get_text(key) or _() function; loads active language
    en.py             # English strings dict (source of truth)
    fr.py             # French strings dict
    es.py             # Spanish strings dict
    strings_base.py   # Fallback logic: missing key → English fallback + warning
```

Each language file is a flat Python dict:

```python
# en.py
STRINGS = {
    "main.title": "AbCS — Audiobook Collector Scanner",
    "main.menu.file": "&File",
    "book_details.save_btn": "Save",
    "book_details.save_btn.accessible": "Save book changes",
    "import.status.found": "Found {count} books in {folder}",
    # ...
}
```

Usage at call sites:

```python
from src.i18n import _
self.save_btn.setText(_("book_details.save_btn"))
self.save_btn.setAccessibleName(_("book_details.save_btn.accessible"))
set_status(_("import.status.found").format(count=n, folder=p), announce=True)
```

Language is set once at startup (from preferences) and held in a module-level singleton.

---

## Categories of Work

- **Phase 1 — Catalog extraction:** Read every UI file and build `en.py` with all strings. This is the bulk of the mechanical work — touching ~955 API-call lines plus QLabel/QPushButton constructor literals.
- **Phase 2 — Call-site replacement:** Replace inline strings with `_("key")` at each call site.
- **Phase 3 — Dynamic strings:** Convert f-string status/error messages (~250+) to format-string templates in the catalog.
- **Phase 4 — Accessibility text pairs:** Ensure every visible label key has a matching `.accessible` key where the wording differs.
- **Phase 5 — Preferences UI:** Add a Language selector to `preferences_window.py`; store choice in app settings; apply on next launch (or live reload if desired).
- **Phase 6 — Translation files:** Produce `fr.py` and `es.py` by translating `en.py`. Help docs (`help_docs/*.md`) are a separate translation pipeline — one set of `.md` files per language, loaded by `help_window.py` based on active locale.
- **Phase 7 — Testing:** Verify no English strings leak; test with JAWS/NVDA in each language.

---

## Special Considerations

- **Accessible names vs. visible text:** Many controls set both. The catalog must store them as separate keys. This is the main reason Qt Linguist alone is awkward here.
- **Plural forms:** Strings like "1 book found" vs. "3 books found" need a small plural helper (`ngettext`-style).
- **Help docs:** The 22 `help_docs/*.md` files are rendered by `help_window.py`. Localization would mean a `help_docs/fr/` subfolder structure and a path-selection rule in `help_paths.py`.
- **Keyboard shortcut descriptions** in `shortcuts.py` are already in a dict — these are the easiest to migrate.
- **Dialog prose** in `about_dialogue.py`, `license_dialogue.py`, `setup_dialogue.py` uses `("heading"|"body", "text")` tuple lists — these can become catalog keys with the same tuple structure.
- **Theme names** (12 entries in `theme_manager.py`) are short and easy to catalog.

---

## Feasibility Assessment

| Factor | Assessment |
|--------|-----------|
| Technical complexity | Medium-high — no blockers, purely mechanical + careful |
| Volume | Large — ~1,500 strings to extract and key |
| Risk to accessibility | Low if done carefully; accessible names travel with visible labels in catalog |
| Translation maintenance | Ongoing — new strings added to `en.py` must be mirrored in all language files |
| Estimated effort | 3–5 weeks of focused work (extraction + replacement + 2 languages) |

**Verdict: Fully feasible.** The codebase has no technical barriers. The work is large and methodical but carries low risk of breaking functionality if done file-by-file with testing between phases.

---

## Next Steps

Review this plan in fall and decide whether to proceed with i18n work. If approved, a detailed implementation plan can be written with file-by-file extraction order and translation workflow.
