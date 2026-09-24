# Collections Process

## What this is

Collections let you organize books into separate groups — for example, "Audible", "Library CDs", or "Wish List". AbCS has two collection-related workflows:

1. **Manage collections** — create, rename, activate, or delete collections.
2. **Filter by collection** — show only books from one collection in the main list (does not change your data).

Every book belongs to one collection. A default collection named **Audio Books** is created when the database is first set up, so you can import right away.

## When to use it

- Renaming the default collection or adding collections to organize your library.
- Organizing books into logical groups.
- Narrowing the main book list to one collection while browsing.

## Before you start

- At least one collection must always remain **active**. You cannot deactivate or delete the last active collection.
- A collection in use by books cannot be deleted until those books are moved or removed.
- Each collection may have an optional **library root folder** on disk. Changing that folder does not move files or change stored book paths.
- If you have only one collection, AbCS keeps that library root and the Preferences **default import directory** in step. When one is empty, the other fills it. Two or more collections are left as you set them.

## Steps — Manage collections

1. Open **Manage → Collections** (**Alt+M**, then **C**).
2. The **collection list** has three columns: **Collection**, **Path**, and **Status**. Collection and Status size to their contents. Path uses the remaining width. Status is Active or Inactive.
3. To **add** a collection:
   - Click **New** (Alt+N).
   - Type a name in the **Name** field (Alt+E to edit).
   - Optionally set a **Library root folder**. Type a path or click **Browse** (Alt+B).
   - Check or uncheck **Active** (Alt+A in some contexts — see F1 help).
   - Click **Save** (Alt+S).
4. To **edit** a collection:
   - Select a row by clicking it in the list (or press **Alt+L** to focus the list with the keyboard).
   - Click **Edit** (Alt+E) or press Enter on a row.
   - Change the name, library root folder, or active status.
   - Click **Save** (Alt+S).
5. To **delete** a collection:
   - Select an unused collection.
   - Click **Delete** (Alt+D).
   - Confirm. Collections that still contain books cannot be deleted.
6. Press **Escape** to close the Collection Manager.

## Steps — Filter by collection (main window)

1. Open **View → Collections** (**Alt+V**, then **C**) on the main window menu.
2. Choose a collection name, or **All Collections** to show everything.
3. The book list updates to show only books in that collection.
4. The filter summary in the status area shows which collection is active (for example, "Collection: Audible").

Import windows use this filter: if the main window shows a specific collection, Import and Import Book List pre-select that collection.

## What happens next

- New or edited collections appear in the Manage list and in the View → Collections menu.
- Inactive collections do not appear in import collection dropdowns but remain in the database.
- Filtering does not move or delete books — it only changes what you see.
- If a library root folder is set and that folder exists, **File → Import** pre-fills the scan folder from it. You can still browse a different folder. Changing the root does not rewrite book paths.

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
| Alt+N | New collection |
| Alt+E | Edit / name field |
| Alt+B | Browse library root folder |
| Alt+S | Save |
| Alt+D | Delete |
| F1 | Help |
| Alt+/ | Re-read status |
| Escape | Cancel edit or close |

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

**What if the library root folder is missing or empty?**
Save and Browse warn if the folder does not exist, or if it has no recognized audiobook files. You can keep the path anyway (for example if the drive is not mounted yet). Import does not pre-fill a missing root; it uses the Preferences default import directory instead.
