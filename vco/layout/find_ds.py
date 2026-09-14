import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
# XSW0 sits at x -8, y -108. Its source bus is at 20% of the strip height and
# its drain bus at 50%; both are Metal2 plus the Metal1 pads. Print every
# Metal1 and Metal2 shape across the device so the bridge is visible.
W = pya.DBox(-11.0, -111.5, -5.0, -104.5)
for lay, dt, nm in [(8, 0, "M1"), (10, 0, "M2")]:
    r = pya.Region(top.begin_shapes_rec(ly.layer(lay, dt))) & \
        pya.Region(W.to_itype(ly.dbu))
    print(f"\n{nm}: {r.merged().count()} merged polygon(s)")
    for p in r.merged().each():
        b = p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
