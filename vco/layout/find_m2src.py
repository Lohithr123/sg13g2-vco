import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
W = pya.DBox(-10.5, -112.5, -5.5, -103.5)
wr = pya.Region(W.to_itype(ly.dbu))
mine = pya.Region(top.shapes(ly.layer(10, 0))) & wr
print(f"Metal2 drawn in the top cell: {mine.count()} shapes")
for p in sorted(mine.each(), key=lambda q: -q.area()):
    b = p.bbox().to_dtype(ly.dbu)
    print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}"
          f"   {b.width():.3f} x {b.height():.3f}")
