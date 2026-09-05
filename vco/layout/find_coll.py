import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
for inst in top.each_inst():
    nm=ly.cell(inst.cell_index).name
    if "npn" not in nm: continue
    b=inst.dbbox()
    if abs(b.center().x) > 20: continue      # keep only the cross-coupled pair
    print(f"\n{nm} bbox {b.to_s()}")
    m1=ly.layer(8,0)
    for sh in ly.cell(inst.cell_index).shapes(m1).each():
        sb=sh.dbbox().transformed(inst.dcplx_trans)
        print(f"   M1 x {sb.left:7.2f}..{sb.right:7.2f}  y {sb.bottom:8.2f}..{sb.top:8.2f}")
