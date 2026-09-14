import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
W = pya.DBox(-146, -207, -114, -193)
wr = pya.Region(W.to_itype(ly.dbu))
mine = pya.Region(top.shapes(ly.layer(8, 0))) & wr
pc = (pya.Region(top.begin_shapes_rec(ly.layer(8, 0))) - mine) & wr

print("PCell alone:", pc.merged().count(), "polygons")
print("Mine alone:", mine.merged().count(), "polygons")
print("Together:", (mine + pc).merged().count(), "polygons")
print("\nMy shapes that touch the PCell's guard ring:")
ring = [p for p in pc.each() if p.bbox().to_dtype(ly.dbu).width() > 20]
rr = pya.Region(ring)
for p in mine.each():
    if not (pya.Region(p) & rr).is_empty():
        b = p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:8.2f}..{b.top:8.2f}")
