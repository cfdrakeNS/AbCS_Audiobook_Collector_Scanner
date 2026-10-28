# Import Detail

## What this is

The **Import Detail** window lets you review and fix one held import book at a time. Books are held when import finds a duplicate, a validation issue, a fallback guess, a text auto-correct (**C:** flag), or another problem that needs your attention.

## When to use it

- A row in the Import review table needs editing before you add it.
- You want to step through the held books with Page Up and Page Down.
- You want to save corrections, keep a book, or discard it.

## Before you start

- Run a folder import. Held books appear in the Import review table.
- In the review table, select a row and press **Enter**, or double-click the row, to open detail.

## Window layout

- The fields use the same two-column arrangement as Book Details, without a cover picture.
- On the left: **Title**, **Author**, **Series**, **Genre**, and **Plot**.
- On the right: **Year**, **Time**, **Files**, **Format**, and **Bitrate**.
- Below, one row each: **Narrator**, **Collection**, **Size**, **Source**, **Path**, and **Errors**. Collection, Time, Source, Path, and Errors are read only.
- Status bar above the buttons.
- Buttons: **Save**, **Keep**, and **Discard**. **Save** appears only after you change a field.

Tab order: the fields from Title to Errors, then Save, Keep, and Discard.

## Review one import book

1. In the Import window review table, select a held book row.
2. Press **Enter**, or double-click the row, to open **Import Detail**.
3. Read the **Errors** field (**Alt+E**) and edit fields as needed.
4. Press **Save** (**Ctrl+S**) to keep your changes. The book stays in the review list and detail stays open.
5. Press **Keep** (**Alt+K**) to accept the fallback or correction warnings and add this book, using the same rules as **Add Selected**. Detail moves to the next held book.
6. Press **Discard** (**Alt+D**) to drop this book from the review list.
7. Press **Page Up** or **Page Down** to move to the previous or next held book.
8. Press **Escape** to close detail and return to Import.

**Duplicates:** Import Detail opens for a duplicate so you can edit it and **Save**. **Keep** and **Add Selected** skip duplicates. A book whose files cannot be read shows a message instead of opening detail.

## What happens next

- Saved changes update the row in the Import review table.
- **Keep** adds the book to your library, removes it from the review list, and moves to the next held book.
- **Add Selected** (**Alt+S**) in Import adds several approved rows at once.
- Discarded books are removed from the review list.

## Mouse, shortcuts, and accessibility

- Click a field to edit it; click **Save**, **Keep**, or **Discard** when finished.
- Press **Page Up** and **Page Down** to step through held books.

| Shortcut | Action |
|----------|--------|
| Alt+T | Title |
| Alt+A | Author |
| Alt+P | Plot |
| Alt+Y | Year |
| Alt+M | Time |
| Alt+N | Narrator |
| Alt+I | Series |
| Alt+G | Genre |
| Alt+C | Collection |
| Alt+E | Errors |
| Alt+H | Path |
| Ctrl+S | Save |
| Alt+K | Keep |
| Alt+D | Discard |
| Page Up | Previous item |
| Page Down | Next item |
| Escape | Close detail |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Save, Keep, or Add Selected — what is the difference?**
**Save** stores your edits and leaves the book in the review list. **Keep** adds this one book to the library and moves to the next. **Add Selected** in the Import window adds every selected OK or Warning row at once.

**Discard or leave it in the list?**
**Discard** removes the book from the review list. You can also leave books in the list and close Import; AbCS asks you to confirm.

**Author Blank stays after I typed a name.**
Press **Save** (**Ctrl+S**) after editing the author. Validation runs again on save, and **Author Blank** clears once the author field has text. A new name you type is added to the name list when you save.

**Why won't Keep add a Duplicate row?**
A duplicate matches a book already in the library. You can edit it and press **Save**. To remove it from the review list, press **Discard**.

## Related help

- Folder import: [Import (Folder Scan)](02_import.md)
- Scenarios and rules: [Import preferences](18_import_preferences.md)
