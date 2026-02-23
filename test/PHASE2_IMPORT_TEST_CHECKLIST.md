# Phase 2 Import Test Checklist

Date: 2026-02-15  
Scope: Import Window, Preferences import rules, Import Detail, scanner/rules integration  
Goal: Validate all Phase 2 import behavior before wider regression

---

## How to Use This Checklist

- Mark each case as: **Pass / Fail / Blocked**
- If Fail, record: actual result, sample file/folder path, and setting values
- Re-run critical cases at 100%, 125%, and 150% zoom

---

## A. Import Window Core Flow

| ID | Test | Steps | Expected | Status |
|---|---|---|---|---|
| A-01 | Open import window | Open via Ctrl+I and File → Import | Window opens; title includes Formats/Mode/Flip Author summary | |
| A-02 | Collection gating | With multiple collections, leave Collection as None | Scan remains disabled until collection selected | |
| A-03 | Folder browse | Select folder with valid audio files | Folder path appears in header field | |
| A-04 | Scan summary | Run scan on mixed folder | Status summary shows Scanned/Valid/Errors/Duplicates/Elapsed | |
| A-05 | Error filter | Switch All/Valid/Warning/Error/Duplicate filter | Row visibility updates correctly for each filter | |
| A-06 | Add selected | Select only valid rows, click Add Selected | Only selected valid items imported; rows removed from list | |
| A-07 | Add all valid | Click Add All Valid | All valid/warning rows imported; invalid/duplicate rows remain | |
| A-08 | Cancel scan | Start scan, click Cancel, confirm Yes | Scan stops; partial handling/status matches current design | |
| A-09 | Detail open | Double-click row or Ctrl+Enter | Import Detail opens for selected row | |

---

## B. Scenario + Fallback Behavior

Prepare sample folder trees for each mode.

| ID | Test | Setup | Expected | Status |
|---|---|---|---|---|
| B-01 | Mass Standard | Author folders with mixed subfolders/files | Author/title fallback is sensible; no author=title collision when parent can resolve | |
| B-02 | Series from directory | author/series/file | Series inferred from directory; author inferred from parent when needed | |
| B-03 | Series from filename | Series in `(Series Name NN)` pattern | Series parsed from filename where present | |
| B-04 | Single item mode | Single author folder / single file import | Import works with selected file/folder and format filter | |
| B-05 | Author fallback None | Disable author fallback | Missing tag stays blank and triggers appropriate rule result | |
| B-06 | Title fallback File/Folder | Toggle title fallback modes | Missing title resolves according to selected fallback mode | |

---

## C. Duplicate Rules

Use known data with controlled duplicates.

| ID | Test | Duplicate Match setting | Expected | Status |
|---|---|---|---|---|
| C-01 | Title+Author+Collection | `title_author` | Duplicate if same title/author in same collection | |
| C-02 | Title+Author+Year | `title_author_year` | Duplicate depends on year match; collection ignored | |
| C-03 | Title+Author+Year+Collection | `title_author_year_collection` | Duplicate only when all match | |
| C-04 | Legacy alias: ignore_collection | `ignore_collection` | Loads/migrates to `title_author_year` behavior | |
| C-05 | Fuzzy threshold off | 0% | Only exact matching applies | |
| C-06 | Fuzzy threshold on | e.g. 85% | Near-match title/author gets flagged as duplicate | |

---

## D. Tag Quality Rules

| ID | Rule | Preference setup | Expected | Status |
|---|---|---|---|---|
| D-01 | Year range enabled | Set min/max and severity | Out-of-range year yields configured severity message | |
| D-02 | Year invalid format | Non-numeric/invalid year source | Rule reports invalid year format message | |
| D-03 | Missing genre enabled | Severity=Warning/Error | Empty genre yields configured message | |
| D-04 | Minimum bitrate enabled | Set min kbps (e.g., 96) | Low bitrate yields configured message | |
| D-05 | Disabled quality rules | Set severity=None | No related quality warnings/errors produced | |

---

## E. Auto-Correction Rules

Use intentionally messy metadata to verify normalization.

| ID | Rule | Input sample | Expected | Status |
|---|---|---|---|---|
| E-01 | Trim whitespace | `  John   Doe  ` | `John Doe` | |
| E-02 | Strip leading punctuation | `...!John Doe` | `John Doe` | |
| E-03 | Remove special chars | `Jo#hn D@oe` | Special chars removed per rule | |
| E-04 | Proper case | `jOhN dOE` | `John Doe` | |
| E-05 | Move leading The | `The Beatles` | `Beatles, The` | |
| E-06 | Combined rules | Multiple toggles enabled | Output reflects ordered combination without data loss | |

---

## F. Import Detail Window

| ID | Test | Steps | Expected | Status |
|---|---|---|---|---|
| F-01 | Edit metadata | Update title/author/year/etc, Save & Return | Row updates in Import Window and persists for add operation | |
| F-02 | Skip/Discard | Open row, choose Skip/Discard | Row removed from import list; summary recalculates | |
| F-03 | Prev/Next navigation | Use Alt+P/Alt+N and PageUp/PageDown | Navigates items and keeps edits as designed | |
| F-04 | Error display | Open row with multiple errors | Errors display clearly and include duplicate when applicable | |

---

## G. Accessibility + Keyboard (Import)

| ID | Test | Steps | Expected | Status |
|---|---|---|---|---|
| G-01 | Window title announcement | Open Import window with JAWS | Title announces format/mode/flip summary | |
| G-02 | Header keyboard flow | Tab through header controls | Predictable focus order, no traps | |
| G-03 | Status read shortcut | Use Alt+/ during scan and after scan | Current status announced/read correctly | |
| G-04 | List selection keys | Shift+Space, arrows, Shift+arrows | Multi-select behavior and status count work correctly | |

---

## H. Regression Spot Checks

| ID | Test | Expected | Status |
|---|---|---|---|
| H-01 | Main Window unaffected | Normal browse/search/edit still works | |
| H-02 | Book Detail unaffected | Open/save/delete behavior unchanged | |
| H-03 | Preferences save/load | Reopen Preferences; all Phase 2 options persist | |
| H-04 | Import speed sanity | No major slowdown from new rules on typical library | |

---

## Defect Log Template

- Case ID:
- Settings used:
- Test data path:
- Expected:
- Actual:
- Screenshot/log:
- Severity:
- Notes:
