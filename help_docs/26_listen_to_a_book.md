# Listen to a book

## What this is

**Listen** plays an audiobook inside AbCS. It can resume from a saved listening position.

## Quick steps

1. On the main window, move to the book.
2. Press **Ctrl+L**.
3. Press **Space** to play or pause.
4. Press **Escape** to close, and answer **Yes** to save your place.

## Open Listen

1. From the main window, focus a book and choose **Edit → Listen**, press the **Listen** toolbar button, or press **Ctrl+L**. Clear any selection of several books first.
2. In Book Details, press **Listen**. In edit mode the button is hidden; save or press **Escape** first.

## Window layout

- **Book information** at the top: Title and Author, then Series when the book has one, and Length when it is set.
- **Part line**, for a book with more than one file: the current file, such as Part 6 / 12, then that file's title tag. When the title tag is empty, the file name is shown without its extension.
- **Cover picture**, when the audio file has one.
- **Time display** and **Play position** slider for the current file.
- **Transport buttons**, left to right: Previous file, Rewind 30 seconds, Play or pause, Forward 30 seconds, and Next file.
- **Playback speed** list.
- Status bar at the bottom.

## Playback controls

1. Press **Space** to play or pause. After Next, Previous, or Play or pause, focus returns to Play or pause.
2. Press **Alt+Left** or **Alt+Right** to rewind or move forward 30 seconds. After Rewind or Forward, focus stays on that button so you can press it again.
3. Press **Alt+P** or **Alt+N** for the previous or next file.
4. On the time display or the seek slider, Left and Right arrows move five seconds, and Page Up and Page Down move thirty seconds. Home goes to the start of the file, and End to the end. The time is read when you seek.
5. On **Speed** (**Alt+S**), plain Up and Down arrows beep and keep the speed. Press **Alt+Down** or **Space** to open the list, then **Enter** to choose. One speed setting is used for every book.

## Listening position

1. Press **Escape** to close Listen.
2. If you listened for five minutes or more, AbCS asks whether to save your place. **Yes** is the default.
3. If you listened for less than five minutes, Listen closes and keeps the place that was already saved. Time spent paused is not counted.
4. Opening Listen again resumes from the saved place.
5. Reaching the end of the last file clears the saved place.

Book Details **Listen progress** shows the percent of the book completed. To clear a saved place, press **Clear** beside **Listen progress**, or choose **Edit → Clear listening position** on the main window for the selection. Setting a read date also clears the listening position and Want to read.

## When Listen looks for a book

Listen tries the book's stored path first. When the path is blank or gone, it looks in the collection's **collection folder**: first in the author folder, then in the series folder inside it when the book has a series. When the book is found there, its folder is saved as the book's path.

If the stored path is from an old drive letter or a moved folder, and the same folders exist under the collection folder, Listen plays the book and keeps the stored path. For example, a USB drive with a new letter stays portable.

Matching rules for folder and file names:

- A book folder or file may have a number before or after the title, such as `3 - The Moonstone`, `2 Whose Body`, or `The Moonstone - 03`.
- A series tag at the end of the name also works, such as `1 Whose Body(Lord Peter Wimsey 01).m4b` for the book Whose Body?.
- A tag with no number, such as `(Unabridged)`, is ignored in both the book title and the folder or file name.
- When the book has a series number, only the folder with that number is used. When it has none, a folder is used only if it is the only one with that title.
- If the book has no series, Listen also looks one folder down inside the author folder, for example in a series folder.
- If the book has a series but is not in its series folder, Listen also looks one folder down and plays the book. That folder is not saved as the book's path.
- When the author has several names separated by commas, such as `Charles Dickens, Wilkie Collins`, Listen tries a folder with the full name, then a folder for the first author.

## When Listen cannot find a book

1. A message says what was missing and where Listen looked, for example that the author folder or the book title folder was not found.
2. Most messages offer **Browse**. The folder you choose is saved on the book when it has playable audio.
3. Press **Escape** to close the message and keep the book as it was.
4. If the message says the collection folder is missing or not set, open **Manage → Collections**, edit the collection, and set the **Collection folder**.

A stored path that no longer exists, with nothing found in the collection folder, reports **Book not found in -** and the missing path.

For the full list of folders checked and messages, see [Import Book List explained](20_import_book_list_explained.md).

## Mouse, shortcuts, and accessibility

- Click the transport buttons to play, pause, rewind, or move forward.
- Drag the seek slider to move within the current file.

| Shortcut | Action |
|----------|--------|
| Ctrl+L | Open Listen (main window) |
| Space | Play or pause |
| Alt+Left | Rewind 30 seconds |
| Alt+Right | Forward 30 seconds |
| Alt+P | Previous file |
| Alt+N | Next file |
| Alt+S | Playback speed |
| Alt+Down or Space on Speed | Open the speed list |
| Left/Right on transport buttons | Move between transport buttons |
| Left/Right on time or slider | Seek five seconds |
| Page Up/Down on time or slider | Seek thirty seconds |
| Home/End on time or slider | Start or end of the current file |
| Escape | Close |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Related help

- Editing book information or browsing to a missing path: [Book Details](04_book_details.md)
- Finding the book first: [Find and Filters (Main Window)](03_find_filters.md)
- Fixing many paths: [Check Book Locations](24_check_book_locations.md)
