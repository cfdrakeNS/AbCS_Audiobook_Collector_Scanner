Yeah—this is a *very* common pain point with **PySide6 + **JAWS** on **Windows**. The short version: Qt widgets often *look* fine visually but don’t expose the right accessibility info unless you’re explicit.

Let’s break it down by problem and fix.

---

## 1. Read-only text boxes not being spoken

### The core issue

If you’re using `QLineEdit` or `QTextEdit` set to read-only, JAWS often treats them as *non-interactive* and won’t announce content unless focus lands *inside* them—and sometimes not even then.

### Best practices (this matters a lot)

#### ✅ Use `QLabel` instead of read-only fields (when possible)

If the text is **display-only**, don’t use an input widget at all.

```python
label = QLabel("Status: Ready")
label.setAccessibleName("Status message")
label.setAccessibleDescription("Displays the current application status")
```

JAWS reads `QLabel` **far more reliably** than read-only edits.

---

#### ⚠️ If you MUST use `QLineEdit`

Make it explicitly accessible:

```python
edit = QLineEdit()
edit.setReadOnly(True)
edit.setText("Processing complete")

edit.setAccessibleName("Result")
edit.setAccessibleDescription("Read-only result field")
```

Also:

```python
edit.setFocusPolicy(Qt.StrongFocus)
```

JAWS often ignores widgets that can’t receive focus.

---

#### 🚫 Avoid `setEnabled(False)`

Disabled controls are *invisible* to screen readers.

❌ Bad:

```python
edit.setEnabled(False)
```

✅ Better:

```python
edit.setReadOnly(True)
```

---

## 2. Status bar text not being spoken

### Why this happens

Qt’s `QStatusBar.showMessage()` **does not automatically fire accessibility events**. JAWS won’t announce it unless focus moves.

This is a known Qt accessibility limitation.

---

## 3. Correct way to announce status messages to JAWS

### ✅ Use a hidden “live region” widget

This is the **most reliable pattern**.

```python
self.status_label = QLabel("")
self.status_label.setAccessibleName("Application status")
self.status_label.setAccessibleDescription("Announces application status updates")
self.status_label.setVisible(False)
```

When status changes:

```python
def announce_status(self, message):
    self.status_label.setText(message)
```

JAWS will usually announce this immediately.

---

### ✅ Or mirror status text to a focusable widget

If it’s important enough to announce, it’s important enough to be accessible.

```python
self.status_display = QLineEdit()
self.status_display.setReadOnly(True)
self.status_display.setAccessibleName("Status")
```

Update it alongside the status bar.

---

## 4. Force JAWS to notice updates (important trick)

Sometimes JAWS ignores text changes unless an accessibility event fires.

### 🔧 The “clear then set” trick

```python
label.setText("")
label.repaint()
label.setText("File saved successfully")
```

This often forces JAWS to re-announce.

---

## 5. Tab order REALLY matters

JAWS navigation relies heavily on predictable tab order.

```python
self.setTabOrder(widget1, widget2)
self.setTabOrder(widget2, widget3)
```

If a widget can’t be reached by Tab, JAWS may never read it.

---

## 6. Turn on Qt accessibility (usually on, but check)

```python
import os
os.environ["QT_ACCESSIBILITY"] = "1"
```

Set this **before** creating `QApplication`.

---

## 7. Debugging checklist (JAWS + Qt)

Ask yourself:

* Is this text **display-only**? → use `QLabel`
* Can it receive **keyboard focus**?
* Does it have an **accessible name**?
* Am I relying on `QStatusBar.showMessage()` alone? (Don’t)
* Did the text *change*, or just update visually?

---

## 8. Hard truth (so you don’t chase ghosts)

Qt accessibility on Windows is **good but not perfect**. JAWS works best when:

* Text is in labels
* Widgets are focusable
* Accessible names/descriptions are explicit
* Status updates are mirrored to an accessible control

You’re not doing anything “wrong”—you’re hitting known edges of Qt + MSAA/UIA.

---

## CRITICAL LESSON LEARNED: Web Metadata Window (Mar 2026)

### The Problem:
Hours spent debugging basic accessibility shortcuts (F1, Alt+/, Escape) that should work out of box.

### The Root Cause:
**Window modality and shortcut conflicts** - mixing centralized and local shortcut systems caused blocking.

### The Solution:
**Start from PROVEN working base** - copy exact working accessibility pattern, then add features incrementally.

### Working Pattern:
```python
def setup_shortcuts(self):
    """Setup shortcuts - EXACT copy from working test window."""
    # F1 - local shortcut (PROVEN working)
    self.help_shortcut = QShortcut(QKeySequence("F1"), self)
    self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
    self.help_shortcut.activated.connect(self.on_show_shortcuts)
    
    # Escape - local shortcut (PROVEN working)
    self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
    self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
    self.close_shortcut.activated.connect(self.reject)
    
    # Alt+/ - local shortcut (PROVEN working)
    self.read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
    self.read_status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
    self.read_status_shortcut.activated.connect(self.on_read_status_bar)
```

### Key Rules:
1. **NEVER mix centralized and local shortcuts** - causes conflicts
2. **ALWAYS use local shortcuts for F1, Escape, Alt+/** - proven to work
3. **AVOID `setWindowModality(Qt.ApplicationModal)`** - blocks shortcuts
4. **START from proven working base** - don't reinvent the wheel
5. **TEST incrementally** - add features one by one

### Files Created:
- `accessibility_test_window.py` - Minimal test (PROVEN working)
- `working_web_metadata.py` - Starts from proven base + web fields

### Result:
**F1, Alt+/, and Escape work perfectly** when using the correct pattern.

---

## 9. Table accessibility - suppress row numbers

### The problem
JAWS announces "Row 1, Column 1, Value" which is noise when the actual content is meaningful. Row numbers provide no functional value in most data tables.

### The solution
```python
# Hide row numbers
table.verticalHeader().setVisible(False)
table.setVerticalHeaderLabels([""] * table.rowCount())

# Add meaningful accessible text
item.setData(Qt.AccessibleTextRole, "42 books")  # Instead of just "42"
```

### Reference implementations
- `src/ui/reading_history_window.py` - Statistics tables with meaningful value descriptions
- `src/ui/backup_restore_window.py` - Backup file list in `refresh_backup_list()`
- `src/ui/name_list_window.py` - Author/series lists with empty header labels
- `src/ui/main_window.py` - Book list table with hidden vertical headers

### Implementation notes
- Apply `setVerticalHeaderLabels()` after populating table data
- Use `Qt.AccessibleTextRole` for meaningful descriptions instead of raw values
- Test with JAWS to ensure row numbers are not announced
- Pattern applies to all data tables where row numbers provide no functional value

---

If you want, tell me:

* Which widgets you're using (`QTextEdit`, `QLineEdit`, `QLabel`, etc.)
* Whether this is a dialog, main window, or background task
* How critical the status messages are (info vs errors)

I can give you **exact widget patterns** that JAWS behaves nicely with 👍
