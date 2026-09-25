# Import Detail layout — Version 3 Phase 22

**Status:** Complete (tester). Same column arrangement as Book Details. No cover.  
**Created:** September 2026  
**Related:** [plan_book_details_layout.md](plan_book_details_layout.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

Make Import Detail use the same column arrangement as Book Details. There is no cover image. Want to read and listening progress stay off this window.

---

## Layout

Labels are right-aligned. No empty row. The short fields start at the top of the right column because there is no picture.

```text
          Title [..............................]           Year [......]
         Author [..............................]           Time [......]
         Series [..............................]          Files [......]
          Genre [..............................]         Format [......]
           Plot                                          Bitrate [......]
            [..................................]

         Reader [................................................]
     Collection [................................................]
           Size [................................................]
         Source [................................................]
           Path [................................................]
```

Import Detail keeps the fields it has now. It does not gain Series number, Read, Added, Want to read, or Listen progress. Errors stays as a full-width row under Path.

**Footer:** Status bar (text-field look, above the buttons), then **Save** (dirty only), **Keep** (Alt+K), **Discard** (Alt+D).

## Tab order and shortcuts

Tab order: Title, Author, Series, Genre, Plot, then Year, Time, Files, Format, Bitrate, then Reader, Collection, Size, Source, Path, Errors, then Save / Keep / Discard.

Existing Import Detail Alt+letter shortcuts stay, except Files, Format, Bitrate, and Size (no Alt). **Alt+K** is **Keep**. Do not copy Book Details letters onto this window.

## Keep, Discard, and blocked rows

- **Keep:** Accept OK/Warning rows (including fallback and correction flags), add that book like Add Selected (`quiet` — no Add Complete popup), announce on the status bar, stay open and load the next editable item. Duplicates cannot be Kept (status explains; user may still edit and Save).
- **Discard:** Remove the row, announce on the status bar, stay open on the next editable item (or close when none remain).
- **Unreadable/corrupt file** rows do not open Import Detail (message). Duplicates may open for edit/Save.

## Gate

Passed. Columns line up with Book Details. No cover. Tab and Alt+letter reach the same fields (including Alt+P Plot and Alt+K Keep). No Alt for Files, Format, Bitrate, or Size. Keep/Discard announce via `announce_status_message`.
