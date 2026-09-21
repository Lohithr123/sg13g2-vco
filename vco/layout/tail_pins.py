import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
for tag, xc in (("XMT2", -20.0), ("XMT1", 20.0)):
    for inst in top.each_inst():
        b = inst.dbbox()
        if abs(b.center().x - xc) > 3 or abs(b.center().y + 190) > 3:
            continue
        cell = ly.cell(inst.cell_index)
        st = sorted((sh.dbbox().transformed(inst.dcplx_trans)
                     for sh in cell.shapes(ly.layer(8, 0)).each()
                     if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
                    key=lambda q: q.center().x)
        print(f"\n{tag}: bbox x {b.left:.2f}..{b.right:.2f}  y {b.bottom:.2f}..{b.top:.2f}"
              f"  mirrored={inst.dcplx_trans.is_mirror()}")
        print(f"   {len(st)} strips, x {st[0].center().x:.2f} .. {st[-1].center().x:.2f}"
              f", y {st[0].bottom:.2f}..{st[0].top:.2f}")
        print(f"   even (bussed below): {[round(s.center().x,2) for s in st[0::2]][:4]} ...")
        print(f"   odd  (bussed above): {[round(s.center().x,2) for s in st[1::2]][:4]} ...")
        break

W = pya.DBox(-12, -196, 12, -184)
for lay, nm in ((10, "M2"), (30, "M3"), (50, "M4"), (67, "M5")):
    r = pya.Region(top.begin_shapes_rec(ly.layer(lay, 0))) & pya.Region(W.to_itype(ly.dbu))
    print(f"\n{nm} in the gap between them (x -12..12, y -196..-184):")
    for p in sorted(r.merged().each(), key=lambda q: q.bbox().left)[:6]:
        bb = p.bbox().to_dtype(ly.dbu)
        print(f"   x {bb.left:8.2f}..{bb.right:8.2f}  y {bb.bottom:8.2f}..{bb.top:8.2f}")
