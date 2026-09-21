import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
l2n=pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
L={"M1":(8,0),"M2":(10,0),"M3":(30,0),"M4":(50,0),"M5":(67,0),
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
for y in (-99.5, -101.0, -103.0, -105.0, -110.0, -150.0):
    n=l2n.probe_net(l2n.layer_by_name("M4"), pya.DPoint(16.0, y))
    print(f"  M4 at (16, {y:7.1f}): {n.expanded_name() if n else 'NO METAL'}")
r=pya.Region(top.shapes(ly.layer(50,0))) & pya.Region(pya.DBox(14,-108,18,-98).to_itype(ly.dbu))
print("\nMetal4 shapes near x 16:")
for p in sorted(r.each(), key=lambda q:q.bbox().top, reverse=True):
    b=p.bbox().to_dtype(ly.dbu)
    print(f"   x {b.left:7.2f}..{b.right:7.2f}  y {b.bottom:8.2f}..{b.top:8.2f}")
