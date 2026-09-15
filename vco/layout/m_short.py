import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()

# XSW0 at x -8, y -108. Its drain and source are one net. Find every shape on
# each layer across the device and show which polygons merge, so the bridge is
# read rather than inferred.
W = pya.DBox(-10.5, -112.5, -5.5, -103.5)
wr = pya.Region(W.to_itype(ly.dbu))
for lay, dt, nm in [(6,0,"Cont"), (8,0,"M1"), (19,0,"Via1"), (10,0,"M2")]:
    r = pya.Region(top.begin_shapes_rec(ly.layer(lay, dt))) & wr
    m = r.merged()
    print(f"\n{nm}: {r.count()} shapes -> {m.count()} merged")
    for p in sorted(m.each(), key=lambda q: -q.area())[:4]:
        b = p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}"
              f"   {b.width():.3f} x {b.height():.3f}")
