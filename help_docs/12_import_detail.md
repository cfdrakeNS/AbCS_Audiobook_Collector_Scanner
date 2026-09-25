# Import Detail Process

## What this is

The **Import Detail** window lets you review and fix one held import item at a time. Books land here when import finds duplicates, validation issues, fallback guesses, text auto-corrects (**C:** flags), or other problems that need your attention. The fields use the same two-column arrangement as Book Details. There is no cover. Collection, Time, Source, and Path are read only.

## When to use it

- A row in the Import review table needs editing before you add it.
- You want to step through held items with Previous and Next.
- You need to save corrections, skip an item, or discard it.

## Before you start

- Run a folder import and open Import when books are held for review.
- In the Import review table, select a row and press **Enter**, or double-click the row, to open detail.

## Steps

1. In the Import window review table, click a held book row (or select it with the keyboard).
2. Press **Enter**, or double-click the row, to open **Import Detail**.
3. Review validation errors and edit fields as needed.
4. Click **Save** (**Alt+S**) to keep your changes and stay in detail.
5. Click **Keep** (**Alt+K**) to accept fallback or correction warnings, add this book to the library (same rules as **Add Selected**), and move to the next review item without closing detail.
6. Click **Discard** (**Alt+D**) to drop this item without adding it.
7. Click **Previous** and **Next** if shown, or use **Page Up** and **Page Down**, to move between held items.
8. Press **Escape** to close detail and return to Import.

**Duplicates and unreadable files:** Import Detail opens for **duplicates** so you can edit and **Save** if you choose. **Keep** and **Add Selected** still will not add a duplicate. Unreadable-file problems that cannot be fixed by editing still block opening detail, with a message.

## What happens next

- Saved changes update the row in the Import review table.
- **Keep** adds that one book to your library, removes it from the review list, and advances to the next editable item in detail.
- Use **Add Selected** (Alt+S) in Import to add several approved rows at once without opening detail.
- Discarded items are removed from the review list.

## Related help

- Full folder import workflow: see [Import (Folder Scan)](02_import.md).
- Import settings and scenarios: see [Import Preferences](18_import_preferences.md).

## Mouse, shortcuts, and accessibility

- Click fields to edit them; click **Save** or **Discard** when finished.
- Use **Previous** / **Next** buttons to step through held items without returning to the review table.

| Shortcut | Action |
|----------|--------|
| Alt+T | Title |
| Alt+A | Author |
| Alt+P | Plot |
| Alt+Y | Year |
| Alt+M | Time |
| Alt+R | Reader |
| Alt+I | Series |
| Alt+G | Genre |
| Alt+C | Collection |
| Alt+E | Errors |
| Alt+H | Path |
| Alt+S | Save |
| Alt+K | Keep |
| Alt+D | Discard |
| Page Up | Previous item |
| Page Down | Next item |
| Shift+F1 | Help for this window |
| F1 | Keyboard shortcuts |
| Alt+/ | Re-read status |
| Escape | Close detail |

## Common confusion

**Save vs Keep vs Add Selected — what is the difference?**
**Save** stores edits for this held item and leaves it in the review list. **Keep** (Alt+K) accepts fallback or correction warnings, adds **this** book to the library, and moves to the next item in detail. **Add Selected** on the Import window adds every selected OK or Warning row at once.

**Discard vs skipping in Import**
**Discard** in detail removes the current held item. You can also leave items in the review list and close Import; you will be asked to confirm if unscanned items remain.

**Author Blank after I typed a name**
**Save** (Alt+S) after editing author. Validation is refreshed on save, so **Author Blank** clears when the author field has text. A name you type that is not yet in the name list is kept when you save.

**Why won’t Keep work on a Duplicate row?**
Duplicates already match a book in the library. You can still open detail, edit, and **Save**. **Keep** and **Add Selected** skip duplicates. **Discard** removes the row from the review list.
