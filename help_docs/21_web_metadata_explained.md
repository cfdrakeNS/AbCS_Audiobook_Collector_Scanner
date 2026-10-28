# Web Metadata Explained

## What this is

This guide describes what AbCS does after you start **Fetch Web Info** (**Alt+W**). For the steps and shortcuts, see [Web Metadata Fetch](07_web_metadata.md).

Fetch Web Info looks up text information about a book online and, when you approve, updates fields inside AbCS. Your audio files stay exactly as they were.

## Which books are looked up

- **Main window, one book:** the book on the focused row.
- **Main window, two or more selected books:** every selected book, one after another, as a batch. **Alt+W**, the **Search Web** toolbar button, and the **Web fetch** footer button all start the batch.
- **Book Details:** the book open in that window.

Fetch Web Info is turned off while duplicate mode is active. When no book is focused, the status bar says "No book available for web info fetch".

## What is sent to the web

The search uses the book's **title and author** as stored in your library.

Before searching, AbCS tidies them up:

- It removes a trailing series number from the title, so `The Hound of the Baskervilles - 3` searches as `The Hound of the Baskervilles`.
- It moves a trailing article to the front, so `Moonstone, The` searches as `The Moonstone`.
- It removes extra punctuation and spacing.
- It removes titles such as Sir or Dr. from the author, so `Sir Arthur Conan Doyle` searches as `Arthur Conan Doyle`.
- It leaves out the year, because stored years are often wrong and would hurt matching.

A **Please wait** dialog opens and announces each source as it is tried.

## Searching the web

AbCS tries online catalogs **in order**, and stops at the first result that passes its matching rules.

On the first fetch: Open Library, then Google Books, then WikiData.

On **Re-fetch** (**Alt+F** in the review window): Google Books, then WikiData.

For each source, AbCS:

1. Announces which source it is trying.
2. Searches with the tidied title and author, and tries a few variations, such as the title alone.
3. Scores the results and picks the best title match.
4. Stops when that result passes the matching rules, or moves on to the next source.

### Saved results

AbCS remembers a successful lookup for about a day, and a failed one for about an hour. A repeat fetch for the same book may use the remembered result. **Re-fetch** always searches again.

### Search limits

Google Books, WikiData, and Wikipedia sometimes limit how many searches AbCS can send. When that happens, AbCS pauses that source, for about 15 minutes for Google Books or 5 minutes for WikiData and Wikipedia. The pause is remembered when you restart AbCS.

The message tells you how long to wait, for example "Try again in about 15 minutes". The other sources keep working in the meantime. In a batch, a book that was missed only because of the pause says **No match found**, and the summary line says "Google Books limit hit. Try in N minutes."

### Google Books API key

Without a key, Google Books allows a limited number of searches. You can add a key under **Manage → Preferences**, **Display Settings** tab, **Web Metadata** group.

## Deciding whether a result matches

A result must pass **title and author checks** before AbCS treats it as your book.

Title:

- At least half of the meaningful words in your title must appear in the web title.
- Common words such as "the", "a", and "of" are ignored.
- A web title much longer than yours scores lower.

Author:

- Your author's **last name** must appear in the web author.
- When both names have several parts, a first name or initial must match too.

When no source passes, AbCS tries broader searches:

1. The title without the author in the search, still checking the author in the results.
2. The title alone, only when your author field is empty, looks like a narrator name, or the book appears to come from Librivox.

When everything fails, a **No Web Data Found** message appears.

## Gathering the plot

Once a match is found, AbCS looks for a plot, in this order:

1. The Open Library description.
2. The Wikipedia summary.
3. The Google Books description.

A plot must be at least **80 characters**. When Open Library and Wikipedia have nothing usable, AbCS keeps any plot that came with the match.

A problem while gathering the plot keeps the match, and you still get the review window with the fields that were found.

Series names and series numbers come from your library only. Edit the series in Book Details or the Update window.

## Comparing with your book

AbCS compares the web values with what is stored for your book:

| Field | How a difference is decided |
|-------|-----------------------------|
| Title | Differences in capital letters, punctuation, accents, "&" and "and", article position, series suffix, and filler words are ignored. A leading A, An, or The that is only on the web side is still offered |
| Author | Differences in punctuation, name order, initials, and accents are ignored |
| Year | Compared as numbers |
| Genre | Compared as text |
| Plot | Compared with your comments field, where the plot is kept |

The **rating** is shown for reference. When you save a plot and the web has a rating, the rating line is added at the top of the plot text. The publisher and the source name are shown only.

### What you see

| Result | What you see |
|--------|--------------|
| Web data with differences | The **Web Metadata** review window |
| Web data that already matches | An "Already up to date" message. In a batch: **Plot and metadata up to date.** |
| A match with no plot on the web or in the library | In a batch: **Match found. No plot was found.** |
| Sources that could not be reached | A message listing the sources that failed |
| No match | A "No information found" message. In a batch: **No match found** |

## The review window

The review window shows **your value** and the **web value** for each field that differs.

| Your field | What happens |
|------------|--------------|
| **Empty** | The web value is applied on Save, without a checkbox |
| **Title, Author, Year** with a value | A checkbox, **unchecked** at first. Check it to use the web value |
| **Genre** with a value | A checkbox, **checked** at first. Uncheck it to keep yours |

When the plot differs, it is shown and applied on Save.

**Re-fetch** (**Alt+F**) searches Google Books, then WikiData, and refreshes the web values in the same window.

**Save** (**Ctrl+S**) applies the checked fields and the filled-in empty fields. **Escape** asks "Save web data?": **Yes** saves, and **No** closes and keeps your book as it was.

## Saving

For each field you approved, or that was empty:

- **Title** and **Year** are updated on the book. A year that is not a number is skipped.
- **Author** and **Genre** are found, or added as new names, and linked to the book.
- **Plot** is written to the book's comments, with the rating line when there is one.

The series stays as it is. After saving:

- The main book list or Book Details refreshes.
- The status bar says which fields changed, for example "Updated: Plot, Year".
- Focus returns to the book you started from.

If saving fails, a message explains it and the review window stays open.

## Batch fetch

With two or more books selected, AbCS fetches each book in turn and shows the **batch summary** at the end. **Apply all** saves the changes for every book. **Review each** opens the review window for each book with changes. See [Web Metadata Fetch](07_web_metadata.md) for the batch steps.

## Why several websites are tried

Different catalogs know different books. Open Library is tried first for well-known titles. Google Books often has descriptions. WikiData helps with less common works. The first source that passes the matching rules provides what you see in the review window.

## Related help

- Steps and shortcuts: [Web Metadata Fetch](07_web_metadata.md)
- Editing a book by hand: [Book Details](04_book_details.md)
- Adding books from audio folders: [Import explained](19_import_explained.md)
- Adding books from a spreadsheet: [Import Book List explained](20_import_book_list_explained.md)
