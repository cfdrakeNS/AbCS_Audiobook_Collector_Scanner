# AbCS 2.19 — changes since 2.14

Brief tester notes. Grouped by type.

## Enhancements

- Background web fetch and batch metadata fetch (with clearer Google Books pause messaging)
- Leading-article title compare and selection-mode toolbar / shortcut blocking
- Keep the focused book when sorting or filtering
- Import tag mapping for title and author
- Optional check for updates on startup
- Series number stored and shown on the main list and Book Details; Series sort uses series number then year
- Date Read and Added since calendars show days 10–31
- Collection library root folder
- In-app Play window (preview), then full player: next/previous file, seek, rewind/fast-forward, speed, resume, Escape keeps position
- Embedded cover art on Play and Book Details when the picture is inside the audio file
- Name-list merge when renaming onto an existing author, series, or genre
- Want to read mark, filter, and Edit / selection actions; listening progress on Book Details and Play
- Book Details layout with cover on the right; Import Detail matching layout with Keep and Discard
- In progress filter; Clear listening; Statistics counts for Want to Read and In Progress
- Play on the main toolbar; name-list Copy; menus can arrow over disabled items

## Bugs

- Date and year validation after Book Details / Want to read work
- Book Details no longer writes a series number parsed from the title just by opening the book
- Focus returns to the first selected book after Update closes
- Collection dialog tab order
- Main list clears correctly after a batch web fetch
- Name-list Tab and Ctrl find focus stay on the list during Find
- Preview / Play remapped to the collection library root and import folder path
