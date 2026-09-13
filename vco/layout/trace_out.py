import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
flat=ly.create_cell("_f"); flat.copy_tree(top)
m5=pya.Region(flat.begin_shapes_rec(ly.layer(67,0))).merged()
win=pya.Region(pya.DBox(-160,-220,160,-90).to_itype(ly.dbu))
print("Metal5 polygons spanning both sides:")
for p in (m5&win).each():
    b=p.bbox().to_dtype(ly.dbu)
    if b.left < -50 and b.right > 50:
        print(f"  x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:9.2f}..{b.top:9.2f}")
