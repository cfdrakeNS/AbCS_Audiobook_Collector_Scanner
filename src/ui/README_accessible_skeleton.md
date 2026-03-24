# Accessible Window Skeleton

## PROVEN Working Accessibility Pattern

This skeleton provides a **proven working accessibility foundation** for all future windows.

## 🎯 The Problem This Solves

**No more hours debugging basic shortcuts!** F1, Alt+/, and Escape work out of box.

## 🚀 How to Use

### 1. Copy the Skeleton
```bash
cp src/ui/accessible_window_skeleton.py src/ui/your_new_window.py
```

### 2. Rename and Customize
```python
# Change class name
class YourWindowName(AccessibleWindowSkeleton):
    def __init__(self, ...):
        super().__init__(parent, window_title="Your Window Title", ...)
```

### 3. Add UI Elements
```python
def setup_ui(self, layout):
    # Add your fields
    form = QFormLayout()
    
    # Your field
    your_field_label = QLabel("&Your Field:")
    self.your_field_edit = QLineEdit()
    your_field_label.setBuddy(self.your_field_edit)
    form.addRow(your_field_label, self.your_field_edit)
    
    layout.addLayout(form)
```

### 4. Add Field Shortcuts
```python
def setup_shortcuts(self):
    # Add your field shortcut
    self.your_field_shortcut = QShortcut(QKeySequence("Alt+Y"), self)
    self.your_field_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
    self.your_field_shortcut.activated.connect(lambda: self.your_field_edit.setFocus())
```

### 5. Test It Works
```bash
python src/ui/your_new_window.py
```

**Test F1, Alt+/, and Escape - they should work immediately!**

## ✅ What Works Out of Box

- **✅ F1**: Shows help dialog
- **✅ Alt+/**: Reads status bar for JAWS
- **✅ Escape**: Closes window
- **✅ Alt+Letter**: Focuses fields (when you add them)
- **✅ Screen Readers**: Full JAWS/NVDA support

## 🔧 Key Rules

1. **NEVER mix centralized and local shortcuts** - causes conflicts
2. **ALWAYS use local shortcuts for F1, Escape, Alt+/** - proven to work
3. **AVOID `setWindowModality(Qt.ApplicationModal)`** - blocks shortcuts
4. **START from this skeleton** - don't reinvent the wheel
5. **TEST incrementally** - add features one by one

## 📁 Files

- `accessible_window_skeleton.py` - Template to copy
- `working_web_metadata.py` - Example implementation
- `Screen_Reader_and_PySide6_best_practices.md` - Full documentation

## 🎉 Result

**Accessibility that just works** - no more debugging basic shortcuts!

---

*"This skeleton prevents the accessibility frustration we went through with the web metadata window."*
