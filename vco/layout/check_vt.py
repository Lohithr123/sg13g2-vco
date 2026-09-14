# vt is the only unresolved port. The extracted subcircuit lists "W", which is
# the varactor PCell's own label for the well terminal, so the net exists and
# is named — just not "vt".
#
# Two possibilities, and they need different fixes:
#   a) my vt label sits on metal that is genuinely a different net from W
#   b) it is the same net, and the PCell's W label simply wins
#
# Probe both points and compare.

import pya

ly = pya.Layout()
ly.read("/foss/designs/vco/layout/vco_20g_routed.gds")
top = ly.top_cell()

l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
L = {"M1": (8, 0), "M2": (10, 0), "M3": (30, 0), "M4": (50, 0),
     "M5": (67, 0), "TM1": (126, 0), "TM2": (134, 0), "V1": (19, 0),
     "V2": (29, 0), "V3": (49, 0), "V4": (66, 0), "V5": (125, 0),
     "V6": (133, 0)}
for k, (a, b) in L.items():
    l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(a, b))), k)
    l2n.connect(l2n.layer_by_name(k))
for v, (a, b) in [("V1", ("M1", "M2")), ("V2", ("M2", "M3")),
                  ("V3", ("M3", "M4")), ("V4", ("M4", "M5")),
                  ("V5", ("M5", "TM1")), ("V6", ("TM1", "TM2"))]:
    l2n.connect(l2n.layer_by_name(a), l2n.layer_by_name(v))
    l2n.connect(l2n.layer_by_name(v), l2n.layer_by_name(b))
l2n.extract_netlist()

# Where the vt label sits, and where the varactor well actually is.
pts = [("vt label", "M2", -20.0, -155.0),
       ("well route start", "M2", -3.83, -172.0),
       ("well route mid", "M2", -20.0, -172.0)]
for nm, lyr, x, y in pts:
    n = l2n.probe_net(l2n.layer_by_name(lyr), pya.DPoint(x, y))
    print(f"  {nm:18} ({x:7.2f},{y:8.2f}) on {lyr}: "
          f"{n.expanded_name() if n else 'NO NET'}")
