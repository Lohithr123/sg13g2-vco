import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
l2n=pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
names={"M1":(8,0),"M2":(10,0),"M3":(30,0),"M4":(50,0),"M5":(67,0),"TM1":(126,0)}
vias={"V1":(19,0),"V2":(29,0),"V3":(49,0),"V4":(66,0),"V5":(125,0)}
for k,(a,b) in {**names,**vias}.items():
    l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(a,b))), k)
    l2n.connect(l2n.layer_by_name(k))
for v,(a,b) in [("V1",("M1","M2")),("V2",("M2","M3")),("V3",("M3","M4")),
                ("V4",("M4","M5")),("V5",("M5","TM1"))]:
    l2n.connect(l2n.layer_by_name(a), l2n.layer_by_name(v))
    l2n.connect(l2n.layer_by_name(v), l2n.layer_by_name(b))
l2n.extract_netlist()
n=l2n.probe_net(l2n.layer_by_name("M1"), pya.DPoint(-9.0,-99.1))
for k in ["M3","M4","M5","TM1"]:
    r=l2n.shapes_of_net(n, l2n.layer_by_name(k), True)
    print(f"\n{k}: {r.count()} shapes on the shorted net")
    for p in list(r.each())[:10]:
        b=p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:9.2f}..{b.top:9.2f}")
