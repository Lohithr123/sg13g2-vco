import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
W = pya.DBox(-11.0, -112.0, -5.0, -104.0)
for lay, dt, nm in [(8, 0, "M1"), (10, 0, "M2")]:
    r = (pya.Region(top.begin_shapes_rec(ly.layer(lay, dt)))
         & pya.Region(W.to_itype(ly.dbu))).merged()
    print(f"\n{nm}: {r.count()} merged polygon(s)")
    for p in r.each():
        b = p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
