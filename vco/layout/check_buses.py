# Are the two mirror gate buses actually shorted, or connected through the
# reference devices?
#
# XMR1 is diode-connected in a cascode reference: its gate ties to its own
# drain, and XMR2's gate ties to the node above. If the two buses extract as
# one net, either the routing shorted them, or the reference wiring joins them
# legitimately through a device — and only one of those is a bug.

import pya

ly = pya.Layout()
ly.read("/foss/designs/vco/layout/vco_20g_routed.gds")
top = ly.top_cell()

l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
LMAP = {"M1": (8, 0), "M2": (10, 0), "M3": (30, 0), "M4": (50, 0),
        "M5": (67, 0), "TM1": (126, 0), "V1": (19, 0), "V2": (29, 0),
        "V3": (49, 0), "V4": (66, 0), "V5": (125, 0)}
for k, (a, b) in LMAP.items():
    l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(a, b))), k)
    l2n.connect(l2n.layer_by_name(k))
for v, (a, b) in [("V1", ("M1", "M2")), ("V2", ("M2", "M3")),
                  ("V3", ("M3", "M4")), ("V4", ("M4", "M5")),
                  ("V5", ("M5", "TM1"))]:
    l2n.connect(l2n.layer_by_name(a), l2n.layer_by_name(v))
    l2n.connect(l2n.layer_by_name(v), l2n.layer_by_name(b))
l2n.extract_netlist()

n = l2n.probe_net(l2n.layer_by_name("M2"), pya.DPoint(-30.0, -212.0))
if n is None:
    print("no net at the cascode bus probe")
    raise SystemExit

print(f"cascode bus is net {n.expanded_name()}")
print("\nMetal2 shapes on it, sorted by y:")
r = l2n.shapes_of_net(n, l2n.layer_by_name("M2"), True)
boxes = sorted((p.bbox().to_dtype(ly.dbu) for p in r.each()),
               key=lambda b: b.bottom)
for b in boxes:
    tag = ""
    if b.width() > 100:
        tag = "  <-- a bus spine"
    print(f"   x {b.left:9.2f}..{b.right:9.2f}  y {b.bottom:9.2f}..{b.top:9.2f}"
          f"   {b.width():7.2f} x {b.height():5.2f}{tag}")

spines = [b for b in boxes if b.width() > 100]
print(f"\n{len(spines)} bus spine(s) on this net")
if len(spines) > 1:
    print("Both spines are on the same net — they are shorted somewhere.")
    print("Look for a shape that touches both y bands:")
    for b in boxes:
        if b.bottom < -211.0 and b.top > -219.0 and b.width() < 100:
            print(f"   BRIDGE x {b.left:.2f}..{b.right:.2f}  "
                  f"y {b.bottom:.2f}..{b.top:.2f}")
