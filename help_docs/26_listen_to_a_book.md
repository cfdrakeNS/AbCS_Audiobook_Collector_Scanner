# Listen to a book

## What this is

**Listen** plays an audiobook inside AbCS. It can resume from a saved listening position.

## Open Listen

1. In Book Details, click **Listen**. The button is hidden while Book Details is in edit mode; save or press Escape first.
2. From the main window, focus a book and choose **Edit → Listen**, click the **Listen** toolbar button, or press **Ctrl+L**. Listen is unavailable while one or more books are selected for bulk actions.

## Player information

The Listen window shows the book's Title and Author. Length appears when it is set, and Series appears when the book has a series. Embedded cover art appear when available.


## Playback controls

Press **Space** to play or pause. After Next, Previous, or Play/Pause, focus returns to Play/Pause. After Rewind or Forward, focus stays on that button so you can press it again.

Press **Alt+Left** or **Alt+Right** to rewind or move forward 30 seconds.

The time display and the seek slider both move through the current file. On either one, Left and Right arrows move five seconds, Page Up and Page Down move thirty seconds, Home goes to the start of the file, and End goes to the end. Time is read when you seek, not while the book plays.

Press **Alt+P** or **Alt+N** to move to the previous or next file. Playback speed is one setting for every book. On Speed (**Alt+S**), plain Up and Down arrows do nothing (a beep); press **Alt+Down** or **Space** to open the list, then Enter to choose.

## Listening position

Press **Escape** to close Listen. If you listened for five minutes or more, AbCS asks whether to save the place (**Yes** is the default). If you listened for less than five minutes, AbCS does not ask and the saved place is not changed. Time spent paused does not count. The place is never saved without asking. Reaching the end of the last file clears the saved position. Opening Listen again resumes from the saved place.

Book Details **Listen progress** shows the percent of the book completed. It does not show the stop time. To clear a saved place before finishing the book, use **Clear** beside **Listen progress**, or choose **Edit → Clear listening position** on the main window for the selection. Setting a read date also clears listening position and Want to read.

## When Listen cannot find a book

Listen tries the book's stored path first. If the path is blank or gone, it looks in the collection's **collection folder**, using the folders your Preferences **Import scenario** expects. When the book is found there, its folder is saved as the book's path.

Book folders may have a number before or after the title, such as `3 - All That Remains`, `4 Bad Blood`, or `All That Remains - 03`. When the book has a series number, only the folder with that number is used. When it has none, the folder is used only if it is the only one with that title. If the book has no series, Listen also looks one folder down inside the author folder, for example in a series folder.

If the book is still not found, a message says what was missing and where Listen looked. For example, the author folder or the book title folder was not found. Most messages offer **Browse**. The folder you choose is saved on the book only if it has playable audio. Press **Escape** to close without changing the book.

If the message says the collection folder is missing, has no audiobook files, or is not set, open **Manage → Collections**. Edit the collection and set the **Collection folder**.

A stored path that no longer exists, with nothing found in the collection folder, reports **Book not found in -** and the missing path.

For the full list of folders checked and messages, see [Import Book List explained](20_import_book_list_explained.md). 

## Related help

- To edit book information or browse to a missing audio path, see [Book Details](04_book_details.md).
- To find and filter the focused book before listening, see [Find and Filters](03_find_filters.md).

## Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+L | Open Listen from the main window |
| Space | Play or pause |
| Alt+Left | Rewind 30 seconds |
| Alt+Right | Forward 30 seconds |
| Alt+P | Previous file |
| Alt+N | Next file |
| Alt+S | Playback speed |
| Alt+Down or Space on Speed | Open the speed list |
| Left/Right on transport buttons | Move between transport buttons |
| Left/Right on time or seek slider | Seek five seconds in the current file |
| Page Up/Down on time or seek slider | Seek thirty seconds in the current file |
| Home/End on time or seek slider | Start or end of the current file |
| Escape | Close Listen |
| Alt+/ | Re-read status |
| F1 | Show keyboard shortcuts |
| Shift+F1 | Open Listen help |
