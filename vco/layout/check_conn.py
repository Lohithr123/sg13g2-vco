import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
m1=ly.layer(8,0)
# flatten so device geometry and route geometry are in the same space
flat=ly.create_cell("flat"); flat.copy_tree(top)
r=pya.Region(flat.begin_shapes_rec(m1)).merged()
# a connected route+collector merges into one polygon; a gap leaves two
for x in (-9.0, 9.0):
    probe=pya.Region(pya.DBox(x-1.0, -100.0, x+1.0, -87.0).to_itype(ly.dbu))
    hit=r & probe
    print(f"x={x:+5.1f}: {hit.count()} merged polygon(s) between y -100 and -87")
    for p in hit.each():
        b=p.bbox().to_dtype(ly.dbu)
        print(f"         y {b.bottom:.2f}..{b.top:.2f}")
