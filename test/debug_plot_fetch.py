"""Debug script to test Open Library plot fetching for John Connolly books."""
import sys
sys.path.insert(0, 'c:/Users/cfran/PythonProjects/abcs/src')

import json
import urllib.request
import urllib.parse

# Test with a John Connolly book
test_books = [
    ("The Book of Lost Things", "John Connolly"),
    ("A Time of Torment", "John Connolly"),
    ("The Gates", "John Connolly"),
]

open_library_url = "https://openlibrary.org/search.json"
open_library_work_url = "https://openlibrary.org/works"

def test_search(title, author):
    print(f"\n=== Testing: {title} by {author} ===")

    query = f"{title} author:{author}"
    params = {
        "q": query,
        "limit": 3,
        "fields": "key,title,author_name,first_publish_year",
    }

    url = f"{open_library_url}?{urllib.parse.urlencode(params)}"
    print(f"Search URL: {url}")

    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "AbCS-Test/1.0")

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data.get("docs"):
            print("  No results found")
            return

        print(f"  Found {len(data['docs'])} result(s)")

        for i, doc in enumerate(data['docs'][:2]):
            work_key = doc.get("key", "")
            print(f"\n  Result {i+1}:")
            print(f"    Title: {doc.get('title', 'N/A')}")
            print(f"    Work key: {work_key}")

            if work_key:
                # Try to fetch description
                work_id = work_key.split("/")[-1] if "/" in work_key else work_key
                work_url = f"{open_library_work_url}/{work_id}.json"
                print(f"    Work URL: {work_url}")

                try:
                    work_req = urllib.request.Request(work_url)
                    with urllib.request.urlopen(work_req, timeout=6) as work_response:
                        work_data = json.loads(work_response.read().decode("utf-8"))

                    desc = work_data.get("description", "")
                    if isinstance(desc, dict):
                        desc = desc.get("value", "")

                    if desc:
                        preview = desc[:100].replace('\n', ' ') + "..." if len(desc) > 100 else desc
                        print(f"    Description: {preview}")
                    else:
                        print(f"    Description: [NONE FOUND]")
                        print(f"    Available fields: {list(work_data.keys())}")
                except Exception as e:
                    print(f"    Error fetching work: {e}")

    except Exception as e:
        print(f"  Error: {e}")

# Run tests
for title, author in test_books:
    test_search(title, author)

print("\n=== Debug complete ===")
