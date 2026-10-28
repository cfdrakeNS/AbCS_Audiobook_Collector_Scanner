# Update

## What this is

The **Update** window changes the **Series**, **Genre**, or **Collection** of the books you selected in the main table. Each choice is applied to every selected book as soon as you make it. Choose **None** in Series or Genre to clear that field on every selected book.

For editing one book with all its fields, use [Book Details](04_book_details.md) instead.

## When to use it

- You need to set the same **Series** or **Genre** on several books at once.
- You want to clear the series or genre from several books.
- You want to move books to a different **Collection**.

## Before you start

- Select one or more books in the main table. Use **Shift+Down Arrow** or **Shift+Up Arrow** with the keyboard. With the mouse, click a row, **Ctrl+click** to add rows, and **Shift+click** for a range.
- Update is turned off during duplicate mode.

## Window layout

- **Header row:** **Series** combo, **Genre** combo, and **Collection** combo. Collection appears only when you have two or more collections. Series and Genre are editable, so you can type a new name.
- **Selected books list:** columns Title, Year, Series, Genre, and Collection. It shows the current values of the selected books and refreshes after each change.
- **Status bar** at the bottom. It reports each change, for example "Series: Sherlock Holmes added to 2 books".

The window has no Save button. Each choice is saved as soon as you make it.

Tab order: Series, Genre, Collection (when shown), then the selected books list.

## Update selected books

1. In the main window, select one or more books.
2. Open **Edit → Update**, press **Alt+U**, or press the **Update** button in the main window footer.
3. The **Update** window opens with focus on **Series**.
4. To set a series, press **Alt+Down** to open the **Series** list (**Alt+S**), choose a name, and press **Enter**. Or type a new series name and press **Enter**. AbCS asks before it adds a new name.
5. To set a genre, do the same in **Genre** (**Alt+G**).
6. To move the books to another collection, choose it in **Collection** (**Alt+C**).
7. To clear the series or genre on all selected books, choose **None** in that list.
8. After each choice, the status bar reports the change, the list refreshes, and the combo goes back to blank.
9. Press **Escape** to close. If you made a change, the main list refreshes, the selection clears, and focus returns to the first selected book.

## What happens next

- Changes appear in the main book list when Update closes.
- If filters would hide the updated books, AbCS clears filters so the books stay in view.
- If you closed Update without making a change, the selection stays.

## Mouse, shortcuts, and accessibility

- Choose **Edit → Update** after selecting books, or click **Update** in the main window footer.
- In the Update window, pick a value from the Series, Genre, or Collection list with the mouse. It is applied right away.

| Shortcut | Action |
|----------|--------|
| Alt+U | Open Update (main window) |
| Alt+S | Series |
| Alt+G | Genre |
| Alt+C | Collection |
| Alt+Down | Open combo dropdown |
| Alt+L | Book list |
| Escape | Close window |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

Plain Up and Down arrows in the combos do nothing. Press **Alt+Down** to open the list, then use the arrow keys and **Enter**.

## Common confusion

**Update or Book Details — which should I use?**
Use **Book Details** to work on one book with all fields. Use **Update** to set or clear the **Series**, **Genre**, or **Collection** on several selected books at once.

**Where is the Save button?**
Update has none. Each choice is saved as soon as you make it, and the status bar confirms it.

**Why did my selection clear after Update?**
After a change, Update clears the selection so you can continue browsing. Focus returns to the first book you had selected.

**How do I clear the series or genre on selected books?**
Choose **None** in the **Series** or **Genre** list. **None** removes the series or genre from each selected book. Collection has no None choice because every book belongs to a collection.

## Related help

- One book at a time: [Book Details](04_book_details.md)
- Selecting books on the main window: [Find and Filters (Main Window)](03_find_filters.md)
- Renaming a series or genre everywhere: [Name List](15_name_list.md)
