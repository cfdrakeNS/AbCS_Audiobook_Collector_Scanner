To improve the search in `web_metadata` and `book_api.py` so that results are more accurate and avoid mismatched authors/titles, you should:

**1. Author Last Name Check:**  
- Extract the last name from the DB author (e.g., "Agatha Christie" → "Christie").
- Only accept web results where the web author string contains this last name (case-insensitive, ignore punctuation).

**2. Title Word Match (50% rule):**  
- Split the DB title into words (ignoring common stopwords and punctuation).
- Split the web result title into words.
- Count how many words from the DB title appear in the web title.
- Only accept the result if at least 50% of the DB title words are present in the web title.

**Implementation Steps:**  
- Add a function to extract the last name from the DB author.
- Add a function to compute the percentage of DB title words found in the web title.
- In your matching logic (where you compare DB and web results), only accept a match if:
  - The web author contains the DB author last name, AND
  - At least 50% of the DB title words are present in the web title.

**Result:**  
- This will prevent mismatches where the author is completely different, and will filter out web results with unrelated titles.

