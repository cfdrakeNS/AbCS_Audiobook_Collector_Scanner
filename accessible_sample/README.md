# Standalone Accessible Sample Application

This is a **complete standalone accessible sample** that demonstrates all accessibility patterns without any AbCS dependencies.

## Purpose

- **True Reference Implementation**: Shows how to implement accessibility patterns in any PySide6 application
- **Self-Contained**: All necessary files included - no external dependencies
- **Complete Patterns**: Demonstrates all 9 accessibility patterns working together
- **JAWS Compatible**: Tested and optimized for JAWS screen reader

## Files

- `main.py` - Main application window with all accessibility patterns
- `accessibility_patterns.py` - Mixin providing all accessibility functionality
- `styled_dialogs.py` - Helper for accessible styled message boxes
- `README.md` - This documentation

## Running the Sample

```bash
cd accessible_sample
python main.py
```

## Accessibility Patterns Demonstrated

### 1. Status Bar Pattern with Alt+/ Readback
- Status messages displayed in status bar
- Alt+/ reads current status message
- Screen reader announcements

### 2. Alt+Letter Hygiene
- Blocks unmapped Alt+keys for JAWS compatibility
- Beep feedback for blocked keys
- Allowlist for permitted Alt+keys

### 3. Combo Box Anti-Noise Pattern
- Blocks plain Up/Down arrows (prevents noise)
- Alt+Down opens dropdown
- Enter commits value and moves focus

### 4. Table Row Number Suppression
- Hidden vertical headers for JAWS
- No row numbers announced
- Meaningful accessible text for cells

### 5. Screen Reader-Optimized Buttons
- Always enabled (no conditional disabling)
- Error feedback instead of silent failures
- Proper accessible names and descriptions

### 6. Focus Management After Operations
- Predictable focus after save/delete
- Error focus returns to invalid fields
- Logical focus flow

### 7. Explicit Tab Order
- Defined tab order follows visual layout
- Prevents focus jumping
- JAWS navigation optimized

### 8. Modal Message Boxes
- Styled, accessible dialogs
- Proper focus management
- Screen reader compatible

### 9. Global Enter Shortcut Avoidance
- No global Return/Enter shortcuts
- Enter works on focused buttons
- keyPressEvent for specific handling

## Working Shortcuts

### Basic Shortcuts
- **F1** - Show help with all patterns
- **Alt+/** - Read status message
- **Escape** - Close with confirmation

### Field Shortcuts
- **Alt+T** - Focus Title field
- **Alt+C** - Focus Category field
- **Alt+Y** - Focus Year field
- **Alt+I** - Focus Items table
- **Alt+L** - Focus Items table
- **Alt+S** - Focus Save button
- **Alt+D** - Focus Delete button

## Testing Instructions

1. **Basic Functionality**
   - All shortcuts should work immediately
   - Tab order follows visual layout
   - Enter activates focused buttons

2. **Screen Reader Testing**
   - Test with JAWS screen reader
   - Verify all elements are announced
   - Check Alt+/ status readback

3. **Accessibility Patterns**
   - Combo box: Plain arrows blocked, Alt+Down opens dropdown
   - Table: No row numbers announced
   - Alt+letter blocking: Unmapped keys beep

## Usage as Reference

Copy these files to any project:

1. **Copy the `accessible_sample` folder** to your project
2. **Inherit from `AccessibilityMixin`** in your dialogs
3. **Use `show_styled_message_box()`** for modal dialogs
4. **Follow the shortcut patterns** in `main.py`
5. **All accessibility patterns work out of box**

## Key Features

- ✅ **Zero Dependencies** - Works in any PySide6 application
- ✅ **Complete Patterns** - All 9 accessibility patterns implemented
- ✅ **JAWS Optimized** - Tested with JAWS screen reader
- ✅ **Copy & Paste** - Use as starting point for new applications
- ✅ **Self-Contained** - All helper files included
- ✅ **Documented** - Clear code with comments

This is the definitive reference for implementing accessibility patterns in PySide6 applications.
