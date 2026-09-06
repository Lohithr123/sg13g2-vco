import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
l2n=pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
for lay,dt,nm in [(8,0,"M1"),(10,0,"M2"),(30,0,"M3"),(19,0,"V1"),(29,0,"V2")]:
    l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(lay,dt))), nm)
for a in ["M1","M2","M3","V1","V2"]:
    if l2n.layer_by_name(a): l2n.connect(l2n.layer_by_name(a))
for a,b in [("M1","V1"),("V1","M2"),("M2","V2"),("V2","M3")]:
    if l2n.layer_by_name(a) and l2n.layer_by_name(b):
        l2n.connect(l2n.layer_by_name(a), l2n.layer_by_name(b))
l2n.extract_netlist()
n=l2n.probe_net(l2n.layer_by_name("M1"), pya.DPoint(-9.0,-99.1))
print("net:", n.expanded_name())
for nm in ["M1","M2","M3"]:
    li=l2n.layer_by_name(nm)
    if not li: continue
    r=l2n.shapes_of_net(n, li, True)
    print(f"\n{nm}: {r.count()} shapes")
    for p in list(r.each())[:14]:
        b=p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:9.2f}..{b.top:9.2f}")
