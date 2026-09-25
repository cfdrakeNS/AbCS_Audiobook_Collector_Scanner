# Import Detail layout — Version 3 Phase 22

**Status:** Planned — after Phase 18 Book Details layout is tested.  
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

Import Detail keeps the fields it has now. It does not gain Series number, Read, Added, Want to read, or Listen progress. Footer actions stay as they are.

## Tab order and shortcuts

Set tab order to match the picture: Title, Author, Series, Genre, Plot, then Year, Time, Files, Format, Bitrate, then Reader, Collection, Size, Source, Path, then the footer buttons.

Keep the existing Import Detail Alt+letter shortcuts. Do not copy Book Details letters onto this window.

## Gate

The columns line up with Book Details. No cover is shown. Tab follows the list above. Each existing Alt+letter still opens the same field.
