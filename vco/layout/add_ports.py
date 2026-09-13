import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

block = '''
print("\\n=== port labels ===")
# LVS extracted the layout as ".SUBCKT vco_20g G1 G2 W" — three ports, and
# those are the varactor PCell's own labels leaking through. Nothing else in
# the layout is named, so the comparison had no anchors at all: every net was
# an anonymous $n and could match anything or nothing.
#
# The deck reads net names from datatype 25 on each metal — metal1_text is
# labels(8, 25), metal2_text labels(10, 25), and so on. A text object on the
# right layer, sitting on the right piece of metal, names that net.
#
# One label per top-level port, placed where that net actually runs.

PORTS = [
    # (name, layer, x, y)
    ("vcc",   "TM2", 0.0,    -160.0),   # supply rail
    ("gnd",   "TM1", 0.0,    -300.0),   # ground rail
    ("vg",    "M2",  -120.0, -150.0),   # varactor gate bias
    ("vt",    "M2",  -20.0,  -155.0),   # tune input, on the well route
    ("nb0",   "M2",  -38.0,  -145.0),   # band select
    ("nb1",   "M2",  -33.0,  -145.0),
    ("outbp", "M5",  -145.0, -95.23),   # buffer outputs
    ("outbn", "M5",  145.0,  -95.23),
]

_TEXTLAYER = {"M1": (8, 25), "M2": (10, 25), "M3": (30, 25), "M4": (50, 25),
              "M5": (67, 25), "TM1": (126, 25), "TM2": (134, 25)}

for nm, lyr, px, py in PORTS:
    li = layout.layer(*_TEXTLAYER[lyr])
    top.shapes(li).insert(pya.DText(nm, pya.DTrans(snap(px), snap(py))))
    print(f"  {nm:6} on {lyr:4} at ({px:7.1f},{py:8.1f})")

'''

s = s.replace('layout.write(OUT)', block + 'layout.write(OUT)')
p.write_text(s)
print("port labelling added")
