import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
for inst in top.each_inst():
    b=inst.dbbox()
    if b.center().y > -260 or b.height() < 5: continue
    nm=ly.cell(inst.cell_index).name
    print(f"\n{nm} bbox {b.to_s()}")
    li=ly.layer(8,0)
    n=0
    for sh in ly.cell(inst.cell_index).shapes(li).each():
        sb=sh.dbbox().transformed(inst.dcplx_trans)
        print(f"   M1 x {sb.left:8.2f}..{sb.right:8.2f}  y {sb.bottom:8.2f}..{sb.top:8.2f}")
        n+=1
        if n>6: break
