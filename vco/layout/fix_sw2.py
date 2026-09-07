import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The guard-ring stack at x -8 spans Metal1 to TopMetal1 and so passes through
# Metal2 at the exact point the band-select line leaves the gate, and Metal5
# where the tail runs nearby. The ring is 3.4 um wide, so the stack can sit at
# its far edge instead of its centre — 3 um from the gate and its control line.
old = '''        b = dev.dbbox()
        gnd_pts.append((nm + "_ring", b.center().x, b.bottom + 0.15))'''
new = '''        b = dev.dbbox()
        # Contact the ring at its left edge, away from the gate and the
        # source/drain stacks that sit near the centre of the device.
        gnd_pts.append((nm + "_ring", b.left + 0.15, b.center().y))'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("guard rings contacted at their left edge")
