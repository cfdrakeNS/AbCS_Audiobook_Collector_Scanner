"""Test direct Wikipedia page access for John Connolly books."""
import sys
sys.path.insert(0, 'c:/Users/cfran/PythonProjects/abcs/src')

import json
import urllib.request
import urllib.parse

wikipedia_url = "https://en.wikipedia.org/w/api.php"

test_pages = [
    "The Book of Lost Things (novel)",
    "The Book of Lost Things",
    "A Time of Torment (novel)",
    "The Gates (novel)",
    "Every Dead Thing (novel)",
]

for page_title in test_pages:
    print(f"\n=== Testing page: {page_title} ===")
    
    try:
        extract_params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": True,
            "exsentences": 10,
            "titles": page_title,
            "format": "json",
            "origin": "*",
        }

        extract_url = f"{wikipedia_url}?{urllib.parse.urlencode(extract_params)}"
        req = urllib.request.Request(extract_url)
        req.add_header("User-Agent", "AbCS-Test/1.0")

        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                print(f"  Page not found")
                continue
            extract = page_data.get("extract", "")
            if extract:
                preview = extract[:100].replace('\n', ' ')
                print(f"  FOUND: {preview}...")
            else:
                print(f"  No extract")
    except Exception as e:
        print(f"  Error: {e}")

print("\n=== Done ===")
