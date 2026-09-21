import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
for inst in top.each_inst():
    bb=inst.dbbox()
    if abs(bb.center().x+20)>3 or abs(bb.center().y+190)>3: continue
    cell=ly.cell(inst.cell_index)
    polys=sorted((sh.dbbox().transformed(inst.dcplx_trans)
                  for sh in cell.shapes(ly.layer(5,0)).each()),
                 key=lambda q:q.center().x)
    strips=sorted((sh.dbbox().transformed(inst.dcplx_trans)
                   for sh in cell.shapes(ly.layer(8,0)).each()
                   if sh.dbbox().width()<0.25 and sh.dbbox().height()>2),
                  key=lambda q:q.center().x)
    gx=polys[0].center().x
    print(f"leftmost gate x {gx:.3f}")
    print(f"strips x: {[round(s.center().x,2) for s in strips[:4]]}")
    print(f"instance top y {bb.top:.3f}, strips top y {strips[0].top:.3f}")
    W=pya.DBox(gx-1.2, strips[0].top-0.3, gx+1.5, bb.top)
    for lay,nm in ((10,"M2"),(8,"M1"),(5,"poly")):
        r=pya.Region(top.begin_shapes_rec(ly.layer(lay,0))) & pya.Region(W.to_itype(ly.dbu))
        print(f"  {nm}:")
        for p in sorted(r.merged().each(), key=lambda q:q.bbox().left)[:6]:
            b=p.bbox().to_dtype(ly.dbu)
            print(f"     x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
    break
