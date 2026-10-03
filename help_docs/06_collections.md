# Collections Process

## What this is

A **collection** is a virtual library inside AbCS: a named group of books that usually matches one real audiobook store on disk. Examples include a **portable hard drive**, a NAS share, CDs you rip to a folder, or a **Wish List** that has no folder yet.

Each collection can point at an optional **collection folder** (the top folder where that library lives). AbCS does not move files when you change the folder; it only uses the path to import, Listen, and Check Book Locations.

AbCS has two collection-related workflows:

1. **Manage collections** — create, rename, activate, set the collection folder, or delete collections.
2. **Filter by collection** — show only books from one virtual library in the main list (does not change your data).

Every book belongs to exactly one collection. A default collection named **Audio Books** is created when the database is first set up, so you can import right away.

## When to use it

- You keep audiobooks on more than one drive or share — add a collection per location.
- You want separate lists (for example owned vs wish list) without mixing them in the main table.
- You need to rename the default collection or narrow the main book list to one group while browsing.

## Before you start

- At least one collection must always remain **active**. You cannot deactivate or delete the last active collection.
- A collection in use by books cannot be deleted until those books are moved or removed.
- Each collection may have an optional **collection folder** on disk. Changing that folder does not move files or rewrite stored book paths.
- If you have only one collection, AbCS keeps that collection folder and the Preferences **default import directory** in step. When one is empty, the other fills it. Two or more collections are left as you set them.

## Manage collections

1. Open **Manage → Collections** (**Alt+M**, then **C**).
2. At the top, **Name** and **Collection folder** sit in a block for editing above the table. The **collection list** has three columns: **Collection**, **Path**, and **Status**.
3. To **add** a collection:
   - Click **New** (Ctrl+N).
   - Type a name in the **Name** field (Alt+E to edit).
   - Optionally set a **Collection folder**. Type a path or click **Browse** (Alt+B).
   - Check or uncheck **Active** (Alt+A in some contexts — see F1 help).
   - Click **Save** (Ctrl+S).
4. To **edit** a collection:
   - Select a row by clicking it in the list (or press **Alt+L** to focus the list with the keyboard).
   - Click **Edit** (Alt+E), double-click a row, or press Enter on a row.
   - Change the name, collection folder, or active status.
   - Click **Save** (Ctrl+S). If you press **Escape** with unsaved changes, AbCS asks whether to save them: **Yes** saves, **No** discards. Escape with no changes just leaves edit mode.
5. To **delete** a collection:
   - Select an unused collection.
   - Click **Delete** (Alt+D).
   - Confirm. Collections that still contain books cannot be deleted.
6. Press **Escape** to close the Collection Manager.

## Filter by collection (main window)

1. Open **View → Collections** (**Alt+V**, then **C**) on the main window menu.
2. Choose a collection name, or **All Collections** to show everything.
3. The book list updates to show only books in that collection.
4. The filter summary in the status area shows which collection is active (for example, "Collection: Portable Drive").

Import windows use this filter: if the main window shows a specific collection, Import and Import Book List pre-select that collection.

## What happens next

- New or edited collections appear in the Manage list and in the View → Collections menu.
- Inactive collections do not appear in import collection dropdowns but remain in the database.
- Filtering does not move or delete books — it only changes what you see.
- **File → Import** always starts with the Preferences **default import directory**. Choosing a collection in Import does not change the scan folder.
- **Listen** looks in the collection folder for books with no path, such as books from Import Book List. If the folder is wrong, missing, or not set, Listen says so and points you here. Changing the folder does not rewrite book paths.

## Settings that affect this

None specific to collections beyond having at least one active collection at all times.

## Mouse, shortcuts, and accessibility

- Click **New**, **Edit**, **Browse**, **Save**, and **Delete** in the Collection Manager.
- On the main window, use **View → Collections** to filter by collection.

### Collection Manager

| Shortcut | Action |
|----------|--------|
| Alt+M, C | Open Collection Manager (Manage menu) |
| Alt+L | Focus collection list |
| Tab | Name, Active, Collection folder, Browse, list, then buttons |
| Ctrl+N | New collection |
| Alt+E | Edit selected row |
| Enter / double-click | Edit selected row |
| Alt+M | Name field (while editing) |
| Alt+A | Active checkbox (while editing) |
| Alt+F | Collection folder field (while editing) |
| Alt+B | Browse collection folder (while editing; otherwise says to press Alt+E or Ctrl+N first) |
| Ctrl+S | Save |
| Alt+D | Delete |
| F1 | Show keyboard shortcuts |
| Shift+F1 | Open this help document |
| Alt+/ | Re-read status |
| Escape | Leave New or Edit (asks to save changes), or close |

### Main window filter

| Shortcut | Action |
|----------|--------|
| Alt+V, C | View → Collections filter |

## Common confusion

**Filter vs Manage — what is the difference?**
Filtering (View menu) only changes what you see. Managing (Manage menu) creates or changes collections themselves.

**Why can't I import without a collection?**
Every book must belong to a collection. AbCS creates a default **Audio Books** collection when the database is first set up, so import is available immediately. Use Manage → Collections only if you want to rename it or add more collections.

**What happens to books in an inactive collection?**
Books remain in the database. The collection is just hidden from import dropdowns until you activate it again.

**What if the collection folder is missing or empty?**
Save and Browse warn if the folder does not exist, or if it has no recognized audiobook files. You can keep the path anyway (for example if the drive is not mounted yet). Import does not pre-fill a missing folder; it uses the Preferences default import directory instead.

**Is a collection the same as the folder on disk?**
No. The collection is the virtual library in AbCS (name, active flag, and book membership). The **collection folder** is optional storage on disk that import and Listen use for that library.
