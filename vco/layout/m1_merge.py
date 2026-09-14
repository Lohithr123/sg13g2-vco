import pya

ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
W = pya.DBox(-146, -207, -114, -193)
wr = pya.Region(W.to_itype(ly.dbu))

# What I draw, in the top cell only.
mine = pya.Region(top.shapes(ly.layer(8, 0))) & wr
print(f"Metal1 I draw here: {mine.count()} shapes")
for p in sorted(mine.each(), key=lambda q: -q.area())[:6]:
    b = p.bbox().to_dtype(ly.dbu)
    print(f"   x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:8.2f}..{b.top:8.2f}"
          f"   {b.width():.2f} x {b.height():.2f}")

# What the PCell contains.
pc = (pya.Region(top.begin_shapes_rec(ly.layer(8, 0))) - mine) & wr
print(f"\nMetal1 from the PCell: {pc.count()} shapes, "
      f"{pc.merged().count()} after merging")

# And the two together.
both = (mine + pc).merged()
print(f"together: {both.count()} merged polygon(s)")
for p in sorted(both.each(), key=lambda q: -q.area())[:3]:
    b = p.bbox().to_dtype(ly.dbu)
    print(f"   x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:8.2f}..{b.top:8.2f}")
