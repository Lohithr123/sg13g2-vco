import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
for tag, yc in (("XSW0", -108.0), ("XSW1", -130.0)):
    print(f"\n=== {tag} at y {yc} ===")
    for inst in top.each_inst():
        b = inst.dbbox()
        if abs(b.center().x + 8) > 2 or abs(b.center().y - yc) > 2:
            continue
        for sh in ly.cell(inst.cell_index).shapes(ly.layer(8, 2)).each():
            sb = sh.dbbox().transformed(inst.dcplx_trans)
            print(f"  pin   x {sb.left:8.3f}..{sb.right:8.3f}")
        break
    W = pya.DBox(-11, yc - 5, -5, yc + 5)
    for lay, nm in ((10, "M2"), (67, "M5")):
        r = pya.Region(top.shapes(ly.layer(lay, 0))) & pya.Region(W.to_itype(ly.dbu))
        for p in sorted(r.each(), key=lambda q: -q.area())[:5]:
            bb = p.bbox().to_dtype(ly.dbu)
            print(f"  {nm}    x {bb.left:8.3f}..{bb.right:8.3f}  "
                  f"y {bb.bottom:9.3f}..{bb.top:9.3f}")
