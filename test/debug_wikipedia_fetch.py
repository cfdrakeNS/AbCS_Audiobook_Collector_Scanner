"""Debug script to test Wikipedia plot fetching for John Connolly books."""

import sys

sys.path.insert(0, "c:/Users/cfran/PythonProjects/abcs/src")

from web.web_book_api import WebBookAPI

api = WebBookAPI()

test_books = [
    ("The Book of Lost Things", "John Connolly"),
    ("A Time of Torment", "John Connolly"),
    ("The Gates", "John Connolly"),
    ("Every Dead Thing", "John Connolly"),
]

for title, author in test_books:
    print(f"\n=== Testing: {title} by {author} ===")
    plot = api._fetch_plot_from_wikipedia(title, author)
    if plot:
        preview = plot[:150].replace("\n", " ")
        if len(plot) > 150:
            preview = preview + "..."
        # Safe print for Windows
        try:
            print(f"  [FOUND] {preview}")
        except UnicodeEncodeError:
            print(f"  [FOUND] (plot found but contains special characters)")
    else:
        print(f"  [NOT FOUND]")

print("\n=== Done ===")
