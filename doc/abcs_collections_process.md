# Collections Process

## What this is

Collections let you organize books into separate groups — for example, "Audible", "Library CDs", or "Wish List". AbCS has two collection-related workflows:

1. **Manage collections** — create, rename, activate, or delete collections.
2. **Filter by collection** — show only books from one collection in the main list (does not change your data).

You need at least one active collection before you can import books.

## When to use it

- Setting up AbCS for the first time — create your collections before importing.
- Organizing books into logical groups.
- Narrowing the main book list to one collection while browsing.

## Before you start

- At least one collection must always remain **active**. You cannot deactivate or delete the last active collection.
- A collection in use by books cannot be deleted until those books are moved or removed.

## Steps — Manage collections

1. Open **Manage → Collections** (**Alt+M**, then **C**).
2. The **collection list** shows all collections and whether each is active (Yes or No).
3. To **add** a collection:
   - Click **New** (Alt+N).
   - Type a name in the **Name** field (Alt+E to edit).
   - Check or uncheck **Active** (Alt+A in some contexts — see F1 help).
   - Click **Save** (Alt+S).
4. To **edit** a collection:
   - Select a row in the list (Alt+L to focus list).
   - Click **Edit** (Alt+E) or press Enter on a row.
   - Change the name or active status.
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

## Settings that affect this

None specific to collections beyond having at least one active collection at all times.

## Shortcuts and accessibility

### Collection Manager

| Shortcut | Action |
|----------|--------|
| Alt+M, C | Open Collection Manager (Manage menu) |
| Alt+L | Focus collection list |
| Alt+N | New collection |
| Alt+E | Edit / name field |
| Alt+S | Save |
| Alt+D | Delete |
| F1 | Help |
| Alt+/ | Re-read status |
| Escape | Cancel edit or close |

### Main window filter

| Shortcut | Action |
|----------|--------|
| Alt+V, C | View → Collections filter |

## Verification

Manual QA for this workflow is complete. See [QA verification](qa_verification.md).

## Common confusion

**Filter vs Manage — what is the difference?**
Filtering (View menu) only changes what you see. Managing (Manage menu) creates or changes collections themselves.

**Why can't I import without a collection?**
Every book belongs to one collection. Create and activate at least one collection first.

**What happens to books in an inactive collection?**
Books remain in the database. The collection is just hidden from import dropdowns until you activate it again.
