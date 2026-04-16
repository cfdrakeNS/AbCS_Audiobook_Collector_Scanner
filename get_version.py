import pathlib
import re

t = pathlib.Path("src/build_config.py").read_text(encoding="utf-8")
m = re.search(r'^\s*APP_VERSION\s*=\s*"([^"]+)"', t, re.MULTILINE)
print(m.group(1) if m else "")
