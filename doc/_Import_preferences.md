# Import Preferences 

1. **Import Rules for Each Scenario (including Fallback):**
   - **Mass Standard Import:**
     - Author folders are scanned; books may be in title folders, single files under author, or nested in series folders.
     - Fallback: If author or title is missing, fallback is applied from folder or file name based on preferences.
   - **Series From Directory:**
     - Author folders contain series subfolders; books are single files in series folders.
     - Fallback: Author from parent folder, title from file name if missing.
   - **Series From Filename:**
     - Author folders with single-file books; series parsed from file name (in parentheses).
     - Fallback: Author from folder, title from file name if missing.
   - **Single Item:**
     - Import one author folder, one series/book folder, or one file.
     - Fallback: Author from folder, title from file name if missing.
   - **General Fallback Logic:**
     - If author/title is blank, fallback is applied only if enabled in preferences. Otherwise, missing author/title is treated as a hard error and blocks auto-add.

2. **Fuzzy Duplicate % (How It Works):**
   - Fuzzy duplicate matching compares author/title text similarity using a percentage threshold.
   - **High value (e.g., 90-100%):** Only nearly identical author/title pairs are considered duplicates. Safer, less likely to block legitimate imports.
   - **Low value (e.g., 70-80%):** More aggressive; even small differences are flagged as duplicates. May block more books, including some that are not true duplicates.
   - Adjust in preferences for stricter or looser duplicate detection.
