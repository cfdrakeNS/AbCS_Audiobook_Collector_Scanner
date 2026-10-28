# Collections

## What this is

A **collection** is a virtual library inside AbCS: a named group of books that usually matches one real audiobook store on disk. Examples include a portable hard drive, a network share, CDs you rip to a folder, or a **Wish List** with no folder yet.

Each collection can have a **collection folder**: the top folder where that library lives. AbCS uses that folder for Import, Listen, and Check Book Locations. Changing it leaves your files and stored book paths as they are.

There are two collection tasks:

1. **Manage collections** — create, rename, activate, set the collection folder, or delete collections.
2. **Filter by collection** — show only books from one collection in the main list.

Every book belongs to exactly one collection. A default collection named **Audiobooks** is created when the database is first set up, so you can import right away.

## When to use it

- You keep audiobooks on more than one drive or share: add a collection per location.
- You want separate lists, for example owned books and a wish list.
- You want to rename the default collection, or show one group of books while browsing.

## Before you start

- At least one collection must stay **active**. The last active collection cannot be deactivated or deleted.
- A collection can be deleted only after its books are moved or removed.
- If you have only one collection, AbCS keeps its collection folder and the Preferences **default import directory** in step. When one is empty, it is filled from the other.

## Window layout

- **Editor at the top:** **Name** field and **Active** checkbox on the first row, **Collection folder** field and **Browse** button on the second row. These are grayed out until you press **New** or **Edit**.
- **Collection list:** columns Collection, Path, and Status.
- **Footer:** status bar on the left, then the buttons.
- Buttons while browsing the list: **New**, **Edit**, and **Delete**.
- Buttons while adding or editing: **Save** only.

Tab order while browsing: the collection list, then the buttons. While editing: Name, Active, Collection folder, Browse, the list, then Save.

## Manage collections

1. Open **Manage → Collections** (**Alt+M**, then **C**).
2. To **add** a collection:
   - Press **New** (**Ctrl+N**).
   - Type a name in **Name** (**Alt+M**).
   - Optionally set a **Collection folder** (**Alt+F**). Type a path or press **Browse** (**Alt+B**).
   - Check or uncheck **Active** (**Alt+A**).
   - Press **Save** (**Ctrl+S**).
3. To **edit** a collection:
   - Select a row in the list (**Alt+L** moves to the list).
   - Press **Edit** (**Alt+E**), press **Enter** on the row, or double-click the row.
   - Change the name, collection folder, or active status.
   - Press **Save** (**Ctrl+S**). If you press **Escape** with unsaved changes, AbCS asks whether to save them: **Yes** saves, **No** discards. With no changes, Escape returns to the list.
4. To **delete** a collection:
   - Select a collection that has no books.
   - Press **Delete** (**Alt+D**) and confirm.
5. Press **Escape** to close the Collection Manager.

## Filter by collection (main window)

1. Open **View → Collections** (**Alt+V**, then **C**) on the main window.
2. Choose a collection name, or **All Collections** to show everything.
3. The book list shows only books in that collection.
4. The filter summary shows the active collection.

Import and Import Book List pre-select the collection shown by this filter.

## What happens next

- New or edited collections appear in the list and in the **View → Collections** menu.
- Inactive collections are left out of the import collection lists. Their books stay in the database.
- **File → Import** always starts with the Preferences **default import directory**, whatever collection you choose.
- **Listen** looks in the collection folder for books with no path, such as books from Import Book List. If the folder is wrong, missing, or not set, Listen says so and points you here.

## Mouse, shortcuts, and accessibility

- Click **New**, **Edit**, **Browse**, **Save**, and **Delete** in the Collection Manager.
- On the main window, use **View → Collections** to filter by collection.

| Shortcut | Action |
|----------|--------|
| Alt+M, C | Open Collection Manager (main window) |
| Alt+L | Jump to list |
| Ctrl+N | New |
| Alt+E | Edit selected row |
| Enter | Edit selected row |
| Alt+M | Name field (while editing) |
| Alt+A | Active checkbox (while editing) |
| Alt+F | Collection folder field (while editing) |
| Alt+B | Browse collection folder (while editing; otherwise it says to press Alt+E or Ctrl+N first) |
| Ctrl+S | Save |
| Alt+D | Delete |
| Escape | Cancel edit or new, or close window |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Filter or Manage — what is the difference?**
Filtering (View menu) changes which books you see. Managing (Manage menu) creates and changes the collections themselves.

**Why do I need a collection to import?**
Every book belongs to a collection. AbCS creates the **Audiobooks** collection when the database is first set up, so you can import right away.

**What happens to books in an inactive collection?**
They stay in the database. The collection is left out of the import lists until you make it active again.

**What if the collection folder is missing or empty?**
Save and Browse warn when the folder is missing or has no audiobook files. You can keep the path anyway, for example when the drive is not connected yet. Import then starts in the Preferences default import directory.

**Is a collection the same as the folder on disk?**
No. The collection is the library inside AbCS: its name, active status, and books. The **collection folder** is where that library's files are stored on disk.

## Related help

- Main window filters: [Find and Filters (Main Window)](03_find_filters.md)
- Fixing book paths: [Check Book Locations](24_check_book_locations.md)
- Playing books with no path: [Listen to a book](26_listen_to_a_book.md)
- Words such as collection folder and path: [Glossary](27_glossary.md)
