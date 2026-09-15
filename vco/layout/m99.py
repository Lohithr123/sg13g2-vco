import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
# XSW1 is the remaining short. Find its pins, then every Metal2 shape I draw
# across it.
for inst in top.each_inst():
    b = inst.dbbox()
    if abs(b.center().x + 8) > 2 or abs(b.center().y + 130) > 2:
        continue
    for sh in ly.cell(inst.cell_index).shapes(ly.layer(8, 2)).each():
        sb = sh.dbbox().transformed(inst.dcplx_trans)
        print(f"  pin x {sb.left:8.3f}..{sb.right:8.3f}")
    break
W = pya.DBox(-11, -136, -5, -124)
mine = pya.Region(top.shapes(ly.layer(10, 0))) & pya.Region(W.to_itype(ly.dbu))
print(f"\nMetal2 I draw there: {mine.count()}")
for p in sorted(mine.each(), key=lambda q: -q.area())[:6]:
    b = p.bbox().to_dtype(ly.dbu)
    print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
