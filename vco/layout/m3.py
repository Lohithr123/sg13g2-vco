import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
for tag, W in [("XSW1 x-8 y-130", pya.DBox(-11, -135, -5, -125)),
               ("XMB2A x-130 y-200", pya.DBox(-147, -208, -113, -192))]:
    wr = pya.Region(W.to_itype(ly.dbu))
    mine = pya.Region(top.shapes(ly.layer(10, 0))) & wr
    m = (pya.Region(top.begin_shapes_rec(ly.layer(10, 0))) & wr).merged()
    print(f"\n{tag}: {mine.count()} of mine, {m.count()} merged")
    for p in sorted(m.each(), key=lambda q: -q.area())[:3]:
        b = p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}"
              f"   {b.width():.3f} x {b.height():.3f}")
