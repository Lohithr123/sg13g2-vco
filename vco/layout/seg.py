import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
# Every Metal4 shape crossing XSW0's row, with its full extent.
W = pya.DBox(-30, -111, 30, -105)
r = pya.Region(top.shapes(ly.layer(50, 0))) & pya.Region(W.to_itype(ly.dbu))
print(f"Metal4 crossing XSW0's row: {r.count()}")
for p in sorted(r.each(), key=lambda q: -q.area()):
    b = p.bbox().to_dtype(ly.dbu)
    print(f"   x {b.left:9.3f}..{b.right:9.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
