import pya
ly=pya.Layout(); ly.read("vco_20g.gds")
top=ly.top_cell()
for inst in top.each_inst():
    nm=ly.cell(inst.cell_index).name
    b=inst.dbbox()
    if "Varicap" not in nm and not (nm.startswith("cmim") and b.width()>40):
        continue
    print(f"\n=== {nm} at ({b.center().x:+.2f},{b.center().y:.2f})  "
          f"{b.width():.2f} x {b.height():.2f} ===")
    for sh in ly.cell(inst.cell_index).shapes(ly.layer(63,0)).each():
        if sh.is_text():
            p=inst.dcplx_trans.trans(pya.DPoint(sh.text.x*ly.dbu, sh.text.y*ly.dbu))
            print(f"   LABEL '{sh.text.string}' at {p.x:.2f},{p.y:.2f}")
    for lay,dt,t in [(8,0,"M1"),(8,2,"M1.pin"),(5,0,"poly"),(5,2,"poly.pin"),
                     (126,0,"TM1"),(67,0,"M5"),(10,0,"M2")]:
        shs=list(ly.cell(inst.cell_index).shapes(ly.layer(lay,dt)).each())
        if not shs: continue
        print(f"   {t}: {len(shs)} shapes")
        for sh in shs[:4]:
            sb=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"      x {sb.left:8.2f}..{sb.right:8.2f}  y {sb.bottom:9.2f}..{sb.top:9.2f}")
