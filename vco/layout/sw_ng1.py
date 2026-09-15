import pathlib
import re

p = pathlib.Path('build_layout.py')
s = p.read_text()

# Show the BANK table so the change is made against what is actually there.
m = re.search(r'BANK\s*=\s*\[(.*?)\]', s, re.S)
print("BANK table as it stands:")
print(m.group(0) if m else "  not found")
