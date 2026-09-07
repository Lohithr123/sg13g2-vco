# What are nb0 and nb1 actually connected to?
#
# The expected-grouping check says both fail, but it only reports that the
# group does not match — not what it matched instead. Print the full net for
# each so the answer is visible rather than guessed.

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

PROBES = {
    "gnd":       (0.0, -300.0, "TM1"),
    "gnd_xmt1":  (-155.0, -300.0, "TM1"),
    "gnd_ring":  (155.0, -300.0, "TM1"),
    "nb0":       (-33.0, -143.0, "M2"),
    "nb1":       (-38.0, -143.0, "M2"),
    "casc_bus":  (-30.0, -212.0, "M2"),
    "lower_bus": (-30.0, -218.0, "M2"),
    "XQ1_C":     (-9.0, -99.1, "M1"),
    "XQ2_C":     (9.0, -99.1, "M1"),
    "XQ1_E":     (-9.0, -100.23, "M2"),
}

seen = {}
for nm, (x, y, lyr) in PROBES.items():
    n = l2n.probe_net(l2n.layer_by_name(lyr), pya.DPoint(x, y))
    seen[nm] = n.expanded_name() if n else "NONE"

groups = {}
for nm, net in seen.items():
    groups.setdefault(net, []).append(nm)

print("probe -> net:")
for nm, net in seen.items():
    print(f"  {nm:10} {net}")
print("\ngrouped:")
for net, members in sorted(groups.items()):
    print(f"  {net:8} {', '.join(sorted(members))}")

# What does nb0's net actually contain?
n0 = l2n.probe_net(l2n.layer_by_name("M2"), pya.DPoint(-33.0, -116.0))
if n0:
    print(f"\nnb0 is net {n0.expanded_name()}; Metal2 shapes on it:")
    r = l2n.shapes_of_net(n0, l2n.layer_by_name("M2"), True)
    for p in list(r.each())[:16]:
        b = p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:9.2f}..{b.right:9.2f}  y {b.bottom:9.2f}..{b.top:9.2f}")
else:
    print("\nnb0 probe found no net — the route may not reach that point")
