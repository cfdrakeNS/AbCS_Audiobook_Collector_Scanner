apt install linux-image-virtual linux-tools-virtual linux-cloud-tools-virtual


# Linux Build Guide for AbCS

This guide covers building AbCS (Audio Book Collector Scanner) on Ubuntu for distribution.

---

## Prerequisites

### 1. Ubuntu VM Setup

Create an Ubuntu VM (recommended):
- **OS**: Ubuntu 22.04 LTS or 24.04 LTS (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 20GB minimum free space
- **CPU**: x86_64 architecture

### 2. Install System Dependencies

Open a terminal and run:

```bash
sudo apt update && sudo apt upgrade -y

# Install Python and build tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install Qt platform dependencies (required for PySide6)
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1 libegl1

# Install Git
sudo apt install -y git

# Install PyInstaller dependencies
sudo apt install -y binutils
```

### 3. Configure Git (First Time Setup)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Optional: Set default branch name
git config --global init.defaultBranch main
```

---

## Getting the Code

### Step 1: Generate SSH Key (One-Time Setup)

In the terminal, run:

```bash
# Generate SSH key - use your GitHub email (hotmail account)
ssh-keygen -t ed25519 -C "your-hotmail@hotmail.com"

# Display the public key (run this in terminal)
cat ~/.ssh/id_ed25519.pub
```

**Important:** Copy from the TERMINAL OUTPUT, not from this document. The output will look like:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIME8AOTbmZGmcP/d7B69FukNm+rMwf2shH83EYjCUsWZ cfdrake@gmail.com
```

To copy in terminal: Select the text with your mouse, then right-click → Copy. Or use Ctrl+Shift+C after selecting.

### Step 2: Add SSH Key to GitHub

1. Open Chrome/Firefox in your VM
2. Go to `github.com` and sign in with your Google account
3. Click your profile picture (top right) → **Settings**
4. Click **SSH and GPG keys** (left sidebar)
5. Click **New SSH key** (green button)
6. Title: `Ubuntu VM`
7. Key: Paste what you copied from `cat ~/.ssh/id_ed25519.pub`
8. Click **Add SSH key**

### Step 3: Test SSH Connection

Back in terminal:

```bash
# First connection - type 'yes' when asked
ssh -T git@github.com
```

You should see: `Hi cfdrakeNS! You've successfully authenticated...`

**If you see "Permission denied (publickey)":** Go back to Step 2 - your key wasn't added correctly.

### Step 4: Clone the Repository

```bash
cd ~
git clone git@github.com:cfdrakeNS/redevelop-AbCS-project.git abcs
cd abcs
```

### Switch to the Correct Branch

```bash
# List available branches
git branch -a

# Switch to the final branch (or whichever you need)
git checkout final

# Verify current branch
git branch --show-current
```

---

## Build Environment Setup

### 1. Create Python Virtual Environment

```bash
cd ~/abcs

# Create venv
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify (should show path to venv python)
which python
```

### 2. Install Dependencies

```bash
# Ensure you're in venv (prompt should show (venv))
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### 3. Test the App (Optional but Recommended)

```bash
source venv/bin/activate
python src/main.py
```

If you see Qt platform errors, install additional dependencies:
```bash
sudo apt install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0
```

---

## Building the Executable

### Option 1: Standard Build (build_linux.sh)

This creates a single-file executable:

```bash
cd ~/abcs
source venv/bin/activate

# Make script executable and run
chmod +x build_linux.sh
./build_linux.sh
```

Output: `dist/AbCS` (single executable file)

### Option 2: Debug Build (build_linux_debug.sh)

Use this when the app won't start and you need error messages:

```bash
cd ~/abcs
chmod +x build_linux_debug.sh
./build_linux_debug.sh
```

This will:
- Build with console output enabled
- Create log files: `abcs_linux_build.log` and `abcs_linux_run.log`
- Run the app immediately after building
- Show helpful error messages if Qt dependencies are missing

---

## Legacy CPU Support (If Needed)

If building for older CPUs that lack SSE4.2/POPCNT support:

```bash
cd ~/abcs
chmod +x fix_linux_legacy_cpu_env.sh
./fix_linux_legacy_cpu_env.sh
```

This script:
- Requires Python 3.12
- Installs PySide6 < 6.7 (compatible with older CPUs)
- Backs up existing .venv

---

## Distribution

### Single File Distribution

The built executable is at `dist/AbCS`. You can distribute this single file to users.

**Note**: Single-file PyInstaller builds extract to `/tmp` on first run, which may cause slower startup.

### For Better Performance (Onedir Mode)

To build as a folder (faster startup, like Windows onedir mode):

```bash
source venv/bin/activate

# Build as directory instead of single file
python -m PyInstaller \
  --name="AbCS" \
  --onedir \
  --windowed \
  --clean \
  --noconfirm \
  --add-data="data/abcdDB_def.sql:data" \
  --hidden-import="PySide6.QtCore" \
  --hidden-import="PySide6.QtGui" \
  --hidden-import="PySide6.QtWidgets" \
  --hidden-import="mutagen" \
  --hidden-import="mutagen.mp3" \
  --hidden-import="mutagen.mp4" \
  --hidden-import="mutagen.flac" \
  --hidden-import="mutagen.oggvorbis" \
  --hidden-import="mutagen.wave" \
  --hidden-import="openpyxl" \
  --hidden-import="odf" \
  --hidden-import="odf.opendocument" \
  --collect-submodules="odf" \
  --exclude-module="PySide6.QtSql" \
  --exclude-module="PySide6.QtQml" \
  --exclude-module="PySide6.QtQuick" \
  --exclude-module="PySide6.QtQuickShapes" \
  src/main.py
```

Output: `dist/AbCS/` folder containing the executable and all dependencies.

Distribute the entire `dist/AbCS/` folder or create a tarball:
```bash
cd dist
tar -czf AbCS-linux.tar.gz AbCS/
```

---

## Troubleshooting

### Qt Platform Plugin Errors

**Error**: `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"`

**Fix**:
```bash
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1 libegl1
sudo apt install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0
```

### Missing Audio Codec Support

For full audio file support, install:
```bash
sudo apt install -y libmad0 libvorbis0a libflac8
```

### Illegal Instruction (Core Dumped)

Your CPU doesn't support the required instruction set. Use the legacy CPU script:
```bash
./fix_linux_legacy_cpu_env.sh
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Clone repo | `git clone https://github.com/cfdrakeNS/redevelop-AbCS-project.git abcs` |
| Switch branch | `git checkout final` |
| Create venv | `python3 -m venv venv` |
| Activate venv | `source venv/bin/activate` |
| Install deps | `pip install -r requirements.txt` |
| Build (standard) | `./build_linux.sh` |
| Build (debug) | `./build_linux_debug.sh` |
| Run test | `python src/main.py` |
| Build output | `dist/AbCS` |

---

## Notes

- The `build_linux.sh` script uses `onefile` mode by default
- The Windows build uses `onedir` mode (folder) for better antivirus compatibility
- Linux onefile builds extract to `/tmp` on each run, causing slower startup
- Consider using `onedir` mode for Linux if startup performance is important
