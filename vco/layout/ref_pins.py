import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
# The reference branch: XMR2 at x -55 and XMR1 at x -42, both y -190.
# Netlist wants MMR2 = NC NC NB (gate tied to drain) and MMR1 = NB NB GND.
for tag, xc in (("XMR2", -55.0), ("XMR1", -42.0)):
    for inst in top.each_inst():
        b = inst.dbbox()
        if abs(b.center().x - xc) > 2 or abs(b.center().y + 190) > 2:
            continue
        cell = ly.cell(inst.cell_index)
        print(f"\n{tag}: bbox x {b.left:.2f}..{b.right:.2f}  y {b.bottom:.2f}..{b.top:.2f}")
        strips = sorted((sh.dbbox().transformed(inst.dcplx_trans)
                         for sh in cell.shapes(ly.layer(8, 0)).each()
                         if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
                        key=lambda q: q.center().x)
        for i, s in enumerate(strips):
            kind = "source" if i % 2 == 0 else "drain"
            print(f"   strip {i} ({kind}): x {s.center().x:8.3f}  y {s.bottom:.3f}..{s.top:.3f}")
        polys = sorted((sh.dbbox().transformed(inst.dcplx_trans)
                        for sh in cell.shapes(ly.layer(5, 0)).each()),
                       key=lambda q: q.center().x)
        for p in polys:
            print(f"   gate      : x {p.center().x:8.3f}")
        break
