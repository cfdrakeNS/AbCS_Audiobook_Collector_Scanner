# AbCS Friend Setup (Review-Only, Windows)

This guide is for a friend who will **review and run AbCS locally**, but **not contribute code or docs** to the repository.

## 1) Full local setup for a novice (separate from talk3270)

## A. Install required software (one time)

1. Install **Git for Windows**:
   - https://git-scm.com/download/win
2. Install **Python 3.11 or 3.12**:
   - https://www.python.org/downloads/windows/
   - During install, check: **Add Python to PATH**.
3. Install **VS Code**:
   - https://code.visualstudio.com/
4. In VS Code, install extensions:
   - **Python** (publisher: Microsoft)
   - **Pylance** (publisher: Microsoft)

## B. Important: use a separate VS Code profile for AbCS

This keeps AbCS settings separate from your other project (`talk3270`).

1. Open VS Code.
2. Click the profile icon at the bottom-left.
3. Choose **Profiles** → **Create Profile**.
4. Name it **AbCS**.
5. Switch to the **AbCS** profile before working on this repo.

## C. Understand the two terminals (very important)

### Option 1: Windows PowerShell app
- Open from Start Menu: type **PowerShell**.
- This is a separate Windows app.

### Option 2: VS Code integrated terminal
- In VS Code: menu **Terminal** → **New Terminal**.
- This opens a terminal panel inside VS Code.

For this guide, either terminal is fine. All commands below are **PowerShell commands**.

---

## D. Download (clone) AbCS to its own folder

Do this in **PowerShell** (Windows app or VS Code terminal):

```powershell
cd $HOME
mkdir projects -ErrorAction SilentlyContinue
cd projects
git clone https://github.com/cfdrakeNS/redevelop-AbCS-project.git abcs
cd abcs
```

This places AbCS in a dedicated folder, separate from `talk3270`.

## E. Open the project folder in VS Code

In VS Code:
1. **File** → **Open Folder...**
2. Select the folder you just cloned (`abcs`).
3. Confirm you are still using profile **AbCS**.

## F. Create a project-local Python environment (`.venv`)

In the **VS Code terminal** (Terminal → New Terminal), run:

```powershell
py -3.11 -m venv .venv
```

If that fails because 3.11 is missing, run:

```powershell
py -3.12 -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this once, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

When active, your terminal prompt usually starts with `(.venv)`.

## G. Install Python packages

Still in the same terminal (with `(.venv)` active):

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## H. Tell VS Code to use this `.venv`

1. Press **Ctrl+Shift+P** in VS Code.
2. Type: **Python: Select Interpreter**.
3. Choose interpreter ending with:
   - `.venv\Scripts\python.exe`

## I. Run AbCS locally

In the VS Code terminal:

```powershell
python src/main.py
```

If the app opens, setup is complete.

---

## 3) How to pull latest code from GitHub using VS Code

Use this when you want the newest AbCS changes from GitHub.

### Method A (recommended): VS Code buttons (no typing)
1. Open VS Code (profile: **AbCS**).
2. Open the AbCS folder.
3. Click the **Source Control** icon on the left sidebar (branch icon).
4. At the top of Source Control, click **...** (More Actions).
5. Click **Pull**.
6. Wait until VS Code shows pull completed in the status/message area.

Tip: You can also click the branch/sync icon in the bottom status bar and choose **Pull**.

### Method B: VS Code terminal (simple command)
1. In VS Code, open **Terminal** → **New Terminal**.
2. Make sure you are in the AbCS folder (you should see it in terminal path).
3. Run:

```powershell
git pull
```

If Git asks anything (rare for review-only), stop and ask you before continuing.

### After pulling
If requirements changed, update packages:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then run the app again:

```powershell
python src/main.py
```

---

## 4) Daily review use (no contribution)

For review/testing only:
1. Open VS Code with **AbCS profile**.
2. Open the `abcs` folder.
3. Open terminal and activate venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Run app:

```powershell
python src/main.py
```

No Git push/PR steps are needed for this review-only setup.

---

## Quick summary

- Use **GitHub Read access** for review-only.
- File-type permissions (`.md` write, `.py` read) are **not supported** as a simple GitHub role.
- Keep AbCS separate from `talk3270` by using:
  - a separate folder,
  - a separate VS Code profile,
  - a separate `.venv` in the AbCS folder.
