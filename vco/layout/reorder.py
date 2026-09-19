import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()
lines = s.split('\n')

# The gate bus block starts at the "mirror gate buses" banner and runs until
# the next top-level banner. Find both boundaries by content, not line number.
start = next(i for i, l in enumerate(lines)
             if '=== mirror gate buses ===' in l)
end = next(i for i in range(start + 1, len(lines))
           if lines[i].startswith('print("\\n=== ') and i > start)

block = lines[start:end]

# The commoning block ends just before layout.write(OUT).
rest = lines[:start] + lines[end:]
wr = next(i for i, l in enumerate(rest) if l.startswith('layout.write(OUT)'))

out = rest[:wr] + [
    '# The gate bus runs AFTER the finger commoning: it contacts the poly bar',
    '# that bus_fingers draws, and reads POLYBAR and _COMB which the commoning',
    '# populates. Running it first — as it did — meant the contact was placed',
    '# before the thing it contacts existed, which is why all eight mirror',
    '# gates extracted as isolated nets.',
    '',
] + block + [''] + rest[wr:]

p.write_text('\n'.join(out))
print(f"moved {len(block)} lines of gate-bus code after the commoning")
