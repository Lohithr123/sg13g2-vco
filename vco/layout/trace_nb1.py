# XSW1's source extracts as nb1 — its own gate net. The gate contact and the
# drain bus both sit above the device, so one of them is reaching the other.
# Trace the nb1 net and list what it touches near XSW1, rather than inferring.

import pya

ly = pya.Layout()
ly.read("/foss/designs/vco/layout/vco_20g_routed.gds")
top = ly.top_cell()

l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
L = {"M1": (8, 0), "M2": (10, 0), "M3": (30, 0), "M4": (50, 0),
     "M5": (67, 0), "TM1": (126, 0), "TM2": (134, 0), "V1": (19, 0),
     "V2": (29, 0), "V3": (49, 0), "V4": (66, 0), "V5": (125, 0),
     "V6": (133, 0), "poly": (5, 0), "Cont": (6, 0)}
for k, (a, b) in L.items():
    l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(a, b))), k)
    l2n.connect(l2n.layer_by_name(k))
for v, (a, b) in [("V1", ("M1", "M2")), ("V2", ("M2", "M3")),
                  ("V3", ("M3", "M4")), ("V4", ("M4", "M5")),
                  ("V5", ("M5", "TM1")), ("V6", ("TM1", "TM2")),
                  ("Cont", ("poly", "M1"))]:
    l2n.connect(l2n.layer_by_name(a), l2n.layer_by_name(v))
    l2n.connect(l2n.layer_by_name(v), l2n.layer_by_name(b))
l2n.extract_netlist()

n = l2n.probe_net(l2n.layer_by_name("M2"), pya.DPoint(-8.51, -108.0))
print("net at XSW0 pin:", n.expanded_name() if n else "none")

for lyr in ("poly", "M1", "M2", "M5"):
    r = l2n.shapes_of_net(n, l2n.layer_by_name(lyr))
    near = [p.bbox().to_dtype(ly.dbu) for p in r.each()]
    near = [b for b in near if -30 < b.left < -12 and -196 < b.bottom < -182]
    if not near:
        continue
    print(f"\n  {lyr}: {len(near)} shapes near XSW1")
    for b in sorted(near, key=lambda q: q.bottom):
        tag = ""
        if b.width() > 1.5:
            tag = "   <-- spans the device"
        print(f"     x {b.left:8.3f}..{b.right:8.3f}  "
              f"y {b.bottom:9.3f}..{b.top:9.3f}{tag}")
