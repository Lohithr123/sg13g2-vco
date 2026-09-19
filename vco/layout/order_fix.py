import pathlib
import re

p = pathlib.Path('route_v2.py')
lines = pathlib.Path('route_v2.py').read_text().split('\n')

# 1. Find the gate bus block: from its banner to the next top-level banner.
start = next(i for i, l in enumerate(lines) if '=== mirror gate buses ===' in l)
end = next(i for i in range(start + 1, len(lines))
           if re.match(r'^print\("\\n=== ', lines[i]))
print(f"gate bus block: lines {start+1}..{end}")

block = lines[start:end]

# 2. Pull the XMR lookups out of it — other code after the block needs them.
hoist = [l for l in block if re.match(r'^XMR[12] = find', l)]
block = [l for l in block if not re.match(r'^XMR[12] = find', l)]
print(f"hoisting {len(hoist)} lookup(s): {[h.split('=')[0].strip() for h in hoist]}")

# 3. Rebuild: remove the block, insert the hoisted lookups beside XMT2/XMT1,
#    and place the block after the commoning.
rest = lines[:start] + lines[end:]

anchor = next(i for i, l in enumerate(rest) if l.startswith('XMT1 = find'))
rest = rest[:anchor + 1] + hoist + rest[anchor + 1:]
print(f"lookups inserted after XMT1 at line {anchor+1}")

wr = next(i for i, l in enumerate(rest) if l.startswith('layout.write(OUT)'))
out = rest[:wr] + [
    '# The gate bus runs AFTER the commoning: it contacts the poly bar that',
    '# bus_fingers draws and reads what the commoning records. Running it',
    '# before — as the file originally did — placed the contact before the bar',
    '# existed, which is why all eight mirror gates extracted as isolated nets',
    '# and the tail and buffer current sources had no bias at all.',
    '',
] + block + [''] + rest[wr:]

pathlib.Path('route_v2.py').write_text('\n'.join(out))
print(f"block moved before layout.write at line {wr+1}")
