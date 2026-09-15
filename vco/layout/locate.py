import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
for inst in top.each_inst():
    b = inst.dbbox()
    if abs(b.center().x + 130) > 3 or abs(b.center().y + 200) > 3:
        continue
    cell = ly.cell(inst.cell_index)
    print(f"{cell.name} at ({b.center().x:.1f},{b.center().y:.1f})")
    for sh in cell.shapes(ly.layer(8, 2)).each():
        sb = sh.dbbox().transformed(inst.dcplx_trans)
        print(f"   M1.pin x {sb.left:9.3f}..{sb.right:9.3f}  "
              f"y {sb.bottom:9.3f}..{sb.top:9.3f}")
    break
