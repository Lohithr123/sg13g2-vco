import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()

# XMT2: find it, get its leftmost gate and its drain strips, then ask directly
# which shape touches both the gate contact and a drain strip.
for inst in top.each_inst():
    b = inst.dbbox()
    if abs(b.center().x + 130) > 3 or abs(b.center().y + 200) > 3:
        continue
    cell = ly.cell(inst.cell_index)
    polys = sorted((sh.dbbox().transformed(inst.dcplx_trans)
                    for sh in cell.shapes(ly.layer(5, 0)).each()),
                   key=lambda q: q.center().x)
    strips = sorted((sh.dbbox().transformed(inst.dcplx_trans)
                     for sh in cell.shapes(ly.layer(8, 0)).each()
                     if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
                    key=lambda q: q.center().x)
    gx = polys[0].center().x
    gy = b.top - 1.21 + 0.41
    gate_r = pya.Region(pya.DBox(gx-0.16, gy-0.16, gx+0.16, gy+0.16).to_itype(ly.dbu))
    drn = strips[1]
    drn_r = pya.Region(pya.DBox(drn.left, drn.bottom, drn.right, drn.top).to_itype(ly.dbu))
    print(f"gate contact ({gx:.3f},{gy:.3f})   drain strip x {drn.center().x:.3f}")
    for lay, dt, nm in [(5,0,"poly"),(6,0,"Cont"),(8,0,"M1"),(19,0,"Via1"),(10,0,"M2")]:
        reg = pya.Region(top.begin_shapes_rec(ly.layer(lay, dt)))
        for p in reg.each():
            pr = pya.Region(p)
            if not (pr & gate_r).is_empty() and not (pr & drn_r).is_empty():
                bb = p.bbox().to_dtype(ly.dbu)
                print(f"   BRIDGE {nm}: x {bb.left:.3f}..{bb.right:.3f}  "
                      f"y {bb.bottom:.3f}..{bb.top:.3f}")
    break
