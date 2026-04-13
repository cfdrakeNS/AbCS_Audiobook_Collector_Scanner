# Accessibility best-practice rules (PySide6-specific)

These matter more than the toolkit itself.

### ✅ Rule 1: Never rely on visuals alone

If text is important:

* Put it in a `QLabel`
* Or a focusable read-only control

### ✅ Rule 2: Everything must be reachable by keyboard

No mouse-only UI. Ever.

```python
widget.setFocusPolicy(Qt.StrongFocus)

### ✅ Rule 3: Accessible names are NOT optional

```python
widget.setAccessibleName("Search results")
widget.setAccessibleDescription("List of matching items")
```

If you don’t set these, JAWS guesses—and guessing is bad.

### ✅ Rule 4: Status updates must be announced

Never rely solely on `QStatusBar`.

Mirror status messages to:

* A hidden label
* Or a read-only focusable control

### ✅ Rule 5: Errors should move focus

If something fails:

* Move focus to the error text
* Or use a modal dialog

JAWS will not announce background errors reliably.

## 5. One underrated resource: NVDA

Even if your users are JAWS users, test with **NVDA**.

Why?

* It’s free
* It exposes accessibility bugs faster
* If NVDA can’t read it, JAWS probably won’t either

## 6. Practical reality check (important)

No Python GUI toolkit gives you *perfect* accessibility out of the box.

Accessibility success comes from:

* Widget choice
* Focus management
* Explicit labels
* Predictable navigation
