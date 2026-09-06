import pya
ly=pya.Layout(); ly.read("vco_20g.gds")
top=ly.top_cell()
for inst in top.each_inst():
    nm=ly.cell(inst.cell_index).name
    b=inst.dbbox()
    if not nm.startswith("cmim"): continue
    if b.center().y < -160 or b.center().y > -100: continue
    print(f"\n{nm} at ({b.center().x:+.2f},{b.center().y:.2f})  {b.width():.2f} x {b.height():.2f}")
    for lay,dt,t in [(126,0,"TopMetal1"),(67,0,"Metal5"),(36,0,"MIM"),(129,0,"Vmim")]:
        for sh in ly.cell(inst.cell_index).shapes(ly.layer(lay,dt)).each():
            sb=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"   {t:10} x {sb.left:8.2f}..{sb.right:8.2f}  y {sb.bottom:9.2f}..{sb.top:9.2f}")
print("\n--- bank switches ---")
for inst in top.each_inst():
    nm=ly.cell(inst.cell_index).name
    b=inst.dbbox()
    if not nm.startswith("nmos"): continue
    if b.center().y < -140 or b.center().y > -100: continue
    print(f"\n{nm} at ({b.center().x:+.2f},{b.center().y:.2f})")
    for lay,dt,t in [(8,2,"M1.pin"),(5,2,"poly.pin")]:
        for sh in ly.cell(inst.cell_index).shapes(ly.layer(lay,dt)).each():
            sb=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"   {t:9} x {sb.left:8.2f}..{sb.right:8.2f}  y {sb.bottom:9.2f}..{sb.top:9.2f}")
