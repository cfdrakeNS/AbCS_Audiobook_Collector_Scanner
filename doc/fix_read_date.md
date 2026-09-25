# Date and year validation — bug fix (testing miss)

**Status:** Done (shared helpers in `src/accessibility/masked_date_fields.py`; calendars in `FullDayNumberCalendar`).  
**Kind:** Bug fix missed in Phase 18 / 20 testing — not a new v3 phase. Year range, no-future dates, clear/blank classic dates, and screen-reader typed fields were incomplete or inconsistent across windows.  
**Applies to:** Book Details (Year + Read), main-window read-date popup, Reading History From/To, Added-since filter (max today), Import Detail Year.  
**UI:** Screen reader → typed fields. No screen reader → spin/calendar. Same validation either way.

**Standards docs:** Keep the rules here and in the phase plans for now. **Do not** copy into AGENTS.md / accessibility standards yet — promote after a broader UI/date-control review (Phase 16 help review or a dedicated pass).

**Revisit later:** Screen-reader typed dates/years are a workaround for `QDateEdit` / `QSpinBox` section highlight and key stealing. Prefer a better accessible Qt date/year control (or a custom calendar that works cleanly with JAWS/NVDA). Do not reintroduce Alt+Up/Down hacks on `QDateEdit`.

---

## Why typed fields for screen readers

On a normal `QDateEdit`, **Tab usually moves inside the control** from year → month → day (section highlight), instead of leaving the field for the next control. Confirmed with JAWS; re-check with NVDA when revisiting. That section focus, plus Alt keys opening the calendar, made Alt+Up/Down and confirm-on-leave unreliable. Typed `yyyy-MM-dd` / `yyyy` fields keep Tab as “leave the field.”

---

## Workaround implemented (screen reader)

| Problem | Workaround |
|---------|------------|
| `QDateEdit`: Tab cycles year → month → day; sections highlight; Alt keys fight the calendar | When `is_screen_reader_active()`, use plain typed fields (`MaskedDateEdit` / `MaskedYearEdit`) with placeholders `yyyy-MM-dd` / `yyyy` |
| `QSpinBox` year also highlights / steps awkwardly under screen readers | Same typed year field |
| Status-only errors often not heard | Invalid values use a warning dialog that includes the typed text |
| Classic `QDateEdit` blank | Qt ignores empty `specialValueText` and would show `1752-09-14`. Use a non-empty blank text (space) at minimumDate; **Clear** button in Book Details (view and edit) and main read-date popup. |

---

**Calendar note:** Qt puts weekday names in grid row 0 (QHeaderView is only 1..7 — keep it hidden). `FullDayNumberCalendar` uses `NoVerticalHeader`, **`SingleLetterDayNames`** (S M T W T F S), Fixed column widths, and a font that **follows UIScaler** (app font / base 9pt × scale) so high zoom stays proportional. Shared by main read-date, Book Details, and Reading History.

---

## Rules (do not diverge by window)

1. **Publication year:** Preferences year consistency (default **1801** through **current year**), or blank. Import Detail without a screen reader keeps spin **up/down arrows**.
2. **Read date / history dates:** Valid calendar day as `yyyy-MM-dd`. Blank only where allowed (read date yes; history From/To no).
3. **Never in the future:** Read date and history dates must be **today or earlier**. Classic calendars also clamp max to today.
4. **Invalid:** beep + warning that includes the typed value. Screen-reader typed text is not cleared so it can be fixed.
5. **Clear read date:** Yes/No confirmation when a date was already set. Sighted path uses the **Clear** button (then leave field / Enter as usual).

---

## Call sites

| Place | Year | Date |
|--------|------|------|
| Book Details | Preferences range on leave + Save | No future; validate on leave + Save; Clear button when no screen reader |
| Main read-date popup | — | No future; validate before OK/Enter; Clear button when no screen reader |
| Reading History From/To | — | No future; start ≤ end; validate on leave + Search |
| Added since | — | Calendar max = today |
| Import Detail Year | Preferences range; spin arrows when no screen reader | — |

Use `validate_year_spin`, `validate_date_edit(..., disallow_future=True)`, and `configure_no_future_date_edit` — do not add one-off checks per window.

---

## Earlier QDateEdit Alt-key work (parked / do not revive)

Alt+Up/Down on `QDateEdit` opened the calendar, highlighted sections, and fought confirm dialogs. Tab also stayed inside year/month/day rather than moving to the next field (JAWS; verify again with NVDA). That path is abandoned in favor of typed fields for screen readers. Revisit only with a better control, not more Alt-key filters.
