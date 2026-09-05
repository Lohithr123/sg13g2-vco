import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
for inst in top.each_inst():
    nm=ly.cell(inst.cell_index).name
    if nm!="npn13G2": continue
    b=inst.dbbox()
    if abs(b.center().x)>20: continue
    print(f"\n{nm} at x={b.center().x:+.2f}")
    for lay,dt,t in [(10,0,"Metal2"),(19,0,"Via1"),(8,0,"Metal1")]:
        li=ly.layer(lay,dt)
        for sh in ly.cell(inst.cell_index).shapes(li).each():
            sb=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"   {t:7} x {sb.left:7.2f}..{sb.right:7.2f}  y {sb.bottom:8.2f}..{sb.top:8.2f}")
