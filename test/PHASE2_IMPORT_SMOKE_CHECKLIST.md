# Phase 2 Import Smoke Checklist

Date: 2026-02-15  
Purpose: Fast validation pass before full checklist  
Target: 20-40 minutes

---

## Run Order

| ID | Area | Steps | Expected | Status |
|---|---|---|---|---|
| S-01 | Open Import | Open via Ctrl+I and File → Import | Import window opens; title announces Formats/Mode/Flip Author summary | |
| S-02 | Collection gating | With multiple collections, leave Collection as None | Scan is disabled until a collection is selected | |
| S-03 | Scan baseline | Pick collection, browse folder, run scan | Summary shows Scanned/Valid/Errors/Duplicates/Elapsed | |
| S-04 | Error filters | Switch All/Valid/Error/Duplicate | Row visibility changes correctly for each filter | |
| S-05 | Add all valid | Click Add All Valid on mixed results | Valid/warning items import; invalid/duplicates remain | |
| S-06 | Import detail edit | Open a row (double-click/Ctrl+Enter), edit title, Save & Return | Row updates in list and imports with edited value | |
| S-07 | Skip/discard | Open another row, choose Skip/Discard | Row removed; summary/counts recalculate | |
| S-08 | Scenario fallback | Use a missing-tag sample for current scenario mode | Author/title/series fallback resolves sensibly from path/file context | |
| S-09 | Duplicate mode | Set duplicate mode to `title_author_year_collection`, rescan duplicate sample | Duplicate rows flagged correctly | |
| S-10 | Tag quality | Enable year-range + missing genre + min bitrate, scan mixed sample | Expected quality warnings/errors appear by configured severity | |
| S-11 | Auto-correction | Enable trim + strip punctuation + proper case + move leading The, rescan | Normalized author/title/fields reflect configured corrections | |
| S-12 | Accessibility quick check | With JAWS: open Import, tab header controls, use Alt+/ | Title/context and status are announced correctly; no focus traps | |

---

## Minimum Data Set Recommendation

- `Sample A`: Clean tagged files (should import cleanly)
- `Sample B`: Missing author/title tags (fallback tests)
- `Sample C`: Known duplicates of existing DB rows (duplicate tests)
- `Sample D`: Low bitrate / no genre / odd year (tag quality tests)
- `Sample E`: Messy text (`...!the beatles`, extra spaces, mixed case) (auto-correction tests)

---

## Fail Capture (Quick Template)

- Smoke ID:
- Settings snapshot:
- Test data path:
- Expected:
- Actual:
- Severity:
- Notes:
