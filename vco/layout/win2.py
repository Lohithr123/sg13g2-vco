import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
flat=ly.create_cell("_f"); flat.copy_tree(top)
W=pya.DBox(44.0, -165.0, 47.0, -162.5)
for li in ly.layer_indexes():
    i=ly.get_info(li)
    r=pya.Region(flat.begin_shapes_rec(li)) & pya.Region(W.to_itype(ly.dbu))
    if r.is_empty(): continue
    print(f"  {i.layer}/{i.datatype}:")
    for p in r.each():
        b=p.bbox().to_dtype(ly.dbu)
        print(f"     x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
