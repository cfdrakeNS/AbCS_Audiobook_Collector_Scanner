# AbCS - Audiobook Collector Scanner User Guide

## 1. Introduction
AbCS (Audiobook Collector Scanner) is a cross-platform manager for your audiobook collection. It allows you to scan folders, import metadata from ID3 tags, and manage your library with a focus on ease of use and accessibility.

This application is designed specifically for:
* **Sighted Users:** High-contrast UI and intuitive layouts.
* **Low-Vision Users:** Built-in UI scaling (zoom) and large fonts.
* **Screen Reader Users (JAWS/NVDA):** Full keyboard control, ARIA-like status announcements, and optimized tab orders.

---

## 2. Accessibility Features
### 2.1 UI Scaling (Zoom)
The app defaults to **150% zoom** for readability.
* **Zoom In:** `Ctrl` + `+`
* **Zoom Out:** `Ctrl` + `-`
* **Reset Zoom (100%):** `Ctrl` + `0`

### 2.2 Screen Reader Support
* **Status Bar (Alt + /):** Press this at any time to have your screen reader re-read the current status message or focus hint.
* **Silent Redundancy:** Focus changes and major actions are automatically announced to the status bar.
* **Table Navigation:** Use Arrow keys to navigate. To exit a table and reach other buttons, use `Tab` or `Shift + Tab`.

### 2.3 Visual Themes
Access via **View > Preferences**. Choose from Default (System), Dark, or High Contrast themes.

---

## 3. Keyboard Shortcuts Reference

### Global
* **F1:** Open Keyboard Shortcuts / Help
* **Alt + /:** Read Status Bar
* **Esc:** Cancel current operation / Close window

### Main Window
* **Alt + C:** Collection Filter
* **Alt + R:** Read Filter
* **Alt + O:** Order By (Sort)
* **Alt + S:** Search Box (Type `?` for keyword search)
* **Alt + M:** Open Menu
* **Alt + U:** Update Selected Books
* **Alt + D:** Delete Selected Books
* **Space:** Select / Deselect book for bulk operations
* **Ctrl + A:** Select All books
* **Insert:** Add a New Book manually

### Book Details / Import Detail
* **Alt + T:** Title
* **Alt + A:** Author
* **Alt + Y:** Year
* **Alt + I:** Series
* **Alt + G:** Genre
* **Alt + O:** Format (Book Details)
* **Alt + V:** Save Changes
* **Page Up / Page Down:** Navigate to Previous / Next record

---

## 4. Using the Application

### 4.1 Importing Books
1. Press **Ctrl + I** or go to **File > Import**.
2. Click **Browse (Alt + W)** to select a folder.
3. AbCS will scan all subfolders for audio files (MP3, M4B, etc.).
4. **Reviewing Results:**
   * Books with missing data appear in the Errors list. 
   * Use **Space** to toggle books between "Add" and "Error" lists.
   * Double-click a book to edit details before adding to the database.
5. Click **Add (Alt + A)** to finish the import.

### 4.2 Searching and Filtering
* **Search (Alt + S):** Type a name to jump to it in the list.
* **Keyword Search:** Type `?` followed by a word (e.g., `?Dragon`) to filter the list to only books containing that word.
* **Filters:** Use **Collection (Alt + C)** and **Read (Alt + R)** to narrow down your view.

### 4.3 Managing Metadata
* **Book Details:** Open by double-clicking a title or pressing `Enter`.
* **Web Metadata:** If a book is missing a plot or genre, use the **Fetch Web Info** button in the Book Details window. It will search Google Books, Open Library, and WikiData.
* **Sanitization:** AbCS automatically cleans titles and authors (removing leading punctuation, fixing case) to keep your library organized.

### 4.4 Reading History
Track your progress via **View > Reading History**.
* View books read in the last 3 months (default), by month, or by custom date range.
* Use **Alt + L** to jump directly to the history list.

---

## 5. Preferences and Customization
Go to **View > Preferences** to customize your experience:
* **Display:** Adjust Theme and Zoom level.
* **Import Rules:** Set how the scanner handles missing data (e.g., Warning if title is too short).
* **Duplicates:** Configure "Fuzzy Matching" (default 90%) to catch nearly identical titles.
* **Restore Defaults (Alt + E):** Quickly reset all settings to the recommended AbCS configuration.

---

## 6. Technical Notes
* **Database:** Uses a standard SQLite database located in the `data/` folder.
* **Backups:** Use **File > Backup/Restore** frequently. Backups are timestamped and stored in the `backups/` folder.
* **Source Fields:** The "Source" field helps you track where a book came from (e.g., "Import" or manual entry).

---

**Guide Version:** 1.9.4 (Python Edition)
**Last Updated:** April 2026