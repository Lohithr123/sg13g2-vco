import pya
ly=pya.Layout(); ly.read("vco_20g.gds")
top=ly.top_cell()
for inst in top.each_inst():
    nm=ly.cell(inst.cell_index).name
    b=inst.dbbox()
    if b.center().y > -100 or b.center().y < -135: continue
    if not (nm.startswith("cmim") or nm.startswith("nmos")): continue
    print(f"\n{nm} at ({b.center().x:+.2f},{b.center().y:.2f})")
    for lay,dt,t in [(126,0,"TM1_top"),(67,0,"M5_bot"),(8,2,"M1.pin"),(5,2,"poly.pin")]:
        for sh in ly.cell(inst.cell_index).shapes(ly.layer(lay,dt)).each():
            sb=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"   {t:9} x {sb.left:8.2f}..{sb.right:8.2f}  y {sb.bottom:9.2f}..{sb.top:9.2f}")
