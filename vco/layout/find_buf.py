import pya
ly=pya.Layout(); ly.read("vco_20g.gds")
top=ly.top_cell()
for inst in top.each_inst():
    nm=ly.cell(inst.cell_index).name
    b=inst.dbbox()
    if "npn" not in nm or abs(b.center().y + 95) > 5: continue
    print(f"\n=== {nm} at ({b.center().x:+.2f},{b.center().y:.2f}) "
          f"{b.width():.2f} x {b.height():.2f} ===")
    for sh in ly.cell(inst.cell_index).shapes(ly.layer(63,0)).each():
        if sh.is_text():
            p=inst.dcplx_trans.trans(pya.DPoint(sh.text.x*ly.dbu, sh.text.y*ly.dbu))
            print(f"   LABEL '{sh.text.string}' at {p.x:.2f},{p.y:.2f}")
    for lay,dt,t in [(8,0,"M1"),(10,0,"M2"),(19,0,"Via1")]:
        shs=list(ly.cell(inst.cell_index).shapes(ly.layer(lay,dt)).each())
        print(f"   {t}: {len(shs)} shapes")
        for sh in shs[:6]:
            sb=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"      x {sb.left:8.2f}..{sb.right:8.2f}  y {sb.bottom:9.2f}..{sb.top:9.2f}")
