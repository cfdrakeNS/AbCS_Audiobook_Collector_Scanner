# Book Details layout — Version 3 Phase 18

**Status:** Tester accepted. Help review is last. The cover is a tab stop (Book cover or No cover). A missing cover uses `graphics/no_book_cover_512x512.png`. Read date and Want to read save without Update. Shortcuts dropped for Files, Format, Bitrate, and Size. Want to read is Alt+K.  
**Picture:** [book_details_layout.png](book_details_layout.png)  
**Created:** September 2026  
**Related:** [plan_book_details_cover.md](plan_book_details_cover.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

Rearrange Book Details. Do not change what the fields do. The picture stays the embedded cover from Phase 17.

---

## Layout

Labels are right-aligned. Fields in a column start on the same vertical line. No empty row and no spacer. The cover box stays the same size for every book. A real cover fills it. Until a custom `cover_placeholder.png` exists, a missing cover shows `graphics/abcs_icon_256x256.png` in that box. The icon is not a tab stop and has no accessible name.

```text
          Title [..............................]  +------------------+
         Author [..............................]  |                  |
         Series [....................] # [....]  |      Cover       |
          Genre [..............................]  |                  |
           Plot                                   +------------------+
            [..................................]           Year [......]
                                                          Time [......]
                                                Listen progress [......]
                                                         Files [......]
                                                        Format [......]
                                                       Bitrate [......]

         Reader [................................................]
     Collection [................................................]
           Read [................................................]
   Want to read [ ]
           Size [................................................]
         Source [................................................]
          Added [................................................]
           Path [................................................]
```

Plot is the tall field on the left. It does not add blank lines when the text is short. The header card that is hidden for a screen reader stays hidden. The cover stays outside that card.

Footer buttons stay where they are: New, Edit, Save, Delete, Web, Preview, Previous, Next.

## Tab order

Set this order in code. Do not rely on widget creation order.

1. Title
2. Author (view label, then combo, as today)
3. Series (view label, then combo)
4. Series number
5. Genre (view label, then combo)
6. Plot
7. Year, Time, Listen progress, Files, Format, Bitrate
8. Reader, Collection (view label, then combo), Read, Want to read, Size, Source, Added, Path
9. Footer buttons in their current order

Cover is not a tab stop. Focus still starts on Title.

## Shortcuts

Keep every existing shortcut. Letters do not move because the fields moved.

From [`BOOK_DETAILS_SHORTCUTS`](../src/accessibility/shortcuts.py): Alt+T Title, Alt+A Author, Alt+I Series, Alt+G Genre, Alt+P Plot, Alt+Y Year, Alt+M Time, Alt+F Files, Alt+O Format, Alt+B Bitrate, Alt+R Reader, Alt+C Collection, Alt+E Read date, Alt+Z Size, Alt+H Path, Alt+W Web. Series number stays Alt+I, then Tab.

Also keep Alt+N New, Alt+U Edit, Alt+S Save, Alt+D Delete, Alt+Shift+P Preview, Alt+/ status, F1, Shift+F1, Page Up, Page Down, and Escape.

## Help and tests

- One sentence in [`help_docs/04_book_details.md`](../help_docs/04_book_details.md): cover on the right, short fields under it, Tab order as above.
- A test walks Tab from Title through Path in the order above, asserts Cover is skipped, and asserts a book with no art still shows the icon in a box of the same size.

## Gate

Labels line up. The cover box stays the same size with or without art. The icon is not announced. Alt+letter still lands on the same field. Tab follows the list above and skips Cover. Title still takes focus when the window opens.
