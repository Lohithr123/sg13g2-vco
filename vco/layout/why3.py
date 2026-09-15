import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
L = {"M1":(8,0),"M2":(10,0),"M3":(30,0),"M4":(50,0),"M5":(67,0),
     "TM1":(126,0),"TM2":(134,0),"V1":(19,0),"V2":(29,0),"V3":(49,0),
     "V4":(66,0),"V5":(125,0),"V6":(133,0)}
for k,(a,b) in L.items():
    l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(a,b))), k)
    l2n.connect(l2n.layer_by_name(k))
for v,(a,b) in [("V1",("M1","M2")),("V2",("M2","M3")),("V3",("M3","M4")),
                ("V4",("M4","M5")),("V5",("M5","TM1")),("V6",("TM1","TM2"))]:
    l2n.connect(l2n.layer_by_name(a), l2n.layer_by_name(v))
    l2n.connect(l2n.layer_by_name(v), l2n.layer_by_name(b))
l2n.extract_netlist()

# XMB2A drain and source are both "outbp". Which shapes carry that net through
# the device? List them sorted by y so the path is visible.
n = l2n.probe_net(l2n.layer_by_name("M2"), pya.DPoint(-142.42, -200.0))
print("net there:", n.expanded_name() if n else "none")
for k in ("M1","M2","M5"):
    r = l2n.shapes_of_net(n, l2n.layer_by_name(k))
    got = [p.bbox().to_dtype(ly.dbu) for p in r.each()]
    near = [b for b in got if -210 < b.bottom < -190 and -150 < b.left < -110]
    print(f"\n  {k}: {len(near)} shapes at XMB2A")
    for b in sorted(near, key=lambda q: q.bottom)[:8]:
        print(f"     x {b.left:9.3f}..{b.right:9.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
