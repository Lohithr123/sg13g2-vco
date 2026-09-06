import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
flat=ly.create_cell("_f"); flat.copy_tree(top)
m1=pya.Region(flat.begin_shapes_rec(ly.layer(8,0))).merged()
# the single polygon covering the pair: print its full outline
win=pya.Region(pya.DBox(-30,-130,30,-85).to_itype(ly.dbu))
for p in (m1&win).each():
    b=p.bbox().to_dtype(ly.dbu)
    if b.width()>10:
        print(f"bridging polygon: x {b.left:.2f}..{b.right:.2f} y {b.bottom:.2f}..{b.top:.2f}")
        print(f"  {p.num_points()} points")
        pts=[pya.DPoint(pt.x*ly.dbu, pt.y*ly.dbu) for pt in p.each_point_hull()]
        for q in pts[:24]:
            print(f"    {q.x:8.2f},{q.y:9.2f}")
