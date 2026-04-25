import pathlib
import re

# Read version from src/build_config.py instead of src/main.py
t = pathlib.Path("src/build_config.py").read_text(encoding="utf-8")
m = re.search(r'^\s*APP_VERSION\s*=\s*"([^"]+)"', t, re.MULTILINE)
print(m.group(1) if m else "")
