# default preference 
 - theme: Default (system)
 - Zoom: 150% 
 - directory: empty 
 - formats: all checked 
 - scenario: mass standard import 
 - author fall back to folder checked
 - title fall back to file checked
 - reader keywords: reader, read by, narrator, narrated by
 - author in title: warning 
 - title in author: error
 - unknown/various: warning
 - min title length: 3
 - minimum book length in minutes: 0, disabled
 - maximum book length in hours: 0, disabled
 - Duplicate match: title + author + year
 - fuzzy duplicate %: 90
 - File structure warning 
 - year consistency: warning 

## Fuzzy Threshold Explained:

**How it works:** Uses Python's `SequenceMatcher` which calculates similarity between two strings (0.0 to 1.0, converted to 0-100%).

**BOTH title AND author must pass the threshold** (AND logic - not OR).

### Settings Explained:

| Setting | What It Means | Example Matches |
|---------|---------------|-----------------|
| **0%** | **Fuzzy OFF** - Only exact matches | "The Hobbit" = "The Hobbit" only |
| **50%** | **Lenient** - Catches typos/variations | "Hobbit" ≈ "The Hobbit", "Christie" ≈ "Agatha Christie" |
| **90%** | **Strict** - Minor differences only | "Hobitt" ≈ "Hobbit" (typo), "Color" ≈ "Colour" |
| **100%** | **Nearly exact** - Almost identical | "The Hobbit" ≈ "the hobbit" (case only) |


### Real Examples at 50% Threshold:

| DB Book | Import Book | Title Match? | Author Match? | Duplicate? |
|---------|-------------|--------------|---------------|------------|
| "The Hobbit" / "Tolkien" | "Hobbit" / "Tolkien" | ✅ ~70% | ✅ 100% | ✅ YES |
| "The Hobbit" / "Tolkien" | "Hobbit" / "J.R.R. Tolkien" | ✅ ~70% | ✅ ~90% | ✅ YES |
| "Hobbit" / "Tolkien" | "Lord of the Rings" / "Tolkien" | ❌ ~30% | ✅ 100% | ❌ NO (title fails) |
| "The Hobbit" / "Tolkien" | "Hobbit" / "Rowling" | ✅ ~70% | ❌ ~20% | ❌ NO (author fails) |

### Key Points:

1. **0 = disabled** - Use only when you want strict exact matches
2. **50-70 = sweet spot** - Catches common variations without false positives
3. **90+ = very strict** - Only catches typos, still requires titles to be nearly identical
4. **Higher % = fewer duplicates found** (more strict)
5. **Lower % = more duplicates found** (more lenient)

**Recommendation:** Start with **50%** - it catches "The Hobbit" vs "Hobbit" but won't match completely different titles.

