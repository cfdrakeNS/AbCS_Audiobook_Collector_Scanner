# Copilot_JAWS_ Working_Agreement (AbCS)

This file is the shared workflow for productive, low-friction coding with JAWS.

## 1) Default Collaboration Mode (Notepad Mode)

Use these defaults unless explicitly changed:

- Short replies
- Plain text first
- One task at a time
- One file at a time
- One function at a time
- Small patches only (no large rewrites)
- No speculative edits
- Accessibility-first for JAWS/NVDA
- “Done check” included for each change

---

## 2) Best AI Setup for Python + JAWS

- IDE: Visual Studio Code (stable)
- AI: GitHub Copilot Chat
- Model for coding tasks: GPT-5.3-Codex
- Core extensions:
  - Python
  - Pylance
  - Ruff
  - GitHub Copilot
  - GitHub Copilot Chat

### Reading output accessibly
Prefer log files over terminal scroll:

```powershell
py src/main.py *> run.log
```

Open `run.log` in editor or Notepad.

---

## 3) One-Page Workflow (Daily Use)

1. Define one small outcome.
2. Name exact file and function.
3. Apply minimal patch only.
4. Save file.
5. Run app or targeted check.
6. Confirm expected text/behavior.
7. Commit small working change.

### Golden rule
If a change is not visible in file diff, it did not happen.

---

## 4) Request Template (User → Copilot)

Use this exact format:

- File: `src/...`
- Function: `...`
- Change: `single behavior`
- Do not touch: `list`
- Done when: `exact expected result`

Example:

- File: `src/ui/main_window.py`
- Function: `on_help_about`
- Change: replace message box with read-only text box for JAWS
- Do not touch: menu wiring, other dialogs
- Done when: About opens as read-only text area and can be read continuously by screen reader

---

## 5) Response Template (Copilot → User)

1. Goal  
2. File  
3. Replace this  
4. With this  
5. Done check

No extra files unless requested.

---

## 6) Verification Checklist (Per Change)

- [ ] `git diff -- <file>` shows expected edits
- [ ] No indentation/runtime errors
- [ ] Keyboard shortcuts still valid
- [ ] Status messages are screen-reader friendly
- [ ] Behavior matches “Done when”

---

## 7) Accessibility/Scope Rules for AbCS

- Keep 14pt+ scaling model intact
- Keep status bar announcements meaningful
- Preserve existing shortcut conventions
- Do not add raw SQL in UI layer
- Prefer small, reversible commits

---

## 8) Quick Recovery When Things Drift

If work gets messy:

1. Stop.
2. Revert partial edits in that file.
3. Re-state one outcome with request template.
4. Apply only one minimal patch.
5. Verify with `git diff` before running.

---

## 9) Session Start Line

Paste this at the start of any session:

**“Notepad mode, one fix at a time, one file only, minimal patch, include done check.”**
````

If you want, next I can create a second file `copilot_jaws_quick_ref.txt` (ultra-short version for fast copy/paste).