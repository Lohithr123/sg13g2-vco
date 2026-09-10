import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# V1.a: Via1 must be exactly 0.19 um, and the PCell stack produced 0.19 x 0.365
# — two vias merging. V1.b wants 0.22 um between vias, M1.b 0.18 um between
# Metal1 shapes.
#
# The pads are 0.6 um square with 0.39 um to each neighbour, so there is room.
# Draw the via and its Metal2 landing directly instead of instantiating a
# stack: one 0.19 um square of Via1, with Metal1 below and Metal2 above.
old = '''            top.shapes(LI["M1"]).insert(pya.DBox(
                snap(x - PAD), snap(ylev - PAD),
                snap(x + PAD), snap(ylev + PAD)))
            drop(x, ylev, "M2", cols=1, rows=1)'''
new = '''            for lyr in ("M1", "M2"):
                top.shapes(LI[lyr]).insert(pya.DBox(
                    snap(x - PAD), snap(ylev - PAD),
                    snap(x + PAD), snap(ylev + PAD)))
            top.shapes(layout.layer(19, 0)).insert(pya.DBox(
                snap(x - 0.095), snap(ylev - 0.095),
                snap(x + 0.095), snap(ylev + 0.095)))'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("vias drawn directly at exactly 0.19 um")
