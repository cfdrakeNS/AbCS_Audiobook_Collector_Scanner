# Fix 8,000-Book Database Slowness

**Problem:** The imported 8k-book database is missing indexes, causing sort operations to take minutes.

**Solution:** Run the repair script to add indexes and optimize the database.

## Steps for Wayne:

### 1. Locate the database file
Your 8k-book database file (should be named something like `abcs.db` or `books.db`)

### 2. Run the repair script
Open a terminal/command prompt in the AbCS folder and run:

```bash
python test/repair_abcs_db.py <path_to_your_8k_database.db>
```

**Example:**
```bash
python test/repair_abcs_db.py C:\Users\Wayne\Music\my_books.db
```

### 3. What it does
- Adds 12 indexes that speed up sorting and searching
- Runs ANALYZE to optimize query performance
- Runs VACUUM to compact the database
- Takes 1–5 seconds (depending on system speed)

### 4. Test the fix
Open the repaired database in AbCS and try switching sort order (Alt+O):
- Title → Author → Genre → Series

**Expected:** Order changes complete in **< 1 second** (not minutes).

### 5. Use the repaired database
The script updates the file in-place. You can now use it as your main database in AbCS.

---

## What Changed?

The 8k-book import process skipped the automatic index creation that normally happens when you open AbCS. 

Indexes are essentially "shortcuts" that SQL uses to find and sort data quickly:
- Without indexes: Database reads all 8,000 books to sort them → minutes.
- With indexes: Database uses a pre-built "sorted list" → < 1 second.

The repair script adds the same indexes that AbCS automatically creates for new databases.

---

## Questions?

If sort operations are still slow after running the script:
1. Verify the script ran successfully (you should see ✓ checkmarks for all 12 indexes)
2. Check the .db file size increased slightly (VACUUM compresses it)
3. Test with a small sort operation first (Author order on 8k books)
4. Contact support with the database file name and size
