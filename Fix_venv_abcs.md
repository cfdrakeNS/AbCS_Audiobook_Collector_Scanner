# Fixing a Wrong Virtual Environment (Windows + VS Code)

This guide is for a fresh setup when the virtual environment (`.venv`) was created in the wrong folder.

## Goal

Your project should look like this:

- `...\abcs project\abcs\`  ← **repo folder**
- `...\abcs project\abcs\.venv\`  ← **correct virtual environment location**

If your `.venv` is at:

- `...\abcs project\.venv\`  ← **wrong location**

delete it and recreate it inside the inner `abcs` folder.

---

### 1) Open the project in VS Code

1. Open **VS Code**.
2. Click **File → Open Folder...**
3. Open the inner repo folder: `...\abcs project\abcs\`

> Important: You should see files like `README.md`, `requirements.txt`, and the `src` folder in Explorer.

---

### 2) Open a terminal in VS Code

1. In VS Code menu, click **Terminal → New Terminal**.
2. A PowerShell terminal opens at the bottom.

Run this to check where you are:

```powershell
Get-Location
```

You should be in the inner repo folder path ending with `\abcs`.

---

### 3) Remove the wrong venv (parent folder)

From the terminal in `...\abcs project\abcs\`, run:

```powershell
# Move up one folder to ...\abcs project\
cd ..

# If wrong .venv exists here, delete it
if (Test-Path ".venv") { Remove-Item ".venv" -Recurse -Force }
```

Optional check:

```powershell
Get-ChildItem -Force
```

You should no longer see `.venv` in the parent folder.

---

### 4) Go back to correct repo folder

```powershell
cd .\abcs
Get-Location
```

Confirm path ends with `\abcs`.

---

### 5) Create the correct venv inside repo

```powershell
py -m venv .venv
```

This creates:

- `...\abcs project\abcs\.venv\`

---

### 6) Activate the venv

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, you should see `(.venv)` at the start of the terminal prompt.

---

### 7) Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 8) Verify Python path is correct

```powershell
python -c "import sys; print(sys.executable)"
```

Expected result: a path ending with:

- `...\abcs project\abcs\.venv\Scripts\python.exe`

---

### 9) Run the app

```powershell
python src/main.py
```

---

## Set VS Code Interpreter (important)

1. Press **Ctrl+Shift+P**.
2. Type: **Python: Select Interpreter**.
3. Choose interpreter from:
   - `...\abcs project\abcs\.venv\Scripts\python.exe`

If you cannot find it in the list:

1. Choose **Enter interpreter path**.
2. Browse to `...\abcs project\abcs\.venv\Scripts\python.exe`.

---

## If activation is blocked (PowerShell execution policy)

If you get an error running `Activate.ps1`, run this in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This change is temporary and only affects the current terminal window.

---

## Quick success checklist

- [ ] No `.venv` at `...\abcs project\`
- [ ] `.venv` exists at `...\abcs project\abcs\`
- [ ] Terminal shows `(.venv)`
- [ ] `python -c "import sys; print(sys.executable)"` points to inner `.venv`
- [ ] App starts with `python src/main.py`

---

## One-shot command block (advanced)

If you already understand terminals, this does everything quickly:

```powershell
cd "C:\path\to\abcs project";
if (Test-Path ".venv") { Remove-Item ".venv" -Recurse -Force };
cd ".\abcs";
if (Test-Path ".venv") { Remove-Item ".venv" -Recurse -Force };
py -m venv .venv;
.\.venv\Scripts\Activate.ps1;
python -m pip install --upgrade pip;
pip install -r requirements.txt;
python -c "import sys; print(sys.executable)"
```
