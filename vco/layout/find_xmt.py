import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
for inst in top.each_inst():
    b=inst.dbbox()
    if abs(b.center().y + 190) > 3 or b.width() < 10: continue
    nm=ly.cell(inst.cell_index).name
    print(f"\n{nm} bbox {b.to_s()}")
    for lay,dt,t in [(8,0,"Metal1"),(5,0,"GatPoly"),(10,0,"Metal2")]:
        li=ly.layer(lay,dt)
        shs=list(ly.cell(inst.cell_index).shapes(li).each())
        print(f"  {t}: {len(shs)} shapes")
        for sh in shs[:5]:
            sb=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"     x {sb.left:8.2f}..{sb.right:8.2f}  y {sb.bottom:8.2f}..{sb.top:8.2f}")
