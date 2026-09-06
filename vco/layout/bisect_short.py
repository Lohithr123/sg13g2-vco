# Which routing group causes the short?
#
# Eleven fixes have each addressed a plausible bridge and none has cleared it,
# which means the bridge is somewhere I have not been looking. Rather than
# guess a twelfth time, build the layout in stages and extract after each: the
# stage that merges the nets is the one at fault.

import os
import sys

import pya

PDK = os.environ.get("PDK_ROOT", "/foss/pdks") + "/ihp-sg13g2"
sys.path.insert(0, PDK + "/libs.tech/klayout/python")
import sg13g2_pycell_lib  # noqa: F401

src = open("/foss/designs/vco/layout/route_v2.py").read()

# Cut the script at each section boundary and run the prefix.
MARKS = [
    ("tank only",        'print("=== outn on Metal4 ===")'),
    ("+ outn",           'print("=== tail on Metal5 ===")'),
    ("+ tail",           'print("\\n=== bank branches ===")'),
    ("+ bank",           'layout.write(OUT)'),
]

probe_code = '''
_l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(layout, top, []))
_names = {"M1": (8, 0), "M2": (10, 0), "M3": (30, 0), "M4": (50, 0),
          "M5": (67, 0), "TM1": (126, 0)}
_vias = {"V1": (19, 0), "V2": (29, 0), "V3": (49, 0), "V4": (66, 0),
         "V5": (125, 0)}
for _k, (_a, _b) in {**_names, **_vias}.items():
    _l2n.register(pya.Region(top.begin_shapes_rec(layout.layer(_a, _b))), _k)
    _l2n.connect(_l2n.layer_by_name(_k))
for _v, (_a, _b) in [("V1", ("M1", "M2")), ("V2", ("M2", "M3")),
                     ("V3", ("M3", "M4")), ("V4", ("M4", "M5")),
                     ("V5", ("M5", "TM1"))]:
    _l2n.connect(_l2n.layer_by_name(_a), _l2n.layer_by_name(_v))
    _l2n.connect(_l2n.layer_by_name(_v), _l2n.layer_by_name(_b))
_l2n.extract_netlist()
_pts = {"XQ1_C": (c1.x, c1.y, "M1"), "XQ2_C": (c2.x, c2.y, "M1"),
        "XQ1_B": (b1.x, b1.y, "M1"), "XQ2_B": (b2.x, b2.y, "M1"),
        "XQ1_E": (e1.x, e1.y, "M2"), "XQ2_E": (e2.x, e2.y, "M2")}
_g = {}
for _nm, (_x, _y, _ly) in _pts.items():
    _n = _l2n.probe_net(_l2n.layer_by_name(_ly), pya.DPoint(snap(_x), snap(_y)))
    _g.setdefault(_n.expanded_name() if _n else "none", []).append(_nm)
print("   groups:", " | ".join(",".join(sorted(v)) for v in _g.values()))
'''

for tag, mark in MARKS:
    if mark not in src:
        print(f"{tag:12} marker not found, skipped")
        continue
    stage = src[:src.index(mark)] + probe_code
    print(f"\n{tag}:")
    try:
        exec(compile(stage, "<stage>", "exec"), {"__name__": "__main__"})
    except Exception as exc:
        print(f"   failed: {exc}")
