# AbCS - Accessibility Testing Instructions

## What You're Testing
This is an audiobook collection manager designed for blind/low-vision users with JAWS/NVDA support. 

## Setup Instructions

1. **Extract the zip file** to a folder on your computer

2. **Run setup.bat** (double-click it)
   - This installs all required dependencies
   - Takes 1-2 minutes
   - Creates a virtual environment

3. **Run the application**:
   - Double-click `run.bat` 
   - OR open terminal and type: `python src\main.py`

## What to Test

### Keyboard Navigation
- **Alt+L** - Collection filter
- **Alt+R** - Read filter  
- **Alt+O** - Order by
- **Alt+S** - Search box
- **Alt+B** - Focus book list
- **Ctrl+Q** - Quit application
- **Ctrl+W** - Close window
- **Del** - Delete selected books

### Search Testing
- Type in search box → filters as you type
- Type `?searchterm` → press Enter for keyword search
- Check status bar messages

### Test Plan: Enter-to-Search Focus (Series/Genre)

#### Preconditions
- App launches successfully.
- Main window displays columns: Author, Title, Year, Plot, Series, Genre, Time, Tracks, Read, Added.

#### Core Functional Tests
1. **Series search focus**
   - Set **Order By** to Series.
   - Enter a Series value known to exist.
   - Press Enter.
   - **Expected:** Focus moves to the Series column cell in the first matching row (not the column before).

2. **Genre search focus**
   - Set **Order By** to Genre.
   - Enter a Genre value known to exist.
   - Press Enter.
   - **Expected:** Focus moves to the Genre column cell in the first matching row.

3. **Author/Title regression**
   - Set **Order By** to Author, search, press Enter.
   - **Expected:** Focus moves to the Author column cell in the first matching row.
   - Repeat for Title.

#### No-Result Behavior
- Search for a Series or Genre that does not exist.
- Press Enter.
- **Expected:** Status bar shows “No … found,” focus remains in search box (or unchanged if that is current behavior).

#### Keyword Search Behavior
- Enter `?SeriesName` and press Enter.
- **Expected:** Search runs only on Enter and focus goes to Series column in first match.

#### Accessibility Verification
- With JAWS/NVDA on, confirm status announcements occur after Enter search.
- Confirm focus change is announced correctly for Series/Genre.

#### Regression: Table Navigation
- After Enter search, use arrow keys to move within the table.
- **Expected:** Navigation and announcements are correct for Plot/Series/Genre columns.

#### Edge Cases
- Empty search text + Enter: no search, no focus jump.
- Leading/trailing spaces in search text: behavior consistent with current search normalization.

### Screen Reader Testing
- Navigate the book table with arrow keys
- Select multiple books (Shift+Click, Ctrl+Click)
- Check status bar announcements
- Test with 14pt fonts and scaling (Ctrl++ / Ctrl+-)

### What to Report
- What works well
- What's confusing
- What JAWS/NVDA announces incorrectly
- Any crashes or errors

## Requirements
- Windows 10 or higher
- Python 3.8 or higher
- JAWS or NVDA screen reader

## Contact
Report issues to: [Your contact info]
