import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
flat=ly.create_cell("_f"); flat.copy_tree(top)
m1=pya.Region(flat.begin_shapes_rec(ly.layer(8,0)))
print(f"unmerged Metal1 shapes in region: ")
win=pya.Region(pya.DBox(-16,-112,16,-96).to_itype(ly.dbu))
for p in (m1 & win).each():
    b=p.bbox().to_dtype(ly.dbu)
    print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
