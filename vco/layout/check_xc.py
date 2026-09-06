import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
flat=ly.create_cell("_f"); flat.copy_tree(top)
for lay,dt,nm in [(8,0,"Metal1"),(10,0,"Metal2")]:
    r=pya.Region(flat.begin_shapes_rec(ly.layer(lay,dt))).merged()
    win=pya.Region(pya.DBox(-16,-110,16,-96).to_itype(ly.dbu))
    hit=r&win
    print(f"\n{nm}: {hit.count()} polygons in the cross-couple region")
    for p in hit.each():
        b=p.bbox().to_dtype(ly.dbu)
        print(f"   x {b.left:7.2f}..{b.right:7.2f}  y {b.bottom:8.2f}..{b.top:8.2f}")
