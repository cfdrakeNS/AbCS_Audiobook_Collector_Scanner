# Listen to a book

## What this is

**Listen** plays an audiobook inside AbCS. It can resume from a saved listening position.

## Open Listen

1. In Book Details, click **Listen**. The button is hidden while Book Details is in edit mode; save or press Escape first.
2. From the main window, focus a book and choose **Edit → Listen**, click the **Listen** toolbar button, or press **Ctrl+L**. Listen is unavailable while one or more books are selected for bulk actions.

## Player information

The Listen window shows the book's Title and Author. Length appears when it is set, and Series appears when the book has a series. The current file name and embedded cover art appear when available.

For a folder of tracks, files play in disc and track number order.

## When Listen cannot find a book

Listen tries the book's stored path first. If the path is blank or gone, it looks in the collection's **Library root folder**, using the folders your Preferences **Import scenario** expects. When the book is found there, its folder is saved as the book's path.

If the book is still not found, a message says what was missing and where Listen looked. For example, the author folder or the book title folder was not found. Most messages offer **Browse**. The folder you choose is saved on the book only if it has playable audio. Press **Escape** to close without changing the book.

If the message says the collection folder is missing, has no audiobook files, or is not set, open **Manage → Collections**. Edit the collection and update **Library root folder**.

A stored path that no longer exists, with nothing found in the Library root folder, reports **Book not found in -** and the missing path.

For the full list of folders checked and messages, see [Import Book List explained](20_import_book_list_explained.md).

## Playback controls

Press **Space** to play or pause. After Next, Previous, Rewind, Forward, or Play/Pause, focus returns to Play/Pause.

Press **Alt+Left** or **Alt+Right** to rewind or move forward 30 seconds. The seek slider moves through the current file. Its arrow keys move five seconds; Page Up and Page Down move thirty seconds.

Press **Alt+P** or **Alt+N** to move to the previous or next file. Playback speed is one setting for every book.

## Listening position

Press **Escape** to close Listen. If you listened for less than five minutes, AbCS asks whether to save the place. Reaching the end of the last file clears the saved position. Opening Listen again resumes from the saved place.

Book Details **Listen progress** shows the stop time and, when Time is set, the percent of the book completed. To clear a saved place before finishing the book, use **Clear** beside **Listen progress**, or choose **Edit → Clear listening position** on the main window for the selection. Setting a read date also clears listening position and Want to read.

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
| Left/Right on seek slider | Seek five seconds in the current file |
| Page Up/Down on seek slider | Seek thirty seconds in the current file |
| Escape | Close Listen |
| Alt+/ | Re-read status |
| F1 | Show keyboard shortcuts |
| Shift+F1 | Open Listen help |
